from __future__ import annotations

import argparse
import json
from collections import defaultdict
from datetime import datetime
from pathlib import Path
from typing import Any
from zoneinfo import ZoneInfo


SH_TZ = ZoneInfo("Asia/Shanghai")
DEFAULT_STATE_DIR = Path("runtime/state/sample_evidence")
DEFAULT_OUTPUT_DIR = Path("reports/daily")

QUALITY_FIELDS = [
    "price_complete",
    "market_complete",
    "benchmark_complete",
    "participation_complete",
    "financing_complete_or_not_applicable",
    "disclosure_scan_complete",
    "manual_execution_complete",
]


def read_latest_daily_records(state_dir: Path) -> list[dict[str, Any]]:
    daily_dir = state_dir / "daily"
    if not daily_dir.exists():
        return []

    latest: dict[str, dict[str, Any]] = {}
    for path in sorted(daily_dir.glob("*.jsonl")):
        for line in path.read_text(encoding="utf-8").splitlines():
            if not line.strip():
                continue
            try:
                row = json.loads(line)
            except Exception:
                continue
            key = str(row.get("record_key", ""))
            if not key:
                continue
            current = latest.get(key)
            if current is None or int(row.get("revision_number", 0)) >= int(current.get("revision_number", 0)):
                latest[key] = row
    return list(latest.values())


def pct(numerator: int, denominator: int) -> float | None:
    if denominator <= 0:
        return None
    return round(numerator / denominator * 100.0, 2)


def classify_maturity(evidence_snapshot_days: int, coverage: dict[str, float | None]) -> str:
    if evidence_snapshot_days == 0:
        return "NO_DATA"
    if evidence_snapshot_days < 5:
        return "EARLY_ACCUMULATION"
    if evidence_snapshot_days < 15:
        return "ACCUMULATING"

    core = [
        coverage.get("price_complete_pct"),
        coverage.get("market_complete_pct"),
        coverage.get("benchmark_complete_pct"),
        coverage.get("disclosure_scan_complete_pct"),
    ]
    if all(v is not None and v >= 90.0 for v in core):
        return "OPERATIONALLY_MATURE_FOR_FEATURE_RESEARCH"
    return "COVERAGE_GAPS"


def _effective_quality(row: dict[str, Any]) -> dict[str, Any]:
    """Normalize quality semantics across collector schema revisions.

    Early v1 evidence tied participation completeness to the optional vendor-flow
    endpoint. Current governance defines base participation from primary observable
    price/volume/turnover evidence plus exchange margin when applicable; vendor flow
    is corroborative only. We preserve the immutable old row and normalize only the
    maturity interpretation.
    """
    quality = dict(row.get("data_quality") or {})
    participation = row.get("participation_evidence") or {}
    if "base_complete" in participation:
        quality["participation_complete"] = participation.get("base_complete") is True
    else:
        price_ok = quality.get("price_complete") is True
        financing_ok = quality.get("financing_complete_or_not_applicable") is True
        if price_ok and financing_ok:
            quality["participation_complete"] = True
    return quality


def _latest_historical_path_days(rows: list[dict[str, Any]]) -> int | None:
    values: list[int] = []
    for row in rows:
        path = ((row.get("price_and_path") or {}).get("sample_path") or {})
        value = path.get("holding_trading_days_inclusive")
        if isinstance(value, int):
            values.append(value)
        elif isinstance(value, float) and value.is_integer():
            values.append(int(value))
    return max(values) if values else None


def summarize(records: list[dict[str, Any]]) -> dict[str, Any]:
    grouped: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in records:
        sample_id = str(row.get("sample_id", ""))
        if sample_id:
            grouped[sample_id].append(row)

    sample_summaries: list[dict[str, Any]] = []
    for sample_id, rows in sorted(grouped.items()):
        rows = sorted(rows, key=lambda r: str(r.get("effective_date", "")))
        counts = {field: 0 for field in QUALITY_FIELDS}
        for row in rows:
            quality = _effective_quality(row)
            for field in QUALITY_FIELDS:
                if quality.get(field) is True:
                    counts[field] += 1

        evidence_days = len(rows)
        coverage = {f"{field}_pct": pct(counts[field], evidence_days) for field in QUALITY_FIELDS}
        prospective_rows = [r for r in rows if str(r.get("sample_role")) != "RETROSPECTIVE_LIVE_MANUAL"]
        model_snapshot_true = 0
        for row in prospective_rows:
            q = _effective_quality(row)
            if q.get("model_snapshot_complete") is True:
                model_snapshot_true += 1
        prospective_snapshot_pct = pct(model_snapshot_true, len(prospective_rows)) if prospective_rows else None

        historical_path_days = _latest_historical_path_days(rows)
        role = rows[-1].get("sample_role")
        sample_summaries.append(
            {
                "sample_id": sample_id,
                "code": rows[-1].get("code"),
                "name": rows[-1].get("name"),
                "sample_role": role,
                "evidence_snapshot_days_total": evidence_days,
                "historical_path_trading_days_available": historical_path_days,
                "first_effective_date": rows[0].get("effective_date"),
                "last_effective_date": rows[-1].get("effective_date"),
                "coverage": coverage,
                "prospective_model_snapshot_complete_pct": prospective_snapshot_pct,
                "data_maturity": classify_maturity(evidence_days, coverage),
                "forward_alpha_eligibility_note": (
                    "RETROSPECTIVE_PATH_NOT_FORWARD_EVIDENCE"
                    if str(role) == "RETROSPECTIVE_LIVE_MANUAL"
                    else "CHECK_FORWARD_CONTRACT"
                ),
                "alpha_validation_status": "NOT_INFERRED_FROM_DATA_COMPLETENESS",
            }
        )

    total_snapshots = sum(s["evidence_snapshot_days_total"] for s in sample_summaries)
    aggregate_counts = {field: 0 for field in QUALITY_FIELDS}
    for row in records:
        quality = _effective_quality(row)
        for field in QUALITY_FIELDS:
            if quality.get(field) is True:
                aggregate_counts[field] += 1

    aggregate_coverage = {
        f"{field}_pct": pct(aggregate_counts[field], total_snapshots) for field in QUALITY_FIELDS
    }

    return {
        "sample_count": len(sample_summaries),
        "evidence_snapshot_days_total": total_snapshots,
        "aggregate_coverage": aggregate_coverage,
        "samples": sample_summaries,
        "interpretation": (
            "Evidence-snapshot maturity measures automated PIT/audit coverage. Historical path days may be larger for retrospective samples, "
            "but retrospective availability does not turn them into untouched forward evidence. Data completeness does not prove alpha."
        ),
    }


def render_markdown(report: dict[str, Any]) -> str:
    lines = [
        f"# Short/Mid Sample Data Maturity — {report['date']}",
        "",
        f"- generated_at: `{report['generated_at']}`",
        f"- sample_count: `{report['summary']['sample_count']}`",
        f"- evidence_snapshot_days_total: `{report['summary']['evidence_snapshot_days_total']}`",
        "- alpha interpretation: `NOT_INFERRED_FROM_DATA_COMPLETENESS`",
        "",
        "## Aggregate coverage",
        "",
        "```json",
        json.dumps(report["summary"]["aggregate_coverage"], ensure_ascii=False, indent=2),
        "```",
        "",
        "## Samples",
        "",
        "| Sample | Code | Evidence snapshots | Historical path days | Maturity | Price % | Market % | Benchmark % | Participation % | Financing % | Disclosure % |",
        "|---|---|---:|---:|---|---:|---:|---:|---:|---:|---:|",
    ]
    for sample in report["summary"]["samples"]:
        c = sample["coverage"]
        fmt = lambda value: "" if value is None else f"{value:.2f}"
        path_days = sample.get("historical_path_trading_days_available")
        lines.append(
            "| {sample} | {code} | {snapshots} | {path_days} | {maturity} | {price} | {market} | {benchmark} | {part} | {fin} | {disc} |".format(
                sample=sample["sample_id"],
                code=sample.get("code", ""),
                snapshots=sample["evidence_snapshot_days_total"],
                path_days="" if path_days is None else path_days,
                maturity=sample["data_maturity"],
                price=fmt(c.get("price_complete_pct")),
                market=fmt(c.get("market_complete_pct")),
                benchmark=fmt(c.get("benchmark_complete_pct")),
                part=fmt(c.get("participation_complete_pct")),
                fin=fmt(c.get("financing_complete_or_not_applicable_pct")),
                disc=fmt(c.get("disclosure_scan_complete_pct")),
            )
        )
    lines.extend(
        [
            "",
            "> `Historical path days` can be reconstructed for retrospective research. `Evidence snapshots` measure automated PIT/audit accumulation. Neither by itself establishes Alpha.",
            "",
        ]
    )
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--state-dir", type=Path, default=DEFAULT_STATE_DIR)
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT_DIR)
    args = parser.parse_args()

    now = datetime.now(SH_TZ)
    records = read_latest_daily_records(args.state_dir)
    summary = summarize(records)
    report = {
        "schema_version": "1.2",
        "date": now.date().isoformat(),
        "generated_at": now.isoformat(),
        "summary": summary,
    }

    args.output_dir.mkdir(parents=True, exist_ok=True)
    json_path = args.output_dir / f"{report['date']}-sample-data-maturity.json"
    md_path = args.output_dir / f"{report['date']}-sample-data-maturity.md"
    json_path.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    md_path.write_text(render_markdown(report), encoding="utf-8")

    print(json.dumps({"report": str(md_path), **summary}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
