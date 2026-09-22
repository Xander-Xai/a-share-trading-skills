"""Private persistence for frozen pre-trade authorization cards."""
from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Mapping


def _canonical_hash(value: Mapping[str, Any]) -> str:
    payload = json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


def persist_pretrade_card(
    card: Mapping[str, Any],
    *,
    snapshot: Mapping[str, Any],
    policy_versions: Mapping[str, str],
    root: str | Path = "runtime/pretrade_authorizations",
) -> Path:
    """Persist a card below a caller-controlled private directory.

    The function rejects paths outside the requested root and writes atomically
    enough for a local CLI. Callers must keep the root ignored by Git.
    """
    target_root = Path(root)
    target_root.mkdir(parents=True, exist_ok=True)
    decision_id = str(card.get("decision_id", "")).strip()
    if not decision_id or any(part in decision_id for part in ("/", "\\", "..")):
        raise ValueError("decision_id must be a safe identifier")
    payload = dict(card)
    payload.update(
        timestamp=datetime.now(timezone.utc).isoformat(),
        input_snapshot_hash=_canonical_hash(snapshot),
        policy_versions=dict(policy_versions),
    )
    destination = (target_root / f"{decision_id}.json").resolve()
    if target_root.resolve() not in destination.parents:
        raise ValueError("authorization card path escaped private root")
    destination.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return destination
