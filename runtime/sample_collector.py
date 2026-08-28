from __future__ import annotations

import argparse
import hashlib
import json
from datetime import date, datetime, timedelta
from pathlib import Path
from typing import Any
from zoneinfo import ZoneInfo

import akshare as ak
import pandas as pd

from src.core.strategy_boundary import require_strategy_context


SH_TZ = ZoneInfo("Asia/Shanghai")
SHORT_MID_STRATEGY_ID = "a_share_short_mid"
SHORT_MID_SLEEVE = "short_mid"

DEFAULT_REGISTRY = Path("runtime/config/sample_registry.json")
DEFAULT_STATE_DIR = Path("runtime/state/sample_evidence")
DEFAULT_REPORT_DIR = Path("reports/daily")


def safe_call(errors: list[str], label: str, func, *args, **kwargs):
    try:
        return func(*args, **kwargs)
    except Exception as exc:  # preserve provider failure instead of fabricating data
        errors.append(f"{label}: {type(exc).__name__}: {exc}")
        return None


def load_registry(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as f:
        payload = json.load(f)
    require_strategy_context(
        strategy_id=str(payload.get("strategy_id", "")),
        sleeve=str(payload.get("sleeve", "")),
        expected_strategy_id=SHORT_MID_STRATEGY_ID,
        expected_sleeve=SHORT_MID_SLEEVE,
    )
    if not isinstance(payload.get("samples"), list):
        raise ValueError("sample registry requires a samples list")
    return payload


def to_float(value: Any) -> float | None:
    try:
        result = float(pd.to_numeric(value, errors="coerce"))
    except Exception:
        return None
    return None if pd.isna(result) else result


def to_iso_date(value: Any) -> str | None:
    try:
        parsed = pd.to_datetime(value, errors="coerce")
    except Exception:
        return None
    if pd.isna(parsed):
        return None
    return parsed.date().isoformat()


def stable_hash(payload: Any) -> str:
    raw = json.dumps(payload, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()


def market_prefix(exchange: str, code: str) -> str:
    ex = str(exchange).upper()
    if ex in {"SSE", "SH"} or code.startswith(("5", "6", "9")):
        return "sh"
    if ex in {"SZSE", "SZ"} or code.startswith(("0", "1", "2", "3")):
        return "sz"
    return "bj"


def fetch_stock_history(
    code: str,
    start_date: date,
    end_date: date,
    errors: list[str],
) -> pd.DataFrame | None:
    df = safe_call(
        errors,
        f"stock_zh_a_hist:{code}",
        ak.stock_zh_a_hist,
        symbol=code,
        period="daily",
        start_date=start_date.strftime("%Y%m%d"),
        end_date=end_date.strftime("%Y%m%d"),
        adjust="",
    )
    if df is None or df.empty:
        return None

    required = {"日期", "开盘", "收盘", "最高", "最低", "成交量", "成交额"}
    if not required.issubset(df.columns):
        errors.append(f"stock_zh_a_hist:{code}: missing columns {sorted(required - set(df.columns))}")
        return None

    out = df.copy()
    out["trade_date"] = pd.to_datetime(out["日期"], errors="coerce")
    for col in ["开盘", "收盘", "最高", "最低", "成交量", "成交额", "换手率", "涨跌幅"]:
        if col in out.columns:
            out[col] = pd.to_numeric(out[col], errors="coerce")
    out = out.dropna(subset=["trade_date", "收盘"]).sort_values("trade_date").reset_index(drop=True)
    return out if not out.empty else None


def fetch_benchmark_history(
    symbol: str,
    start_date: date,
    end_date: date,
    errors: list[str],
) -> pd.DataFrame | None:
    df = safe_call(
        errors,
        f"stock_zh_index_daily_em:{symbol}",
        ak.stock_zh_index_daily_em,
        symbol=symbol,
        start_date=start_date.strftime("%Y%m%d"),
        end_date=end_date.strftime("%Y%m%d"),
    )
    if df is None or df.empty or "date" not in df.columns or "close" not in df.columns:
        return None
    out = df.copy()
    out["trade_date"] = pd.to_datetime(out["date"], errors="coerce")
    out["close"] = pd.to_numeric(out["close"], errors="coerce")
    out = out.dropna(subset=["trade_date", "close"]).sort_values("trade_date").reset_index(drop=True)
    return out if not out.empty else None


def trailing_return_pct(closes: pd.Series, sessions: int) -> float | None:
    values = pd.to_numeric(closes, errors="coerce").dropna().reset_index(drop=True)
    if len(values) <= sessions:
        return None
    start = float(values.iloc[-(sessions + 1)])
    end = float(values.iloc[-1])
    if start <= 0:
        return None
    return (end / start - 1.0) * 100.0


def prior_mean(series: pd.Series, window: int) -> float | None:
    values = pd.to_numeric(series, errors="coerce").dropna().reset_index(drop=True)
    if len(values) <= window:
        return None
    reference = values.iloc[-(window + 1) : -1]
    if reference.empty:
        return None
    result = float(reference.mean())
    return result if result > 0 else None


def derive_price_features(
    hist: pd.DataFrame,
    benchmark: pd.DataFrame | None,
    sample: dict[str, Any],
) -> dict[str, Any]:
    latest = hist.iloc[-1]
    latest_date = latest["trade_date"].date()
    entry_date = date.fromisoformat(str(sample["entry_date"]))
    entry_cost = float(sample["actual_average_cost"])

    prev_close = None
    if len(hist) >= 2:
        prev_close = to_float(hist.iloc[-2]["收盘"])

    current_close = to_float(latest["收盘"])
    current_volume_lots = to_float(latest["成交量"])
    current_volume_shares = None if current_volume_lots is None else current_volume_lots * 100.0

    volume5 = prior_mean(hist["成交量"], 5)
    volume20 = prior_mean(hist["成交量"], 20)
    rvol5 = None if volume5 in (None, 0) or current_volume_lots is None else current_volume_lots / volume5
    rvol20 = None if volume20 in (None, 0) or current_volume_lots is None else current_volume_lots / volume20

    mas: dict[str, float | None] = {}
    for window in (5, 10, 20):
        values = pd.to_numeric(hist["收盘"], errors="coerce").dropna().tail(window)
        mas[f"ma{window}"] = float(values.mean()) if len(values) == window else None

    returns: dict[str, float | None] = {}
    for n in (1, 3, 5, 10, 15):
        returns[f"stock_return_{n}d_pct"] = trailing_return_pct(hist["收盘"], n)

    benchmark_returns: dict[str, float | None] = {}
    excess: dict[str, float | None] = {}
    if benchmark is not None and not benchmark.empty:
        benchmark = benchmark[benchmark["trade_date"].dt.date <= latest_date].copy()
        for n in (1, 3, 5, 10, 15):
            b = trailing_return_pct(benchmark["close"], n)
            benchmark_returns[f"benchmark_return_{n}d_pct"] = b
            s = returns[f"stock_return_{n}d_pct"]
            excess[f"excess_return_{n}d_pct"] = None if b is None or s is None else s - b
    else:
        for n in (1, 3, 5, 10, 15):
            benchmark_returns[f"benchmark_return_{n}d_pct"] = None
            excess[f"excess_return_{n}d_pct"] = None

    since_entry = hist[hist["trade_date"].dt.date >= entry_date].copy()
    after_entry_day = hist[hist["trade_date"].dt.date > entry_date].copy()
    holding_days = int(len(since_entry))

    # With daily bars and an unknown intraday fill time, entry-day high/low may have
    # occurred before the fill. Use next-session-onward excursion as the auditable
    # post-fill metric and keep entry-day excursion explicitly unresolved.
    mfe_price = None
    mae_price = None
    mfe_pct = None
    mae_pct = None
    if not after_entry_day.empty:
        mfe_price = to_float(after_entry_day["最高"].max())
        mae_price = to_float(after_entry_day["最低"].min())
        if mfe_price is not None:
            mfe_pct = (mfe_price / entry_cost - 1.0) * 100.0
        if mae_price is not None:
            mae_pct = (mae_price / entry_cost - 1.0) * 100.0

    peak_close = to_float(since_entry["收盘"].max()) if not since_entry.empty else None
    close_drawdown = None
    if peak_close and current_close:
        close_drawdown = (current_close / peak_close - 1.0) * 100.0

    return_vs_entry = None
    if current_close is not None and entry_cost > 0:
        return_vs_entry = (current_close / entry_cost - 1.0) * 100.0

    return {
        "trade_date": latest_date.isoformat(),
        "bar": {
            "open": to_float(latest["开盘"]),
            "high": to_float(latest["最高"]),
            "low": to_float(latest["最低"]),
            "close": current_close,
            "prev_close": prev_close,
            "volume_lots": current_volume_lots,
            "volume_shares": current_volume_shares,
            "turnover_rmb": to_float(latest["成交额"]),
            "turnover_rate_pct": to_float(latest.get("换手率")),
            "day_return_pct": to_float(latest.get("涨跌幅")),
            "price_basis": "UNADJUSTED",
        },
        "rolling": {
            **mas,
            "prior_volume_5d_mean_lots": volume5,
            "prior_volume_20d_mean_lots": volume20,
            "rvol_5d": rvol5,
            "rvol_20d": rvol20,
            **returns,
            **benchmark_returns,
            **excess,
        },
        "sample_path": {
            "entry_date": entry_date.isoformat(),
            "actual_average_cost": entry_cost,
            "holding_trading_days_inclusive": holding_days,
            "return_vs_entry_pct": return_vs_entry,
            "post_entry_excursion_basis": "NEXT_SESSION_ONWARD_DAILY_BAR",
            "entry_day_excursion_status": "UNRESOLVED_WITH_DAILY_BARS_UNLESS_INTRADAY_FILL_DATA_EXISTS",
            "MFE_price": mfe_price,
            "MFE_pct": mfe_pct,
            "MAE_price": mae_price,
            "MAE_pct": mae_pct,
            "peak_close_since_entry": peak_close,
            "current_close_drawdown_from_post_entry_peak_pct": close_drawdown,
        },
    }


def fetch_vendor_flow(sample: dict[str, Any], as_of: date, errors: list[str]) -> dict[str, Any]:
    if not sample.get("collect_vendor_flow", True):
        return {"status": "NOT_APPLICABLE"}
    code = str(sample["code"])
    prefix = market_prefix(str(sample.get("exchange", "")), code)
    df = safe_call(
        errors,
        f"stock_individual_fund_flow:{code}",
        ak.stock_individual_fund_flow,
        stock=code,
        market=prefix,
    )
    if df is None or df.empty or "日期" not in df.columns:
        return {"status": "PROVIDER_ERROR"}
    out = df.copy()
    out["_date"] = pd.to_datetime(out["日期"], errors="coerce")
    out = out[out["_date"].dt.date <= as_of].sort_values("_date")
    if out.empty:
        return {"status": "INSUFFICIENT_HISTORY"}
    row = out.iloc[-1]
    return {
        "status": "AVAILABLE",
        "source": "AKShare/Eastmoney stock_individual_fund_flow",
        "data_effective_date": row["_date"].date().isoformat(),
        "vendor_main_flow_net_rmb": to_float(row.get("主力净流入-净额")),
        "vendor_main_flow_pct": to_float(row.get("主力净流入-净占比")),
        "vendor_super_large_net_rmb": to_float(row.get("超大单净流入-净额")),
        "vendor_large_net_rmb": to_float(row.get("大单净流入-净额")),
        "vendor_medium_net_rmb": to_float(row.get("中单净流入-净额")),
        "vendor_small_net_rmb": to_float(row.get("小单净流入-净额")),
        "interpretation_boundary": "CORROBORATIVE_ONLY_NOT_INSTITUTIONAL_TRUTH",
    }


def recent_trade_dates(as_of: date, errors: list[str], limit: int = 6) -> list[date]:
    df = safe_call(errors, "tool_trade_date_hist_sina", ak.tool_trade_date_hist_sina)
    if df is None or df.empty:
        return []
    col = "trade_date" if "trade_date" in df.columns else df.columns[0]
    values = pd.to_datetime(df[col], errors="coerce").dropna().dt.date
    valid = sorted({d for d in values if d <= as_of}, reverse=True)
    return valid[:limit]


def fetch_margin_row(sample: dict[str, Any], trade_date: date, errors: list[str]) -> dict[str, Any] | None:
    code = str(sample["code"])
    exchange = str(sample.get("exchange", "")).upper()
    date_key = trade_date.strftime("%Y%m%d")

    if exchange in {"SSE", "SH"}:
        df = safe_call(errors, f"stock_margin_detail_sse:{date_key}", ak.stock_margin_detail_sse, date=date_key)
        if df is None or df.empty or "标的证券代码" not in df.columns:
            return None
        frame = df.copy()
        frame["_code"] = frame["标的证券代码"].astype(str).str.extract(r"(\d{6})", expand=False)
        rows = frame[frame["_code"] == code]
        if rows.empty:
            return None
        row = rows.iloc[0]
        return {
            "data_effective_date": trade_date.isoformat(),
            "source": "SSE via AKShare stock_margin_detail_sse",
            "financing_balance_rmb": to_float(row.get("融资余额")),
            "financing_buy_rmb": to_float(row.get("融资买入额")),
            "financing_repayment_rmb": to_float(row.get("融资偿还额")),
            "securities_lending_quantity": to_float(row.get("融券余量")),
            "securities_lending_sell_quantity": to_float(row.get("融券卖出量")),
        }

    if exchange in {"SZSE", "SZ"}:
        df = safe_call(errors, f"stock_margin_detail_szse:{date_key}", ak.stock_margin_detail_szse, date=date_key)
        if df is None or df.empty or "证券代码" not in df.columns:
            return None
        frame = df.copy()
        frame["_code"] = frame["证券代码"].astype(str).str.extract(r"(\d{6})", expand=False)
        rows = frame[frame["_code"] == code]
        if rows.empty:
            return None
        row = rows.iloc[0]
        return {
            "data_effective_date": trade_date.isoformat(),
            "source": "SZSE via AKShare stock_margin_detail_szse",
            "financing_balance_rmb": to_float(row.get("融资余额")),
            "financing_buy_rmb": to_float(row.get("融资买入额")),
            "financing_repayment_rmb": None,
            "securities_lending_balance_rmb": to_float(row.get("融券余额")),
            "securities_lending_quantity": to_float(row.get("融券余量")),
            "securities_lending_sell_quantity": to_float(row.get("融券卖出量")),
        }

    return None


def fetch_latest_margin(sample: dict[str, Any], as_of: date, ingested_at: str, errors: list[str]) -> dict[str, Any]:
    if not sample.get("collect_margin", True):
        return {"status": "NOT_APPLICABLE"}
    dates = recent_trade_dates(as_of, errors)
    found: list[dict[str, Any]] = []
    for d in dates:
        row = fetch_margin_row(sample, d, errors)
        if row is not None:
            found.append(row)
        if len(found) >= 2:
            break
    if not found:
        return {"status": "DELAYED_OR_NOT_APPLICABLE"}

    latest = found[0]
    previous = found[1] if len(found) > 1 else None
    balance_delta = None
    if previous is not None:
        cur = latest.get("financing_balance_rmb")
        prev = previous.get("financing_balance_rmb")
        if cur is not None and prev is not None:
            balance_delta = cur - prev

    financing_net_flow = None
    if latest.get("financing_buy_rmb") is not None and latest.get("financing_repayment_rmb") is not None:
        financing_net_flow = latest["financing_buy_rmb"] - latest["financing_repayment_rmb"]

    return {
        "status": "AVAILABLE",
        **latest,
        "previous_effective_date": None if previous is None else previous.get("data_effective_date"),
        "financing_balance_change_rmb": balance_delta,
        "financing_buy_minus_repayment_rmb": financing_net_flow,
        "available_at": ingested_at,
        "pit_note": "available_at is conservatively set to collection time when exact exchange publication timestamp is not captured",
    }


def fetch_disclosures(
    sample: dict[str, Any],
    as_of: date,
    ingested_at: str,
    errors: list[str],
) -> list[dict[str, Any]]:
    if not sample.get("collect_disclosures", True):
        return []
    code = str(sample["code"])
    start = as_of - timedelta(days=7)
    df = safe_call(
        errors,
        f"stock_zh_a_disclosure_report_cninfo:{code}",
        ak.stock_zh_a_disclosure_report_cninfo,
        symbol=code,
        market="沪深京",
        keyword="",
        category="",
        start_date=start.strftime("%Y%m%d"),
        end_date=as_of.strftime("%Y%m%d"),
    )
    if df is None or df.empty:
        return []

    records: list[dict[str, Any]] = []
    for _, row in df.iterrows():
        title = str(row.get("公告标题", "")).strip()
        raw_time = str(row.get("公告时间", "")).strip()
        locator = str(row.get("公告链接", "")).strip()
        identity = {
            "code": code,
            "title": title,
            "published_at_raw": raw_time,
            "source_locator": locator,
        }
        precision = "DATETIME" if ":" in raw_time else "DATE_ONLY_OR_UNKNOWN"
        records.append(
            {
                "disclosure_id": stable_hash(identity)[:24],
                **identity,
                "available_at": ingested_at,
                "timestamp_precision": precision,
                "source": "CNINFO via AKShare stock_zh_a_disclosure_report_cninfo",
                "pit_note": "when exact publication time is unavailable, available_at remains conservative collection time",
            }
        )
    return records


def load_market_report(report_dir: Path, trade_date: str) -> dict[str, Any] | None:
    path = report_dir / f"{trade_date}-market-monitor.json"
    if not path.exists():
        return None
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return None


def append_unique_jsonl(path: Path, records: list[dict[str, Any]], id_field: str) -> int:
    path.parent.mkdir(parents=True, exist_ok=True)
    existing: set[str] = set()
    if path.exists():
        for line in path.read_text(encoding="utf-8").splitlines():
            if not line.strip():
                continue
            try:
                row = json.loads(line)
            except Exception:
                continue
            value = row.get(id_field)
            if value is not None:
                existing.add(str(value))

    additions = [r for r in records if str(r.get(id_field)) not in existing]
    if not additions:
        return 0
    with path.open("a", encoding="utf-8") as f:
        for row in additions:
            f.write(json.dumps(row, ensure_ascii=False, sort_keys=True) + "\n")
    return len(additions)


def append_revisioned_daily(path: Path, record: dict[str, Any]) -> bool:
    path.parent.mkdir(parents=True, exist_ok=True)
    record_key = str(record["record_key"])
    comparable = {k: v for k, v in record.items() if k not in {"ingested_at", "payload_hash", "revision_number", "supersedes_payload_hash"}}
    payload_hash = stable_hash(comparable)

    rows: list[dict[str, Any]] = []
    if path.exists():
        for line in path.read_text(encoding="utf-8").splitlines():
            if not line.strip():
                continue
            try:
                rows.append(json.loads(line))
            except Exception:
                continue

    prior = [r for r in rows if str(r.get("record_key")) == record_key]
    if any(str(r.get("payload_hash")) == payload_hash for r in prior):
        return False

    last_hash = prior[-1].get("payload_hash") if prior else None
    record = {
        **record,
        "revision_number": len(prior) + 1,
        "supersedes_payload_hash": last_hash,
        "payload_hash": payload_hash,
    }
    with path.open("a", encoding="utf-8") as f:
        f.write(json.dumps(record, ensure_ascii=False, sort_keys=True) + "\n")
    return True


def checkpoint_metrics(
    hist: pd.DataFrame,
    benchmark: pd.DataFrame | None,
    entry_date: date,
    entry_cost: float,
    session_count: int,
) -> dict[str, Any] | None:
    path = hist[hist["trade_date"].dt.date >= entry_date].copy().reset_index(drop=True)
    if len(path) < session_count:
        return None
    window = path.iloc[:session_count].copy()
    checkpoint_date = window.iloc[-1]["trade_date"].date()
    close = to_float(window.iloc[-1]["收盘"])

    # Entry-day excursion is kept separate because exact fill time may be unknown.
    post_fill_safe = window[window["trade_date"].dt.date > entry_date]
    mfe = to_float(post_fill_safe["最高"].max()) if not post_fill_safe.empty else None
    mae = to_float(post_fill_safe["最低"].min()) if not post_fill_safe.empty else None

    stock_return = None if close is None else (close / entry_cost - 1.0) * 100.0
    benchmark_return = None
    if benchmark is not None and not benchmark.empty:
        b = benchmark[benchmark["trade_date"].dt.date <= checkpoint_date].copy()
        if not b.empty:
            entry_or_prior = b[b["trade_date"].dt.date <= entry_date]
            if not entry_or_prior.empty:
                b0 = to_float(entry_or_prior.iloc[-1]["close"])
                b1 = to_float(b.iloc[-1]["close"])
                if b0 and b1:
                    benchmark_return = (b1 / b0 - 1.0) * 100.0

    return {
        "checkpoint": f"D{session_count}",
        "checkpoint_date": checkpoint_date.isoformat(),
        "close": close,
        "return_vs_entry_pct": stock_return,
        "MFE_pct_next_session_onward": None if mfe is None else (mfe / entry_cost - 1.0) * 100.0,
        "MAE_pct_next_session_onward": None if mae is None else (mae / entry_cost - 1.0) * 100.0,
        "benchmark_return_since_entry_pct": benchmark_return,
        "excess_return_since_entry_pct": None if stock_return is None or benchmark_return is None else stock_return - benchmark_return,
        "follow_through_classification": "UNCLASSIFIED_CHALLENGER",
        "classification_note": "raw checkpoint evidence only; no production threshold is implied",
    }


def write_checkpoints(
    path: Path,
    sample: dict[str, Any],
    hist: pd.DataFrame,
    benchmark: pd.DataFrame | None,
    ingested_at: str,
) -> None:
    entry_date = date.fromisoformat(str(sample["entry_date"]))
    entry_cost = float(sample["actual_average_cost"])
    checkpoints = []
    for n in (1, 3, 5, 10, 15):
        result = checkpoint_metrics(hist, benchmark, entry_date, entry_cost, n)
        if result is not None:
            checkpoints.append(result)
    payload = {
        "schema_version": "1.0",
        "sample_id": sample["sample_id"],
        "code": sample["code"],
        "entry_date": sample["entry_date"],
        "updated_at": ingested_at,
        "checkpoint_semantics": "D1/D3/D5/D10/D15 are trading-session checkpoints; raw evidence only unless separately validated",
        "checkpoints": checkpoints,
    }
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")


def build_sample_record(
    sample: dict[str, Any],
    as_of: date,
    ingested_at: str,
    state_dir: Path,
    report_dir: Path,
) -> tuple[dict[str, Any], list[dict[str, Any]], pd.DataFrame | None, pd.DataFrame | None]:
    errors: list[str] = []
    entry_date = date.fromisoformat(str(sample["entry_date"]))
    history_start = min(entry_date, as_of) - timedelta(days=180)

    hist = fetch_stock_history(str(sample["code"]), history_start, as_of, errors)
    benchmark = fetch_benchmark_history(str(sample.get("benchmark_symbol", "sh000001")), history_start, as_of, errors)

    price_features = None
    if hist is not None and not hist.empty:
        price_features = derive_price_features(hist, benchmark, sample)

    trade_date = None if price_features is None else price_features.get("trade_date")
    market_report = None if trade_date is None else load_market_report(report_dir, str(trade_date))
    market_state = {
        "status": "PROVIDER_ERROR" if market_report is None else "AVAILABLE",
        "market_metrics": None if market_report is None else market_report.get("market_metrics"),
        "sentiment": None if market_report is None else market_report.get("sentiment"),
        "spot_provider": None if market_report is None else market_report.get("spot_provider"),
    }

    vendor_flow = fetch_vendor_flow(sample, as_of, errors)
    margin = fetch_latest_margin(sample, as_of, ingested_at, errors)
    disclosures = fetch_disclosures(sample, as_of, ingested_at, errors)

    quality = {
        "price_complete": price_features is not None,
        "market_complete": market_report is not None,
        "benchmark_complete": benchmark is not None and not benchmark.empty,
        "participation_complete": vendor_flow.get("status") == "AVAILABLE",
        "financing_complete_or_not_applicable": margin.get("status") in {"AVAILABLE", "NOT_APPLICABLE"},
        "disclosure_scan_complete": not any("stock_zh_a_disclosure_report_cninfo" in e for e in errors),
        "model_snapshot_complete": False if sample.get("sample_role") == "RETROSPECTIVE_LIVE_MANUAL" else None,
        "manual_execution_complete": sample.get("actual_average_cost") is not None and sample.get("entry_date") is not None,
    }

    effective_date = trade_date or as_of.isoformat()
    record = {
        "schema_version": "1.0",
        "record_key": f"{sample['sample_id']}:{effective_date}",
        "sample_id": sample["sample_id"],
        "sample_role": sample.get("sample_role"),
        "strategy_id": SHORT_MID_STRATEGY_ID,
        "sleeve": SHORT_MID_SLEEVE,
        "code": sample["code"],
        "name": sample.get("name"),
        "exchange": sample.get("exchange"),
        "sample_status": sample.get("status"),
        "effective_date": effective_date,
        "effective_at": f"{effective_date}T15:00:00+08:00" if trade_date is not None else None,
        "available_at": ingested_at,
        "ingested_at": ingested_at,
        "price_and_path": price_features,
        "benchmark": {
            "symbol": sample.get("benchmark_symbol"),
            "name": sample.get("benchmark_name"),
        },
        "market_state": market_state,
        "vendor_flow": vendor_flow,
        "margin": margin,
        "new_disclosures_seen_in_scan": [d["disclosure_id"] for d in disclosures],
        "data_quality": quality,
        "provider_errors": errors,
        "governance": {
            "collection_contract": "skills/a-share-short-midterm-stock-selection/references/sample-data-acquisition-contract.md",
            "risk_resilience_layer": "skills/a-share-short-midterm-stock-selection/references/risk-resilience-layer.md",
            "auto_order": False,
            "note": "sample evidence is research/audit data; collection does not create an order permission",
        },
    }
    return record, disclosures, hist, benchmark


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--registry", type=Path, default=DEFAULT_REGISTRY)
    parser.add_argument("--state-dir", type=Path, default=DEFAULT_STATE_DIR)
    parser.add_argument("--report-dir", type=Path, default=DEFAULT_REPORT_DIR)
    parser.add_argument("--as-of-date", type=str, default=None, help="YYYY-MM-DD override for deterministic research runs")
    args = parser.parse_args()

    registry = load_registry(args.registry)
    now = datetime.now(SH_TZ)
    as_of = date.fromisoformat(args.as_of_date) if args.as_of_date else now.date()
    ingested_at = now.isoformat()

    collected = 0
    disclosure_additions = 0
    for sample in registry["samples"]:
        if str(sample.get("status", "")).upper() not in {"OPEN", "OBSERVING", "REUNDERWRITTEN"}:
            continue
        record, disclosures, hist, benchmark = build_sample_record(sample, as_of, ingested_at, args.state_dir, args.report_dir)
        effective_date = str(record["effective_date"])
        daily_path = args.state_dir / "daily" / f"{effective_date}.jsonl"
        if append_revisioned_daily(daily_path, record):
            collected += 1

        disclosure_path = args.state_dir / "disclosures" / f"{sample['sample_id']}.jsonl"
        disclosure_additions += append_unique_jsonl(disclosure_path, disclosures, "disclosure_id")

        if hist is not None and not hist.empty:
            checkpoint_path = args.state_dir / "checkpoints" / f"{sample['sample_id']}.json"
            write_checkpoints(checkpoint_path, sample, hist, benchmark, ingested_at)

    summary = {
        "as_of_date": as_of.isoformat(),
        "ingested_at": ingested_at,
        "registry_version": registry.get("registry_version"),
        "sample_count_registered": len(registry["samples"]),
        "daily_records_appended": collected,
        "new_disclosures_appended": disclosure_additions,
        "state_dir": str(args.state_dir),
        "auto_order": False,
    }
    args.state_dir.mkdir(parents=True, exist_ok=True)
    (args.state_dir / "latest-run.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(summary, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
