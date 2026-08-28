from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from src.core.pit_store import PITStore


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Build a deterministic point-in-time data snapshot from the local PIT store."
    )
    parser.add_argument("--store-root", type=Path, required=True)
    parser.add_argument("--strategy-id", required=True)
    parser.add_argument("--sleeve", choices=["long", "short_mid"], required=True)
    parser.add_argument("--as-of", required=True, help="Timezone-aware ISO-8601 timestamp")
    parser.add_argument(
        "--intended-use",
        choices=["RESEARCH", "INTERNAL_PRODUCTION", "REDISTRIBUTION"],
        default="RESEARCH",
    )
    parser.add_argument("--entity-type", action="append", dest="entity_types")
    parser.add_argument("--security-id", action="append", dest="security_ids")
    args = parser.parse_args()

    store = PITStore(args.store_root)
    manifest = store.create_snapshot(
        strategy_id=args.strategy_id,
        sleeve=args.sleeve,
        as_of=args.as_of,
        intended_use=args.intended_use,
        entity_types=args.entity_types,
        security_ids=args.security_ids,
    )
    print(json.dumps(manifest, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
