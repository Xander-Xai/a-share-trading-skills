from __future__ import annotations

import re
from dataclasses import dataclass
from datetime import date, datetime
from typing import Iterable

from src.core.pit_store import StoredPITRecord
from src.data.entities import EntityMixin


VALID_SCOPE_TYPES = {"SECURITY", "EXCHANGE", "GLOBAL"}
VALID_COMPLETENESS_STATUS = {"CONFIRMED_COMPLETE", "PARTIAL", "UNRESOLVED"}
_SECURITY_ID_RE = re.compile(r"^\d{6}$")


def _require_text(value: str, field_name: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{field_name} is required")
    return value.strip()


def _validate_date(value: str, field_name: str) -> date:
    try:
        return date.fromisoformat(value)
    except Exception as exc:
        raise ValueError(f"{field_name} must be YYYY-MM-DD") from exc


def _validate_nonnegative_int(value: int | None, field_name: str) -> None:
    if value is None:
        return
    if not isinstance(value, int) or isinstance(value, bool) or value < 0:
        raise ValueError(f"{field_name} must be a non-negative integer")


def _parse_aware(value: str) -> datetime:
    parsed = datetime.fromisoformat(value)
    if parsed.tzinfo is None or parsed.utcoffset() is None:
        raise ValueError("coverage record timestamp must be timezone-aware")
    return parsed


@dataclass(frozen=True)
class DatasetCoverage(EntityMixin):
    """Positive evidence that a dataset family is complete for an explicit scope.

    `no row observed` is not evidence that no event occurred. A source adapter or
    data-quality reconciliation job must emit a coverage assertion only after the
    completeness condition for that dataset family has actually been checked.
    """

    entity_type = "DATASET_COVERAGE"

    coverage_id: str
    dataset_family: str
    scope_type: str
    start_date: str
    end_date: str
    completeness_status: str
    verification_method: str
    security_id: str | None = None
    exchange: str | None = None
    expected_count: int | None = None
    observed_count: int | None = None
    note: str | None = None

    def validate(self) -> None:
        _require_text(self.coverage_id, "coverage_id")
        _require_text(self.dataset_family, "dataset_family")
        _require_text(self.verification_method, "verification_method")
        start = _validate_date(self.start_date, "start_date")
        end = _validate_date(self.end_date, "end_date")
        if end < start:
            raise ValueError("end_date cannot precede start_date")

        if self.scope_type not in VALID_SCOPE_TYPES:
            raise ValueError(f"invalid scope_type: {self.scope_type}")
        if self.completeness_status not in VALID_COMPLETENESS_STATUS:
            raise ValueError(
                f"invalid completeness_status: {self.completeness_status}"
            )

        if self.scope_type == "SECURITY":
            if self.security_id is None or not _SECURITY_ID_RE.match(self.security_id):
                raise ValueError("SECURITY coverage requires six-digit security_id")
        elif self.security_id is not None and not _SECURITY_ID_RE.match(self.security_id):
            raise ValueError("security_id must be six digits when present")

        if self.scope_type == "EXCHANGE" and not self.exchange:
            raise ValueError("EXCHANGE coverage requires exchange")
        if self.exchange is not None:
            _require_text(self.exchange, "exchange")

        _validate_nonnegative_int(self.expected_count, "expected_count")
        _validate_nonnegative_int(self.observed_count, "observed_count")
        if (
            self.completeness_status == "CONFIRMED_COMPLETE"
            and self.expected_count is not None
            and self.observed_count is not None
            and self.expected_count != self.observed_count
        ):
            raise ValueError(
                "CONFIRMED_COMPLETE requires observed_count == expected_count when both are supplied"
            )

        if self.note is not None:
            _require_text(self.note, "note")

    def record_id(self) -> str:
        self.validate()
        scope = self.security_id or self.exchange or "GLOBAL"
        return (
            f"DATASET_COVERAGE:{self.dataset_family}:{self.scope_type}:"
            f"{scope}:{self.coverage_id}:{self.start_date}:{self.end_date}"
        )


@dataclass(frozen=True)
class CoverageResolution:
    dataset_family: str
    requested_start: str
    requested_end: str
    confirmed: bool
    status: str
    reason: str
    assertion_record: StoredPITRecord | None = None
    verification_method: str | None = None
    scope_type: str | None = None

    @property
    def assertion_ref(self) -> str | None:
        if self.assertion_record is None:
            return None
        meta = self.assertion_record.metadata
        return f"{meta.record_id}@{meta.revision_id}"


class CoverageResolver:
    """Resolve the latest applicable coverage assertion from a PIT snapshot.

    The most specific applicable scope wins (security > exchange > global). Within
    the same scope the latest PIT-visible assertion wins. This means a newer
    security-level PARTIAL assertion intentionally overrides an older broader
    CONFIRMED_COMPLETE assertion and fails closed.
    """

    _SCOPE_PRIORITY = {"GLOBAL": 1, "EXCHANGE": 2, "SECURITY": 3}

    def resolve(
        self,
        records: Iterable[StoredPITRecord],
        *,
        dataset_family: str,
        requested_start: str,
        requested_end: str,
        security_id: str | None = None,
        exchange: str | None = None,
        accepted_methods: set[str] | None = None,
    ) -> CoverageResolution:
        family = _require_text(dataset_family, "dataset_family")
        start = _validate_date(requested_start, "requested_start")
        end = _validate_date(requested_end, "requested_end")
        if end < start:
            raise ValueError("requested_end cannot precede requested_start")

        candidates: list[tuple[int, datetime, datetime, str, StoredPITRecord, DatasetCoverage]] = []
        for record in records:
            if record.metadata.entity_type != "DATASET_COVERAGE":
                continue
            try:
                assertion = DatasetCoverage(**record.payload)
                assertion.validate()
            except Exception as exc:
                raise ValueError(
                    f"invalid DATASET_COVERAGE record {record.metadata.record_id}: {exc}"
                ) from exc

            if assertion.dataset_family != family:
                continue
            if date.fromisoformat(assertion.start_date) > start:
                continue
            if date.fromisoformat(assertion.end_date) < end:
                continue
            if assertion.scope_type == "SECURITY":
                if security_id is None or assertion.security_id != security_id:
                    continue
            elif assertion.scope_type == "EXCHANGE":
                if exchange is None or assertion.exchange != exchange:
                    continue

            candidates.append(
                (
                    self._SCOPE_PRIORITY[assertion.scope_type],
                    _parse_aware(record.metadata.available_at),
                    _parse_aware(record.metadata.ingested_at),
                    record.metadata.record_id,
                    record,
                    assertion,
                )
            )

        if not candidates:
            return CoverageResolution(
                dataset_family=family,
                requested_start=requested_start,
                requested_end=requested_end,
                confirmed=False,
                status="UNRESOLVED",
                reason="NO_APPLICABLE_COVERAGE_ASSERTION",
            )

        candidates.sort(key=lambda row: (row[0], row[1], row[2], row[3]))
        _, _, _, _, record, assertion = candidates[-1]

        if accepted_methods is not None and assertion.verification_method not in accepted_methods:
            return CoverageResolution(
                dataset_family=family,
                requested_start=requested_start,
                requested_end=requested_end,
                confirmed=False,
                status=assertion.completeness_status,
                reason="VERIFICATION_METHOD_NOT_ACCEPTED",
                assertion_record=record,
                verification_method=assertion.verification_method,
                scope_type=assertion.scope_type,
            )

        confirmed = assertion.completeness_status == "CONFIRMED_COMPLETE"
        return CoverageResolution(
            dataset_family=family,
            requested_start=requested_start,
            requested_end=requested_end,
            confirmed=confirmed,
            status=assertion.completeness_status,
            reason=("CONFIRMED" if confirmed else "ASSERTION_NOT_COMPLETE"),
            assertion_record=record,
            verification_method=assertion.verification_method,
            scope_type=assertion.scope_type,
        )
