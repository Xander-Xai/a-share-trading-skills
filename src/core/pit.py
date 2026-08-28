from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Iterable


VALID_SLEEVES = {"long", "short_mid"}
VALID_PERMITTED_USE = {
    "RESEARCH_ONLY",
    "INTERNAL_PRODUCTION_ALLOWED",
    "REDISTRIBUTION_ALLOWED",
    "UNRESOLVED_LICENSE",
}


def _parse_aware_timestamp(value: str | None, field_name: str) -> datetime | None:
    if value is None:
        return None
    parsed = datetime.fromisoformat(value)
    if parsed.tzinfo is None or parsed.utcoffset() is None:
        raise ValueError(f"{field_name} must be timezone-aware ISO-8601")
    return parsed


@dataclass(frozen=True)
class PITMetadata:
    record_id: str
    entity_type: str
    source: str
    source_tier: str
    source_snapshot_id: str
    revision_id: str
    available_at: str
    ingested_at: str
    strategy_visibility: tuple[str, ...]
    permitted_use: str = "UNRESOLVED_LICENSE"
    effective_at: str | None = None
    published_at: str | None = None
    payload_hash: str | None = None
    security_id: str | None = None
    exchange: str | None = None
    source_locator: str | None = None
    supersedes_revision_id: str | None = None
    is_current_revision: bool | None = None
    redistribution_allowed: bool | None = None
    retention_rule: str | None = None

    def validate(self) -> None:
        required_text = {
            "record_id": self.record_id,
            "entity_type": self.entity_type,
            "source": self.source,
            "source_tier": self.source_tier,
            "source_snapshot_id": self.source_snapshot_id,
            "revision_id": self.revision_id,
            "available_at": self.available_at,
            "ingested_at": self.ingested_at,
        }
        for field_name, value in required_text.items():
            if not isinstance(value, str) or not value.strip():
                raise ValueError(f"{field_name} is required")

        for field_name, value in (
            ("source_locator", self.source_locator),
            ("security_id", self.security_id),
            ("exchange", self.exchange),
            ("supersedes_revision_id", self.supersedes_revision_id),
            ("retention_rule", self.retention_rule),
        ):
            if value is not None and (not isinstance(value, str) or not value.strip()):
                raise ValueError(f"{field_name} must be non-empty when present")

        available_at = _parse_aware_timestamp(self.available_at, "available_at")
        ingested_at = _parse_aware_timestamp(self.ingested_at, "ingested_at")
        published_at = _parse_aware_timestamp(self.published_at, "published_at")
        _parse_aware_timestamp(self.effective_at, "effective_at")

        if published_at is not None and available_at is not None and available_at < published_at:
            raise ValueError("available_at cannot precede published_at")

        # Backfills are allowed: a historical record may be ingested much later.
        if available_at is not None and ingested_at is not None and ingested_at < available_at:
            raise ValueError("ingested_at cannot precede available_at")

        if not self.strategy_visibility:
            raise ValueError("strategy_visibility must contain at least one sleeve")
        invalid_sleeves = set(self.strategy_visibility) - VALID_SLEEVES
        if invalid_sleeves:
            raise ValueError(f"invalid strategy_visibility: {sorted(invalid_sleeves)}")

        if self.permitted_use not in VALID_PERMITTED_USE:
            raise ValueError(f"invalid permitted_use: {self.permitted_use}")

        if self.is_current_revision is not None and not isinstance(self.is_current_revision, bool):
            raise ValueError("is_current_revision must be bool when present")
        if self.redistribution_allowed is not None and not isinstance(self.redistribution_allowed, bool):
            raise ValueError("redistribution_allowed must be bool when present")

    def visible_to(self, sleeve: str, replay_as_of: str) -> bool:
        """Return whether this record is observable to a sleeve at replay time."""
        self.validate()
        if sleeve not in VALID_SLEEVES:
            raise ValueError(f"invalid sleeve: {sleeve}")
        if sleeve not in self.strategy_visibility:
            return False

        replay_time = _parse_aware_timestamp(replay_as_of, "replay_as_of")
        available_time = _parse_aware_timestamp(self.available_at, "available_at")
        assert replay_time is not None and available_time is not None
        return available_time <= replay_time


def normalize_visibility(values: Iterable[str]) -> tuple[str, ...]:
    visibility = tuple(dict.fromkeys(str(v) for v in values))
    invalid = set(visibility) - VALID_SLEEVES
    if invalid:
        raise ValueError(f"invalid strategy visibility: {sorted(invalid)}")
    if not visibility:
        raise ValueError("strategy visibility cannot be empty")
    return visibility
