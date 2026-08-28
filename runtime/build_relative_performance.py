from __future__ import annotations

import argparse
import json
from pathlib import Path

from src.core.pit_store import PITStore
from src.data.adjustments import AdjustmentFactorBuilder
from src.data.benchmarks import BenchmarkSeriesBuilder
from src.features.relative_performance import RelativePerformanceBuilder


def main() -> None:
    parser = argparse.ArgumentParser(
        description=(
            "Build deterministic Short/Mid relative performance from one PIT snapshot, "
            "one explicit benchmark id and one frozen benchmark-selection contract id."
        )
    )
    parser.add_argument("store", type=Path, help="PITStore root")
    parser.add_argument("data_snapshot_id", help="Existing PIT data snapshot id")
    parser.add_argument("security_id", help="Six-digit A-share security id")
    parser.add_argument("benchmark_id", help="Benchmark id already frozen by research contract")
    parser.add_argument("benchmark_selection_contract_id", help="Frozen selection-contract id")
    parser.add_argument("--benchmark-role", default="PRIMARY")
    parser.add_argument("--exchange", default=None)
    parser.add_argument("--windows", nargs="*", type=int, default=[])
    parser.add_argument("--output", type=Path, default=None)
    args = parser.parse_args()

    store = PITStore(args.store)
    records = tuple(store.materialize_snapshot(args.data_snapshot_id))
    stock = AdjustmentFactorBuilder().build(
        records,
        security_id=args.security_id,
        exchange=args.exchange,
    )
    benchmark = BenchmarkSeriesBuilder().build(records, benchmark_id=args.benchmark_id)
    result = RelativePerformanceBuilder().build(
        stock,
        benchmark,
        benchmark_selection_contract_id=args.benchmark_selection_contract_id,
        benchmark_role=args.benchmark_role,
        diagnostic_windows=args.windows,
    )
    rendered = json.dumps(result.to_dict(), ensure_ascii=False, indent=2, sort_keys=True) + "\n"
    print(rendered, end="")
    if args.output is not None:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(rendered, encoding="utf-8")


if __name__ == "__main__":
    main()
