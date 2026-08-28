from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from statistics import mean
from typing import Iterable

from src.core.pit_store import PITStore, StoredPITRecord
from src.core.strategy_boundary import (
    SHORT_MID_SLEEVE,
    SHORT_MID_STRATEGY_ID,
    require_strategy_context,
)
from src.data.entities import CorporateAction, DailyBar
from src.features.snapshot import FeatureSnapshot, FeatureValue


FEATURE_SET_VERSION = "short-mid-market-v0"
IMPLEMENTATION_VERSION = "short-mid-market-v0.2"
CONFIG_VERSION = "short-mid-market-v0"
CALC_PREFIX = "short-mid-market-v0"


def _record_ref(record: StoredPITRecord) -> str:
    return f"{record.metadata.record_id}@{record.metadata.revision_id}"


def _feature(
    name: str,
    *,
    status: str,
    value=None,
    unit: str | None = None,
    records: Iterable[StoredPITRecord] = (),
) -> FeatureValue:
    return FeatureValue(
        name=name,
        status=status,
        value=value,
        unit=unit,
        source_record_ids=tuple(_record_ref(record) for record in records),
        calculation_id=f"{CALC_PREFIX}:{name}",
    )


def _pct(numerator: float, denominator: float) -> float:
    return (numerator / denominator - 1.0) * 100.0


def _range_pct(high: float, low: float, prev_close: float) -> float:
    return (high - low) / prev_close * 100.0


@dataclass(frozen=True)
class _BarRecord:
    record: StoredPITRecord
    bar: DailyBar


@dataclass(frozen=True)
class _ActionRecord:
    record: StoredPITRecord
    action: CorporateAction


class ShortMidMarketFeatureBuilder:
    """Build a conservative deterministic market-feature slice for Short/Mid.

    Canonical DAILY_BAR values are unadjusted. Multi-session calculations are
    therefore available only when both daily-bar coverage and corporate-action
    coverage have been explicitly confirmed by an upstream data-quality process.

    An empty action set is not treated as proof that no corporate action occurred.
    Missing coverage confirmation fails adjustment-sensitive features closed to
    `UNRESOLVED` rather than silently assuming a continuous price series.
    """

    def build_from_store(
        self,
        store: PITStore,
        *,
        data_snapshot_id: str,
        security_id: str,
        daily_bar_coverage_confirmed: bool = False,
        corporate_action_coverage_confirmed: bool = False,
    ) -> FeatureSnapshot:
        manifest = store.load_snapshot(data_snapshot_id)
        require_strategy_context(
            strategy_id=str(manifest["strategy_id"]),
            sleeve=str(manifest["sleeve"]),
            expected_strategy_id=SHORT_MID_STRATEGY_ID,
            expected_sleeve=SHORT_MID_SLEEVE,
        )
        records = store.materialize_snapshot(data_snapshot_id)
        return self.build(
            records,
            data_snapshot_id=data_snapshot_id,
            as_of=str(manifest["as_of"]),
            security_id=security_id,
            daily_bar_coverage_confirmed=daily_bar_coverage_confirmed,
            corporate_action_coverage_confirmed=corporate_action_coverage_confirmed,
        )

    def build(
        self,
        records: Iterable[StoredPITRecord],
        *,
        data_snapshot_id: str,
        as_of: str,
        security_id: str,
        daily_bar_coverage_confirmed: bool = False,
        corporate_action_coverage_confirmed: bool = False,
    ) -> FeatureSnapshot:
        if type(daily_bar_coverage_confirmed) is not bool:
            raise ValueError("daily_bar_coverage_confirmed must be boolean")
        if type(corporate_action_coverage_confirmed) is not bool:
            raise ValueError("corporate_action_coverage_confirmed must be boolean")

        materialized = tuple(records)
        bars = self._bars(materialized, security_id)
        actions = self._actions(materialized, security_id)
        if not bars:
            raise ValueError(f"no DAILY_BAR records for security_id={security_id}")

        features: list[FeatureValue] = []
        latest = bars[-1]
        latest_records = (latest.record,)
        latest_bar = latest.bar

        features.extend(
            [
                _feature(
                    "market.daily_bar_coverage_confirmed",
                    status="AVAILABLE",
                    value=daily_bar_coverage_confirmed,
                ),
                _feature(
                    "market.corporate_action_coverage_confirmed",
                    status="AVAILABLE",
                    value=corporate_action_coverage_confirmed,
                ),
                _feature(
                    "market.latest_trade_date",
                    status="AVAILABLE",
                    value=latest_bar.trade_date,
                    records=latest_records,
                ),
                _feature(
                    "market.bar_count",
                    status="AVAILABLE",
                    value=len(bars),
                    records=tuple(item.record for item in bars),
                ),
                _feature(
                    "market.close",
                    status="AVAILABLE",
                    value=float(latest_bar.close),
                    unit=latest_bar.currency,
                    records=latest_records,
                ),
                _feature(
                    "market.volume",
                    status="AVAILABLE",
                    value=float(latest_bar.volume),
                    records=latest_records,
                ),
                _feature(
                    "market.turnover",
                    status="AVAILABLE",
                    value=float(latest_bar.turnover),
                    records=latest_records,
                ),
                _feature(
                    "market.latest_suspended",
                    status="AVAILABLE",
                    value=bool(latest_bar.suspended),
                    records=latest_records,
                ),
            ]
        )

        last20 = bars[-20:]
        last20_start = date.fromisoformat(last20[0].bar.trade_date)
        latest_date = date.fromisoformat(latest_bar.trade_date)
        actions_20 = self._actions_in_window(actions, last20_start, latest_date)
        actions_latest = [
            item
            for item in actions
            if item.action.ex_date == latest_bar.trade_date
        ]

        features.extend(
            [
                _feature(
                    "market.observed_corporate_action_in_20d_window",
                    status="AVAILABLE",
                    value=bool(actions_20),
                    records=tuple(item.record for item in actions_20),
                ),
                _feature(
                    "market.observed_latest_ex_date_action",
                    status="AVAILABLE",
                    value=bool(actions_latest),
                    records=tuple(item.record for item in actions_latest),
                ),
                _feature(
                    "market.observed_suspension_count_20d",
                    status="AVAILABLE",
                    value=sum(1 for item in last20 if item.bar.suspended),
                    records=tuple(item.record for item in last20),
                ),
                _feature(
                    "market.close_vs_open_pct",
                    status="AVAILABLE",
                    value=_pct(latest_bar.close, latest_bar.open),
                    unit="pct",
                    records=latest_records,
                ),
            ]
        )

        if latest_bar.prev_close is None:
            for name in ("market.return_1d_pct", "market.gap_pct", "market.range_pct"):
                features.append(_feature(name, status="MISSING", records=latest_records))
        elif not corporate_action_coverage_confirmed:
            affected = latest_records + tuple(item.record for item in actions_latest)
            for name in ("market.return_1d_pct", "market.gap_pct", "market.range_pct"):
                features.append(_feature(name, status="UNRESOLVED", records=affected))
        elif actions_latest:
            affected = latest_records + tuple(item.record for item in actions_latest)
            for name in ("market.return_1d_pct", "market.gap_pct", "market.range_pct"):
                features.append(_feature(name, status="UNRESOLVED", records=affected))
        else:
            features.extend(
                [
                    _feature(
                        "market.return_1d_pct",
                        status="AVAILABLE",
                        value=_pct(latest_bar.close, latest_bar.prev_close),
                        unit="pct",
                        records=latest_records,
                    ),
                    _feature(
                        "market.gap_pct",
                        status="AVAILABLE",
                        value=_pct(latest_bar.open, latest_bar.prev_close),
                        unit="pct",
                        records=latest_records,
                    ),
                    _feature(
                        "market.range_pct",
                        status="AVAILABLE",
                        value=_range_pct(
                            latest_bar.high,
                            latest_bar.low,
                            latest_bar.prev_close,
                        ),
                        unit="pct",
                        records=latest_records,
                    ),
                ]
            )

        common_coverage = (
            daily_bar_coverage_confirmed,
            corporate_action_coverage_confirmed,
        )
        self._append_return_feature(features, bars, actions, sessions=5, coverage=common_coverage)
        self._append_return_feature(features, bars, actions, sessions=10, coverage=common_coverage)
        self._append_return_feature(features, bars, actions, sessions=20, coverage=common_coverage)
        self._append_ma_feature(features, bars, actions, window=5, coverage=common_coverage)
        self._append_ma_feature(features, bars, actions, window=10, coverage=common_coverage)
        self._append_ma_feature(features, bars, actions, window=20, coverage=common_coverage)
        self._append_distance_to_high_feature(
            features,
            bars,
            actions,
            window=20,
            coverage=common_coverage,
        )
        self._append_activity_ratio_feature(
            features,
            bars,
            actions,
            field="volume",
            name="market.rvol_1_vs_20",
            coverage=common_coverage,
        )
        self._append_activity_ratio_feature(
            features,
            bars,
            actions,
            field="turnover",
            name="market.turnover_ratio_1_vs_20",
            coverage=common_coverage,
        )

        return FeatureSnapshot.build(
            strategy_id=SHORT_MID_STRATEGY_ID,
            sleeve=SHORT_MID_SLEEVE,
            as_of=as_of,
            data_snapshot_id=data_snapshot_id,
            feature_set_version=FEATURE_SET_VERSION,
            implementation_version=IMPLEMENTATION_VERSION,
            config_version=CONFIG_VERSION,
            features=features,
        )

    @staticmethod
    def _bars(
        records: Iterable[StoredPITRecord],
        security_id: str,
    ) -> list[_BarRecord]:
        rows: list[_BarRecord] = []
        seen_dates: set[str] = set()
        for record in records:
            if record.metadata.entity_type != "DAILY_BAR":
                continue
            if record.metadata.security_id != security_id:
                continue
            bar = DailyBar(**record.payload)
            bar.validate()
            if bar.security_id != security_id:
                raise ValueError("DAILY_BAR payload security_id disagrees with metadata")
            if bar.trade_date in seen_dates:
                raise ValueError(f"duplicate DAILY_BAR trade_date: {bar.trade_date}")
            seen_dates.add(bar.trade_date)
            rows.append(_BarRecord(record=record, bar=bar))
        return sorted(rows, key=lambda item: item.bar.trade_date)

    @staticmethod
    def _actions(
        records: Iterable[StoredPITRecord],
        security_id: str,
    ) -> list[_ActionRecord]:
        rows: list[_ActionRecord] = []
        for record in records:
            if record.metadata.entity_type != "CORPORATE_ACTION":
                continue
            if record.metadata.security_id != security_id:
                continue
            action = CorporateAction(**record.payload)
            action.validate()
            if action.security_id != security_id:
                raise ValueError("CORPORATE_ACTION payload security_id disagrees with metadata")
            rows.append(_ActionRecord(record=record, action=action))
        return rows

    @staticmethod
    def _actions_in_window(
        actions: Iterable[_ActionRecord],
        start: date,
        end: date,
    ) -> list[_ActionRecord]:
        result: list[_ActionRecord] = []
        for item in actions:
            if item.action.ex_date is None:
                continue
            ex_date = date.fromisoformat(item.action.ex_date)
            if start <= ex_date <= end:
                result.append(item)
        return result

    @staticmethod
    def _coverage_confirmed(coverage: tuple[bool, bool]) -> bool:
        daily_bar_coverage_confirmed, corporate_action_coverage_confirmed = coverage
        return daily_bar_coverage_confirmed and corporate_action_coverage_confirmed

    def _append_return_feature(
        self,
        features: list[FeatureValue],
        bars: list[_BarRecord],
        actions: list[_ActionRecord],
        *,
        sessions: int,
        coverage: tuple[bool, bool],
    ) -> None:
        name = f"market.return_{sessions}d_pct"
        required = sessions + 1
        if len(bars) < required:
            features.append(
                _feature(name, status="MISSING", records=tuple(item.record for item in bars))
            )
            return

        window = bars[-required:]
        start = date.fromisoformat(window[0].bar.trade_date)
        end = date.fromisoformat(window[-1].bar.trade_date)
        action_rows = self._actions_in_window(actions, start, end)
        lineage = tuple(item.record for item in window) + tuple(
            item.record for item in action_rows
        )
        if not self._coverage_confirmed(coverage) or action_rows:
            features.append(_feature(name, status="UNRESOLVED", records=lineage))
            return

        features.append(
            _feature(
                name,
                status="AVAILABLE",
                value=_pct(window[-1].bar.close, window[0].bar.close),
                unit="pct",
                records=lineage,
            )
        )

    def _append_ma_feature(
        self,
        features: list[FeatureValue],
        bars: list[_BarRecord],
        actions: list[_ActionRecord],
        *,
        window: int,
        coverage: tuple[bool, bool],
    ) -> None:
        ma_name = f"market.ma{window}"
        distance_name = f"market.close_to_ma{window}_pct"
        if len(bars) < window:
            lineage = tuple(item.record for item in bars)
            features.append(_feature(ma_name, status="MISSING", records=lineage))
            features.append(_feature(distance_name, status="MISSING", records=lineage))
            return

        selected = bars[-window:]
        start = date.fromisoformat(selected[0].bar.trade_date)
        end = date.fromisoformat(selected[-1].bar.trade_date)
        action_rows = self._actions_in_window(actions, start, end)
        lineage = tuple(item.record for item in selected) + tuple(
            item.record for item in action_rows
        )
        if not self._coverage_confirmed(coverage) or action_rows:
            features.append(_feature(ma_name, status="UNRESOLVED", records=lineage))
            features.append(_feature(distance_name, status="UNRESOLVED", records=lineage))
            return

        ma_value = mean(item.bar.close for item in selected)
        features.append(
            _feature(
                ma_name,
                status="AVAILABLE",
                value=float(ma_value),
                unit=selected[-1].bar.currency,
                records=lineage,
            )
        )
        features.append(
            _feature(
                distance_name,
                status="AVAILABLE",
                value=_pct(selected[-1].bar.close, ma_value),
                unit="pct",
                records=lineage,
            )
        )

    def _append_distance_to_high_feature(
        self,
        features: list[FeatureValue],
        bars: list[_BarRecord],
        actions: list[_ActionRecord],
        *,
        window: int,
        coverage: tuple[bool, bool],
    ) -> None:
        name = f"market.distance_to_{window}d_high_pct"
        if len(bars) < window:
            features.append(
                _feature(name, status="MISSING", records=tuple(item.record for item in bars))
            )
            return

        selected = bars[-window:]
        start = date.fromisoformat(selected[0].bar.trade_date)
        end = date.fromisoformat(selected[-1].bar.trade_date)
        action_rows = self._actions_in_window(actions, start, end)
        lineage = tuple(item.record for item in selected) + tuple(
            item.record for item in action_rows
        )
        if not self._coverage_confirmed(coverage) or action_rows:
            features.append(_feature(name, status="UNRESOLVED", records=lineage))
            return

        high = max(item.bar.high for item in selected)
        features.append(
            _feature(
                name,
                status="AVAILABLE",
                value=_pct(selected[-1].bar.close, high),
                unit="pct",
                records=lineage,
            )
        )

    def _append_activity_ratio_feature(
        self,
        features: list[FeatureValue],
        bars: list[_BarRecord],
        actions: list[_ActionRecord],
        *,
        field: str,
        name: str,
        coverage: tuple[bool, bool],
    ) -> None:
        # Latest session versus the prior 20 sessions, so 21 bars are required.
        if len(bars) < 21:
            features.append(
                _feature(name, status="MISSING", records=tuple(item.record for item in bars))
            )
            return

        selected = bars[-21:]
        start = date.fromisoformat(selected[0].bar.trade_date)
        end = date.fromisoformat(selected[-1].bar.trade_date)
        action_rows = self._actions_in_window(actions, start, end)
        lineage = tuple(item.record for item in selected) + tuple(
            item.record for item in action_rows
        )
        if not self._coverage_confirmed(coverage) or action_rows:
            features.append(_feature(name, status="UNRESOLVED", records=lineage))
            return

        prior_values = [float(getattr(item.bar, field)) for item in selected[:-1]]
        denominator = mean(prior_values)
        if denominator <= 0:
            features.append(_feature(name, status="UNRESOLVED", records=lineage))
            return

        current = float(getattr(selected[-1].bar, field))
        features.append(
            _feature(
                name,
                status="AVAILABLE",
                value=current / denominator,
                unit="ratio",
                records=lineage,
            )
        )
