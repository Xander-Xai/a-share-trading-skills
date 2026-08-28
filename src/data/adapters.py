from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Iterable, Mapping, Protocol

from src.core.pit import PITMetadata
from src.data.entities import EntityMixin


@dataclass(frozen=True)
class NormalizedRecordCandidate:
    metadata: PITMetadata
    payload: dict[str, Any]

    def validate(self) -> None:
        self.metadata.validate()
        if not isinstance(self.payload, dict):
            raise ValueError("payload must be a dict")

    @classmethod
    def from_entity(
        cls,
        *,
        entity: EntityMixin,
        source: str,
        source_tier: str,
        source_snapshot_id: str,
        revision_id: str,
        available_at: str,
        ingested_at: str,
        strategy_visibility: tuple[str, ...],
        permitted_use: str,
        published_at: str | None = None,
        effective_at: str | None = None,
        exchange: str | None = None,
        source_locator: str | None = None,
        supersedes_revision_id: str | None = None,
        is_current_revision: bool | None = None,
        redistribution_allowed: bool | None = None,
        retention_rule: str | None = None,
    ) -> "NormalizedRecordCandidate":
        entity.validate()
        payload = entity.to_payload()
        security_id = getattr(entity, "security_id", None)
        metadata = PITMetadata(
            record_id=entity.record_id(),
            entity_type=entity.entity_type,
            source=source,
            source_tier=source_tier,
            source_snapshot_id=source_snapshot_id,
            revision_id=revision_id,
            available_at=available_at,
            ingested_at=ingested_at,
            strategy_visibility=strategy_visibility,
            permitted_use=permitted_use,
            effective_at=effective_at,
            published_at=published_at,
            security_id=security_id,
            exchange=exchange,
            source_locator=source_locator,
            supersedes_revision_id=supersedes_revision_id,
            is_current_revision=is_current_revision,
            redistribution_allowed=redistribution_allowed,
            retention_rule=retention_rule,
        )
        candidate = cls(metadata=metadata, payload=payload)
        candidate.validate()
        return candidate


class SourceAdapter(Protocol):
    """Contract for a source-specific adapter.

    An adapter may fetch raw evidence using any lawful/approved mechanism, but it
    must emit normalized PIT candidates. Strategy logic must never parse vendor
    rows directly.
    """

    adapter_id: str

    def collect(self, *, as_of: str) -> Iterable[NormalizedRecordCandidate]:
        ...


@dataclass(frozen=True)
class RawEvidenceReference:
    """Minimal lineage pointer for raw evidence archived outside normalized payloads."""

    source: str
    source_snapshot_id: str
    locator: str
    content_hash: str | None = None
    metadata: Mapping[str, Any] | None = None

    def validate(self) -> None:
        for field_name, value in (
            ("source", self.source),
            ("source_snapshot_id", self.source_snapshot_id),
            ("locator", self.locator),
        ):
            if not isinstance(value, str) or not value.strip():
                raise ValueError(f"{field_name} is required")
