from __future__ import annotations

import hashlib
import json
import os
import tempfile
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any, Mapping

from src.core.pit import VALID_PERMITTED_USE


RAW_ARCHIVE_SCHEMA_VERSION = "1.0"


def _canonical_json(value: Any) -> str:
    return json.dumps(
        value,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
        allow_nan=False,
    )


def _sha256_bytes(content: bytes) -> str:
    return hashlib.sha256(content).hexdigest()


def _sha256_text(content: str) -> str:
    return hashlib.sha256(content.encode("utf-8")).hexdigest()


def _parse_aware(value: str, field_name: str) -> datetime:
    parsed = datetime.fromisoformat(value)
    if parsed.tzinfo is None or parsed.utcoffset() is None:
        raise ValueError(f"{field_name} must be timezone-aware ISO-8601")
    return parsed


def _require_text(value: str, field_name: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{field_name} is required")
    return value.strip()


def _atomic_write_bytes(path: Path, content: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, tmp_name = tempfile.mkstemp(prefix=f".{path.name}.", dir=str(path.parent))
    try:
        with os.fdopen(fd, "wb") as handle:
            handle.write(content)
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(tmp_name, path)
    finally:
        if os.path.exists(tmp_name):
            os.unlink(tmp_name)


def _atomic_write_text(path: Path, content: str) -> None:
    _atomic_write_bytes(path, content.encode("utf-8"))


@dataclass(frozen=True)
class RawEvidenceManifest:
    raw_snapshot_id: str
    source: str
    locator: str
    observed_at: str
    content_hash: str
    byte_length: int
    content_type: str
    permitted_use: str
    source_tier: str | None = None
    encoding: str | None = None
    status_code: int | None = None
    headers: Mapping[str, str] | None = None

    def validate(self) -> None:
        for field_name, value in (
            ("raw_snapshot_id", self.raw_snapshot_id),
            ("source", self.source),
            ("locator", self.locator),
            ("observed_at", self.observed_at),
            ("content_hash", self.content_hash),
            ("content_type", self.content_type),
        ):
            _require_text(value, field_name)
        _parse_aware(self.observed_at, "observed_at")
        if len(self.content_hash) != 64:
            raise ValueError("content_hash must be SHA-256 hex")
        try:
            int(self.content_hash, 16)
        except ValueError as exc:
            raise ValueError("content_hash must be SHA-256 hex") from exc
        if not isinstance(self.byte_length, int) or self.byte_length <= 0:
            raise ValueError("byte_length must be a positive integer")
        if self.permitted_use not in VALID_PERMITTED_USE:
            raise ValueError(f"invalid permitted_use: {self.permitted_use}")
        if self.status_code is not None:
            if not isinstance(self.status_code, int) or not 100 <= self.status_code <= 599:
                raise ValueError("status_code must be a valid HTTP status when present")
        if self.headers is not None:
            for key, value in self.headers.items():
                _require_text(str(key), "header name")
                if not isinstance(value, str):
                    raise ValueError("header values must be strings")

    def identity_payload(self) -> dict[str, Any]:
        self.validate()
        return {
            "schema_version": RAW_ARCHIVE_SCHEMA_VERSION,
            "source": self.source,
            "locator": self.locator,
            "observed_at": self.observed_at,
            "content_hash": self.content_hash,
            "byte_length": self.byte_length,
            "content_type": self.content_type,
            "permitted_use": self.permitted_use,
            "source_tier": self.source_tier,
            "encoding": self.encoding,
            "status_code": self.status_code,
            "headers": None if self.headers is None else dict(sorted(self.headers.items())),
        }

    def to_dict(self) -> dict[str, Any]:
        return {**self.identity_payload(), "raw_snapshot_id": self.raw_snapshot_id}


class RawEvidenceArchive:
    """Content-addressed immutable archive for raw source evidence.

    This reference backend stores response/content bytes by SHA-256 and a
    separate observation manifest. It is intentionally source-agnostic and does
    not perform network requests itself.
    """

    def __init__(self, root: str | Path):
        self.root = Path(root)
        self.objects_dir = self.root / "objects"
        self.manifests_dir = self.root / "manifests"

    def _object_path(self, content_hash: str) -> Path:
        return self.objects_dir / content_hash[:2] / content_hash

    def _manifest_path(self, raw_snapshot_id: str) -> Path:
        return self.manifests_dir / f"{raw_snapshot_id}.json"

    def archive_bytes(
        self,
        *,
        source: str,
        locator: str,
        observed_at: str,
        content: bytes,
        content_type: str,
        permitted_use: str = "UNRESOLVED_LICENSE",
        source_tier: str | None = None,
        encoding: str | None = None,
        status_code: int | None = None,
        headers: Mapping[str, str] | None = None,
    ) -> RawEvidenceManifest:
        _require_text(source, "source")
        _require_text(locator, "locator")
        _parse_aware(observed_at, "observed_at")
        _require_text(content_type, "content_type")
        if not isinstance(content, bytes) or not content:
            raise ValueError("content must be non-empty bytes")
        if permitted_use not in VALID_PERMITTED_USE:
            raise ValueError(f"invalid permitted_use: {permitted_use}")

        content_hash = _sha256_bytes(content)
        provisional = RawEvidenceManifest(
            raw_snapshot_id="pending",
            source=source,
            locator=locator,
            observed_at=observed_at,
            content_hash=content_hash,
            byte_length=len(content),
            content_type=content_type,
            permitted_use=permitted_use,
            source_tier=source_tier,
            encoding=encoding,
            status_code=status_code,
            headers=None if headers is None else dict(headers),
        )
        identity = provisional.identity_payload()
        raw_snapshot_id = _sha256_text(_canonical_json(identity))
        manifest = RawEvidenceManifest(
            raw_snapshot_id=raw_snapshot_id,
            source=source,
            locator=locator,
            observed_at=observed_at,
            content_hash=content_hash,
            byte_length=len(content),
            content_type=content_type,
            permitted_use=permitted_use,
            source_tier=source_tier,
            encoding=encoding,
            status_code=status_code,
            headers=None if headers is None else dict(headers),
        )
        manifest.validate()

        object_path = self._object_path(content_hash)
        if object_path.exists():
            existing = object_path.read_bytes()
            if _sha256_bytes(existing) != content_hash:
                raise ValueError("raw evidence object hash mismatch")
        else:
            _atomic_write_bytes(object_path, content)

        manifest_path = self._manifest_path(raw_snapshot_id)
        manifest_text = json.dumps(manifest.to_dict(), ensure_ascii=False, indent=2) + "\n"
        if manifest_path.exists():
            existing_manifest = self.load_manifest(raw_snapshot_id)
            if existing_manifest.to_dict() != manifest.to_dict():
                raise ValueError("raw evidence manifest identity conflict")
        else:
            _atomic_write_text(manifest_path, manifest_text)
        return self.load_manifest(raw_snapshot_id)

    def load_manifest(self, raw_snapshot_id: str) -> RawEvidenceManifest:
        _require_text(raw_snapshot_id, "raw_snapshot_id")
        path = self._manifest_path(raw_snapshot_id)
        if not path.exists():
            raise FileNotFoundError(path)
        row = json.loads(path.read_text(encoding="utf-8"))
        if row.pop("schema_version", None) != RAW_ARCHIVE_SCHEMA_VERSION:
            raise ValueError("unsupported raw archive schema")
        manifest = RawEvidenceManifest(**row)
        manifest.validate()
        expected_id = _sha256_text(_canonical_json(manifest.identity_payload()))
        if expected_id != raw_snapshot_id:
            raise ValueError("raw evidence manifest content does not match raw_snapshot_id")
        return manifest

    def read_bytes(self, raw_snapshot_id: str) -> bytes:
        manifest = self.load_manifest(raw_snapshot_id)
        path = self._object_path(manifest.content_hash)
        if not path.exists():
            raise ValueError("raw evidence object missing")
        content = path.read_bytes()
        if len(content) != manifest.byte_length:
            raise ValueError("raw evidence byte_length mismatch")
        if _sha256_bytes(content) != manifest.content_hash:
            raise ValueError("raw evidence content hash mismatch")
        return content
