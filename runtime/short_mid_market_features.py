from __future__ import annotations

import argparse
import json
from pathlib import Path

from src.core.pit_store import PITStore
from src.features.short_mid_verified import VerifiedShortMidMarketFeatureBuilder


def main() -> None:
    parser = argparse.ArgumentParser(
        description=(
            "Build a deterministic Short/Mid market FeatureSnapshot from an existing "
            "PIT data_snapshot_id. Dataset completeness is resolved from PIT-visible "
            "DATASET_COVERAGE assertions; callers cannot manually promote coverage."
        )
    )
    parser.add_argument("store", type=Path, help="PITStore root")
    parser.add_argument("data_snapshot_id", help="Existing PIT data snapshot id")
    parser.add_argument("security_id", help="Six-digit A-share security id")
    parser.add_argument(
        "--output",
        type=Path,
        default=None,
        help="Optional FeatureSnapshot JSON output path. JSON is always written to stdout.",
    )
    args = parser.parse_args()

    snapshot = VerifiedShortMidMarketFeatureBuilder().build_from_store(
        PITStore(args.store),
        data_snapshot_id=args.data_snapshot_id,
        security_id=args.security_id,
    )
    rendered = json.dumps(snapshot.to_dict(), ensure_ascii=False, indent=2, sort_keys=True) + "\n"
    print(rendered, end="")
    if args.output is not None:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(rendered, encoding="utf-8")


if __name__ == "__main__":
    main()
