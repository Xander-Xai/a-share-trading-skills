from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Iterable, Protocol
from urllib.parse import urlparse

from src.data.adapters import NormalizedRecordCandidate
from src.data.entities import Disclosure


class TimestampResolutionError(ValueError):
    """Raised when disclosure visibility cannot be resolved without inventing time."""


VALID_VISIBILITY_BASIS = {"OFFICIAL_TIMESTAMP", "FIRST_OBSERVED"}


def _parse_aware(value: str | None, field_name: str) -> datetime | None:
    if value is None:
        return None
    parsed = datetime.fromisoformat(value)
    if parsed.tzinfo is None or parsed.utcoffset() is None:
        raise ValueError(f"{field_name} must be timezone-aware ISO-8601")
    return parsed


def _require_https_host(locator: str, allowed_hosts: tuple[str, ...]) -> None:
    parsed = urlparse(locator)
    if parsed.scheme != "https":
        raise ValueError("official disclosure locator must use https")
    host = (parsed.hostname or "").lower()
    if not any(host == allowed or host.endswith(f".{allowed}") for allowed in allowed_hosts):
        raise ValueError(f"locator host is not an approved official host: {host!r}")


@dataclass(frozen=True)
class OfficialDisclosureRow:
    """Source-index observation before canonical normalization.

    `observed_at` is when our collection process actually saw this index row.
    `published_at` is optional because some official listing surfaces expose only
    a date. The adapter never fabricates an intra-day publication timestamp.

    When the raw source response has already been archived, `source_snapshot_id`
    should be the immutable RawEvidenceArchive snapshot id. Static/manual tests may
    omit it and use the deterministic observation fallback.
    """

    security_id: str
    announcement_id: str
    title: str
    category: str
    document_url: str
    observed_at: str
    published_at: str | None = None
    period_end: str | None = None
    revision_id: str = "rev-1"
    supersedes_revision_id: str | None = None
    is_current_revision: bool | None = True
    source_snapshot_id: str | None = None


class OfficialDisclosureTransport(Protocol):
    """Transport boundary for verified official listing/index retrieval.

    v0 intentionally does not ship an undocumented live HTTP endpoint. A future
    transport may use an officially documented endpoint, browser capture, file
    export, or another approved acquisition method and emit these rows.
    """

    def rows(self, *, as_of: str) -> Iterable[OfficialDisclosureRow]:
        ...


@dataclass
class StaticOfficialDisclosureTransport:
    """Deterministic transport for fixtures/manual verified captures."""

    items: tuple[OfficialDisclosureRow, ...]

    def rows(self, *, as_of: str) -> Iterable[OfficialDisclosureRow]:
        _parse_aware(as_of, "as_of")
        as_of_time = _parse_aware(as_of, "as_of")
        assert as_of_time is not None
        for row in self.items:
            observed = _parse_aware(row.observed_at, "observed_at")
            assert observed is not None
            if observed <= as_of_time:
                yield row


@dataclass
class OfficialDisclosureAdapter:
    adapter_id: str
    exchange: str
    source_name: str
    source_tier: str
    source_index_url: str
    allowed_hosts: tuple[str, ...]
    transport: OfficialDisclosureTransport
    visibility_basis: str = "FIRST_OBSERVED"
    permitted_use: str = "UNRESOLVED_LICENSE"
    strategy_visibility: tuple[str, ...] = ("long", "short_mid")

    def __post_init__(self) -> None:
        if self.visibility_basis not in VALID_VISIBILITY_BASIS:
            raise ValueError(f"invalid visibility_basis: {self.visibility_basis}")
        _require_https_host(self.source_index_url, self.allowed_hosts)

    def _resolve_times(self, row: OfficialDisclosureRow) -> tuple[str | None, str, str]:
        observed_at = _parse_aware(row.observed_at, "observed_at")
        published_at = _parse_aware(row.published_at, "published_at")
        assert observed_at is not None

        if published_at is not None and observed_at < published_at:
            raise ValueError("observed_at cannot precede published_at")

        if self.visibility_basis == "OFFICIAL_TIMESTAMP":
            if published_at is None:
                raise TimestampResolutionError(
                    "official timestamp required; date-only disclosure listing cannot be given an invented time"
                )
            available_at = published_at
        else:
            # Forward-safe default: if the official index does not expose exact
            # publication time, use the time our system first observed the row.
            # This may be conservative, but cannot leak information backward.
            available_at = observed_at

        return (
            None if published_at is None else published_at.isoformat(),
            available_at.isoformat(),
            observed_at.isoformat(),
        )

    def normalize(self, row: OfficialDisclosureRow) -> NormalizedRecordCandidate:
        _require_https_host(row.document_url, self.allowed_hosts)
        published_at, available_at, ingested_at = self._resolve_times(row)

        entity = Disclosure(
            security_id=row.security_id,
            disclosure_id=row.announcement_id,
            title=row.title,
            category=row.category,
            source_locator=row.document_url,
            period_end=row.period_end,
        )
        source_snapshot_id = row.source_snapshot_id or (
            f"{self.exchange}:{row.announcement_id}:observed:{ingested_at}"
        )
        return NormalizedRecordCandidate.from_entity(
            entity=entity,
            source=self.source_name,
            source_tier=self.source_tier,
            source_snapshot_id=source_snapshot_id,
            source_locator=row.document_url,
            revision_id=row.revision_id,
            published_at=published_at,
            available_at=available_at,
            ingested_at=ingested_at,
            strategy_visibility=self.strategy_visibility,
            permitted_use=self.permitted_use,
            exchange=self.exchange,
            supersedes_revision_id=row.supersedes_revision_id,
            is_current_revision=row.is_current_revision,
        )

    def collect(self, *, as_of: str) -> Iterable[NormalizedRecordCandidate]:
        _parse_aware(as_of, "as_of")
        for row in self.transport.rows(as_of=as_of):
            yield self.normalize(row)


def build_sse_disclosure_adapter(
    transport: OfficialDisclosureTransport,
    *,
    visibility_basis: str = "FIRST_OBSERVED",
    permitted_use: str = "UNRESOLVED_LICENSE",
) -> OfficialDisclosureAdapter:
    return OfficialDisclosureAdapter(
        adapter_id="SSE_OFFICIAL_DISCLOSURE_V0",
        exchange="SSE",
        source_name="Shanghai Stock Exchange",
        source_tier="TIER1",
        source_index_url="https://www.sse.com.cn/disclosure/listedinfo/announcement/",
        allowed_hosts=("sse.com.cn",),
        transport=transport,
        visibility_basis=visibility_basis,
        permitted_use=permitted_use,
    )


def build_szse_disclosure_adapter(
    transport: OfficialDisclosureTransport,
    *,
    visibility_basis: str = "FIRST_OBSERVED",
    permitted_use: str = "UNRESOLVED_LICENSE",
) -> OfficialDisclosureAdapter:
    return OfficialDisclosureAdapter(
        adapter_id="SZSE_OFFICIAL_DISCLOSURE_V0",
        exchange="SZSE",
        source_name="Shenzhen Stock Exchange",
        source_tier="TIER1",
        source_index_url="https://www.szse.cn/disclosure/notice/company/index.html",
        allowed_hosts=("szse.cn",),
        transport=transport,
        visibility_basis=visibility_basis,
        permitted_use=permitted_use,
    )
