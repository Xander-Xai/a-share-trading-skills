from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from src.core.pit_store import PITStore
from src.data.coverage import CoverageResolver
from src.data.ingest import ingest_candidates
from src.data.official_trading_calendar import (
    OfficialAnnualTradingCalendarPlan,
    load_official_calendar_plans,
    plan_from_mapping,
)


CONFIG = Path("configs/data/trading_calendar/cn-a-share-2026-official.json")


class OfficialTradingCalendarTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.plans = load_official_calendar_plans(CONFIG)
        cls.by_exchange = {plan.exchange: plan for plan in cls.plans}

    def test_config_contains_sse_and_szse_2026(self):
        self.assertEqual(set(self.by_exchange), {"SSE", "SZSE"})
        self.assertEqual({plan.year for plan in self.plans}, {2026})
        self.assertTrue(
            self.by_exchange["SSE"].source_url.startswith("https://www.sse.com.cn/")
        )
        self.assertTrue(
            self.by_exchange["SZSE"].source_url.startswith("https://www.szse.cn/")
        )

    def test_calendar_plan_enumerates_every_calendar_date(self):
        for plan in self.plans:
            sessions = plan.sessions()
            self.assertEqual(len(sessions), 365)
            self.assertEqual(sessions[0].trade_date, "2026-01-01")
            self.assertEqual(sessions[-1].trade_date, "2026-12-31")

    def test_known_2026_open_and_closed_dates(self):
        for plan in self.plans:
            sessions = {row.trade_date: row for row in plan.sessions()}
            self.assertFalse(sessions["2026-01-01"].is_open)
            self.assertTrue(sessions["2026-01-05"].is_open)
            self.assertFalse(sessions["2026-02-23"].is_open)
            self.assertTrue(sessions["2026-02-24"].is_open)
            self.assertTrue(sessions["2026-08-28"].is_open)
            self.assertFalse(sessions["2026-09-25"].is_open)
            self.assertFalse(sessions["2026-10-10"].is_open)  # Saturday remains closed.
            self.assertTrue(sessions["2026-10-08"].is_open)

    def test_date_only_notice_uses_conservative_next_day_visibility(self):
        for plan in self.plans:
            self.assertEqual(plan.publication_date, "2025-12-22")
            self.assertEqual(plan.available_at, "2025-12-23T00:00:00+08:00")
            before = list(plan.collect(as_of="2025-12-22T23:59:59+08:00"))
            after = list(plan.collect(as_of="2025-12-23T00:00:00+08:00"))
            self.assertEqual(before, [])
            self.assertEqual(len(after), 366)  # 365 sessions + one coverage assertion.

    def test_collect_emits_exchange_level_complete_coverage(self):
        for plan in self.plans:
            rows = list(plan.collect(as_of="2026-08-28T23:26:00+08:00"))
            coverage = [
                row for row in rows if row.metadata.entity_type == "DATASET_COVERAGE"
            ]
            self.assertEqual(len(coverage), 1)
            payload = coverage[0].payload
            self.assertEqual(payload["dataset_family"], "TRADING_SESSION")
            self.assertEqual(payload["scope_type"], "EXCHANGE")
            self.assertEqual(payload["exchange"], plan.exchange)
            self.assertEqual(payload["completeness_status"], "CONFIRMED_COMPLETE")
            self.assertEqual(
                payload["verification_method"], "EXCHANGE_CALENDAR_ENUMERATION"
            )
            self.assertEqual(payload["expected_count"], 365)
            self.assertEqual(payload["observed_count"], 365)

    def test_ingested_calendar_resolves_coverage_from_pit_snapshot(self):
        with tempfile.TemporaryDirectory() as tmp:
            store = PITStore(tmp)
            plan = self.by_exchange["SSE"]
            ingest_candidates(
                store,
                plan.collect(as_of="2026-08-28T23:26:00+08:00"),
                adapter_id="SSE_OFFICIAL_TRADING_CALENDAR_PLAN_V1",
            )
            snapshot = store.create_snapshot(
                strategy_id="a_share_short_mid",
                sleeve="short_mid",
                as_of="2026-08-28T23:26:00+08:00",
                intended_use="RESEARCH",
                entity_types=["TRADING_SESSION", "DATASET_COVERAGE"],
            )
            records = store.materialize_snapshot(snapshot["snapshot_id"])
            resolution = CoverageResolver().resolve(
                records,
                dataset_family="TRADING_SESSION",
                requested_start="2026-08-01",
                requested_end="2026-08-28",
                exchange="SSE",
                accepted_methods={"EXCHANGE_CALENDAR_ENUMERATION"},
            )
            self.assertTrue(resolution.confirmed)
            self.assertEqual(resolution.scope_type, "EXCHANGE")

    def test_wrong_official_host_is_rejected(self):
        with self.assertRaises(ValueError):
            plan_from_mapping(
                {
                    "exchange": "SSE",
                    "year": 2026,
                    "source_name": "Shanghai Stock Exchange",
                    "source_url": "https://example.com/calendar",
                    "source_snapshot_id": "bad-source",
                    "publication_date": "2025-12-22",
                    "available_at": "2025-12-23T00:00:00+08:00",
                    "ingested_at": "2026-08-28T23:26:00+08:00",
                    "session_rule_version": "SSE_CALENDAR_PLAN_2026_V1",
                    "revision_id": "2026-v1",
                    "closures": [],
                }
            )

    def test_same_day_available_at_for_date_only_notice_is_rejected(self):
        source = self.by_exchange["SSE"]
        with self.assertRaises(ValueError):
            OfficialAnnualTradingCalendarPlan(
                exchange=source.exchange,
                year=source.year,
                source_name=source.source_name,
                source_url=source.source_url,
                source_snapshot_id=source.source_snapshot_id,
                publication_date=source.publication_date,
                available_at="2025-12-22T23:59:59+08:00",
                ingested_at=source.ingested_at,
                session_rule_version=source.session_rule_version,
                revision_id=source.revision_id,
                closures=source.closures,
            ).validate()


if __name__ == "__main__":
    unittest.main()
