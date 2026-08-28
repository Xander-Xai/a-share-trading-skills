from __future__ import annotations

import json
from datetime import date
from pathlib import Path

import akshare as ak
import pandas as pd

from runtime import sample_collector as core


_primary_stock_history = core.fetch_stock_history
_primary_benchmark_history = core.fetch_benchmark_history
_primary_build_sample_record = core.build_sample_record
_primary_append_revisioned_daily = core.append_revisioned_daily


def _market_symbol(code: str) -> str:
    return f"sh{code}" if str(code).startswith(("5", "6", "9")) else f"sz{code}"


def _quality_score(record: dict) -> int:
    quality = record.get("data_quality") or {}
    return sum(1 for value in quality.values() if value is True)


def _semantic_payload(record: dict) -> dict:
    """Compare evidence semantics, not observation-time/network-noise fields."""
    return {
        key: value
        for key, value in record.items()
        if key
        not in {
            "available_at",
            "ingested_at",
            "payload_hash",
            "revision_number",
            "supersedes_payload_hash",
            "provider_errors",
        }
    }


def fetch_stock_history_resilient(
    code: str,
    start_date: date,
    end_date: date,
    errors: list[str],
) -> pd.DataFrame | None:
    primary = _primary_stock_history(code, start_date, end_date, errors)
    if primary is not None and not primary.empty:
        primary.attrs["sample_source"] = "AKShare stock_zh_a_hist / Eastmoney"
        return primary

    fallback = core.safe_call(
        errors,
        f"stock_zh_a_hist_tx:{code}",
        ak.stock_zh_a_hist_tx,
        symbol=_market_symbol(code),
        start_date=start_date.strftime("%Y%m%d"),
        end_date=end_date.strftime("%Y%m%d"),
        adjust="",
    )
    if fallback is None or fallback.empty:
        return None

    required = {"date", "open", "close", "high", "low", "volume", "amount"}
    if not required.issubset(fallback.columns):
        errors.append(f"stock_zh_a_hist_tx:{code}: missing columns {sorted(required - set(fallback.columns))}")
        return None

    out = pd.DataFrame()
    out["日期"] = pd.to_datetime(fallback["date"], errors="coerce")
    out["开盘"] = pd.to_numeric(fallback["open"], errors="coerce")
    out["收盘"] = pd.to_numeric(fallback["close"], errors="coerce")
    out["最高"] = pd.to_numeric(fallback["high"], errors="coerce")
    out["最低"] = pd.to_numeric(fallback["low"], errors="coerce")
    # Core collector expects the Eastmoney convention of lots for 成交量.
    out["成交量"] = pd.to_numeric(fallback["volume"], errors="coerce") / 100.0
    out["成交额"] = pd.to_numeric(fallback["amount"], errors="coerce")
    if "turnover" in fallback.columns:
        # Tencent returns decimal turnover (e.g. 0.0021); canonical monitor field is percent.
        out["换手率"] = pd.to_numeric(fallback["turnover"], errors="coerce") * 100.0
    else:
        out["换手率"] = pd.NA
    out["涨跌幅"] = out["收盘"].pct_change() * 100.0
    out["trade_date"] = out["日期"]
    out = out.dropna(subset=["trade_date", "收盘"]).sort_values("trade_date").reset_index(drop=True)
    out.attrs["sample_source"] = "AKShare stock_zh_a_hist_tx / Tencent fallback"
    return out if not out.empty else None


def fetch_benchmark_history_resilient(
    symbol: str,
    start_date: date,
    end_date: date,
    errors: list[str],
) -> pd.DataFrame | None:
    primary = _primary_benchmark_history(symbol, start_date, end_date, errors)
    if primary is not None and not primary.empty:
        primary.attrs["sample_source"] = "AKShare stock_zh_index_daily_em / Eastmoney"
        return primary

    fallback = core.safe_call(
        errors,
        f"stock_zh_index_daily_tx:{symbol}",
        ak.stock_zh_index_daily_tx,
        symbol=symbol,
        start_date=start_date.strftime("%Y%m%d"),
        end_date=end_date.strftime("%Y%m%d"),
    )
    if fallback is None or fallback.empty or "date" not in fallback.columns or "close" not in fallback.columns:
        return None

    out = fallback.copy()
    out["trade_date"] = pd.to_datetime(out["date"], errors="coerce")
    out["close"] = pd.to_numeric(out["close"], errors="coerce")
    out = out.dropna(subset=["trade_date", "close"]).sort_values("trade_date").reset_index(drop=True)
    out.attrs["sample_source"] = "AKShare stock_zh_index_daily_tx / Tencent fallback"
    return out if not out.empty else None


def build_sample_record_resilient(sample, as_of, ingested_at, state_dir, report_dir):
    record, disclosures, hist, benchmark = _primary_build_sample_record(
        sample, as_of, ingested_at, state_dir, report_dir
    )

    # If every price adapter fails, anchor the failed collection attempt to the
    # latest known trading session rather than inventing a weekend/holiday sample day.
    if record.get("price_and_path") is None:
        calendar_errors: list[str] = []
        trade_dates = core.recent_trade_dates(as_of, calendar_errors, limit=1)
        if trade_dates:
            latest_session = trade_dates[0].isoformat()
            record["effective_date"] = latest_session
            record["effective_at"] = f"{latest_session}T15:00:00+08:00"
            record["record_key"] = f"{sample['sample_id']}:{latest_session}"
            market_report = core.load_market_report(report_dir, latest_session)
            if market_report is not None:
                record["market_state"] = {
                    "status": "AVAILABLE",
                    "market_metrics": market_report.get("market_metrics"),
                    "sentiment": market_report.get("sentiment"),
                    "spot_provider": market_report.get("spot_provider"),
                }
                record["data_quality"]["market_complete"] = True
        if calendar_errors:
            record.setdefault("provider_errors", []).extend(calendar_errors)

    record["provider_provenance"] = {
        "stock_history": None if hist is None else hist.attrs.get("sample_source"),
        "benchmark_history": None if benchmark is None else benchmark.attrs.get("sample_source"),
    }
    return record, disclosures, hist, benchmark


def append_revisioned_daily_resilient(path: Path, record: dict) -> bool:
    """Do not let a transient provider outage supersede better evidence."""
    prior_same_key: list[dict] = []
    if path.exists():
        for line in path.read_text(encoding="utf-8").splitlines():
            if not line.strip():
                continue
            try:
                row = json.loads(line)
            except Exception:
                continue
            if str(row.get("record_key")) == str(record.get("record_key")):
                prior_same_key.append(row)

    if prior_same_key:
        best_prior_quality = max(_quality_score(row) for row in prior_same_key)
        new_quality = _quality_score(record)
        if new_quality < best_prior_quality:
            return False

        latest_best = max(
            (row for row in prior_same_key if _quality_score(row) == best_prior_quality),
            key=lambda row: int(row.get("revision_number", 0)),
        )
        if _semantic_payload(latest_best) == _semantic_payload(record):
            return False

    return _primary_append_revisioned_daily(path, record)


def main() -> int:
    # Patch only adapter/orchestration behavior. Core PIT, checkpoint, margin,
    # disclosure and sample-governance semantics remain unchanged.
    core.fetch_stock_history = fetch_stock_history_resilient
    core.fetch_benchmark_history = fetch_benchmark_history_resilient
    core.build_sample_record = build_sample_record_resilient
    core.append_revisioned_daily = append_revisioned_daily_resilient
    return core.main()


if __name__ == "__main__":
    raise SystemExit(main())
