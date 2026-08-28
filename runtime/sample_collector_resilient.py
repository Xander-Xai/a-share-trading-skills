from __future__ import annotations

from datetime import date

import akshare as ak
import pandas as pd

from runtime import sample_collector as core


_primary_stock_history = core.fetch_stock_history
_primary_benchmark_history = core.fetch_benchmark_history


def _market_symbol(code: str) -> str:
    return f"sh{code}" if str(code).startswith(("5", "6", "9")) else f"sz{code}"


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


def main() -> int:
    # Monkey-patch only the public historical price adapters. The core collector
    # retains all PIT, revision, margin, disclosure and checkpoint semantics.
    core.fetch_stock_history = fetch_stock_history_resilient
    core.fetch_benchmark_history = fetch_benchmark_history_resilient
    return core.main()


if __name__ == "__main__":
    raise SystemExit(main())
