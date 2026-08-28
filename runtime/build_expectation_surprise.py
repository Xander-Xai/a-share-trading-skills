from __future__ import annotations

import argparse
import json
from pathlib import Path

from src.core.pit_store import PITStore
from src.features.erg_expectation_surprise import (
    ExpectationSurpriseContract,
    PITExpectationSurpriseAdapter,
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Build source-backed ERG expectation/surprise evidence from a frozen PIT snapshot."
    )
    parser.add_argument("--store-dir", required=True)
    parser.add_argument("--snapshot-id", required=True)
    parser.add_argument("--config", required=True, help="JSON config containing contract and information_timestamp")
    parser.add_argument("--output", required=True)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    config = json.loads(Path(args.config).read_text(encoding="utf-8"))
    contract = ExpectationSurpriseContract.from_dict(config["contract"])
    information_timestamp = str(config["information_timestamp"])

    store = PITStore(args.store_dir)
    manifest = store.load_snapshot(args.snapshot_id)
    if manifest["strategy_id"] != "a_share_short_mid" or manifest["sleeve"] != "short_mid":
        raise ValueError("expectation/surprise runtime requires a_share_short_mid / short_mid snapshot")
    records = store.materialize_snapshot(args.snapshot_id)

    result = PITExpectationSurpriseAdapter().build(
        records,
        contract=contract,
        as_of=str(manifest["as_of"]),
        information_timestamp=information_timestamp,
    )
    output = Path(args.output)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(result.to_dict(), ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(result.result_id)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
