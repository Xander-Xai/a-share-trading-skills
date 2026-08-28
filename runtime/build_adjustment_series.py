from __future__ import annotations

import argparse
import json
from pathlib import Path

from src.core.pit_store import PITStore
from src.data.adjustments import AdjustmentFactorBuilder


def main() -> None:
    parser = argparse.ArgumentParser(
        description=(
            "Build a deterministic backward exchange-reference adjusted price series "
            "from an existing PIT data_snapshot_id."
        )
    )
    parser.add_argument("store", type=Path, help="PITStore root")
    parser.add_argument("data_snapshot_id", help="Existing PIT data snapshot id")
    parser.add_argument("security_id", help="Six-digit A-share security id")
    parser.add_argument("--exchange", default=None, help="Optional explicit SSE/SZSE")
    parser.add_argument("--output", type=Path, default=None)
    args = parser.parse_args()

    store = PITStore(args.store)
    records = tuple(store.materialize_snapshot(args.data_snapshot_id))
    series = AdjustmentFactorBuilder().build(
        records,
        security_id=args.security_id,
        exchange=args.exchange,
    )
    rendered = json.dumps(series.to_dict(), ensure_ascii=False, indent=2, sort_keys=True) + "\n"
    print(rendered, end="")
    if args.output is not None:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(rendered, encoding="utf-8")


if __name__ == "__main__":
    main()
