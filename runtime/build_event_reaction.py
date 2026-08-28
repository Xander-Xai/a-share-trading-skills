from __future__ import annotations

import argparse
import json
from pathlib import Path

from src.core.pit_store import PITStore
from src.data.adjustments import AdjustmentFactorBuilder
from src.data.benchmarks import BenchmarkSeriesBuilder
from src.features.event_reaction import EventReactionMeasurementBuilder
from src.features.relative_performance import RelativePerformanceBuilder


def main() -> None:
    parser = argparse.ArgumentParser(
        description=(
            "Build deterministic Short/Mid event prepricing/reaction measurements "
            "from a PIT snapshot and already-frozen benchmark/window contracts."
        )
    )
    parser.add_argument("store", type=Path)
    parser.add_argument("data_snapshot_id")
    parser.add_argument("security_id")
    parser.add_argument("benchmark_id")
    parser.add_argument("benchmark_selection_contract_id")
    parser.add_argument("event_id")
    parser.add_argument("event_family")
    parser.add_argument("information_timestamp")
    parser.add_argument("first_tradable_timestamp")
    parser.add_argument("reaction_window_contract_id")
    parser.add_argument("--exchange", default=None)
    parser.add_argument("--benchmark-role", default="PRIMARY")
    parser.add_argument("--prepricing-windows", nargs="*", type=int, default=[])
    parser.add_argument("--reaction-windows", nargs="*", type=int, default=[])
    parser.add_argument("--primary-reaction-window", type=int, default=None)
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
    relative = RelativePerformanceBuilder().build(
        stock,
        benchmark,
        benchmark_selection_contract_id=args.benchmark_selection_contract_id,
        benchmark_role=args.benchmark_role,
    )
    result = EventReactionMeasurementBuilder().build(
        relative,
        event_id=args.event_id,
        event_family=args.event_family,
        information_timestamp=args.information_timestamp,
        first_tradable_timestamp=args.first_tradable_timestamp,
        reaction_window_contract_id=args.reaction_window_contract_id,
        prepricing_windows=args.prepricing_windows,
        reaction_windows=args.reaction_windows,
        primary_reaction_window_sessions=args.primary_reaction_window,
    )
    rendered = json.dumps(result.to_dict(), ensure_ascii=False, indent=2, sort_keys=True) + "\n"
    print(rendered, end="")
    if args.output is not None:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(rendered, encoding="utf-8")


if __name__ == "__main__":
    main()
