from __future__ import annotations

import hashlib
import json
import math
from dataclasses import asdict, dataclass
from datetime import date
from typing import Any, ClassVar, Iterable

from src.core.pit_store import StoredPITRecord
from src.data.coverage import CoverageResolver
from src.data.entities import EntityMixin


BENCHMARK_SERIES_SCHEMA_VERSION = "1.0"
BENCHMARK_COVERAGE_FAMILY = "BENCHMARK_DAILY_BAR"
BENCHMARK_COVERAGE_METHODS = {
    "OFFICIAL_INDEX_SERIES_RECONCILED",
    "LICENSED_VENDOR_RECONCILED",
    "OFFICIAL_VENDOR_RECONCILED",
}
VALID_BENCHMARK_TYPES = {"BROAD_INDEX", "SECTOR_INDEX", "PEER_BASKET", "CUSTOM"}


def _require_text(value: str, field_name: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{field_name} is required")
    return value.strip()


def _validate_date(value: str, field_name: str) -> date:
    try:
        return date.fromisoformat(value)
    except Exception as exc:
        raise ValueError(f"{field_name} must be YYYY-MM-DD") from exc


def _finite(value: float | int | None, field_name: str, *, allow_none: bool = False) -> None:
    if value is None:
        if allow_none:
            return
        raise ValueError(f"{field_name} is required")
    if not isinstance(value, (int, float)) or isinstance(value, bool) or not math.isfinite(float(value)):
        raise ValueError(f"{field_name} must be finite")


def _canonical_json(value: Any) -> str:
    return json.dumps(
        value,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
        allow_nan=False,
    )


def _sha256(value: Any) -> str:
    return hashlib.sha256(_canonical_json(value).encode("utf-8")).hexdigest()


def _record_ref(record: StoredPITRecord) -> str:
    return f"{record.metadata.record_id}@{record.metadata.revision_id}"


@dataclass(frozen=True)
class BenchmarkMaster(EntityMixin):
    entity_type: ClassVar[str] = "BENCHMARK_MASTER"

    benchmark_id: str
    benchmark_type: str
    name: str
    currency: str = "CNY"
    taxonomy: str | None = None
    methodology_version: str | None = None

    def validate(self) -> None:
        _require_text(self.benchmark_id, "benchmark_id")
        if self.benchmark_type not in VALID_BENCHMARK_TYPES:
            raise ValueError(f"invalid benchmark_type: {self.benchmark_type}")
        _require_text(self.name, "name")
        _require_text(self.currency, "currency")
        if self.taxonomy is not None:
            _require_text(self.taxonomy, "taxonomy")
        if self.methodology_version is not None:
            _require_text(self.methodology_version, "methodology_version")

    def record_id(self) -> str:
        self.validate()
        return f"BENCHMARK_MASTER:{self.benchmark_id}"


@dataclass(frozen=True)
class BenchmarkDailyBar(EntityMixin):
    entity_type: ClassVar[str] = "BENCHMARK_DAILY_BAR"

    benchmark_id: str
    trade_date: str
    open: float
    high: float
    low: float
    close: float
    prev_close: float | None
    level_basis: str = "INDEX_LEVEL"

    def validate(self) -> None:
        _require_text(self.benchmark_id, "benchmark_id")
        _validate_date(self.trade_date, "trade_date")
        for name in ("open", "high", "low", "close"):
            value = getattr(self, name)
            _finite(value, name)
            if value <= 0:
                raise ValueError(f"{name} must be > 0")
        _finite(self.prev_close, "prev_close", allow_none=True)
        if self.prev_close is not None and self.prev_close <= 0:
            raise ValueError("prev_close must be > 0 when present")
        if self.high < max(self.open, self.close, self.low):
            raise ValueError("high must be >= open/close/low")
        if self.low > min(self.open, self.close, self.high):
            raise ValueError("low must be <= open/close/high")
        if self.level_basis != "INDEX_LEVEL":
            raise ValueError("canonical benchmark bars must use INDEX_LEVEL")

    def record_id(self) -> str:
        self.validate()
        return f"BENCHMARK_DAILY_BAR:{self.benchmark_id}:{self.trade_date}"


@dataclass(frozen=True)
class BenchmarkPoint:
    trade_date: str
    close: float
    return_1d: float | None
    source_bar_ref: str

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class BenchmarkSeries:
    benchmark_series_id: str
    schema_version: str
    benchmark_id: str
    start_date: str
    end_date: str
    coverage_ref: str
    points: tuple[BenchmarkPoint, ...]

    def identity_payload(self) -> dict[str, Any]:
        return {
            "schema_version": self.schema_version,
            "benchmark_id": self.benchmark_id,
            "start_date": self.start_date,
            "end_date": self.end_date,
            "coverage_ref": self.coverage_ref,
            "points": [point.to_dict() for point in self.points],
        }

    def validate(self) -> None:
        if self.schema_version != BENCHMARK_SERIES_SCHEMA_VERSION:
            raise ValueError("unsupported benchmark series schema")
        _require_text(self.benchmark_id, "benchmark_id")
        if not self.points:
            raise ValueError("benchmark series requires points")
        if self.start_date != self.points[0].trade_date:
            raise ValueError("start_date must equal first point date")
        if self.end_date != self.points[-1].trade_date:
            raise ValueError("end_date must equal last point date")
        _require_text(self.coverage_ref, "coverage_ref")
        if _sha256(self.identity_payload()) != self.benchmark_series_id:
            raise ValueError("benchmark_series_id does not match content")

    def to_dict(self) -> dict[str, Any]:
        return {**self.identity_payload(), "benchmark_series_id": self.benchmark_series_id}


class BenchmarkSeriesBuilder:
    """Build a deterministic PIT-visible benchmark close/return series.

    Benchmark selection is intentionally out of scope. The caller must already
    provide a benchmark_id chosen under a frozen research contract.
    """

    def __init__(self, resolver: CoverageResolver | None = None):
        self.resolver = resolver or CoverageResolver()

    def build(
        self,
        records: Iterable[StoredPITRecord],
        *,
        benchmark_id: str,
    ) -> BenchmarkSeries:
        benchmark_id = _require_text(benchmark_id, "benchmark_id")
        rows = self._bars(records, benchmark_id=benchmark_id)
        if len(rows) < 2:
            raise ValueError("at least two BENCHMARK_DAILY_BAR records are required")
        start_date = rows[0][1].trade_date
        end_date = rows[-1][1].trade_date

        resolution = self.resolver.resolve(
            records,
            dataset_family=BENCHMARK_COVERAGE_FAMILY,
            dataset_key=benchmark_id,
            requested_start=start_date,
            requested_end=end_date,
            accepted_methods=set(BENCHMARK_COVERAGE_METHODS),
        )
        if not resolution.confirmed:
            raise ValueError(f"benchmark coverage not confirmed: {resolution.reason}")
        assert resolution.assertion_ref is not None

        points: list[BenchmarkPoint] = []
        previous_close: float | None = None
        for record, bar in rows:
            return_1d = None if previous_close is None else (bar.close / previous_close) - 1.0
            if return_1d is not None and not math.isfinite(return_1d):
                raise ValueError(f"invalid benchmark return on {bar.trade_date}")
            points.append(
                BenchmarkPoint(
                    trade_date=bar.trade_date,
                    close=bar.close,
                    return_1d=return_1d,
                    source_bar_ref=_record_ref(record),
                )
            )
            previous_close = bar.close

        provisional = BenchmarkSeries(
            benchmark_series_id="pending",
            schema_version=BENCHMARK_SERIES_SCHEMA_VERSION,
            benchmark_id=benchmark_id,
            start_date=start_date,
            end_date=end_date,
            coverage_ref=resolution.assertion_ref,
            points=tuple(points),
        )
        series = BenchmarkSeries(
            benchmark_series_id=_sha256(provisional.identity_payload()),
            schema_version=provisional.schema_version,
            benchmark_id=provisional.benchmark_id,
            start_date=provisional.start_date,
            end_date=provisional.end_date,
            coverage_ref=provisional.coverage_ref,
            points=provisional.points,
        )
        series.validate()
        return series

    @staticmethod
    def _bars(
        records: Iterable[StoredPITRecord],
        *,
        benchmark_id: str,
    ) -> list[tuple[StoredPITRecord, BenchmarkDailyBar]]:
        rows: list[tuple[StoredPITRecord, BenchmarkDailyBar]] = []
        seen: set[str] = set()
        for record in records:
            if record.metadata.entity_type != "BENCHMARK_DAILY_BAR":
                continue
            bar = BenchmarkDailyBar(**record.payload)
            bar.validate()
            if bar.benchmark_id != benchmark_id:
                continue
            if bar.trade_date in seen:
                raise ValueError(f"duplicate benchmark trade_date: {bar.trade_date}")
            seen.add(bar.trade_date)
            rows.append((record, bar))
        return sorted(rows, key=lambda item: item[1].trade_date)
