from __future__ import annotations

import argparse
import json
from pathlib import Path

from src.features.erg_shadow import ERGEvidenceBundle, ERGShadowStateMachine


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Validate an ERG Shadow evidence bundle and resolve research state."
    )
    parser.add_argument("--input", required=True, help="ERG evidence-bundle JSON path")
    parser.add_argument("--output", help="Optional output JSON path")
    args = parser.parse_args()

    payload = json.loads(Path(args.input).read_text(encoding="utf-8"))
    bundle = ERGEvidenceBundle.from_dict(payload)
    bundle.validate()
    decision = ERGShadowStateMachine().evaluate(bundle)

    output = {
        "evidence_bundle": bundle.to_dict(),
        "shadow_decision": decision.to_dict(),
    }
    text = json.dumps(output, ensure_ascii=False, indent=2) + "\n"
    if args.output:
        path = Path(args.output)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text, encoding="utf-8")
    else:
        print(text, end="")


if __name__ == "__main__":
    main()
