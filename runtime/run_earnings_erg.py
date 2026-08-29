from __future__ import annotations

import argparse
import json
import os
import tempfile
from pathlib import Path

from src.core.pit_store import PITStore
from src.features.earnings_erg_pipeline import (
    EarningsERGAssemblyContract,
    EarningsERGEndToEndPipeline,
    event_reaction_measurement_from_dict,
)
from src.features.erg_earnings_materiality import EarningsMaterialityContract
from src.features.erg_expectation_surprise import ExpectationSurpriseContract


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Run one content-addressed, Shadow-only EARNINGS ERG research pipeline."
    )
    parser.add_argument("--store-dir", required=True)
    parser.add_argument("--snapshot-id", required=True)
    parser.add_argument(
        "--config",
        required=True,
        help="JSON containing expectation_surprise_contract, earnings_materiality_contract and assembly_contract",
    )
    parser.add_argument(
        "--event-measurement",
        required=True,
        help="Serialized EventReactionMeasurement JSON built under a frozen reaction-window contract",
    )
    parser.add_argument(
        "--output-dir",
        required=True,
        help="Directory where <erg_run_id>.json is persisted idempotently",
    )
    return parser.parse_args()


def _canonical_pretty(payload: dict) -> str:
    return json.dumps(payload, ensure_ascii=False, sort_keys=True, indent=2, allow_nan=False) + "\n"


def _atomic_write_idempotent(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.exists():
        existing = path.read_text(encoding="utf-8")
        if existing != content:
            raise ValueError(f"refusing to overwrite mismatched existing ERG run artifact: {path}")
        return
    fd, tmp_name = tempfile.mkstemp(prefix=f".{path.name}.", dir=str(path.parent))
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as handle:
            handle.write(content)
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(tmp_name, path)
    finally:
        if os.path.exists(tmp_name):
            os.unlink(tmp_name)


def main() -> int:
    args = parse_args()
    config = json.loads(Path(args.config).read_text(encoding="utf-8"))
    measurement_payload = json.loads(Path(args.event_measurement).read_text(encoding="utf-8"))

    expectation_contract = ExpectationSurpriseContract.from_dict(
        config["expectation_surprise_contract"]
    )
    materiality_contract = EarningsMaterialityContract.from_dict(
        config["earnings_materiality_contract"]
    )
    assembly_contract = EarningsERGAssemblyContract.from_dict(config["assembly_contract"])
    event_measurement = event_reaction_measurement_from_dict(measurement_payload)

    store = PITStore(args.store_dir)
    manifest = store.load_snapshot(args.snapshot_id)
    if manifest["strategy_id"] != "a_share_short_mid" or manifest["sleeve"] != "short_mid":
        raise ValueError("earnings ERG runtime requires a_share_short_mid / short_mid snapshot")
    records = store.materialize_snapshot(args.snapshot_id)

    artifacts = EarningsERGEndToEndPipeline().run(
        records,
        data_snapshot_id=str(manifest["snapshot_id"]),
        as_of=str(manifest["as_of"]),
        expectation_contract=expectation_contract,
        materiality_contract=materiality_contract,
        event_measurement=event_measurement,
        assembly_contract=assembly_contract,
    )
    payload = artifacts.to_dict()
    output = Path(args.output_dir) / f"{artifacts.run.run_id}.json"
    _atomic_write_idempotent(output, _canonical_pretty(payload))
    print(artifacts.run.run_id)
    print(output)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
