from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from typing import Iterable

from src.core.pit_store import PITStore, StoredPITRecord
from src.core.strategy_boundary import (
    SHORT_MID_SLEEVE,
    SHORT_MID_STRATEGY_ID,
    require_strategy_context,
)
from src.data.coverage import CoverageResolution, CoverageResolver
from src.data.entities import DailyBar
from src.features.short_mid_market import ShortMidMarketFeatureBuilder
from src.features.snapshot import FeatureSnapshot, FeatureValue


DAILY_BAR_ACCEPTED_METHODS = {
    "TRADING_CALENDAR_RECONCILED",
    "EXCHANGE_CALENDAR_RECONCILED",
}
CORPORATE_ACTION_ACCEPTED_METHODS = {
    "OFFICIAL_SOURCE_ENUMERATION",
    "LICENSED_VENDOR_RECONCILED",
    "OFFICIAL_VENDOR_RECONCILED",
}


@dataclass(frozen=True)
class VerifiedCoverageBundle:
    requested_start: str
    requested_end: str
    exchange: str | None
    daily_bar: CoverageResolution
    corporate_action: CoverageResolution

    @property
    def confirmed(self) -> bool:
        return self.daily_bar.confirmed and self.corporate_action.confirmed


class VerifiedShortMidMarketFeatureBuilder:
    """Production-facing wrapper that derives coverage from PIT evidence.

    The lower-level `ShortMidMarketFeatureBuilder` still accepts boolean coverage
    flags for deterministic fixture/research use. This wrapper is the approved
    production path: it resolves those booleans from PIT-visible DATASET_COVERAGE
    assertions so a caller cannot promote trailing features merely by passing
    `True` on the command line.
    """

    def __init__(self, resolver: CoverageResolver | None = None):
        self.resolver = resolver or CoverageResolver()

    def build_from_store(
        self,
        store: PITStore,
        *,
        data_snapshot_id: str,
        security_id: str,
    ) -> FeatureSnapshot:
        manifest = store.load_snapshot(data_snapshot_id)
        require_strategy_context(
            strategy_id=str(manifest["strategy_id"]),
            sleeve=str(manifest["sleeve"]),
            expected_strategy_id=SHORT_MID_STRATEGY_ID,
            expected_sleeve=SHORT_MID_SLEEVE,
        )
        records = tuple(store.materialize_snapshot(data_snapshot_id))
        coverage = self.resolve_coverage(records, security_id=security_id)

        base = ShortMidMarketFeatureBuilder().build(
            records,
            data_snapshot_id=data_snapshot_id,
            as_of=str(manifest["as_of"]),
            security_id=security_id,
            daily_bar_coverage_confirmed=coverage.daily_bar.confirmed,
            corporate_action_coverage_confirmed=coverage.corporate_action.confirmed,
        )
        return self._attach_coverage_lineage(base, coverage)

    def resolve_coverage(
        self,
        records: Iterable[StoredPITRecord],
        *,
        security_id: str,
    ) -> VerifiedCoverageBundle:
        materialized = tuple(records)
        bars = self._bars(materialized, security_id)
        if not bars:
            raise ValueError(f"no DAILY_BAR records for security_id={security_id}")

        # The current market-feature slice needs at most the latest 21 observed
        # sessions. Request coverage over exactly that calendar span; the upstream
        # coverage assertion is responsible for proving that no trading session is
        # missing inside it.
        selected = bars[-21:]
        requested_start = selected[0].trade_date
        requested_end = selected[-1].trade_date

        exchanges = {
            record.metadata.exchange
            for record in materialized
            if record.metadata.entity_type == "DAILY_BAR"
            and record.metadata.security_id == security_id
            and record.metadata.exchange
        }
        if len(exchanges) > 1:
            raise ValueError(f"conflicting DAILY_BAR exchanges for {security_id}: {sorted(exchanges)}")
        exchange = next(iter(exchanges), None)

        daily = self.resolver.resolve(
            materialized,
            dataset_family="DAILY_BAR",
            requested_start=requested_start,
            requested_end=requested_end,
            security_id=security_id,
            exchange=exchange,
            accepted_methods=set(DAILY_BAR_ACCEPTED_METHODS),
        )
        actions = self.resolver.resolve(
            materialized,
            dataset_family="CORPORATE_ACTION",
            requested_start=requested_start,
            requested_end=requested_end,
            security_id=security_id,
            exchange=exchange,
            accepted_methods=set(CORPORATE_ACTION_ACCEPTED_METHODS),
        )
        return VerifiedCoverageBundle(
            requested_start=requested_start,
            requested_end=requested_end,
            exchange=exchange,
            daily_bar=daily,
            corporate_action=actions,
        )

    @staticmethod
    def _bars(records: Iterable[StoredPITRecord], security_id: str) -> list[DailyBar]:
        bars: list[DailyBar] = []
        seen: set[str] = set()
        for record in records:
            if record.metadata.entity_type != "DAILY_BAR":
                continue
            if record.metadata.security_id != security_id:
                continue
            bar = DailyBar(**record.payload)
            bar.validate()
            if bar.trade_date in seen:
                raise ValueError(f"duplicate DAILY_BAR trade_date: {bar.trade_date}")
            seen.add(bar.trade_date)
            bars.append(bar)
        return sorted(bars, key=lambda item: item.trade_date)

    @staticmethod
    def _attach_coverage_lineage(
        snapshot: FeatureSnapshot,
        coverage: VerifiedCoverageBundle,
    ) -> FeatureSnapshot:
        replacements = {
            "market.daily_bar_coverage_confirmed": coverage.daily_bar,
            "market.corporate_action_coverage_confirmed": coverage.corporate_action,
        }
        features: list[FeatureValue] = []
        for feature in snapshot.features:
            resolution = replacements.get(feature.name)
            if resolution is None:
                features.append(feature)
                continue
            refs = () if resolution.assertion_ref is None else (resolution.assertion_ref,)
            features.append(
                FeatureValue(
                    name=feature.name,
                    status="AVAILABLE",
                    value=resolution.confirmed,
                    source_record_ids=refs,
                    calculation_id=(
                        f"dataset-coverage-v1:{resolution.dataset_family}:"
                        f"{resolution.reason}:{resolution.verification_method or 'NONE'}"
                    ),
                )
            )

        # Add non-alpha diagnostics so replay can explain why coverage failed.
        for prefix, resolution in (
            ("market.daily_bar_coverage", coverage.daily_bar),
            ("market.corporate_action_coverage", coverage.corporate_action),
        ):
            refs = () if resolution.assertion_ref is None else (resolution.assertion_ref,)
            features.extend(
                [
                    FeatureValue(
                        name=f"{prefix}.status",
                        status="AVAILABLE",
                        value=resolution.status,
                        source_record_ids=refs,
                        calculation_id="dataset-coverage-v1",
                    ),
                    FeatureValue(
                        name=f"{prefix}.reason",
                        status="AVAILABLE",
                        value=resolution.reason,
                        source_record_ids=refs,
                        calculation_id="dataset-coverage-v1",
                    ),
                ]
            )

        features.extend(
            [
                FeatureValue(
                    name="market.coverage.requested_start",
                    status="AVAILABLE",
                    value=coverage.requested_start,
                    calculation_id="dataset-coverage-v1",
                ),
                FeatureValue(
                    name="market.coverage.requested_end",
                    status="AVAILABLE",
                    value=coverage.requested_end,
                    calculation_id="dataset-coverage-v1",
                ),
            ]
        )

        return FeatureSnapshot.build(
            strategy_id=snapshot.strategy_id,
            sleeve=snapshot.sleeve,
            as_of=snapshot.as_of,
            data_snapshot_id=snapshot.data_snapshot_id,
            feature_set_version=snapshot.feature_set_version,
            implementation_version=f"{snapshot.implementation_version}+coverage-v1",
            config_version=snapshot.config_version,
            features=features,
        )
