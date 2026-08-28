from __future__ import annotations

import hashlib
import json
import math
from dataclasses import asdict, dataclass
from datetime import date
from typing import Any, Iterable

from src.core.pit_store import StoredPITRecord
from src.data.coverage import CoverageResolver
from src.data.entities import CorporateAction, DailyBar


ADJUSTMENT_SCHEMA_VERSION = "1.0"
ADJUSTMENT_BASIS = "BACKWARD_EXCHANGE_REFERENCE_V1"
DAILY_BAR_METHODS = {
    "TRADING_CALENDAR_RECONCILED",
    "EXCHANGE_CALENDAR_RECONCILED",
}
CORPORATE_ACTION_METHODS = {
    "OFFICIAL_SOURCE_ENUMERATION",
    "LICENSED_VENDOR_RECONCILED",
    "OFFICIAL_VENDOR_RECONCILED",
}


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


def _finite_positive(value: float, field_name: str) -> float:
    if not math.isfinite(value) or value <= 0:
        raise ValueError(f"{field_name} must be finite and > 0")
    return value


@dataclass(frozen=True)
class AdjustmentEvent:
    ex_date: str
    previous_trade_date: str
    previous_close: float
    reference_price: float
    event_factor: float
    reference_cash_per_share: float
    total_share_change_ratio: float
    rights_value_component: float
    action_refs: tuple[str, ...]

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class AdjustedPricePoint:
    trade_date: str
    adjustment_factor: float
    adjusted_open: float
    adjusted_high: float
    adjusted_low: float
    adjusted_close: float
    source_bar_ref: str

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class AdjustmentSeries:
    adjustment_series_id: str
    schema_version: str
    basis: str
    security_id: str
    exchange: str
    start_date: str
    end_date: str
    anchor_date: str
    daily_bar_coverage_ref: str
    corporate_action_coverage_ref: str
    events: tuple[AdjustmentEvent, ...]
    points: tuple[AdjustedPricePoint, ...]

    def identity_payload(self) -> dict[str, Any]:
        return {
            "schema_version": self.schema_version,
            "basis": self.basis,
            "security_id": self.security_id,
            "exchange": self.exchange,
            "start_date": self.start_date,
            "end_date": self.end_date,
            "anchor_date": self.anchor_date,
            "daily_bar_coverage_ref": self.daily_bar_coverage_ref,
            "corporate_action_coverage_ref": self.corporate_action_coverage_ref,
            "events": [event.to_dict() for event in self.events],
            "points": [point.to_dict() for point in self.points],
        }

    def validate(self) -> None:
        if self.schema_version != ADJUSTMENT_SCHEMA_VERSION:
            raise ValueError("unsupported adjustment series schema")
        if self.basis != ADJUSTMENT_BASIS:
            raise ValueError("unsupported adjustment basis")
        if len(self.security_id) != 6 or not self.security_id.isdigit():
            raise ValueError("security_id must be six digits")
        if not self.exchange:
            raise ValueError("exchange is required")
        if not self.points:
            raise ValueError("adjustment series requires price points")
        if self.start_date != self.points[0].trade_date:
            raise ValueError("start_date must equal first point date")
        if self.end_date != self.points[-1].trade_date:
            raise ValueError("end_date must equal last point date")
        if self.anchor_date != self.end_date:
            raise ValueError("v1 backward-adjusted series must anchor on end_date")
        if abs(self.points[-1].adjustment_factor - 1.0) > 1e-12:
            raise ValueError("anchor-date adjustment factor must equal 1")
        if _sha256(self.identity_payload()) != self.adjustment_series_id:
            raise ValueError("adjustment_series_id does not match content")

    def to_dict(self) -> dict[str, Any]:
        return {**self.identity_payload(), "adjustment_series_id": self.adjustment_series_id}


class AdjustmentFactorBuilder:
    """Build a backward-adjusted price series from PIT-visible facts.

    The engine implements the common SSE/SZSE ex-right/ex-dividend reference-price
    algebra:

        reference = ((previous_close - cash) + rights_price * rights_ratio)
                    / (1 + total_share_change_ratio)

    where `total_share_change_ratio` is bonus + transfer + rights unless an explicit
    issuer/exchange effective denominator override is supplied.

    The result is an exchange-reference adjusted research series. It is not a tax-
    aware investor total-return index and it is not an execution price series.
    """

    def __init__(self, resolver: CoverageResolver | None = None):
        self.resolver = resolver or CoverageResolver()

    def build(
        self,
        records: Iterable[StoredPITRecord],
        *,
        security_id: str,
        exchange: str | None = None,
    ) -> AdjustmentSeries:
        materialized = tuple(records)
        bars_with_records = self._bars(materialized, security_id=security_id)
        if len(bars_with_records) < 2:
            raise ValueError("at least two DAILY_BAR records are required")

        exchanges = {
            record.metadata.exchange
            for record, _ in bars_with_records
            if record.metadata.exchange
        }
        if exchange is not None:
            exchanges.add(exchange)
        if len(exchanges) != 1:
            raise ValueError(f"exactly one exchange is required, got {sorted(exchanges)}")
        resolved_exchange = next(iter(exchanges))

        start_date = bars_with_records[0][1].trade_date
        end_date = bars_with_records[-1][1].trade_date
        daily_coverage = self.resolver.resolve(
            materialized,
            dataset_family="DAILY_BAR",
            requested_start=start_date,
            requested_end=end_date,
            security_id=security_id,
            exchange=resolved_exchange,
            accepted_methods=set(DAILY_BAR_METHODS),
        )
        action_coverage = self.resolver.resolve(
            materialized,
            dataset_family="CORPORATE_ACTION",
            requested_start=start_date,
            requested_end=end_date,
            security_id=security_id,
            exchange=resolved_exchange,
            accepted_methods=set(CORPORATE_ACTION_METHODS),
        )
        if not daily_coverage.confirmed:
            raise ValueError(f"DAILY_BAR coverage not confirmed: {daily_coverage.reason}")
        if not action_coverage.confirmed:
            raise ValueError(
                f"CORPORATE_ACTION coverage not confirmed: {action_coverage.reason}"
            )
        assert daily_coverage.assertion_ref is not None
        assert action_coverage.assertion_ref is not None

        actions = self._actions(
            materialized,
            security_id=security_id,
            start_date=start_date,
            end_date=end_date,
        )
        events = self._events(bars_with_records, actions)

        points: list[AdjustedPricePoint] = []
        for bar_record, bar in bars_with_records:
            factor = 1.0
            for event in events:
                if event.ex_date > bar.trade_date:
                    factor *= event.event_factor
            factor = float(factor)
            for name, value in (
                ("adjustment_factor", factor),
                ("adjusted_open", bar.open * factor),
                ("adjusted_high", bar.high * factor),
                ("adjusted_low", bar.low * factor),
                ("adjusted_close", bar.close * factor),
            ):
                if not math.isfinite(value) or value <= 0:
                    raise ValueError(f"invalid {name} for {bar.trade_date}")
            points.append(
                AdjustedPricePoint(
                    trade_date=bar.trade_date,
                    adjustment_factor=factor,
                    adjusted_open=bar.open * factor,
                    adjusted_high=bar.high * factor,
                    adjusted_low=bar.low * factor,
                    adjusted_close=bar.close * factor,
                    source_bar_ref=_record_ref(bar_record),
                )
            )

        provisional = AdjustmentSeries(
            adjustment_series_id="pending",
            schema_version=ADJUSTMENT_SCHEMA_VERSION,
            basis=ADJUSTMENT_BASIS,
            security_id=security_id,
            exchange=resolved_exchange,
            start_date=start_date,
            end_date=end_date,
            anchor_date=end_date,
            daily_bar_coverage_ref=daily_coverage.assertion_ref,
            corporate_action_coverage_ref=action_coverage.assertion_ref,
            events=tuple(events),
            points=tuple(points),
        )
        series = AdjustmentSeries(
            adjustment_series_id=_sha256(provisional.identity_payload()),
            schema_version=provisional.schema_version,
            basis=provisional.basis,
            security_id=provisional.security_id,
            exchange=provisional.exchange,
            start_date=provisional.start_date,
            end_date=provisional.end_date,
            anchor_date=provisional.anchor_date,
            daily_bar_coverage_ref=provisional.daily_bar_coverage_ref,
            corporate_action_coverage_ref=provisional.corporate_action_coverage_ref,
            events=provisional.events,
            points=provisional.points,
        )
        series.validate()
        return series

    @staticmethod
    def _bars(
        records: Iterable[StoredPITRecord],
        *,
        security_id: str,
    ) -> list[tuple[StoredPITRecord, DailyBar]]:
        rows: list[tuple[StoredPITRecord, DailyBar]] = []
        seen: set[str] = set()
        for record in records:
            if record.metadata.entity_type != "DAILY_BAR":
                continue
            if record.metadata.security_id != security_id:
                continue
            bar = DailyBar(**record.payload)
            bar.validate()
            if bar.security_id != security_id:
                raise ValueError("DAILY_BAR payload security_id disagrees with metadata")
            if bar.trade_date in seen:
                raise ValueError(f"duplicate DAILY_BAR trade_date: {bar.trade_date}")
            seen.add(bar.trade_date)
            rows.append((record, bar))
        return sorted(rows, key=lambda item: item[1].trade_date)

    @staticmethod
    def _actions(
        records: Iterable[StoredPITRecord],
        *,
        security_id: str,
        start_date: str,
        end_date: str,
    ) -> list[tuple[StoredPITRecord, CorporateAction]]:
        start = date.fromisoformat(start_date)
        end = date.fromisoformat(end_date)
        rows: list[tuple[StoredPITRecord, CorporateAction]] = []
        seen: set[str] = set()
        for record in records:
            if record.metadata.entity_type != "CORPORATE_ACTION":
                continue
            if record.metadata.security_id != security_id:
                continue
            action = CorporateAction(**record.payload)
            action.validate()
            if action.ex_date is None:
                continue
            ex_day = date.fromisoformat(action.ex_date)
            if ex_day < start or ex_day > end:
                continue
            if action.action_id in seen:
                raise ValueError(f"duplicate corporate action id: {action.action_id}")
            seen.add(action.action_id)
            rows.append((record, action))
        return sorted(rows, key=lambda item: (item[1].ex_date or "", item[1].action_id))

    def _events(
        self,
        bars: list[tuple[StoredPITRecord, DailyBar]],
        actions: list[tuple[StoredPITRecord, CorporateAction]],
    ) -> list[AdjustmentEvent]:
        bar_index = {bar.trade_date: index for index, (_, bar) in enumerate(bars)}
        grouped: dict[str, list[tuple[StoredPITRecord, CorporateAction]]] = {}
        for row in actions:
            assert row[1].ex_date is not None
            grouped.setdefault(row[1].ex_date, []).append(row)

        events: list[AdjustmentEvent] = []
        for ex_date in sorted(grouped):
            rows = grouped[ex_date]
            if ex_date not in bar_index:
                raise ValueError(f"corporate-action ex_date has no DAILY_BAR: {ex_date}")
            index = bar_index[ex_date]
            if index == 0:
                raise ValueError(f"no previous DAILY_BAR available before ex_date {ex_date}")
            previous_bar = bars[index - 1][1]
            previous_close = _finite_positive(previous_bar.close, "previous_close")

            if any(action.ratio is not None for _, action in rows):
                raise ValueError(
                    f"legacy ambiguous ratio cannot drive adjustment factor on {ex_date}"
                )

            overrides = [
                action.reference_total_share_change_ratio
                for _, action in rows
                if action.reference_total_share_change_ratio is not None
            ]
            if overrides and len(rows) != 1:
                raise ValueError(
                    "reference_total_share_change_ratio override requires one consolidated action row per ex_date"
                )

            cash = sum(
                (
                    action.reference_cash_per_share
                    if action.reference_cash_per_share is not None
                    else (action.cash_per_share or 0.0)
                )
                for _, action in rows
            )
            bonus = sum(action.bonus_ratio or 0.0 for _, action in rows)
            transfer = sum(action.transfer_ratio or 0.0 for _, action in rows)
            rights = sum(action.rights_ratio or 0.0 for _, action in rows)
            rights_value = sum(
                (action.rights_ratio or 0.0) * (action.rights_price or 0.0)
                for _, action in rows
            )
            total_change = overrides[0] if overrides else bonus + transfer + rights

            numerator = (previous_close - cash) + rights_value
            denominator = 1.0 + total_change
            if numerator <= 0 or denominator <= 0:
                raise ValueError(f"non-positive ex-right reference terms on {ex_date}")
            reference_price = numerator / denominator
            _finite_positive(reference_price, "reference_price")
            event_factor = reference_price / previous_close
            _finite_positive(event_factor, "event_factor")

            events.append(
                AdjustmentEvent(
                    ex_date=ex_date,
                    previous_trade_date=previous_bar.trade_date,
                    previous_close=previous_close,
                    reference_price=reference_price,
                    event_factor=event_factor,
                    reference_cash_per_share=cash,
                    total_share_change_ratio=total_change,
                    rights_value_component=rights_value,
                    action_refs=tuple(sorted(_record_ref(record) for record, _ in rows)),
                )
            )
        return events
