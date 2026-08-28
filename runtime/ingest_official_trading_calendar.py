from __future__ import annotations

import argparse
import json
from pathlib import Path

from src.core.pit_store import PITStore
from src.data.ingest import ingest_candidates
from src.data.official_trading_calendar import load_official_calendar_plans


DEFAULT_CONFIG = Path("configs/data/trading_calendar/cn-a-share-2026-official.json")


def main() -> None:
    parser = argparse.ArgumentParser(
        description=(
            "Ingest curated official SSE/SZSE annual trading-calendar plans into "
            "the canonical PITStore. This command performs no undocumented live scraping."
        )
    )
    parser.add_argument("store", type=Path, help="PITStore root")
    parser.add_argument(
        "--config",
        type=Path,
        default=DEFAULT_CONFIG,
        help=f"Official calendar plan config (default: {DEFAULT_CONFIG})",
    )
    parser.add_argument(
        "--as-of",
        required=True,
        help="Timezone-aware replay/collection cutoff, e.g. 2026-08-28T23:26:00+08:00",
    )
    args = parser.parse_args()

    store = PITStore(args.store)
    results = []
    for plan in load_official_calendar_plans(args.config):
        result = ingest_candidates(
            store,
            plan.collect(as_of=args.as_of),
            adapter_id=f"{plan.exchange}_OFFICIAL_TRADING_CALENDAR_PLAN_V1",
        )
        results.append(
            {
                "exchange": plan.exchange,
                "year": plan.year,
                "adapter_id": result.adapter_id,
                "received": result.received,
                "written_or_existing": result.written_or_existing,
                "source_url": plan.source_url,
                "source_snapshot_id": plan.source_snapshot_id,
                "available_at": plan.available_at,
                "permitted_use": plan.permitted_use,
            }
        )

    print(json.dumps({"results": results}, ensure_ascii=False, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
