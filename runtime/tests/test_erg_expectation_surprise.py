from __future__ import annotations

import tempfile
import unittest

from src.core.pit_store import PITStore
from src.data.adapters import NormalizedRecordCandidate
from src.data.entities import CompanyGuidance, ConsensusExpectation, FinancialStatement
from src.data.ingest import ingest_candidates
from src.features.erg_expectation_surprise import (
    ExpectationSurpriseContract,
    PITExpectationSurpriseAdapter,
)


AS_OF = "2026-08-28T18:00:00+08:00"
INFO = "2026-08-28T16:23:00+08:00"
EXPECTATION_AVAILABLE = "2026-08-20T10:00:00+08:00"
ACTUAL_AVAILABLE = "2026-08-28T16:24:00+08:00"
SECURITY = "601600"
METRIC = "ATTRIBUTABLE_NET_PROFIT"
PERIOD = "2026-H1"
PERIOD_END = "2026-06-30"


class ERGExpectationSurpriseTests(unittest.TestCase):
    def candidate(
        self,
        entity,
        *,
        source_tier="TIER1",
        revision_id="rev-1",
        available_at=EXPECTATION_AVAILABLE,
    ):
        return NormalizedRecordCandidate.from_entity(
            entity=entity,
            source="erg-fixture",
            source_tier=source_tier,
            source_snapshot_id=("a" if source_tier == "TIER1" else "b") * 64,
            revision_id=revision_id,
            available_at=available_at,
            ingested_at=available_at,
            strategy_visibility=("short_mid",),
            permitted_use="RESEARCH_ONLY",
            is_current_revision=True,
        )

    def guidance(self, *, low=95.0, high=105.0, point=None, unit="CNY_MILLION"):
        return CompanyGuidance(
            security_id=SECURITY,
            guidance_id="guidance-2026-h1",
            fiscal_period=PERIOD,
            metric=METRIC,
            lower=low,
            upper=high,
            point_estimate=point,
            unit=unit,
        )

    def consensus(self, *, value=100.0, coverage_count=4, dispersion=6.0):
        return ConsensusExpectation(
            security_id=SECURITY,
            fiscal_period=PERIOD,
            metric=METRIC,
            value=value,
            unit="CNY_MILLION",
            baseline_type="SELL_SIDE_CONSENSUS",
            coverage_count=coverage_count,
            dispersion=dispersion,
        )

    def actual(self, value=110.0, *, metric=METRIC, currency="CNY", unit_scale=1_000_000.0):
        return FinancialStatement(
            security_id=SECURITY,
            period_end=PERIOD_END,
            report_type="H1",
            statement_scope="CONSOLIDATED",
            metrics={metric: value},
            currency=currency,
            unit_scale=unit_scale,
            audit_status="UNAUDITED",
        )

    def materialize(self, candidates):
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        store = PITStore(tmp.name)
        ingest_candidates(store, candidates)
        snapshot = store.create_snapshot(
            strategy_id="a_share_short_mid",
            sleeve="short_mid",
            as_of=AS_OF,
            intended_use="RESEARCH",
            entity_types=["GUIDANCE", "CONSENSUS_EXPECTATION", "FINANCIAL_STATEMENT"],
            security_ids=[SECURITY],
        )
        return tuple(store.materialize_snapshot(snapshot["snapshot_id"]))

    def contract(
        self,
        expectation_record_id,
        actual_record_id,
        *,
        baseline_type="COMPANY_GUIDANCE",
        confidence="HIGH",
        surprise_method="RANGE_BREAK",
        polarity="HIGHER_IS_POSITIVE",
        tolerance=0.0,
    ):
        return ExpectationSurpriseContract.build(
            baseline_type=baseline_type,
            expectation_record_id=expectation_record_id,
            actual_record_id=actual_record_id,
            security_id=SECURITY,
            fiscal_period=PERIOD,
            actual_period_end=PERIOD_END,
            metric=METRIC,
            confidence=confidence,
            surprise_method=surprise_method,
            metric_polarity=polarity,
            neutral_tolerance_abs=tolerance,
        )

    def build_guidance(self, actual_value, *, confidence="HIGH", tolerance=0.0, guidance=None):
        guidance = guidance or self.guidance()
        actual = self.actual(actual_value)
        records = self.materialize(
            [
                self.candidate(guidance),
                self.candidate(actual, revision_id="actual-1", available_at=ACTUAL_AVAILABLE),
            ]
        )
        contract = self.contract(
            guidance.record_id(),
            actual.record_id(),
            confidence=confidence,
            tolerance=tolerance,
        )
        return PITExpectationSurpriseAdapter().build(
            records,
            contract=contract,
            as_of=AS_OF,
            information_timestamp=INFO,
        )

    def test_guidance_range_inside_is_verified_neutral(self):
        result = self.build_guidance(100.0)
        self.assertEqual(result.expectation.low, 95_000_000.0)
        self.assertEqual(result.expectation.high, 105_000_000.0)
        self.assertEqual(result.expectation.center, 100_000_000.0)
        self.assertTrue(result.surprise.verified)
        self.assertEqual(result.surprise.direction, "NEUTRAL")

    def test_guidance_range_break_above_is_positive(self):
        result = self.build_guidance(110.0)
        self.assertTrue(result.surprise.verified)
        self.assertEqual(result.surprise.direction, "POSITIVE")
        self.assertAlmostEqual(result.surprise.delta_pct, 0.10)

    def test_guidance_range_break_below_is_negative(self):
        result = self.build_guidance(90.0)
        self.assertEqual(result.surprise.direction, "NEGATIVE")

    def test_range_tolerance_is_frozen_in_contract(self):
        result = self.build_guidance(106.0, tolerance=2_000_000.0)
        self.assertEqual(result.surprise.direction, "NEUTRAL")

    def test_low_confidence_baseline_cannot_verify_surprise(self):
        result = self.build_guidance(110.0, confidence="LOW")
        self.assertFalse(result.surprise.verified)
        self.assertEqual(result.surprise.direction, "UNRESOLVED")
        self.assertAlmostEqual(result.surprise.delta_pct, 0.10)

    def test_point_guidance_can_use_point_delta(self):
        guidance = self.guidance(low=None, high=None, point=100.0)
        actual = self.actual(110.0)
        records = self.materialize(
            [
                self.candidate(guidance),
                self.candidate(actual, revision_id="actual-1", available_at=ACTUAL_AVAILABLE),
            ]
        )
        contract = self.contract(
            guidance.record_id(),
            actual.record_id(),
            surprise_method="POINT_DELTA",
        )
        result = PITExpectationSurpriseAdapter().build(
            records,
            contract=contract,
            as_of=AS_OF,
            information_timestamp=INFO,
        )
        self.assertEqual(result.surprise.direction, "POSITIVE")

    def test_one_sided_range_break_remains_unresolved(self):
        guidance = self.guidance(low=95.0, high=None, point=None)
        actual = self.actual(110.0)
        records = self.materialize(
            [
                self.candidate(guidance),
                self.candidate(actual, revision_id="actual-1", available_at=ACTUAL_AVAILABLE),
            ]
        )
        contract = self.contract(guidance.record_id(), actual.record_id())
        result = PITExpectationSurpriseAdapter().build(
            records,
            contract=contract,
            as_of=AS_OF,
            information_timestamp=INFO,
        )
        self.assertFalse(result.surprise.verified)
        self.assertEqual(result.surprise.direction, "UNRESOLVED")

    def test_consensus_point_delta_is_source_backed(self):
        consensus = self.consensus(value=100.0, coverage_count=4)
        actual = self.actual(110.0)
        records = self.materialize(
            [
                self.candidate(consensus, source_tier="TIER2"),
                self.candidate(actual, revision_id="actual-1", available_at=ACTUAL_AVAILABLE),
            ]
        )
        contract = self.contract(
            consensus.record_id(),
            actual.record_id(),
            baseline_type="CONSENSUS_RECENT",
            confidence="MEDIUM",
            surprise_method="POINT_DELTA",
        )
        result = PITExpectationSurpriseAdapter().build(
            records,
            contract=contract,
            as_of=AS_OF,
            information_timestamp=INFO,
        )
        self.assertEqual(result.expectation.coverage_count, 4)
        self.assertEqual(result.expectation.dispersion, 6_000_000.0)
        self.assertTrue(result.surprise.verified)
        self.assertEqual(result.surprise.direction, "POSITIVE")
        refs = result.surprise.evidence_refs
        self.assertEqual(len(refs), 2)
        self.assertIn("CONSENSUS_EXPECTATION", refs[0].ref)
        self.assertIn("FINANCIAL_STATEMENT", refs[1].ref)

    def test_single_analyst_consensus_fails_closed(self):
        consensus = self.consensus(coverage_count=1)
        actual = self.actual(110.0)
        records = self.materialize(
            [
                self.candidate(consensus, source_tier="TIER2"),
                self.candidate(actual, revision_id="actual-1", available_at=ACTUAL_AVAILABLE),
            ]
        )
        contract = self.contract(
            consensus.record_id(),
            actual.record_id(),
            baseline_type="CONSENSUS_RECENT",
            confidence="MEDIUM",
            surprise_method="POINT_DELTA",
        )
        with self.assertRaisesRegex(ValueError, "coverage_count >= 2"):
            PITExpectationSurpriseAdapter().build(
                records,
                contract=contract,
                as_of=AS_OF,
                information_timestamp=INFO,
            )

    def test_consensus_range_break_contract_is_rejected(self):
        consensus = self.consensus()
        actual = self.actual()
        with self.assertRaisesRegex(ValueError, "requires POINT_DELTA"):
            self.contract(
                consensus.record_id(),
                actual.record_id(),
                baseline_type="CONSENSUS_RECENT",
                surprise_method="RANGE_BREAK",
            )

    def test_expectation_must_be_visible_strictly_before_event(self):
        guidance = self.guidance()
        actual = self.actual()
        records = self.materialize(
            [
                self.candidate(guidance, available_at=INFO),
                self.candidate(actual, revision_id="actual-1", available_at=ACTUAL_AVAILABLE),
            ]
        )
        contract = self.contract(guidance.record_id(), actual.record_id())
        with self.assertRaisesRegex(ValueError, "strictly before information_timestamp"):
            PITExpectationSurpriseAdapter().build(
                records,
                contract=contract,
                as_of=AS_OF,
                information_timestamp=INFO,
            )

    def test_actual_clock_inconsistency_fails_closed(self):
        guidance = self.guidance()
        actual = self.actual()
        records = self.materialize(
            [
                self.candidate(guidance),
                self.candidate(
                    actual,
                    revision_id="actual-1",
                    available_at="2026-08-28T16:00:00+08:00",
                ),
            ]
        )
        contract = self.contract(guidance.record_id(), actual.record_id())
        with self.assertRaisesRegex(ValueError, "event clock is inconsistent"):
            PITExpectationSurpriseAdapter().build(
                records,
                contract=contract,
                as_of=AS_OF,
                information_timestamp=INFO,
            )

    def test_missing_actual_metric_fails_closed(self):
        guidance = self.guidance()
        actual = self.actual(110.0, metric="REVENUE")
        records = self.materialize(
            [
                self.candidate(guidance),
                self.candidate(actual, revision_id="actual-1", available_at=ACTUAL_AVAILABLE),
            ]
        )
        contract = self.contract(guidance.record_id(), actual.record_id())
        with self.assertRaisesRegex(ValueError, "missing metric"):
            PITExpectationSurpriseAdapter().build(
                records,
                contract=contract,
                as_of=AS_OF,
                information_timestamp=INFO,
            )

    def test_lower_is_positive_inverts_direction(self):
        guidance = self.guidance(low=None, high=None, point=100.0)
        actual = self.actual(90.0)
        records = self.materialize(
            [
                self.candidate(guidance),
                self.candidate(actual, revision_id="actual-1", available_at=ACTUAL_AVAILABLE),
            ]
        )
        contract = self.contract(
            guidance.record_id(),
            actual.record_id(),
            surprise_method="POINT_DELTA",
            polarity="LOWER_IS_POSITIVE",
        )
        result = PITExpectationSurpriseAdapter().build(
            records,
            contract=contract,
            as_of=AS_OF,
            information_timestamp=INFO,
        )
        self.assertEqual(result.surprise.direction, "POSITIVE")

    def test_exact_record_selection_prevents_source_substitution(self):
        guidance_a = self.guidance(low=95.0, high=105.0)
        guidance_b = CompanyGuidance(
            security_id=SECURITY,
            guidance_id="other-guidance",
            fiscal_period=PERIOD,
            metric=METRIC,
            lower=80.0,
            upper=90.0,
            unit="CNY_MILLION",
        )
        actual = self.actual(100.0)
        records = self.materialize(
            [
                self.candidate(guidance_a),
                self.candidate(guidance_b, revision_id="other"),
                self.candidate(actual, revision_id="actual-1", available_at=ACTUAL_AVAILABLE),
            ]
        )
        contract = self.contract(guidance_a.record_id(), actual.record_id())
        result = PITExpectationSurpriseAdapter().build(
            records,
            contract=contract,
            as_of=AS_OF,
            information_timestamp=INFO,
        )
        self.assertEqual(result.expectation.low, 95_000_000.0)
        self.assertEqual(result.surprise.direction, "NEUTRAL")

    def test_result_identity_is_deterministic(self):
        first = self.build_guidance(110.0)
        second = self.build_guidance(110.0)
        self.assertEqual(first.result_id, second.result_id)
        self.assertEqual(first.to_dict(), second.to_dict())

    def test_contract_identity_changes_with_tolerance(self):
        guidance = self.guidance()
        actual = self.actual()
        first = self.contract(guidance.record_id(), actual.record_id(), tolerance=0.0)
        second = self.contract(guidance.record_id(), actual.record_id(), tolerance=1.0)
        self.assertNotEqual(first.contract_id, second.contract_id)

    def test_long_sleeve_is_rejected(self):
        guidance = self.guidance()
        actual = self.actual()
        records = self.materialize(
            [
                self.candidate(guidance),
                self.candidate(actual, revision_id="actual-1", available_at=ACTUAL_AVAILABLE),
            ]
        )
        contract = self.contract(guidance.record_id(), actual.record_id())
        with self.assertRaisesRegex(ValueError, "strategy context mismatch"):
            PITExpectationSurpriseAdapter().build(
                records,
                contract=contract,
                as_of=AS_OF,
                information_timestamp=INFO,
                strategy_id="a_share_long_retirement",
                sleeve="long",
            )

    def test_unsupported_unit_fails_closed(self):
        guidance = self.guidance(unit="CNY_PER_SHARE")
        actual = self.actual()
        records = self.materialize(
            [
                self.candidate(guidance),
                self.candidate(actual, revision_id="actual-1", available_at=ACTUAL_AVAILABLE),
            ]
        )
        contract = self.contract(guidance.record_id(), actual.record_id())
        with self.assertRaisesRegex(ValueError, "unsupported expectation unit"):
            PITExpectationSurpriseAdapter().build(
                records,
                contract=contract,
                as_of=AS_OF,
                information_timestamp=INFO,
            )


if __name__ == "__main__":
    unittest.main()
