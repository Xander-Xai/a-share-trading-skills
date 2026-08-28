from __future__ import annotations

import tempfile
import unittest
from datetime import date, datetime, time, timedelta, timezone

from src.core.pit_store import PITStore
from src.core.strategy_boundary import SHORT_MID_SLEEVE, SHORT_MID_STRATEGY_ID
from src.data.adapters import NormalizedRecordCandidate
from src.data.coverage import DatasetCoverage
from src.data.coverage_producers import TradingCalendarCoverageProducer
from src.data.entities import DailyBar
from src.data.ingest import ingest_candidates
from src.data.trading_calendar import TradingSession


CN_TZ = timezone(timedelta(hours=8))
SECURITY_ID = "601600"
EXCHANGE = "SSE"
START = date(2026, 8, 3)
END = date(2026, 8, 28)


def ts(day: date, hh: int, mm: int, ss: int = 0) -> str:
    return datetime.combine(day, time(hh, mm, ss), tzinfo=CN_TZ).isoformat()


def calendar_days(start: date, end: date) -> list[date]:
    rows: list[date] = []
    cursor = start
    while cursor <= end:
        rows.append(cursor)
        cursor += timedelta(days=1)
    return rows


def open_days(start: date, end: date) -> list[date]:
    return [day for day in calendar_days(start, end) if day.weekday() < 5]


class TradingCalendarCoverageProducerTests(unittest.TestCase):
    def make_session_candidates(self):
        candidates = []
        for day in calendar_days(START, END):
            entity = TradingSession(
                exchange=EXCHANGE,
                trade_date=day.isoformat(),
                is_open=day.weekday() < 5,
                session_rule_version="fixture-2026-v1",
            )
            candidates.append(
                NormalizedRecordCandidate.from_entity(
                    entity=entity,
                    source="official-calendar-fixture",
                    source_tier="TIER1",
                    source_snapshot_id=f"calendar-{day.isoformat()}",
                    revision_id="rev-1",
                    available_at="2026-08-01T09:00:00+08:00",
                    ingested_at="2026-08-01T09:01:00+08:00",
                    strategy_visibility=("long", "short_mid"),
                    permitted_use="RESEARCH_ONLY",
                    exchange=EXCHANGE,
                )
            )
        return candidates

    def make_bar_candidates(self, *, omit: date | None = None, extra_closed: date | None = None):
        candidates = []
        prior_close = 10.0
        days = list(open_days(START, END))
        if extra_closed is not None:
            days.append(extra_closed)
            days.sort()
        for idx, day in enumerate(days):
            if day == omit:
                continue
            close = 10.0 + idx * 0.05
            entity = DailyBar(
                security_id=SECURITY_ID,
                trade_date=day.isoformat(),
                open=close - 0.01,
                high=close + 0.04,
                low=close - 0.04,
                close=close,
                prev_close=prior_close,
                volume=1000.0 + idx,
                turnover=10000.0 + idx * 10,
            )
            candidates.append(
                NormalizedRecordCandidate.from_entity(
                    entity=entity,
                    source="market-fixture",
                    source_tier="TIER2",
                    source_snapshot_id=f"bar-{day.isoformat()}",
                    revision_id="rev-1",
                    effective_at=ts(day, 15, 0),
                    available_at=ts(day, 15, 0, 5),
                    ingested_at=ts(day, 15, 1),
                    strategy_visibility=("long", "short_mid"),
                    permitted_use="RESEARCH_ONLY",
                    exchange=EXCHANGE,
                )
            )
            prior_close = close
        return candidates

    def make_calendar_coverage_candidate(self, *, method="EXCHANGE_CALENDAR_ENUMERATION"):
        row_count = len(calendar_days(START, END))
        entity = DatasetCoverage(
            coverage_id="calendar-enumeration-v1",
            dataset_family="TRADING_SESSION",
            scope_type="EXCHANGE",
            exchange=EXCHANGE,
            start_date=START.isoformat(),
            end_date=END.isoformat(),
            completeness_status="CONFIRMED_COMPLETE",
            verification_method=method,
            expected_count=row_count,
            observed_count=row_count,
        )
        return NormalizedRecordCandidate.from_entity(
            entity=entity,
            source="official-calendar-fixture",
            source_tier="TIER1",
            source_snapshot_id="calendar-enumeration-v1",
            revision_id="rev-1",
            available_at="2026-08-01T09:02:00+08:00",
            ingested_at="2026-08-01T09:03:00+08:00",
            strategy_visibility=("long", "short_mid"),
            permitted_use="RESEARCH_ONLY",
            exchange=EXCHANGE,
        )

    def build_records(
        self,
        *,
        include_calendar_coverage=True,
        calendar_method="EXCHANGE_CALENDAR_ENUMERATION",
        omit_bar: date | None = None,
        extra_closed_bar: date | None = None,
    ):
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        store = PITStore(tmp.name)
        candidates = self.make_session_candidates() + self.make_bar_candidates(
            omit=omit_bar,
            extra_closed=extra_closed_bar,
        )
        if include_calendar_coverage:
            candidates.append(
                self.make_calendar_coverage_candidate(method=calendar_method)
            )
        ingest_candidates(store, candidates, adapter_id="TRADING_CALENDAR_COVERAGE_TEST")
        snapshot = store.create_snapshot(
            strategy_id=SHORT_MID_STRATEGY_ID,
            sleeve=SHORT_MID_SLEEVE,
            as_of="2026-08-28T16:00:00+08:00",
            intended_use="RESEARCH",
            entity_types=["TRADING_SESSION", "DAILY_BAR", "DATASET_COVERAGE"],
        )
        return store.materialize_snapshot(snapshot["snapshot_id"])

    def evaluate(self, records):
        return TradingCalendarCoverageProducer().evaluate(
            records,
            security_id=SECURITY_ID,
            exchange=EXCHANGE,
            start_date=START.isoformat(),
            end_date=END.isoformat(),
            coverage_id="daily-bar-reconcile-v1",
        )

    def test_complete_calendar_and_all_open_session_bars_confirm_daily_bar_coverage(self):
        coverage = self.evaluate(self.build_records())
        self.assertEqual(coverage.completeness_status, "CONFIRMED_COMPLETE")
        self.assertEqual(coverage.expected_count, len(open_days(START, END)))
        self.assertEqual(coverage.observed_count, len(open_days(START, END)))
        self.assertEqual(coverage.verification_method, "TRADING_CALENDAR_RECONCILED")

    def test_missing_open_session_bar_produces_partial_coverage(self):
        missing = open_days(START, END)[5]
        coverage = self.evaluate(self.build_records(omit_bar=missing))
        self.assertEqual(coverage.completeness_status, "PARTIAL")
        self.assertEqual(coverage.expected_count, len(open_days(START, END)))
        self.assertEqual(coverage.observed_count, len(open_days(START, END)) - 1)
        self.assertIn(missing.isoformat(), coverage.note or "")

    def test_bar_on_closed_date_produces_partial_coverage(self):
        closed = next(day for day in calendar_days(START, END) if day.weekday() >= 5)
        coverage = self.evaluate(self.build_records(extra_closed_bar=closed))
        self.assertEqual(coverage.completeness_status, "PARTIAL")
        self.assertGreater(coverage.observed_count or 0, coverage.expected_count or 0)
        self.assertIn(closed.isoformat(), coverage.note or "")

    def test_calendar_rows_without_calendar_coverage_do_not_prove_completeness(self):
        coverage = self.evaluate(self.build_records(include_calendar_coverage=False))
        self.assertEqual(coverage.completeness_status, "UNRESOLVED")
        self.assertIsNone(coverage.expected_count)
        self.assertIn("NO_APPLICABLE_COVERAGE_ASSERTION", coverage.note or "")

    def test_unaccepted_calendar_verification_method_does_not_confirm(self):
        coverage = self.evaluate(
            self.build_records(calendar_method="MANUAL_ASSUMPTION")
        )
        self.assertEqual(coverage.completeness_status, "UNRESOLVED")
        self.assertIn("VERIFICATION_METHOD_NOT_ACCEPTED", coverage.note or "")

    def test_duplicate_trading_session_date_is_rejected(self):
        records = list(self.build_records())
        duplicate = next(
            record for record in records if record.metadata.entity_type == "TRADING_SESSION"
        )
        records.append(duplicate)
        with self.assertRaises(ValueError):
            self.evaluate(records)


if __name__ == "__main__":
    unittest.main()
