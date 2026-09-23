from __future__ import annotations

import argparse
import json
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

import akshare as ak
import pandas as pd

from monitor import (
    SHORT_MID_SLEEVE,
    SHORT_MID_STRATEGY_ID,
    calculate_sentiment,
    normalize_stock_code,
)
from src.core.strategy_boundary import require_strategy_context


SH_TZ = ZoneInfo("Asia/Shanghai")
DEFAULT_UNIVERSE = Path("runtime/private/short_mid_universe.json")
DEFAULT_HISTORY = Path("runtime/state/market_history.csv")
DEFAULT_OUTPUT_DIR = Path("reports/private/daily")


def safe_call(errors: list[str], label: str, func, *args, **kwargs):
    try:
        return func(*args, **kwargs)
    except Exception as exc:  # fail closed and preserve evidence
        errors.append(f"{label}: {type(exc).__name__}: {exc}")
        return None


def is_trade_date(today, errors: list[str]) -> bool | None:
    df = safe_call(errors, "tool_trade_date_hist_sina", ak.tool_trade_date_hist_sina)
    if df is None or df.empty:
        return None

    candidate_cols = [c for c in df.columns if str(c).lower() in {"trade_date", "date"}]
    if not candidate_cols:
        candidate_cols = [df.columns[0]]

    dates = pd.to_datetime(df[candidate_cols[0]], errors="coerce").dt.date
    return today in set(dates.dropna())


def fetch_spot_with_fallback(errors: list[str]) -> tuple[pd.DataFrame | None, str]:
    """Fetch the full A-share spot table using independent public providers.

    Eastmoney is the primary provider because its schema is already used by the
    repository. If it fails, use AKShare's Sina full-A-share interface once.
    The caller records the degraded provider state instead of pretending that
    redundancy was fully healthy.
    """
    spot = safe_call(errors, "stock_zh_a_spot_em", ak.stock_zh_a_spot_em)
    if spot is not None and not spot.empty:
        return spot, "EASTMONEY_PRIMARY"

    spot = safe_call(errors, "stock_zh_a_spot", ak.stock_zh_a_spot)
    if spot is not None and not spot.empty:
        return spot, "SINA_FALLBACK"

    return None, "UNAVAILABLE"


def numeric_series(df: pd.DataFrame, column: str) -> pd.Series:
    if column not in df.columns:
        return pd.Series(dtype=float)
    return pd.to_numeric(df[column], errors="coerce").dropna()


def load_turnover_median(history_path: Path, today_str: str) -> float | None:
    if not history_path.exists():
        return None
    try:
        hist = pd.read_csv(history_path, dtype={"date": str})
    except Exception:
        return None
    if "date" not in hist.columns or "total_turnover" not in hist.columns:
        return None
    hist = hist[hist["date"] != today_str].copy()
    values = pd.to_numeric(hist["total_turnover"], errors="coerce").dropna().tail(20)
    if len(values) < 10:
        return None
    return float(values.median())


def append_history(history_path: Path, row: dict) -> None:
    history_path.parent.mkdir(parents=True, exist_ok=True)
    current = pd.DataFrame([row])
    if history_path.exists():
        try:
            old = pd.read_csv(history_path, dtype={"date": str})
            old = old[old["date"] != str(row["date"])]
            current = pd.concat([old, current], ignore_index=True)
        except Exception:
            pass
    current.sort_values("date").to_csv(history_path, index=False)


def count_rows(df: pd.DataFrame | None) -> int | None:
    return None if df is None else int(len(df))


def load_universe(path: Path) -> tuple[list[dict], dict]:
    """Load a runtime universe and enforce short/mid strategy identity.

    Level-4 dated examples are no longer the default runtime source. A caller
    may still pass another file explicitly for replay/research, but the payload
    must declare the short/mid strategy context before tactical rules run.
    """
    if not path.exists():
        raise FileNotFoundError(path)

    with path.open("r", encoding="utf-8") as f:
        data = json.load(f)

    require_strategy_context(
        strategy_id=str(data.get("strategy_id", "")),
        sleeve=str(data.get("sleeve", "")),
        expected_strategy_id=SHORT_MID_STRATEGY_ID,
        expected_sleeve=SHORT_MID_SLEEVE,
    )

    stocks = list(data.get("stocks", []))
    metadata = {
        "runtime_universe_version": data.get("runtime_universe_version"),
        "as_of": data.get("as_of"),
        "source_type": data.get("source_type"),
        "source_note": data.get("source_note"),
        "path": str(path),
    }
    return stocks, metadata


def candidate_pre_action(stock: dict, regime: str, crowding: bool, current_day_pct: float | None) -> str:
    """Return a monitor/research state, never an executable order."""
    status = stock.get("status", "")

    if regime in {"PANIC", "DATA_INSUFFICIENT"}:
        return "NO_NEW_ENTRY"
    if status == "no_new_position":
        return "NO_NEW_ENTRY"
    if status == "event_isolation":
        return "EVENT_REVIEW"
    if regime == "EUPHORIA" and crowding:
        return "WAIT_NO_CHASE"
    if current_day_pct is not None and current_day_pct >= 5.0:
        return "WAIT_NO_CHASE"
    if regime == "RISK_OFF":
        return "RISK_REVIEW"
    if status == "priority_scan":
        return "REFRESH_FULL_GATES"
    if status == "wait_technical_confirmation":
        return "REFRESH_SETUP"
    return "RISK_REVIEW"


def build_candidate_rows(watchlist: list[dict], spot: pd.DataFrame | None, regime: str, crowding: bool) -> list[dict]:
    if spot is None or spot.empty or "代码" not in spot.columns:
        return [
            {
                "code": normalize_stock_code(s.get("code")),
                "name": s.get("name"),
                "pre_action": "NO_ACTION_DATA_MISSING",
            }
            for s in watchlist
        ]

    frame = spot.copy()
    frame["代码"] = frame["代码"].map(normalize_stock_code)
    frame = frame[frame["代码"] != ""].drop_duplicates("代码").set_index("代码")

    rows: list[dict] = []
    for stock in watchlist:
        code = normalize_stock_code(stock.get("code"))
        row = frame.loc[code] if code in frame.index else None

        price = None
        day_pct = None
        if row is not None:
            try:
                price = float(pd.to_numeric(row.get("最新价"), errors="coerce"))
                if pd.isna(price):
                    price = None
            except Exception:
                price = None
            try:
                day_pct = float(pd.to_numeric(row.get("涨跌幅"), errors="coerce"))
                if pd.isna(day_pct):
                    day_pct = None
            except Exception:
                day_pct = None

        baseline = stock.get("baseline_price")
        baseline_return = None
        if price is not None and isinstance(baseline, (int, float)) and baseline > 0:
            baseline_return = (price / baseline - 1.0) * 100.0

        rows.append(
            {
                "code": code,
                "name": stock.get("name"),
                "baseline_price": baseline,
                "current_price": price,
                "day_change_pct": day_pct,
                "return_vs_baseline_pct": None if baseline_return is None else round(baseline_return, 2),
                "snapshot_status": stock.get("status"),
                "dominant_factor": stock.get("dominant_factor"),
                "pre_action": candidate_pre_action(stock, regime, crowding, day_pct),
                "note": "pre_action is short/mid monitor output only; it cannot mutate the long sleeve and cannot become BUY without fresh full gates.",
            }
        )
    return rows


def render_markdown(report: dict) -> str:
    s = report.get("sentiment", {})
    lines = [
        f"# A-share Short/Mid Daily Monitor — {report['date']}",
        "",
        f"- as_of: `{report['as_of']}`",
        f"- strategy_id: `{report['strategy_id']}`",
        f"- sleeve: `{report['sleeve']}`",
        f"- runtime_mode: `{report['runtime_mode']}`",
        f"- trading_day_status: `{report['trading_day_status']}`",
        f"- spot_provider: `{report.get('spot_provider')}`",
        f"- sentiment_score: `{s.get('sentiment_score')}`",
        f"- regime: `{s.get('regime')}`",
        f"- crowding_flag: `{s.get('crowding_flag')}`",
        f"- data_confidence: `{s.get('data_confidence')}`",
        "",
        "## Runtime universe",
        "",
        "```json",
        json.dumps(report.get("universe", {}), ensure_ascii=False, indent=2),
        "```",
        "",
        "## Governance references",
        "",
        "```json",
        json.dumps(report.get("governance_refs", {}), ensure_ascii=False, indent=2),
        "```",
        "",
        "## Market metrics",
        "",
        "```json",
        json.dumps(report.get("market_metrics", {}), ensure_ascii=False, indent=2),
        "```",
        "",
        "## Candidate monitor states",
        "",
        "| Code | Name | Price | Day % | Vs baseline % | Snapshot | Pre-action |",
        "|---|---|---:|---:|---:|---|---|",
    ]

    for row in report.get("candidates", []):
        lines.append(
            "| {code} | {name} | {price} | {day} | {base} | {status} | {action} |".format(
                code=row.get("code", ""),
                name=row.get("name", ""),
                price="" if row.get("current_price") is None else f"{row['current_price']:.2f}",
                day="" if row.get("day_change_pct") is None else f"{row['day_change_pct']:.2f}",
                base="" if row.get("return_vs_baseline_pct") is None else f"{row['return_vs_baseline_pct']:.2f}",
                status=row.get("snapshot_status", ""),
                action=row.get("pre_action", ""),
            )
        )

    lines.extend(["", "## Provider / configuration errors", ""])
    errors = report.get("provider_errors", [])
    if errors:
        lines.extend([f"- {e}" for e in errors])
    else:
        lines.append("- none")

    lines.extend(
        [
            "",
            "> `pre_action` belongs only to `short_mid`. `AUTO_ORDER=false`; no report row is an executable order and no state may mutate the long sleeve.",
            "",
        ]
    )
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser()
    # Keep --watchlist as a compatibility name while the payload is now a
    # strategy-tagged runtime universe config rather than a Level-4 example.
    parser.add_argument("--watchlist", type=Path, default=DEFAULT_UNIVERSE)
    parser.add_argument("--history", type=Path, default=DEFAULT_HISTORY)
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT_DIR)
    args = parser.parse_args()

    now = datetime.now(SH_TZ)
    today = now.date()
    today_str = today.isoformat()
    date_key = today.strftime("%Y%m%d")
    errors: list[str] = []

    trade_day = is_trade_date(today, errors)
    if trade_day is False:
        trading_day_status = "MARKET_CLOSED"
    elif trade_day is None:
        trading_day_status = "TRADE_CALENDAR_UNKNOWN"
    else:
        trading_day_status = "TRADING_DAY"

    spot = None
    spot_provider = "NOT_REQUESTED"
    up_pool = None
    down_pool = None
    broken_pool = None

    if trade_day is not False:
        spot, spot_provider = fetch_spot_with_fallback(errors)
        up_pool = safe_call(errors, "stock_zt_pool_em", ak.stock_zt_pool_em, date=date_key)
        down_pool = safe_call(errors, "stock_zt_pool_dtgc_em", ak.stock_zt_pool_dtgc_em, date=date_key)
        broken_pool = safe_call(errors, "stock_zt_pool_zbgc_em", ak.stock_zt_pool_zbgc_em, date=date_key)

    pct = numeric_series(spot, "涨跌幅") if spot is not None else pd.Series(dtype=float)
    turnover_series = numeric_series(spot, "成交额") if spot is not None else pd.Series(dtype=float)

    advance = int((pct > 0).sum()) if not pct.empty else None
    decline = int((pct < 0).sum()) if not pct.empty else None
    flat = int((pct == 0).sum()) if not pct.empty else None
    strong = int((pct >= 5.0).sum()) if not pct.empty else None
    weak = int((pct <= -5.0).sum()) if not pct.empty else None
    median_return = float(pct.median()) if not pct.empty else None
    total_turnover = float(turnover_series.sum()) if not turnover_series.empty else None
    turnover_20d = load_turnover_median(args.history, today_str)

    metrics = {
        "valid_stock_count": None if pct.empty else int(len(pct)),
        "advance_count": advance,
        "decline_count": decline,
        "flat_count": flat,
        "limit_up_count": count_rows(up_pool),
        "limit_down_count": count_rows(down_pool),
        "broken_limit_count": count_rows(broken_pool),
        "strong_count": strong,
        "weak_count": weak,
        "median_return_pct": None if median_return is None else round(median_return, 4),
        "total_turnover": total_turnover,
        "turnover_20d_median": turnover_20d,
    }

    sentiment = calculate_sentiment(metrics)

    if trade_day is None:
        sentiment = {
            **sentiment,
            "sentiment_score": None,
            "regime": "DATA_INSUFFICIENT",
            "crowding_flag": False,
            "data_confidence": "LOW",
            "calendar_gate": "BLOCKED",
        }
    elif trade_day is False:
        sentiment = {
            **sentiment,
            "sentiment_score": None,
            "regime": "DATA_INSUFFICIENT",
            "crowding_flag": False,
            "data_confidence": "LOW",
            "calendar_gate": "MARKET_CLOSED",
        }
    else:
        sentiment = {**sentiment, "calendar_gate": "PASS"}

    if spot_provider == "SINA_FALLBACK" and sentiment.get("data_confidence") == "HIGH":
        sentiment = {
            **sentiment,
            "data_confidence": "MEDIUM",
            "spot_provider_gate": "DEGRADED_FALLBACK",
        }
    elif spot_provider == "UNAVAILABLE":
        sentiment = {
            **sentiment,
            "sentiment_score": None,
            "regime": "DATA_INSUFFICIENT",
            "crowding_flag": False,
            "data_confidence": "LOW",
            "spot_provider_gate": "BLOCKED",
        }
    else:
        sentiment = {**sentiment, "spot_provider_gate": "PASS"}

    loaded_universe = safe_call(errors, "load_universe", load_universe, args.watchlist)
    if loaded_universe is None:
        watchlist: list[dict] = []
        universe_meta: dict = {
            "path": str(args.watchlist),
            "status": "UNRESOLVED",
        }
        sentiment = {
            **sentiment,
            "sentiment_score": None,
            "regime": "DATA_INSUFFICIENT",
            "crowding_flag": False,
            "data_confidence": "LOW",
            "strategy_context_gate": "BLOCKED",
        }
    else:
        watchlist, universe_meta = loaded_universe
        universe_meta = {**universe_meta, "status": "LOADED"}
        sentiment = {**sentiment, "strategy_context_gate": "PASS"}

    candidates = build_candidate_rows(
        watchlist,
        spot,
        sentiment.get("regime", "DATA_INSUFFICIENT"),
        bool(sentiment.get("crowding_flag", False)),
    )

    report = {
        "schema_version": "1.4",
        "date": today_str,
        "as_of": now.isoformat(),
        "strategy_id": SHORT_MID_STRATEGY_ID,
        "sleeve": SHORT_MID_SLEEVE,
        "runtime_mode": "SHORT_MID_MONITOR_ONLY",
        "trading_day_status": trading_day_status,
        "auto_monitor": True,
        "auto_order": False,
        "spot_provider": spot_provider,
        "universe": universe_meta,
        "governance_refs": {
            "capital_policy": "shared/capital-allocation-and-entry-policy.md",
            "automation_governance": "shared/automation-execution-governance.md",
            "research_model_governance": "shared/research-model-governance.md",
            "strategy_boundary": "shared/strategy-boundary-contract.md",
            "pit_data_contract": "shared/canonical-pit-data-contract.md",
            "short_mid_skill": "skills/a-share-short-midterm-stock-selection/SKILL.md",
            "sentiment_model": "skills/a-share-short-midterm-stock-selection/references/a-share-sentiment-regime-index.md",
        },
        "market_metrics": metrics,
        "sentiment": sentiment,
        "candidates": candidates,
        "provider_errors": errors,
        "provider": {
            "spot_primary": "AKShare stock_zh_a_spot_em / Eastmoney",
            "spot_fallback": "AKShare stock_zh_a_spot / Sina",
            "execution_note": "aggregation providers only; live execution requires official/broker cross-check and permitted-use review",
        },
    }

    args.output_dir.mkdir(parents=True, exist_ok=True)
    json_path = args.output_dir / f"{today_str}-market-monitor.json"
    md_path = args.output_dir / f"{today_str}-market-monitor.md"
    json_path.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    md_path.write_text(render_markdown(report), encoding="utf-8")

    if trade_day is True and total_turnover is not None:
        append_history(
            args.history,
            {
                "date": today_str,
                "total_turnover": total_turnover,
                "sentiment_score": sentiment.get("sentiment_score"),
                "regime": sentiment.get("regime"),
                "spot_provider": spot_provider,
            },
        )

    print(
        json.dumps(
            {
                "report": str(md_path),
                "strategy_id": SHORT_MID_STRATEGY_ID,
                "sleeve": SHORT_MID_SLEEVE,
                "regime": sentiment.get("regime"),
                "spot_provider": spot_provider,
                "errors": errors,
            },
            ensure_ascii=False,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
