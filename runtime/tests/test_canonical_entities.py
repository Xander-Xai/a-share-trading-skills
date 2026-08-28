import tempfile
import unittest

from src.core.pit_store import PITStore
from src.core.strategy_boundary import SHORT_MID_STRATEGY_ID
from src.data.adapters import NormalizedRecordCandidate
from src.data.entities import (
    ConsensusExpectation,
    DailyBar,
    FinancialStatement,
    SecurityMaster,
)
from src.data.ingest import ingest_candidates


class CanonicalEntityTests(unittest.TestCase):
    def test_security_master_record_id_is_stable(self):
        entity = SecurityMaster(
            security_id="601600",
            exchange="SSE",
            name="中国铝业",
            listing_date="2007-04-30",
        )
        self.assertEqual(entity.record_id(), "SECURITY_MASTER:601600")

    def test_daily_bar_requires_valid_ohlc(self):
        with self.assertRaises(ValueError):
            DailyBar(
                security_id="601600",
                trade_date="2026-08-28",
                open=9.80,
                high=9.70,
                low=9.60,
                close=9.82,
                prev_close=9.65,
                volume=1_000_000,
                turnover=9_800_000,
            ).validate()

    def test_daily_bar_canonical_price_basis_is_unadjusted(self):
        bar = DailyBar(
            security_id="601600",
            trade_date="2026-08-28",
            open=9.70,
            high=9.90,
            low=9.60,
            close=9.82,
            prev_close=9.65,
            volume=1_000_000,
            turnover=9_800_000,
            price_basis="FORWARD_ADJUSTED",
        )
        with self.assertRaises(ValueError):
            bar.validate()

    def test_financial_statement_requires_nonempty_metrics(self):
        statement = FinancialStatement(
            security_id="601600",
            period_end="2026-06-30",
            report_type="H1",
            statement_scope="CONSOLIDATED",
            metrics={},
        )
        with self.assertRaises(ValueError):
            statement.validate()

    def test_consensus_expectation_rejects_negative_coverage(self):
        expectation = ConsensusExpectation(
            security_id="601600",
            fiscal_period="2026-H1",
            metric="NET_PROFIT",
            value=118.0,
            unit="CNY_100M",
            coverage_count=-1,
        )
        with self.assertRaises(ValueError):
            expectation.validate()


class CandidateAndIngestTests(unittest.TestCase):
    def make_bar_candidate(self):
        bar = DailyBar(
            security_id="601600",
            trade_date="2026-08-28",
            open=9.70,
            high=9.90,
            low=9.60,
            close=9.82,
            prev_close=9.65,
            volume=1_000_000,
            turnover=9_800_000,
        )
        return NormalizedRecordCandidate.from_entity(
            entity=bar,
            source="licensed-market-data",
            source_tier="TIER2",
            source_snapshot_id="market-20260828-close",
            revision_id="rev-1",
            effective_at="2026-08-28T15:00:00+08:00",
            available_at="2026-08-28T15:00:05+08:00",
            ingested_at="2026-08-28T15:01:00+08:00",
            strategy_visibility=("long", "short_mid"),
            permitted_use="INTERNAL_PRODUCTION_ALLOWED",
            exchange="SSE",
        )

    def test_candidate_entity_type_and_record_id_are_canonical(self):
        candidate = self.make_bar_candidate()
        self.assertEqual(candidate.metadata.entity_type, "DAILY_BAR")
        self.assertEqual(
            candidate.metadata.record_id,
            "DAILY_BAR:601600:2026-08-28",
        )
        self.assertEqual(candidate.payload["price_basis"], "UNADJUSTED")

    def test_ingested_entity_can_be_recovered_by_snapshot(self):
        with tempfile.TemporaryDirectory() as tmp:
            store = PITStore(tmp)
            result = ingest_candidates(
                store,
                [self.make_bar_candidate()],
                adapter_id="TEST_MARKET_ADAPTER",
            )
            self.assertEqual(result.received, 1)

            snapshot = store.create_snapshot(
                strategy_id=SHORT_MID_STRATEGY_ID,
                sleeve="short_mid",
                as_of="2026-08-28T15:02:00+08:00",
                intended_use="INTERNAL_PRODUCTION",
                entity_types=["DAILY_BAR"],
                security_ids=["601600"],
            )
            records = store.materialize_snapshot(snapshot["snapshot_id"])
            self.assertEqual(len(records), 1)
            self.assertEqual(records[0].payload["close"], 9.82)


if __name__ == "__main__":
    unittest.main()
