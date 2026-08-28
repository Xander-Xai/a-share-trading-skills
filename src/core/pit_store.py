from __future__ import annotations

import hashlib
import json
import os
import tempfile
from dataclasses import asdict, dataclass, replace
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable, Mapping

from src.core.pit import PITMetadata
from src.core.strategy_boundary import StrategyContext


SNAPSHOT_SCHEMA_VERSION = "1.0"
STORE_SCHEMA_VERSION = "1.0"
VALID_INTENDED_USE = {"RESEARCH", "INTERNAL_PRODUCTION", "REDISTRIBUTION"}


def _canonical_json(value: Any) -> str:
    return json.dumps(
        value,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
        allow_nan=False,
    )


def _sha256_text(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def payload_hash(payload: Mapping[str, Any]) -> str:
    return _sha256_text(_canonical_json(dict(payload)))


def _parse_aware_timestamp(value: str, field_name: str) -> datetime:
    parsed = datetime.fromisoformat(value)
    if parsed.tzinfo is None or parsed.utcoffset() is None:
        raise ValueError(f"{field_name} must be timezone-aware ISO-8601")
    return parsed


def _atomic_write_text(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
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


def _permitted_for(metadata: PITMetadata, intended_use: str) -> bool:
    if intended_use not in VALID_INTENDED_USE:
        raise ValueError(f"invalid intended_use: {intended_use}")
    if intended_use == "RESEARCH":
        return True
    if intended_use == "INTERNAL_PRODUCTION":
        return metadata.permitted_use in {
            "INTERNAL_PRODUCTION_ALLOWED",
            "REDISTRIBUTION_ALLOWED",
        }
    return metadata.permitted_use == "REDISTRIBUTION_ALLOWED"


@dataclass(frozen=True)
class StoredPITRecord:
    metadata: PITMetadata
    payload: dict[str, Any]

    def validate(self) -> None:
        self.metadata.validate()
        actual_hash = payload_hash(self.payload)
        if self.metadata.payload_hash != actual_hash:
            raise ValueError(
                "payload_hash mismatch: "
                f"metadata={self.metadata.payload_hash!r}, actual={actual_hash!r}"
            )

    @property
    def identity(self) -> tuple[str, str]:
        return (self.metadata.record_id, self.metadata.revision_id)

    def to_storage_dict(self) -> dict[str, Any]:
        self.validate()
        return {
            "store_schema_version": STORE_SCHEMA_VERSION,
            "metadata": asdict(self.metadata),
            "payload": self.payload,
        }

    @classmethod
    def from_storage_dict(cls, row: Mapping[str, Any]) -> "StoredPITRecord":
        if row.get("store_schema_version") != STORE_SCHEMA_VERSION:
            raise ValueError(
                f"unsupported store schema: {row.get('store_schema_version')!r}"
            )
        metadata = PITMetadata(**dict(row["metadata"]))
        payload = dict(row["payload"])
        record = cls(metadata=metadata, payload=payload)
        record.validate()
        return record


class PITStore:
    """Append-only reference PIT store with deterministic snapshot manifests.

    This is the first production-core storage contract, not a high-scale database.
    It deliberately uses an auditable JSONL log so replay semantics can stabilize
    before a Parquet/DuckDB or transactional backend is introduced.
    """

    def __init__(self, root: str | Path):
        self.root = Path(root)
        self.records_path = self.root / "records.jsonl"
        self.snapshots_dir = self.root / "snapshots"

    def append(self, metadata: PITMetadata, payload: Mapping[str, Any]) -> StoredPITRecord:
        metadata.validate()
        normalized_payload = dict(payload)
        actual_hash = payload_hash(normalized_payload)

        if metadata.payload_hash is None:
            metadata = replace(metadata, payload_hash=actual_hash)
        elif metadata.payload_hash != actual_hash:
            raise ValueError("metadata.payload_hash does not match payload")

        candidate = StoredPITRecord(metadata=metadata, payload=normalized_payload)
        candidate.validate()

        records = self.read_all()
        by_identity = {record.identity: record for record in records}
        existing = by_identity.get(candidate.identity)
        if existing is not None:
            if existing.metadata.payload_hash == candidate.metadata.payload_hash:
                return existing
            raise ValueError(
                "immutable PIT identity conflict: same record_id/revision_id has different payload"
            )

        if metadata.supersedes_revision_id:
            prior = [
                record
                for record in records
                if record.metadata.record_id == metadata.record_id
                and record.metadata.revision_id == metadata.supersedes_revision_id
            ]
            if not prior:
                raise ValueError(
                    "supersedes_revision_id does not exist for this record_id"
                )

        self.records_path.parent.mkdir(parents=True, exist_ok=True)
        line = _canonical_json(candidate.to_storage_dict()) + "\n"
        with self.records_path.open("a", encoding="utf-8") as handle:
            handle.write(line)
            handle.flush()
            os.fsync(handle.fileno())
        return candidate

    def read_all(self) -> list[StoredPITRecord]:
        if not self.records_path.exists():
            return []

        records: list[StoredPITRecord] = []
        with self.records_path.open("r", encoding="utf-8") as handle:
            for line_number, raw_line in enumerate(handle, start=1):
                line = raw_line.strip()
                if not line:
                    continue
                try:
                    row = json.loads(line)
                    records.append(StoredPITRecord.from_storage_dict(row))
                except Exception as exc:
                    raise ValueError(
                        f"invalid PIT store row at line {line_number}: {exc}"
                    ) from exc
        return records

    def visible_records(
        self,
        *,
        strategy_id: str,
        sleeve: str,
        as_of: str,
        intended_use: str = "RESEARCH",
        entity_types: Iterable[str] | None = None,
        security_ids: Iterable[str] | None = None,
    ) -> list[StoredPITRecord]:
        StrategyContext(strategy_id=strategy_id, sleeve=sleeve).validate()
        _parse_aware_timestamp(as_of, "as_of")
        if intended_use not in VALID_INTENDED_USE:
            raise ValueError(f"invalid intended_use: {intended_use}")

        entity_filter = None if entity_types is None else set(entity_types)
        security_filter = None if security_ids is None else set(security_ids)

        eligible: list[StoredPITRecord] = []
        blocked_for_use: list[StoredPITRecord] = []
        for record in self.read_all():
            metadata = record.metadata
            if entity_filter is not None and metadata.entity_type not in entity_filter:
                continue
            if security_filter is not None and metadata.security_id not in security_filter:
                continue
            if not metadata.visible_to(sleeve, as_of):
                continue
            if not _permitted_for(metadata, intended_use):
                blocked_for_use.append(record)
                continue
            eligible.append(record)

        if blocked_for_use and intended_use != "RESEARCH":
            blocked_ids = sorted(
                f"{r.metadata.record_id}:{r.metadata.revision_id}"
                for r in blocked_for_use
            )
            raise ValueError(
                f"records are not permitted for {intended_use}: {blocked_ids}"
            )

        # A stable record_id identifies one logical fact across revisions. Replay
        # selects the latest revision that was actually visible at as_of.
        latest: dict[str, StoredPITRecord] = {}
        for record in eligible:
            current = latest.get(record.metadata.record_id)
            if current is None or self._revision_sort_key(record) > self._revision_sort_key(current):
                latest[record.metadata.record_id] = record

        return sorted(
            latest.values(),
            key=lambda record: (
                record.metadata.entity_type,
                record.metadata.security_id or "",
                record.metadata.record_id,
            ),
        )

    @staticmethod
    def _revision_sort_key(record: StoredPITRecord) -> tuple[datetime, datetime, str]:
        return (
            _parse_aware_timestamp(record.metadata.available_at, "available_at"),
            _parse_aware_timestamp(record.metadata.ingested_at, "ingested_at"),
            record.metadata.revision_id,
        )

    def create_snapshot(
        self,
        *,
        strategy_id: str,
        sleeve: str,
        as_of: str,
        intended_use: str = "RESEARCH",
        entity_types: Iterable[str] | None = None,
        security_ids: Iterable[str] | None = None,
    ) -> dict[str, Any]:
        records = self.visible_records(
            strategy_id=strategy_id,
            sleeve=sleeve,
            as_of=as_of,
            intended_use=intended_use,
            entity_types=entity_types,
            security_ids=security_ids,
        )

        selection = [
            {
                "record_id": record.metadata.record_id,
                "revision_id": record.metadata.revision_id,
                "entity_type": record.metadata.entity_type,
                "security_id": record.metadata.security_id,
                "available_at": record.metadata.available_at,
                "source_snapshot_id": record.metadata.source_snapshot_id,
                "payload_hash": record.metadata.payload_hash,
            }
            for record in records
        ]
        identity_payload = {
            "snapshot_schema_version": SNAPSHOT_SCHEMA_VERSION,
            "strategy_id": strategy_id,
            "sleeve": sleeve,
            "as_of": as_of,
            "intended_use": intended_use,
            "records": selection,
        }
        snapshot_id = _sha256_text(_canonical_json(identity_payload))

        manifest = {
            **identity_payload,
            "snapshot_id": snapshot_id,
            "record_count": len(selection),
            "created_at": datetime.now(timezone.utc).isoformat(),
        }
        path = self.snapshots_dir / f"{snapshot_id}.json"
        if not path.exists():
            _atomic_write_text(path, json.dumps(manifest, ensure_ascii=False, indent=2) + "\n")
        return self.load_snapshot(snapshot_id)

    def load_snapshot(self, snapshot_id: str) -> dict[str, Any]:
        path = self.snapshots_dir / f"{snapshot_id}.json"
        if not path.exists():
            raise FileNotFoundError(path)
        manifest = json.loads(path.read_text(encoding="utf-8"))
        if manifest.get("snapshot_id") != snapshot_id:
            raise ValueError("snapshot manifest id mismatch")
        return manifest

    def materialize_snapshot(self, snapshot_id: str) -> list[StoredPITRecord]:
        manifest = self.load_snapshot(snapshot_id)
        records = self.read_all()
        index = {
            (
                record.metadata.record_id,
                record.metadata.revision_id,
                record.metadata.payload_hash,
            ): record
            for record in records
        }

        materialized: list[StoredPITRecord] = []
        for ref in manifest.get("records", []):
            key = (ref["record_id"], ref["revision_id"], ref["payload_hash"])
            record = index.get(key)
            if record is None:
                raise ValueError(f"snapshot record missing or mutated: {key}")
            materialized.append(record)
        return materialized
