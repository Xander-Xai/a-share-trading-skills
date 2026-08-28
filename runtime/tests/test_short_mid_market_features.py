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
from src.data.entities import CorporateAction, DailyBar
from src.data.ingest import ingest_candidates
from src.features.short_mid_market import ShortMidMarketFeatureBuilder


CN_TZ = timezone(timedelta(hours=8))


def business_days_ending(end_date: date, count: int) -> list[date]:
    days: list[date] = []
    cursor = end_date
    while len(days) < count:
        if cursor.weekday() < 5:
            days.append(cursor)
        cursor -= timedelta(days=1)
    return list(reversed(days))


def ts(day: date, hh: int, mm: int, ss: int = 0) -> str:
    return datetime.combine(day, time(hh, mm, ss), tzinfo=CN_TZ).isoformat()


class ShortMidMarketFeatureTests(unittest.TestCase):
    security_id = "601600"

    def make_bar_candidates(self, count: int = 21):
        days = business_days_ending(date(2026, 8, 28), count)
        candidates = []
        prior_close = 10.0
        for idx, day in enumerate(days):
            close = 10.1 + idx * 0.1
            bar = DailyBar(
                security_id=self.security_id,
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
                    entity=bar,
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
        return candidates

    def make_action_candidate(self, ex_date: date):
        announcement_date = ex_date - timedelta(days=5)
        action = CorporateAction(
            security_id=self.security_id,
            action_id=f"cash-div-{ex_date.isoformat()}",
            action_type="CASH_DIVIDEND",
            announcement_date=announcement_date.isoformat(),
            ex_date=ex_date.isoformat(),
            cash_per_share=0.1,
        )
        return NormalizedRecordCandidate.from_entity(
            entity=action,
            source="official-action-fixture",
            source_tier="TIER1",
            source_snapshot_id=f"action-{ex_date.isoformat()}",
            revision_id="rev-1",
            published_at=ts(announcement_date, 16, 0),
            available_at=ts(announcement_date, 16, 0),
            ingested_at=ts(announcement_date, 16, 1),
            strategy_visibility=("long", "short_mid"),
            permitted_use="RESEARCH_ONLY",
            exchange="SSE",
        )

    def build_store(self, *, bar_count=21, action_ex_date: date | None = None):
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        store = PITStore(tmp.name)
        candidates = self.make_bar_candidates(bar_count)
        if action_ex_date is not None:
            candidates.append(self.make_action_candidate(action_ex_date))
        ingest_candidates(store, candidates, adapter_id="MARKET_FEATURE_TEST")
        return store

    def make_snapshot(self, store: PITStore, *, long=False):
        return store.create_snapshot(
            strategy_id=LONG_STRATEGY_ID if long else SHORT_MID_STRATEGY_ID,
            sleeve=LONG_SLEEVE if long else SHORT_MID_SLEEVE,
            as_of="2026-08-28T16:00:00+08:00",
            intended_use="RESEARCH",
            entity_types=["DAILY_BAR", "CORPORATE_ACTION"],
            security_ids=[self.security_id],
        )

    def test_build_is_deterministic_for_same_data_snapshot(self):
        store = self.build_store()
        snapshot = self.make_snapshot(store)
        builder = ShortMidMarketFeatureBuilder()
        first = builder.build_from_store(
            store,
            data_snapshot_id=snapshot["snapshot_id"],
            security_id=self.security_id,
        )
        second = builder.build_from_store(
            store,
            data_snapshot_id=snapshot["snapshot_id"],
            security_id=self.security_id,
        )
        self.assertEqual(first.feature_snapshot_id, second.feature_snapshot_id)

    def test_complete_history_produces_available_low_subjectivity_features(self):
        store = self.build_store()
        snapshot = self.make_snapshot(store)
        result = ShortMidMarketFeatureBuilder().build_from_store(
            store,
            data_snapshot_id=snapshot["snapshot_id"],
            security_id=self.security_id,
        )
        features = result.feature_map()

        self.assertEqual(features["market.bar_count"].value, 21)
        self.assertEqual(features["market.return_5d_pct"].status, "AVAILABLE")
        self.assertEqual(features["market.return_10d_pct"].status, "AVAILABLE")
        self.assertEqual(features["market.return_20d_pct"].status, "AVAILABLE")
        self.assertEqual(features["market.ma20"].status, "AVAILABLE")
        self.assertEqual(features["market.distance_to_20d_high_pct"].status, "AVAILABLE")
        self.assertEqual(features["market.rvol_1_vs_20"].status, "AVAILABLE")
        self.assertEqual(features["market.turnover_ratio_1_vs_20"].status, "AVAILABLE")
        self.assertGreater(features["market.rvol_1_vs_20"].value, 1.0)
        self.assertGreater(features["market.turnover_ratio_1_vs_20"].value, 1.0)
        self.assertFalse(features["market.corporate_action_in_20d_window"].value)

    def test_insufficient_history_is_missing_not_fabricated(self):
        store = self.build_store(bar_count=4)
        snapshot = self.make_snapshot(store)
        result = ShortMidMarketFeatureBuilder().build_from_store(
            store,
            data_snapshot_id=snapshot["snapshot_id"],
            security_id=self.security_id,
        )
        features = result.feature_map()
        self.assertEqual(features["market.return_5d_pct"].status, "MISSING")
        self.assertEqual(features["market.ma5"].status, "MISSING")
        self.assertEqual(features["market.rvol_1_vs_20"].status, "MISSING")
        self.assertEqual(features["market.close"].status, "AVAILABLE")

    def test_corporate_action_in_lookback_blocks_unadjusted_trailing_features(self):
        ex_date = business_days_ending(date(2026, 8, 28), 21)[-5]
        store = self.build_store(action_ex_date=ex_date)
        snapshot = self.make_snapshot(store)
        result = ShortMidMarketFeatureBuilder().build_from_store(
            store,
            data_snapshot_id=snapshot["snapshot_id"],
            security_id=self.security_id,
        )
        features = result.feature_map()
        self.assertTrue(features["market.corporate_action_in_20d_window"].value)
        self.assertEqual(features["market.return_20d_pct"].status, "UNRESOLVED")
        self.assertEqual(features["market.ma20"].status, "UNRESOLVED")
        self.assertEqual(features["market.distance_to_20d_high_pct"].status, "UNRESOLVED")
        self.assertEqual(features["market.rvol_1_vs_20"].status, "UNRESOLVED")
        self.assertEqual(features["market.close"].status, "AVAILABLE")

    def test_latest_ex_date_blocks_prev_close_based_intraday_features(self):
        ex_date = date(2026, 8, 28)
        store = self.build_store(action_ex_date=ex_date)
        snapshot = self.make_snapshot(store)
        result = ShortMidMarketFeatureBuilder().build_from_store(
            store,
            data_snapshot_id=snapshot["snapshot_id"],
            security_id=self.security_id,
        )
        features = result.feature_map()
        self.assertTrue(features["market.latest_ex_date_action"].value)
        self.assertEqual(features["market.return_1d_pct"].status, "UNRESOLVED")
        self.assertEqual(features["market.gap_pct"].status, "UNRESOLVED")
        self.assertEqual(features["market.range_pct"].status, "UNRESOLVED")
        self.assertEqual(features["market.close_vs_open_pct"].status, "AVAILABLE")

    def test_short_mid_builder_rejects_long_data_snapshot(self):
        store = self.build_store()
        snapshot = self.make_snapshot(store, long=True)
        with self.assertRaises(ValueError):
            ShortMidMarketFeatureBuilder().build_from_store(
                store,
                data_snapshot_id=snapshot["snapshot_id"],
                security_id=self.security_id,
            )


if __name__ == "__main__":
    unittest.main()
