from __future__ import annotations

import hashlib
import json
import math
from dataclasses import asdict, dataclass
from datetime import datetime, time
from typing import Any, Iterable
from zoneinfo import ZoneInfo

from src.core.strategy_boundary import (
    SHORT_MID_SLEEVE,
    SHORT_MID_STRATEGY_ID,
    require_strategy_context,
)
from src.features.relative_performance import RelativePerformanceSeries


EVENT_REACTION_SCHEMA_VERSION = "1.0"
MEASUREMENT_BASIS = "DAILY_CLOSE_TO_CLOSE_FIRST_FULL_SESSION_V1"
SHANGHAI = ZoneInfo("Asia/Shanghai")
REGULAR_OPEN = time(9, 30)
VALID_EVENT_FAMILIES = {
    "EARNINGS",
    "EARNINGS_PREANNOUNCEMENT",
    "ORDER_CONTRACT",
    "COMMODITY_PRODUCT_PRICE",
    "POLICY",
    "CAPITAL_STRUCTURE",
    "OTHER",
}


def _require_text(value: str, field_name: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{field_name} is required")
    return value.strip()


def _parse_aware(value: str, field_name: str) -> datetime:
    try:
        parsed = datetime.fromisoformat(value)
    except Exception as exc:
        raise ValueError(f"{field_name} must be ISO-8601") from exc
    if parsed.tzinfo is None or parsed.utcoffset() is None:
        raise ValueError(f"{field_name} must be timezone-aware")
    return parsed


def _validate_windows(values: Iterable[int], field_name: str) -> tuple[int, ...]:
    windows = tuple(values)
    if any(not isinstance(value, int) or isinstance(value, bool) or value <= 0 for value in windows):
        raise ValueError(f"{field_name} must contain positive integers")
    if len(set(windows)) != len(windows):
        raise ValueError(f"{field_name} must be unique")
    return tuple(sorted(windows))


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


@dataclass(frozen=True)
class EventWindowMetric:
    window_kind: str
    sessions: int
    start_date: str
    end_date: str
    stock_return: float
    benchmark_return: float
    excess_return: float
    cumulative_abnormal_return: float

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class EventReactionMeasurement:
    event_measurement_id: str
    schema_version: str
    measurement_basis: str
    strategy_id: str
    sleeve: str
    event_id: str
    event_family: str
    security_id: str
    information_timestamp: str
    first_tradable_timestamp: str
    full_session_anchor_date: str
    partial_session_reaction_omitted: bool
    reaction_window_contract_id: str
    primary_reaction_window_sessions: int | None
    primary_window_status: str
    relative_performance_id: str
    benchmark_id: str
    benchmark_selection_contract_id: str
    prepricing_metrics: tuple[EventWindowMetric, ...]
    reaction_metrics: tuple[EventWindowMetric, ...]

    def identity_payload(self) -> dict[str, Any]:
        return {
            "schema_version": self.schema_version,
            "measurement_basis": self.measurement_basis,
            "strategy_id": self.strategy_id,
            "sleeve": self.sleeve,
            "event_id": self.event_id,
            "event_family": self.event_family,
            "security_id": self.security_id,
            "information_timestamp": self.information_timestamp,
            "first_tradable_timestamp": self.first_tradable_timestamp,
            "full_session_anchor_date": self.full_session_anchor_date,
            "partial_session_reaction_omitted": self.partial_session_reaction_omitted,
            "reaction_window_contract_id": self.reaction_window_contract_id,
            "primary_reaction_window_sessions": self.primary_reaction_window_sessions,
            "primary_window_status": self.primary_window_status,
            "relative_performance_id": self.relative_performance_id,
            "benchmark_id": self.benchmark_id,
            "benchmark_selection_contract_id": self.benchmark_selection_contract_id,
            "prepricing_metrics": [item.to_dict() for item in self.prepricing_metrics],
            "reaction_metrics": [item.to_dict() for item in self.reaction_metrics],
        }

    def validate(self) -> None:
        if self.schema_version != EVENT_REACTION_SCHEMA_VERSION:
            raise ValueError("unsupported event reaction schema")
        if self.measurement_basis != MEASUREMENT_BASIS:
            raise ValueError("unsupported measurement basis")
        require_strategy_context(
            strategy_id=self.strategy_id,
            sleeve=self.sleeve,
            expected_strategy_id=SHORT_MID_STRATEGY_ID,
            expected_sleeve=SHORT_MID_SLEEVE,
        )
        _require_text(self.event_id, "event_id")
        if self.event_family not in VALID_EVENT_FAMILIES:
            raise ValueError(f"invalid event_family: {self.event_family}")
        _require_text(self.security_id, "security_id")
        info = _parse_aware(self.information_timestamp, "information_timestamp")
        tradable = _parse_aware(self.first_tradable_timestamp, "first_tradable_timestamp")
        if tradable < info:
            raise ValueError("first_tradable_timestamp cannot precede information_timestamp")
        _require_text(self.full_session_anchor_date, "full_session_anchor_date")
        _require_text(self.reaction_window_contract_id, "reaction_window_contract_id")
        _require_text(self.relative_performance_id, "relative_performance_id")
        _require_text(self.benchmark_id, "benchmark_id")
        _require_text(
            self.benchmark_selection_contract_id,
            "benchmark_selection_contract_id",
        )
        if self.primary_reaction_window_sessions is None:
            if self.primary_window_status != "UNRESOLVED_RESEARCH":
                raise ValueError("missing primary window must remain UNRESOLVED_RESEARCH")
        else:
            if self.primary_reaction_window_sessions <= 0:
                raise ValueError("primary_reaction_window_sessions must be > 0")
            available = {item.sessions for item in self.reaction_metrics}
            if self.primary_reaction_window_sessions not in available:
                raise ValueError("primary reaction window must be among measured reaction windows")
            if self.primary_window_status != "FROZEN_BY_CONTRACT":
                raise ValueError("resolved primary window must be FROZEN_BY_CONTRACT")
        if _sha256(self.identity_payload()) != self.event_measurement_id:
            raise ValueError("event_measurement_id does not match content")

    def to_dict(self) -> dict[str, Any]:
        return {**self.identity_payload(), "event_measurement_id": self.event_measurement_id}


class EventReactionMeasurementBuilder:
    """Measure prepricing and post-event reaction without choosing windows ex post.

    v1 deliberately uses the first *full regular daily-bar session* that can occur
    after `first_tradable_timestamp`. If information becomes tradable after the
    regular session has started, any same-day partial/post-close reaction is marked
    as omitted and the next aligned full daily session is used as the anchor.

    This is conservative daily-bar research, not an intraday first-reaction engine.
    """

    def build(
        self,
        relative: RelativePerformanceSeries,
        *,
        event_id: str,
        event_family: str,
        information_timestamp: str,
        first_tradable_timestamp: str,
        reaction_window_contract_id: str,
        prepricing_windows: Iterable[int] = (),
        reaction_windows: Iterable[int] = (),
        primary_reaction_window_sessions: int | None = None,
        strategy_id: str = SHORT_MID_STRATEGY_ID,
        sleeve: str = SHORT_MID_SLEEVE,
    ) -> EventReactionMeasurement:
        relative.validate()
        require_strategy_context(
            strategy_id=strategy_id,
            sleeve=sleeve,
            expected_strategy_id=SHORT_MID_STRATEGY_ID,
            expected_sleeve=SHORT_MID_SLEEVE,
        )
        if relative.strategy_id != strategy_id or relative.sleeve != sleeve:
            raise ValueError("relative-performance strategy context mismatch")
        event_id = _require_text(event_id, "event_id")
        if event_family not in VALID_EVENT_FAMILIES:
            raise ValueError(f"invalid event_family: {event_family}")
        contract_id = _require_text(
            reaction_window_contract_id,
            "reaction_window_contract_id",
        )
        info = _parse_aware(information_timestamp, "information_timestamp")
        tradable = _parse_aware(first_tradable_timestamp, "first_tradable_timestamp")
        if tradable < info:
            raise ValueError("first_tradable_timestamp cannot precede information_timestamp")
        pre_windows = _validate_windows(prepricing_windows, "prepricing_windows")
        post_windows = _validate_windows(reaction_windows, "reaction_windows")
        if primary_reaction_window_sessions is not None:
            if primary_reaction_window_sessions not in post_windows:
                raise ValueError("primary reaction window must be predeclared in reaction_windows")

        anchor_index, omitted = self._resolve_full_session_anchor(relative, tradable)
        anchor_date = relative.points[anchor_index].trade_date

        pre_metrics = tuple(
            self._prepricing_metric(relative, anchor_index=anchor_index, sessions=value)
            for value in pre_windows
        )
        reaction_metrics = tuple(
            self._reaction_metric(relative, anchor_index=anchor_index, sessions=value)
            for value in post_windows
        )

        provisional = EventReactionMeasurement(
            event_measurement_id="pending",
            schema_version=EVENT_REACTION_SCHEMA_VERSION,
            measurement_basis=MEASUREMENT_BASIS,
            strategy_id=strategy_id,
            sleeve=sleeve,
            event_id=event_id,
            event_family=event_family,
            security_id=relative.security_id,
            information_timestamp=info.isoformat(),
            first_tradable_timestamp=tradable.isoformat(),
            full_session_anchor_date=anchor_date,
            partial_session_reaction_omitted=omitted,
            reaction_window_contract_id=contract_id,
            primary_reaction_window_sessions=primary_reaction_window_sessions,
            primary_window_status=(
                "UNRESOLVED_RESEARCH"
                if primary_reaction_window_sessions is None
                else "FROZEN_BY_CONTRACT"
            ),
            relative_performance_id=relative.relative_performance_id,
            benchmark_id=relative.benchmark_id,
            benchmark_selection_contract_id=relative.benchmark_selection_contract_id,
            prepricing_metrics=pre_metrics,
            reaction_metrics=reaction_metrics,
        )
        result = EventReactionMeasurement(
            event_measurement_id=_sha256(provisional.identity_payload()),
            schema_version=provisional.schema_version,
            measurement_basis=provisional.measurement_basis,
            strategy_id=provisional.strategy_id,
            sleeve=provisional.sleeve,
            event_id=provisional.event_id,
            event_family=provisional.event_family,
            security_id=provisional.security_id,
            information_timestamp=provisional.information_timestamp,
            first_tradable_timestamp=provisional.first_tradable_timestamp,
            full_session_anchor_date=provisional.full_session_anchor_date,
            partial_session_reaction_omitted=provisional.partial_session_reaction_omitted,
            reaction_window_contract_id=provisional.reaction_window_contract_id,
            primary_reaction_window_sessions=provisional.primary_reaction_window_sessions,
            primary_window_status=provisional.primary_window_status,
            relative_performance_id=provisional.relative_performance_id,
            benchmark_id=provisional.benchmark_id,
            benchmark_selection_contract_id=provisional.benchmark_selection_contract_id,
            prepricing_metrics=provisional.prepricing_metrics,
            reaction_metrics=provisional.reaction_metrics,
        )
        result.validate()
        return result

    @staticmethod
    def _resolve_full_session_anchor(
        relative: RelativePerformanceSeries,
        first_tradable: datetime,
    ) -> tuple[int, bool]:
        local = first_tradable.astimezone(SHANGHAI)
        date_strings = [point.trade_date for point in relative.points]
        local_date = local.date().isoformat()

        if local.time() <= REGULAR_OPEN and local_date in date_strings:
            anchor_index = date_strings.index(local_date)
            omitted = False
        else:
            later = [
                (index, value)
                for index, value in enumerate(date_strings)
                if value > local_date
            ]
            if not later:
                raise ValueError(
                    "no full daily-bar session available after first_tradable_timestamp"
                )
            anchor_index = later[0][0]
            omitted = True

        if anchor_index == 0:
            raise ValueError("reaction anchor requires a prior aligned close")
        return anchor_index, omitted

    @staticmethod
    def _prepricing_metric(
        relative: RelativePerformanceSeries,
        *,
        anchor_index: int,
        sessions: int,
    ) -> EventWindowMetric:
        end_index = anchor_index - 1
        start_index = end_index - sessions
        if start_index < 0:
            raise ValueError(
                "insufficient pre-event history for prepricing window: "
                f"sessions={sessions}"
            )
        return EventReactionMeasurementBuilder._metric(
            relative,
            window_kind="PREPRICING",
            sessions=sessions,
            start_index=start_index,
            end_index=end_index,
        )

    @staticmethod
    def _reaction_metric(
        relative: RelativePerformanceSeries,
        *,
        anchor_index: int,
        sessions: int,
    ) -> EventWindowMetric:
        start_index = anchor_index - 1
        end_index = anchor_index + sessions - 1
        if end_index >= len(relative.points):
            raise ValueError(
                "insufficient post-event history for reaction window: "
                f"sessions={sessions}"
            )
        return EventReactionMeasurementBuilder._metric(
            relative,
            window_kind="REACTION",
            sessions=sessions,
            start_index=start_index,
            end_index=end_index,
        )

    @staticmethod
    def _metric(
        relative: RelativePerformanceSeries,
        *,
        window_kind: str,
        sessions: int,
        start_index: int,
        end_index: int,
    ) -> EventWindowMetric:
        start = relative.points[start_index]
        end = relative.points[end_index]
        stock_return = (end.stock_adjusted_close / start.stock_adjusted_close) - 1.0
        benchmark_return = (end.benchmark_close / start.benchmark_close) - 1.0
        excess_return = stock_return - benchmark_return
        abnormal_values = [
            point.abnormal_return_1d
            for point in relative.points[start_index + 1 : end_index + 1]
        ]
        if len(abnormal_values) != sessions:
            raise AssertionError("event window session count mismatch")
        if any(value is None for value in abnormal_values):
            raise ValueError("event window contains unresolved daily abnormal return")
        cumulative_abnormal = sum(float(value) for value in abnormal_values)
        for name, value in (
            ("stock_return", stock_return),
            ("benchmark_return", benchmark_return),
            ("excess_return", excess_return),
            ("cumulative_abnormal_return", cumulative_abnormal),
        ):
            if not math.isfinite(value):
                raise ValueError(f"non-finite {name}")
        return EventWindowMetric(
            window_kind=window_kind,
            sessions=sessions,
            start_date=start.trade_date,
            end_date=end.trade_date,
            stock_return=stock_return,
            benchmark_return=benchmark_return,
            excess_return=excess_return,
            cumulative_abnormal_return=cumulative_abnormal,
        )
