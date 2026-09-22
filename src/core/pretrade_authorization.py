"""Private persistence for frozen pre-trade authorization cards."""
from __future__ import annotations

import hashlib
import json
import os
import tempfile
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Mapping


REPO_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_PRIVATE_AUTH_ROOT = REPO_ROOT / "runtime" / "pretrade_authorizations"


def _canonical_hash(value: Mapping[str, Any]) -> str:
    payload = json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


def authorization_input_snapshot(inputs: Mapping[str, Any]) -> tuple[dict[str, Any], str]:
    """Return the frozen authorization inputs and their deterministic hash."""
    frozen = json.loads(json.dumps(inputs, ensure_ascii=False, sort_keys=True, separators=(",", ":")))
    return frozen, _canonical_hash(frozen)


def _tighten_directory_permissions(path: Path) -> None:
    """Apply owner-only directory bits where the platform exposes them."""
    if os.name != "nt":
        path.chmod(0o700)


def _write_complete_file(path: Path, content: bytes) -> None:
    """Write and flush a complete private file, propagating any I/O failure."""
    descriptor = os.open(path, os.O_WRONLY | os.O_TRUNC, 0o600)
    try:
        with os.fdopen(descriptor, "wb") as handle:
            handle.write(content)
            handle.flush()
            os.fsync(handle.fileno())
    finally:
        if os.name != "nt" and path.exists():
            path.chmod(0o600)


def _publish_no_overwrite(temp_path: Path, destination: Path, content: bytes) -> None:
    """Publish atomically when hard links are available, with an exclusive fallback."""
    try:
        os.link(temp_path, destination)
        return
    except FileExistsError:
        raise
    except (OSError, NotImplementedError):
        # Some Windows filesystems or restricted runners do not permit hard links.
        # The fallback still creates the destination exclusively and removes it if
        # this invocation cannot finish writing it.
        pass

    descriptor = os.open(destination, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
    created = True
    try:
        with os.fdopen(descriptor, "wb") as handle:
            handle.write(content)
            handle.flush()
            os.fsync(handle.fileno())
    except BaseException:
        if created:
            destination.unlink(missing_ok=True)
        raise
    finally:
        if os.name != "nt" and destination.exists():
            destination.chmod(0o600)


def _write_private_card(path: Path, content: bytes) -> None:
    """Create a complete immutable card without exposing partial final content."""
    descriptor, raw_temp_path = tempfile.mkstemp(
        prefix=f".{path.stem}.", suffix=".tmp", dir=str(path.parent)
    )
    temp_path = Path(raw_temp_path)
    try:
        os.close(descriptor)
        if os.name != "nt":
            temp_path.chmod(0o600)
        _write_complete_file(temp_path, content)
        _publish_no_overwrite(temp_path, path, content)
    finally:
        temp_path.unlink(missing_ok=True)


def persist_pretrade_card(
    card: Mapping[str, Any],
    *,
    snapshot: Mapping[str, Any],
    policy_versions: Mapping[str, str],
    root: str | Path | None = None,
) -> Path:
    """Persist a card below a caller-controlled private directory.

    The function rejects paths outside the requested root and writes atomically
    enough for a local CLI. Callers must keep the root ignored by Git.
    """
    target_root = DEFAULT_PRIVATE_AUTH_ROOT if root is None else Path(root)
    target_root.mkdir(parents=True, exist_ok=True, mode=0o700)
    _tighten_directory_permissions(target_root)
    decision_id = str(card.get("decision_id", "")).strip()
    if not decision_id or any(part in decision_id for part in ("/", "\\", "..")):
        raise ValueError("decision_id must be a safe identifier")
    payload = dict(card)
    frozen_inputs, input_hash = authorization_input_snapshot(snapshot)
    payload.update(
        timestamp=datetime.now(timezone.utc).isoformat(),
        authorization_inputs=frozen_inputs,
        input_snapshot_hash=input_hash,
        policy_versions=dict(policy_versions),
    )
    destination = (target_root / f"{decision_id}.json").resolve()
    if target_root.resolve() not in destination.parents:
        raise ValueError("authorization card path escaped private root")
    encoded = (json.dumps(payload, ensure_ascii=False, indent=2) + "\n").encode("utf-8")
    _write_private_card(destination, encoded)
    return destination
