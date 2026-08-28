from __future__ import annotations

import argparse
import json
from pathlib import Path

from src.features.snapshot import FeatureSnapshot
from src.strategies.short_mid.champion import ChampionScorer, load_champion_config


DEFAULT_CONFIG = Path("configs/short_mid/champion-v1.json")


def score_snapshot(snapshot_path: Path, config_path: Path) -> dict:
    row = json.loads(snapshot_path.read_text(encoding="utf-8"))
    snapshot = FeatureSnapshot.from_dict(row)
    scorer = ChampionScorer(load_champion_config(config_path))
    return scorer.score_feature_snapshot(snapshot).to_dict()


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Score one immutable Short/Mid FeatureSnapshot with the frozen Champion config."
    )
    parser.add_argument("snapshot", type=Path, help="FeatureSnapshot JSON file")
    parser.add_argument(
        "--config",
        type=Path,
        default=DEFAULT_CONFIG,
        help="Champion config JSON",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=None,
        help="Optional output JSON path; stdout is always emitted",
    )
    args = parser.parse_args()

    result = score_snapshot(args.snapshot, args.config)
    rendered = json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True) + "\n"
    print(rendered, end="")
    if args.output is not None:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(rendered, encoding="utf-8")


if __name__ == "__main__":
    main()
