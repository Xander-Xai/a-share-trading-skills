from __future__ import annotations

import tempfile
import unittest
from datetime import date, datetime, time, timedelta, timezone

from src.core.pit_store import PITStore
from src.core.strategy_boundary import (
    LONG_SLEEVE,
    LONG_STRATEGY_ID,
    SHORT_MID_SLEEVE,
    SHORT_MID_STRATEGY_ID,
)
from src.data.adapters import NormalizedRecordCandidate
from src.data.coverage import CoverageResolver, DatasetCoverage
from src.data.entities import DailyBar
from src.data.ingest import ingest_candidates
from src.features.short_mid_verified import VerifiedShortMidMarketFeatureBuilder


CN_TZ = timezone(timedelta(hours=8))
SECURITY_ID = "601600"


def ts(day: date, hh: int, mm: int, ss: int = 0) -> str:
    return datetime.combine(day, time(hh, mm, ss), tzinfo=CN_TZ).isoformat()


def business_days_ending(end_date: date, count: int) -> list[date]:
    rows: list[date] = []
    cursor = end_date
    while len(rows) < count:
        if cursor.weekday() < 5:
            rows.append(cursor)
        cursor -= timedelta(days=1)
    return list(reversed(rows))


class DatasetCoverageTests(unittest.TestCase):
    def make_bar_candidates(self, count: int = 21):
        days = business_days_ending(date(2026, 8, 28), count)
        candidates = []
        prior_close = 10.0
        for idx, day in enumerate(days):
            close = 10.1 + idx * 0.1
            entity = DailyBar(
                security_id=SECURITY_ID,
                trade_date=day.isoformat(),
                open=close - 0.02,
                high=close + 0.05,
                low=close - 0.05,
                close=close,
                prev_close=prior_close,
                volume=1000.0 + idx * 20.0,
                turnover=10000.0 + idx * 250.0,
            )
            candidates.append(
                NormalizedRecordCandidate.from_entity(
                    entity=entity,
                    source="licensed-market-fixture",
                    source_tier="TIER2",
                    source_snapshot_id=f"bar-{day.isoformat()}",
                    revision_id="rev-1",
                    effective_at=ts(day, 15, 0),
                    available_at=ts(day, 15, 0, 5),
                    ingested_at=ts(day, 15, 1),
                    strategy_visibility=("long", "short_mid"),
                    permitted_use="RESEARCH_ONLY",
                    exchange="SSE",
                )
            )
            prior_close = close
        return candidates, days

    def coverage_candidate(
        self,
        *,
        dataset_family: str,
        start: date,
        end: date,
        status: str = "CONFIRMED_COMPLETE",
        method: str,
        scope_type: str = "SECURITY",
        security_id: str | None = SECURITY_ID,
        exchange: str | None = "SSE",
        coverage_id: str = "v1",
        available_at: str = "2026-08-28T15:05:00+08:00",
        expected_count: int | None = None,
        observed_count: int | None = None,
    ):
        entity = DatasetCoverage(
            coverage_id=coverage_id,
            dataset_family=dataset_family,
            scope_type=scope_type,
            start_date=start.isoformat(),
            end_date=end.isoformat(),
            completeness_status=status,
            verification_method=method,
            security_id=security_id,
            exchange=exchange,
            expected_count=expected_count,
            observed_count=observed_count,
        )
        return NormalizedRecordCandidate.from_entity(
            entity=entity,
            source="coverage-fixture",
            source_tier="TIER1",
            source_snapshot_id=f"coverage-{dataset_family}-{coverage_id}",
            revision_id="rev-1",
            available_at=available_at,
            ingested_at="2026-08-28T15:06:00+08:00",
            strategy_visibility=("long", "short_mid"),
            permitted_use="RESEARCH_ONLY",
            exchange=exchange,
        )

    def build_store(self, *, include_coverage=True, action_method="OFFICIAL_SOURCE_ENUMERATION"):
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        store = PITStore(tmp.name)
        candidates, days = self.make_bar_candidates()
        if include_coverage:
            candidates.extend(
                [
                    self.coverage_candidate(
                        dataset_family="DAILY_BAR",
                        start=days[0],
                        end=days[-1],
                        method="TRADING_CALENDAR_RECONCILED",
                        expected_count=len(days),
                        observed_count=len(days),
                    ),
                    self.coverage_candidate(
                        dataset_family="CORPORATE_ACTION",
                        start=days[0],
                        end=days[-1],
                        method=action_method,
                        expected_count=0,
                        observed_count=0,
                    ),
                ]
            )
        ingest_candidates(store, candidates, adapter_id="DATASET_COVERAGE_TEST")
        return store, days

    def make_snapshot(self, store: PITStore, *, long=False):
        return store.create_snapshot(
            strategy_id=LONG_STRATEGY_ID if long else SHORT_MID_STRATEGY_ID,
            sleeve=LONG_SLEEVE if long else SHORT_MID_SLEEVE,
            as_of="2026-08-28T16:00:00+08:00",
            intended_use="RESEARCH",
            entity_types=["DAILY_BAR", "CORPORATE_ACTION", "DATASET_COVERAGE"],
            security_ids=[SECURITY_ID],
        )

    def test_verified_builder_resolves_coverage_from_pit_assertions(self):
        store, _ = self.build_store()
        snapshot = self.make_snapshot(store)
        result = VerifiedShortMidMarketFeatureBuilder().build_from_store(
            store,
            data_snapshot_id=snapshot["snapshot_id"],
            security_id=SECURITY_ID,
        )
        features = result.feature_map()
        self.assertTrue(features["market.daily_bar_coverage_confirmed"].value)
        self.assertTrue(features["market.corporate_action_coverage_confirmed"].value)
        self.assertEqual(features["market.daily_bar_coverage.reason"].value, "CONFIRMED")
        self.assertEqual(features["market.return_20d_pct"].status, "AVAILABLE")
        self.assertTrue(features["market.daily_bar_coverage_confirmed"].source_record_ids)

    def test_missing_assertions_fail_closed_without_manual_override(self):
        store, _ = self.build_store(include_coverage=False)
        snapshot = self.make_snapshot(store)
        result = VerifiedShortMidMarketFeatureBuilder().build_from_store(
            store,
            data_snapshot_id=snapshot["snapshot_id"],
            security_id=SECURITY_ID,
        )
        features = result.feature_map()
        self.assertFalse(features["market.daily_bar_coverage_confirmed"].value)
        self.assertFalse(features["market.corporate_action_coverage_confirmed"].value)
        self.assertEqual(
            features["market.daily_bar_coverage.reason"].value,
            "NO_APPLICABLE_COVERAGE_ASSERTION",
        )
        self.assertEqual(features["market.return_20d_pct"].status, "UNRESOLVED")

    def test_unaccepted_verification_method_does_not_confirm_coverage(self):
        store, _ = self.build_store(action_method="MANUAL_ASSUMPTION")
        snapshot = self.make_snapshot(store)
        result = VerifiedShortMidMarketFeatureBuilder().build_from_store(
            store,
            data_snapshot_id=snapshot["snapshot_id"],
            security_id=SECURITY_ID,
        )
        features = result.feature_map()
        self.assertTrue(features["market.daily_bar_coverage_confirmed"].value)
        self.assertFalse(features["market.corporate_action_coverage_confirmed"].value)
        self.assertEqual(
            features["market.corporate_action_coverage.reason"].value,
            "VERIFICATION_METHOD_NOT_ACCEPTED",
        )
        self.assertEqual(features["market.ma20"].status, "UNRESOLVED")

    def test_security_partial_overrides_broader_exchange_complete(self):
        store, days = self.build_store(include_coverage=False)
        candidates = [
            self.coverage_candidate(
                dataset_family="DAILY_BAR",
                start=days[0],
                end=days[-1],
                method="TRADING_CALENDAR_RECONCILED",
                scope_type="EXCHANGE",
                security_id=None,
                exchange="SSE",
                coverage_id="exchange-complete",
                expected_count=21,
                observed_count=21,
            ),
            self.coverage_candidate(
                dataset_family="DAILY_BAR",
                start=days[0],
                end=days[-1],
                status="PARTIAL",
                method="TRADING_CALENDAR_RECONCILED",
                scope_type="SECURITY",
                security_id=SECURITY_ID,
                exchange="SSE",
                coverage_id="security-partial",
                expected_count=21,
                observed_count=20,
            ),
        ]
        ingest_candidates(store, candidates, adapter_id="COVERAGE_SCOPE_TEST")
        snapshot = self.make_snapshot(store)
        records = store.materialize_snapshot(snapshot["snapshot_id"])
        resolution = CoverageResolver().resolve(
            records,
            dataset_family="DAILY_BAR",
            requested_start=days[0].isoformat(),
            requested_end=days[-1].isoformat(),
            security_id=SECURITY_ID,
            exchange="SSE",
            accepted_methods={"TRADING_CALENDAR_RECONCILED"},
        )
        self.assertFalse(resolution.confirmed)
        self.assertEqual(resolution.status, "PARTIAL")
        self.assertEqual(resolution.scope_type, "SECURITY")

    def test_confirmed_complete_rejects_count_mismatch(self):
        with self.assertRaises(ValueError):
            DatasetCoverage(
                coverage_id="bad",
                dataset_family="DAILY_BAR",
                scope_type="SECURITY",
                security_id=SECURITY_ID,
                start_date="2026-08-01",
                end_date="2026-08-28",
                completeness_status="CONFIRMED_COMPLETE",
                verification_method="TRADING_CALENDAR_RECONCILED",
                expected_count=21,
                observed_count=20,
            ).validate()

    def test_verified_short_mid_builder_rejects_long_snapshot(self):
        store, _ = self.build_store()
        snapshot = self.make_snapshot(store, long=True)
        with self.assertRaises(ValueError):
            VerifiedShortMidMarketFeatureBuilder().build_from_store(
                store,
                data_snapshot_id=snapshot["snapshot_id"],
                security_id=SECURITY_ID,
            )


if __name__ == "__main__":
    unittest.main()
