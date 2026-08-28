from __future__ import annotations

import argparse
import json
from pathlib import Path

from src.core.pit_store import PITStore
from src.features.short_mid_market import ShortMidMarketFeatureBuilder


def main() -> None:
    parser = argparse.ArgumentParser(
        description=(
            "Build a deterministic Short/Mid market FeatureSnapshot from an existing "
            "PIT data_snapshot_id. Coverage-confirmation flags must reflect an upstream "
            "data-quality audit; omitting them keeps adjustment-sensitive fields UNRESOLVED."
        )
    )
    parser.add_argument("store", type=Path, help="PITStore root")
    parser.add_argument("data_snapshot_id", help="Existing PIT data snapshot id")
    parser.add_argument("security_id", help="Six-digit A-share security id")
    parser.add_argument(
        "--daily-bar-coverage-confirmed",
        action="store_true",
        help="Declare that trading-session DAILY_BAR coverage for the required window was independently verified.",
    )
    parser.add_argument(
        "--corporate-action-coverage-confirmed",
        action="store_true",
        help="Declare that corporate-action/ex-date coverage for the required window was independently verified.",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=None,
        help="Optional FeatureSnapshot JSON output path. JSON is always written to stdout.",
    )
    args = parser.parse_args()

    snapshot = ShortMidMarketFeatureBuilder().build_from_store(
        PITStore(args.store),
        data_snapshot_id=args.data_snapshot_id,
        security_id=args.security_id,
        daily_bar_coverage_confirmed=args.daily_bar_coverage_confirmed,
        corporate_action_coverage_confirmed=args.corporate_action_coverage_confirmed,
    )
    rendered = json.dumps(snapshot.to_dict(), ensure_ascii=False, indent=2, sort_keys=True) + "\n"
    print(rendered, end="")
    if args.output is not None:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(rendered, encoding="utf-8")


if __name__ == "__main__":
    main()
