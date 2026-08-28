from __future__ import annotations

import re
from dataclasses import dataclass
from datetime import date, datetime
from typing import Iterable
from urllib.parse import urlparse

from src.data.adapters import NormalizedRecordCandidate
from src.data.coverage import DatasetCoverage
from src.data.entities import CorporateAction


VERIFICATION_METHOD = "OFFICIAL_SOURCE_ENUMERATION"
VALID_EXCHANGES = {"SSE", "SZSE"}
VALID_SCOPE_TYPES = {"SECURITY", "EXCHANGE"}
VALID_COMPLETENESS = {"CONFIRMED_COMPLETE", "PARTIAL", "UNRESOLVED"}
OFFICIAL_HOSTS = {
    "SSE": ("sse.com.cn",),
    "SZSE": ("szse.cn",),
}
_SHA256_RE = re.compile(r"^[0-9a-f]{64}$")
_SECURITY_RE = re.compile(r"^\d{6}$")


def _require_text(value: str, field_name: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{field_name} is required")
    return value.strip()


def _parse_date(value: str, field_name: str) -> date:
    try:
        return date.fromisoformat(value)
    except Exception as exc:
        raise ValueError(f"{field_name} must be YYYY-MM-DD") from exc


def _parse_aware(value: str | None, field_name: str) -> datetime | None:
    if value is None:
        return None
    try:
        parsed = datetime.fromisoformat(value)
    except Exception as exc:
        raise ValueError(f"{field_name} must be ISO-8601") from exc
    if parsed.tzinfo is None or parsed.utcoffset() is None:
        raise ValueError(f"{field_name} must be timezone-aware ISO-8601")
    return parsed


def _validate_official_url(exchange: str, url: str) -> str:
    url = _require_text(url, "source_url")
    parsed = urlparse(url)
    if parsed.scheme != "https":
        raise ValueError("official corporate-action source_url must use https")
    host = (parsed.hostname or "").lower()
    allowed = OFFICIAL_HOSTS.get(exchange, ())
    if not allowed or not any(host == item or host.endswith(f".{item}") for item in allowed):
        raise ValueError(
            f"source_url host {host!r} is not an approved official host for {exchange}"
        )
    return url


@dataclass(frozen=True)
class OfficialCorporateActionRow:
    security_id: str
    action_id: str
    action_type: str
    announcement_date: str
    ex_date: str
    record_date: str | None = None
    pay_date: str | None = None
    cash_per_share: float | None = None
    ratio: float | None = None
    currency: str = "CNY"
    source_locator: str | None = None
    published_at: str | None = None
    revision_id: str = "rev-1"
    supersedes_revision_id: str | None = None
    is_current_revision: bool | None = True

    def validate(self, *, exchange: str, start_date: str, end_date: str) -> None:
        if not _SECURITY_RE.match(self.security_id):
            raise ValueError("security_id must be six numeric digits")
        _require_text(self.action_id, "action_id")
        _require_text(self.action_type, "action_type")
        _parse_date(self.announcement_date, "announcement_date")
        ex_date = _parse_date(self.ex_date, "ex_date")
        start = _parse_date(start_date, "start_date")
        end = _parse_date(end_date, "end_date")
        if ex_date < start or ex_date > end:
            raise ValueError("corporate-action ex_date must lie inside batch coverage range")
        if self.source_locator is not None:
            _validate_official_url(exchange, self.source_locator)
        published = _parse_aware(self.published_at, "published_at")
        if published is not None and published.date() > ex_date:
            raise ValueError("published_at cannot occur after ex_date")
        _require_text(self.revision_id, "revision_id")

        # Canonical entity validation owns the remaining field-level checks.
        CorporateAction(
            security_id=self.security_id,
            action_id=self.action_id,
            action_type=self.action_type,
            announcement_date=self.announcement_date,
            record_date=self.record_date,
            ex_date=self.ex_date,
            pay_date=self.pay_date,
            cash_per_share=self.cash_per_share,
            ratio=self.ratio,
            currency=self.currency,
        ).validate()


@dataclass(frozen=True)
class OfficialCorporateActionBatch:
    """A verified snapshot of an official implemented-corporate-action enumeration.

    Completeness is defined over *implemented actions keyed by ex_date* inside an
    explicit scope/date range. `CONFIRMED_COMPLETE` requires a RawEvidenceArchive
    SHA-256 snapshot id and an exact source-row count match.
    """

    exchange: str
    source_name: str
    source_url: str
    source_snapshot_id: str
    observed_at: str
    start_date: str
    end_date: str
    scope_type: str
    source_row_count: int
    rows: tuple[OfficialCorporateActionRow, ...]
    completeness_status: str = "CONFIRMED_COMPLETE"
    security_id: str | None = None
    permitted_use: str = "UNRESOLVED_LICENSE"
    source_tier: str = "TIER1"
    strategy_visibility: tuple[str, ...] = ("long", "short_mid")
    batch_revision_id: str = "batch-v1"

    def validate(self) -> None:
        if self.exchange not in VALID_EXCHANGES:
            raise ValueError(f"unsupported exchange: {self.exchange}")
        _require_text(self.source_name, "source_name")
        _validate_official_url(self.exchange, self.source_url)
        _require_text(self.source_snapshot_id, "source_snapshot_id")
        observed = _parse_aware(self.observed_at, "observed_at")
        assert observed is not None
        start = _parse_date(self.start_date, "start_date")
        end = _parse_date(self.end_date, "end_date")
        if end < start:
            raise ValueError("end_date cannot precede start_date")
        if self.scope_type not in VALID_SCOPE_TYPES:
            raise ValueError(f"invalid scope_type: {self.scope_type}")
        if self.completeness_status not in VALID_COMPLETENESS:
            raise ValueError(f"invalid completeness_status: {self.completeness_status}")
        if not isinstance(self.source_row_count, int) or isinstance(self.source_row_count, bool):
            raise ValueError("source_row_count must be an integer")
        if self.source_row_count < 0:
            raise ValueError("source_row_count cannot be negative")
        if self.scope_type == "SECURITY":
            if self.security_id is None or not _SECURITY_RE.match(self.security_id):
                raise ValueError("SECURITY batch requires six-digit security_id")
        elif self.security_id is not None:
            raise ValueError("EXCHANGE batch must not carry security_id")
        if self.source_tier != "TIER1":
            raise ValueError("official corporate-action enumeration must remain TIER1")
        if set(self.strategy_visibility) != {"long", "short_mid"}:
            raise ValueError("official corporate-action facts must be visible to both stock sleeves")
        _require_text(self.batch_revision_id, "batch_revision_id")

        if self.completeness_status == "CONFIRMED_COMPLETE":
            if not _SHA256_RE.match(self.source_snapshot_id):
                raise ValueError(
                    "CONFIRMED_COMPLETE official enumeration requires a RawEvidenceArchive SHA-256 source_snapshot_id"
                )
            if self.source_row_count != len(self.rows):
                raise ValueError(
                    "CONFIRMED_COMPLETE requires source_row_count == normalized row count"
                )

        seen: set[tuple[str, str]] = set()
        for row in self.rows:
            row.validate(
                exchange=self.exchange,
                start_date=self.start_date,
                end_date=self.end_date,
            )
            if self.scope_type == "SECURITY" and row.security_id != self.security_id:
                raise ValueError("SECURITY batch contains a row for another security")
            identity = (row.security_id, row.action_id)
            if identity in seen:
                raise ValueError(f"duplicate corporate action in batch: {identity}")
            seen.add(identity)

    def collect(self, *, as_of: str) -> Iterable[NormalizedRecordCandidate]:
        self.validate()
        replay_time = _parse_aware(as_of, "as_of")
        observed = _parse_aware(self.observed_at, "observed_at")
        assert replay_time is not None and observed is not None
        if replay_time < observed:
            return

        for row in self.rows:
            entity = CorporateAction(
                security_id=row.security_id,
                action_id=row.action_id,
                action_type=row.action_type,
                announcement_date=row.announcement_date,
                record_date=row.record_date,
                ex_date=row.ex_date,
                pay_date=row.pay_date,
                cash_per_share=row.cash_per_share,
                ratio=row.ratio,
                currency=row.currency,
            )
            published = _parse_aware(row.published_at, "published_at")
            available_at = observed.isoformat() if published is None else published.isoformat()
            if published is not None and observed < published:
                raise ValueError("observed_at cannot precede row published_at")

            yield NormalizedRecordCandidate.from_entity(
                entity=entity,
                source=self.source_name,
                source_tier=self.source_tier,
                source_snapshot_id=self.source_snapshot_id,
                source_locator=row.source_locator or self.source_url,
                revision_id=row.revision_id,
                published_at=None if published is None else published.isoformat(),
                effective_at=f"{row.ex_date}T00:00:00+08:00",
                available_at=available_at,
                ingested_at=observed.isoformat(),
                strategy_visibility=self.strategy_visibility,
                permitted_use=self.permitted_use,
                exchange=self.exchange,
                supersedes_revision_id=row.supersedes_revision_id,
                is_current_revision=row.is_current_revision,
            )

        coverage = DatasetCoverage(
            coverage_id=(
                f"{self.exchange}-{self.start_date}-{self.end_date}-"
                f"{self.scope_type.lower()}-official-corporate-actions"
            ),
            dataset_family="CORPORATE_ACTION",
            scope_type=self.scope_type,
            security_id=self.security_id,
            exchange=self.exchange,
            start_date=self.start_date,
            end_date=self.end_date,
            completeness_status=self.completeness_status,
            verification_method=VERIFICATION_METHOD,
            expected_count=self.source_row_count,
            observed_count=len(self.rows),
            note=(
                "implemented corporate actions enumerated by ex_date from an official "
                "source snapshot; coverage reflects only the captured scope/date range"
            ),
        )
        yield NormalizedRecordCandidate.from_entity(
            entity=coverage,
            source=self.source_name,
            source_tier=self.source_tier,
            source_snapshot_id=self.source_snapshot_id,
            source_locator=self.source_url,
            revision_id=self.batch_revision_id,
            effective_at=f"{self.start_date}T00:00:00+08:00",
            available_at=observed.isoformat(),
            ingested_at=observed.isoformat(),
            strategy_visibility=self.strategy_visibility,
            permitted_use=self.permitted_use,
            exchange=self.exchange,
            is_current_revision=True,
        )
