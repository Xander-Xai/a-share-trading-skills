from __future__ import annotations

import argparse
import json
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

import akshare as ak
import pandas as pd

from monitor import calculate_sentiment


SH_TZ = ZoneInfo("Asia/Shanghai")
DEFAULT_WATCHLIST = Path(
    "skills/a-share-short-midterm-stock-selection/examples/2026-08-26-final-watchlist.json"
)
DEFAULT_HISTORY = Path("runtime/state/market_history.csv")
DEFAULT_OUTPUT_DIR = Path("reports/daily")


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


def load_watchlist(path: Path) -> list[dict]:
    if not path.exists():
        return []
    with path.open("r", encoding="utf-8") as f:
        data = json.load(f)
    return list(data.get("stocks", []))


def candidate_pre_action(stock: dict, regime: str, crowding: bool, current_day_pct: float | None) -> str:
    status = stock.get("status", "")

    if regime in {"PANIC", "RISK_OFF", "DATA_INSUFFICIENT"}:
        return "NO_NEW_ENTRY"
    if status == "event_isolation":
        return "EVENT_REVIEW"
    if regime == "EUPHORIA" and crowding:
        return "WAIT_NO_CHASE"
    if current_day_pct is not None and current_day_pct >= 5.0:
        return "WAIT_NO_CHASE"
    if status == "priority_scan":
        return "REFRESH_FULL_GATES"
    if status == "wait_technical_confirmation":
        return "REFRESH_SETUP"
    return "RISK_REVIEW"


def build_candidate_rows(watchlist: list[dict], spot: pd.DataFrame | None, regime: str, crowding: bool) -> list[dict]:
    if spot is None or spot.empty or "代码" not in spot.columns:
        return [
            {
                "code": s.get("code"),
                "name": s.get("name"),
                "pre_action": "NO_ACTION_DATA_MISSING",
            }
            for s in watchlist
        ]

    frame = spot.copy()
    frame["代码"] = frame["代码"].astype(str).str.zfill(6)
    frame = frame.drop_duplicates("代码").set_index("代码")

    rows: list[dict] = []
    for stock in watchlist:
        code = str(stock.get("code", "")).zfill(6)
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
                "note": "pre_action is a monitor state, not a buy/sell order; current fundamentals/catalyst/score/invalidation must be refreshed before execution.",
            }
        )
    return rows


def render_markdown(report: dict) -> str:
    s = report.get("sentiment", {})
    lines = [
        f"# A-share Daily Monitor — {report['date']}",
        "",
        f"- as_of: `{report['as_of']}`",
        f"- trading_day_status: `{report['trading_day_status']}`",
        f"- sentiment_score: `{s.get('sentiment_score')}`",
        f"- regime: `{s.get('regime')}`",
        f"- crowding_flag: `{s.get('crowding_flag')}`",
        f"- data_confidence: `{s.get('data_confidence')}`",
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

    lines.extend(
        [
            "",
            "## Provider errors",
            "",
        ]
    )
    errors = report.get("provider_errors", [])
    if errors:
        lines.extend([f"- {e}" for e in errors])
    else:
        lines.append("- none")

    lines.extend(
        [
            "",
            "> `pre_action` is research/monitor output only. `AUTO_ORDER=false`; no report row is an executable order.",
            "",
        ]
    )
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--watchlist", type=Path, default=DEFAULT_WATCHLIST)
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
    up_pool = None
    down_pool = None
    broken_pool = None

    if trade_day is not False:
        spot = safe_call(errors, "stock_zh_a_spot_em", ak.stock_zh_a_spot_em)
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
    watchlist = load_watchlist(args.watchlist)
    candidates = build_candidate_rows(
        watchlist,
        spot,
        sentiment.get("regime", "DATA_INSUFFICIENT"),
        bool(sentiment.get("crowding_flag", False)),
    )

    report = {
        "schema_version": "1.0",
        "date": today_str,
        "as_of": now.isoformat(),
        "trading_day_status": trading_day_status,
        "auto_monitor": True,
        "auto_order": False,
        "market_metrics": metrics,
        "sentiment": sentiment,
        "candidates": candidates,
        "provider_errors": errors,
        "provider": "AKShare aggregation provider; live execution requires official/broker cross-check",
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
            },
        )

    print(json.dumps({"report": str(md_path), "regime": sentiment.get("regime"), "errors": errors}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
