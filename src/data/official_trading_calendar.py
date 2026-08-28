from __future__ import annotations

import calendar
import json
from dataclasses import dataclass
from datetime import date, datetime, timedelta
from pathlib import Path
from typing import Any, Iterable, Mapping
from urllib.parse import urlparse

from src.data.adapters import NormalizedRecordCandidate
from src.data.coverage import DatasetCoverage
from src.data.trading_calendar import TradingSession


CONFIG_SCHEMA_VERSION = "1.0"
VERIFICATION_METHOD = "EXCHANGE_CALENDAR_ENUMERATION"
VALID_EXCHANGES = {"SSE", "SZSE"}
OFFICIAL_HOSTS = {
    "SSE": ("sse.com.cn",),
    "SZSE": ("szse.cn",),
}


def _require_text(value: str, field_name: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{field_name} is required")
    return value.strip()


def _parse_date(value: str, field_name: str) -> date:
    try:
        return date.fromisoformat(value)
    except Exception as exc:
        raise ValueError(f"{field_name} must be YYYY-MM-DD") from exc


def _parse_aware(value: str, field_name: str) -> datetime:
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
        raise ValueError("official calendar source_url must use https")
    host = (parsed.hostname or "").lower()
    allowed = OFFICIAL_HOSTS.get(exchange, ())
    if not allowed or not any(host == item or host.endswith(f".{item}") for item in allowed):
        raise ValueError(
            f"source_url host {host!r} is not an approved official host for {exchange}"
        )
    return url


@dataclass(frozen=True)
class ClosureRange:
    start_date: str
    end_date: str
    label: str

    def validate(self, *, year: int) -> None:
        start = _parse_date(self.start_date, "closure.start_date")
        end = _parse_date(self.end_date, "closure.end_date")
        if end < start:
            raise ValueError("closure end_date cannot precede start_date")
        if start.year != year or end.year != year:
            raise ValueError("closure range must stay inside plan year")
        _require_text(self.label, "closure.label")

    def dates(self) -> Iterable[date]:
        start = _parse_date(self.start_date, "closure.start_date")
        end = _parse_date(self.end_date, "closure.end_date")
        cursor = start
        while cursor <= end:
            yield cursor
            cursor += timedelta(days=1)


@dataclass(frozen=True)
class OfficialAnnualTradingCalendarPlan:
    """Curated machine-readable plan derived from an official exchange notice.

    This adapter deliberately separates *official source provenance* from a live
    undocumented scraping endpoint. A checked-in plan can be replayed and audited;
    a future live transport may replace the curated input while preserving the same
    canonical output contract.

    Date-only source publication is handled with an explicit conservative
    `available_at` supplied by the plan. The implementation never invents an exact
    intra-day publication timestamp.
    """

    exchange: str
    year: int
    source_name: str
    source_url: str
    source_snapshot_id: str
    publication_date: str
    available_at: str
    ingested_at: str
    session_rule_version: str
    revision_id: str
    closures: tuple[ClosureRange, ...]
    permitted_use: str = "UNRESOLVED_LICENSE"
    source_tier: str = "TIER1"
    strategy_visibility: tuple[str, ...] = ("long", "short_mid")

    def validate(self) -> None:
        if self.exchange not in VALID_EXCHANGES:
            raise ValueError(f"unsupported exchange: {self.exchange}")
        if not isinstance(self.year, int) or isinstance(self.year, bool):
            raise ValueError("year must be an integer")
        if self.year < 2000 or self.year > 2100:
            raise ValueError("year outside supported range")
        _require_text(self.source_name, "source_name")
        _validate_official_url(self.exchange, self.source_url)
        _require_text(self.source_snapshot_id, "source_snapshot_id")
        published_day = _parse_date(self.publication_date, "publication_date")
        available = _parse_aware(self.available_at, "available_at")
        ingested = _parse_aware(self.ingested_at, "ingested_at")
        if ingested < available:
            raise ValueError("ingested_at cannot precede available_at")
        # A date-only official notice may be conservatively usable after the
        # publication date, but never before it.
        if available.date() <= published_day:
            raise ValueError(
                "date-only calendar notice requires conservative available_at after publication_date"
            )
        _require_text(self.session_rule_version, "session_rule_version")
        _require_text(self.revision_id, "revision_id")
        if self.source_tier != "TIER1":
            raise ValueError("official exchange calendar must remain TIER1")
        if set(self.strategy_visibility) != {"long", "short_mid"}:
            raise ValueError("official trading calendar must be visible to both stock sleeves")
        for closure in self.closures:
            closure.validate(year=self.year)

        closed_dates: set[date] = set()
        for closure in self.closures:
            for item in closure.dates():
                if item in closed_dates:
                    raise ValueError(f"overlapping closure date: {item.isoformat()}")
                closed_dates.add(item)

    @property
    def start_date(self) -> date:
        return date(self.year, 1, 1)

    @property
    def end_date(self) -> date:
        return date(self.year, 12, 31)

    def _closed_dates(self) -> set[date]:
        result: set[date] = set()
        for closure in self.closures:
            result.update(closure.dates())
        return result

    def sessions(self) -> tuple[TradingSession, ...]:
        self.validate()
        closed = self._closed_dates()
        result: list[TradingSession] = []
        cursor = self.start_date
        while cursor <= self.end_date:
            # SSE/SZSE trading rules define trading days as Monday-Friday,
            # excluding statutory holidays and exchange-announced closure days.
            is_open = cursor.weekday() < 5 and cursor not in closed
            result.append(
                TradingSession(
                    exchange=self.exchange,
                    trade_date=cursor.isoformat(),
                    is_open=is_open,
                    session_rule_version=self.session_rule_version,
                )
            )
            cursor += timedelta(days=1)
        expected_days = 366 if calendar.isleap(self.year) else 365
        if len(result) != expected_days:
            raise AssertionError("calendar enumeration length mismatch")
        return tuple(result)

    def collect(self, *, as_of: str) -> Iterable[NormalizedRecordCandidate]:
        self.validate()
        replay_time = _parse_aware(as_of, "as_of")
        available = _parse_aware(self.available_at, "available_at")
        if replay_time < available:
            return

        for session in self.sessions():
            yield NormalizedRecordCandidate.from_entity(
                entity=session,
                source=self.source_name,
                source_tier=self.source_tier,
                source_snapshot_id=self.source_snapshot_id,
                source_locator=self.source_url,
                revision_id=self.revision_id,
                effective_at=f"{session.trade_date}T00:00:00+08:00",
                available_at=self.available_at,
                ingested_at=self.ingested_at,
                strategy_visibility=self.strategy_visibility,
                permitted_use=self.permitted_use,
                exchange=self.exchange,
                is_current_revision=True,
            )

        count = 366 if calendar.isleap(self.year) else 365
        coverage = DatasetCoverage(
            coverage_id=f"{self.exchange}-{self.year}-official-calendar-plan",
            dataset_family="TRADING_SESSION",
            scope_type="EXCHANGE",
            exchange=self.exchange,
            start_date=self.start_date.isoformat(),
            end_date=self.end_date.isoformat(),
            completeness_status="CONFIRMED_COMPLETE",
            verification_method=VERIFICATION_METHOD,
            expected_count=count,
            observed_count=count,
            note=(
                "annual exchange calendar enumerated from official weekday rule + "
                "official annual closure notice; emergency/ad-hoc closure overrides "
                "must be represented as later PIT revisions"
            ),
        )
        yield NormalizedRecordCandidate.from_entity(
            entity=coverage,
            source=self.source_name,
            source_tier=self.source_tier,
            source_snapshot_id=self.source_snapshot_id,
            source_locator=self.source_url,
            revision_id=self.revision_id,
            effective_at=f"{self.year}-01-01T00:00:00+08:00",
            available_at=self.available_at,
            ingested_at=self.ingested_at,
            strategy_visibility=self.strategy_visibility,
            permitted_use=self.permitted_use,
            exchange=self.exchange,
            is_current_revision=True,
        )


def _closure_from_mapping(row: Mapping[str, Any]) -> ClosureRange:
    return ClosureRange(
        start_date=str(row["start_date"]),
        end_date=str(row["end_date"]),
        label=str(row["label"]),
    )


def plan_from_mapping(row: Mapping[str, Any]) -> OfficialAnnualTradingCalendarPlan:
    plan = OfficialAnnualTradingCalendarPlan(
        exchange=str(row["exchange"]),
        year=int(row["year"]),
        source_name=str(row["source_name"]),
        source_url=str(row["source_url"]),
        source_snapshot_id=str(row["source_snapshot_id"]),
        publication_date=str(row["publication_date"]),
        available_at=str(row["available_at"]),
        ingested_at=str(row["ingested_at"]),
        session_rule_version=str(row["session_rule_version"]),
        revision_id=str(row["revision_id"]),
        closures=tuple(_closure_from_mapping(item) for item in row.get("closures", [])),
        permitted_use=str(row.get("permitted_use", "UNRESOLVED_LICENSE")),
        source_tier=str(row.get("source_tier", "TIER1")),
        strategy_visibility=tuple(row.get("strategy_visibility", ("long", "short_mid"))),
    )
    plan.validate()
    return plan


def load_official_calendar_plans(path: str | Path) -> tuple[OfficialAnnualTradingCalendarPlan, ...]:
    row = json.loads(Path(path).read_text(encoding="utf-8"))
    if row.get("schema_version") != CONFIG_SCHEMA_VERSION:
        raise ValueError("unsupported official calendar config schema")
    plans = tuple(plan_from_mapping(item) for item in row.get("plans", []))
    if not plans:
        raise ValueError("official calendar config contains no plans")
    identities = {(plan.exchange, plan.year) for plan in plans}
    if len(identities) != len(plans):
        raise ValueError("duplicate exchange/year official calendar plan")
    return plans
