from __future__ import annotations

import unittest

from src.features.erg_shadow import (
    ERGEvidenceBundle,
    ERGShadowStateMachine,
    EligibilityEvidence,
    EvidenceRef,
    ExpectationEvidence,
    MaterialityEvidence,
    PrepricingEvidence,
    ReactionEvidence,
    SurpriseEvidence,
)


AS_OF = "2026-08-29T01:30:00+08:00"
INFO = "2026-08-28T16:23:00+08:00"
TRADABLE = "2026-08-31T09:30:00+08:00"
EVENT_MEASUREMENT = "event-measurement-001"
SOURCE = EvidenceRef(
    ref="DISCLOSURE:601600:2026-H1",
    source_tier="TIER1",
    source_snapshot_id="a" * 64,
)


class ERGShadowTests(unittest.TestCase):
    def expectation(self, **overrides):
        values = dict(
            baseline_type="COMPANY_GUIDANCE",
            confidence="HIGH",
            center=100.0,
            low=95.0,
            high=105.0,
            coverage_flag=True,
            fiscal_period="2026-H1",
            metric="ATTRIBUTABLE_NET_PROFIT",
            unit="CNY_MILLION",
            evidence_refs=(SOURCE,),
        )
        values.update(overrides)
        return ExpectationEvidence(**values)

    def surprise(self, direction="POSITIVE", verified=True, **overrides):
        values = dict(
            direction=direction,
            verified=verified,
            metric="ATTRIBUTABLE_NET_PROFIT",
            actual=110.0,
            expected_center=100.0,
            delta=10.0,
            delta_pct=0.10,
            calculation_method="ACTUAL_MINUS_EXPECTED_V1",
            classification_contract_id="surprise-contract-v1",
            evidence_refs=(SOURCE,),
        )
        values.update(overrides)
        return SurpriseEvidence(**values)

    def materiality(self, state="MATERIAL", **overrides):
        values = dict(
            state=state,
            transmission_path="reported profit -> normalized earnings power -> valuation expectation",
            assessment_contract_id="materiality-contract-v1",
            impact_metrics={"profit_delta_pct": 0.10},
            evidence_refs=(SOURCE,),
        )
        values.update(overrides)
        if state == "UNRESOLVED":
            values.setdefault("transmission_path", None)
            values.setdefault("assessment_contract_id", None)
            values.setdefault("impact_metrics", None)
            values.setdefault("evidence_refs", ())
        return MaterialityEvidence(**values)

    def prepricing(self, state="PARTIALLY_PRICED", **overrides):
        values = dict(
            state=state,
            event_measurement_id=EVENT_MEASUREMENT,
            classification_contract_id="prepricing-contract-v1",
            metrics={"pre_event_car_5": 0.02, "pre_event_car_20": 0.06},
        )
        values.update(overrides)
        if state == "UNRESOLVED":
            values.setdefault("event_measurement_id", None)
            values.setdefault("classification_contract_id", None)
        return PrepricingEvidence(**values)

    def reaction(self, state="POSITIVE_CONFIRMATION", **overrides):
        values = dict(
            state=state,
            event_measurement_id=EVENT_MEASUREMENT,
            classification_contract_id="reaction-classification-v1",
            primary_reaction_window_sessions=1,
            benchmark_id="CSI300",
            benchmark_selection_contract_id="benchmark-contract-v1",
            metrics={"abnormal_return_primary": 0.015},
        )
        values.update(overrides)
        if state == "UNRESOLVED":
            values.setdefault("event_measurement_id", None)
            values.setdefault("classification_contract_id", None)
            values.setdefault("primary_reaction_window_sessions", None)
        return ReactionEvidence(**values)

    def bundle(self, **overrides):
        values = dict(
            event_id="601600-2026-H1",
            event_family="EARNINGS",
            security_id="601600",
            as_of=AS_OF,
            information_timestamp=INFO,
            first_tradable_timestamp=TRADABLE,
            primary_source_tier="TIER1",
            eligibility=EligibilityEvidence(status="PASS"),
            expectation=self.expectation(),
            surprise=self.surprise(),
            materiality=self.materiality(),
            prepricing=self.prepricing(),
            reaction=self.reaction(),
        )
        values.update(overrides)
        return ERGEvidenceBundle.build(**values)

    def test_positive_verified_surprise_and_positive_reaction_confirms(self):
        bundle = self.bundle()
        decision = ERGShadowStateMachine().evaluate(bundle)
        self.assertEqual(decision.research_state, "CONFIRMED")
        self.assertEqual(decision.confirmation_basis, "EVENT_REACTION")
        self.assertEqual(decision.position_state, "FLAT")
        self.assertFalse(decision.executable)

    def test_decision_identity_is_deterministic(self):
        bundle = self.bundle()
        first = ERGShadowStateMachine().evaluate(bundle)
        second = ERGShadowStateMachine().evaluate(bundle)
        self.assertEqual(first.decision_id, second.decision_id)
        self.assertEqual(first.to_dict(), second.to_dict())

    def test_hard_gate_failure_rejects(self):
        bundle = self.bundle(
            eligibility=EligibilityEvidence(
                status="FAIL",
                reasons=("UNRESOLVED_PIT_CONFLICT",),
            )
        )
        decision = ERGShadowStateMachine().evaluate(bundle)
        self.assertEqual(decision.research_state, "REJECT")
        self.assertEqual(decision.reason_code, "HARD_GATE_NOT_PASS")

    def test_unresolved_hard_gate_also_fails_closed(self):
        bundle = self.bundle(
            eligibility=EligibilityEvidence(
                status="UNRESOLVED",
                reasons=("BROKER_EXECUTION_STATE_UNKNOWN",),
            )
        )
        decision = ERGShadowStateMachine().evaluate(bundle)
        self.assertEqual(decision.research_state, "REJECT")

    def test_low_materiality_remains_watch(self):
        bundle = self.bundle(materiality=self.materiality(state="LOW_MATERIALITY"))
        decision = ERGShadowStateMachine().evaluate(bundle)
        self.assertEqual(decision.research_state, "WATCH")
        self.assertEqual(decision.reason_code, "LOW_MATERIALITY")

    def test_unresolved_materiality_remains_watch(self):
        materiality = MaterialityEvidence(state="UNRESOLVED")
        bundle = self.bundle(materiality=materiality)
        decision = ERGShadowStateMachine().evaluate(bundle)
        self.assertEqual(decision.research_state, "WATCH")
        self.assertEqual(decision.reason_code, "MATERIALITY_UNRESOLVED")

    def test_unverified_surprise_cannot_confirm(self):
        bundle = self.bundle(surprise=self.surprise(verified=False))
        decision = ERGShadowStateMachine().evaluate(bundle)
        self.assertEqual(decision.research_state, "CANDIDATE")
        self.assertEqual(decision.reason_code, "SURPRISE_NOT_VERIFIED")
        self.assertIsNone(decision.confirmation_basis)

    def test_low_confidence_expectation_cannot_back_verified_surprise(self):
        with self.assertRaisesRegex(ValueError, "verified surprise requires"):
            self.bundle(
                expectation=self.expectation(confidence="LOW"),
                surprise=self.surprise(verified=True),
            )

    def test_single_analyst_cannot_be_consensus_recent(self):
        expectation = self.expectation(
            baseline_type="CONSENSUS_RECENT",
            confidence="HIGH",
            coverage_count=1,
        )
        with self.assertRaisesRegex(ValueError, "single analyst"):
            expectation.validate()

    def test_consensus_requires_coverage_for_verified_surprise(self):
        with self.assertRaisesRegex(ValueError, "verified surprise requires"):
            self.bundle(
                expectation=self.expectation(
                    baseline_type="CONSENSUS_RECENT",
                    confidence="HIGH",
                    coverage_count=None,
                ),
                surprise=self.surprise(verified=True),
            )

    def test_unresolved_prepricing_blocks_confirmation(self):
        bundle = self.bundle(prepricing=PrepricingEvidence(state="UNRESOLVED"))
        decision = ERGShadowStateMachine().evaluate(bundle)
        self.assertEqual(decision.research_state, "CANDIDATE")
        self.assertEqual(decision.reason_code, "PREPRICING_UNRESOLVED")

    def test_unresolved_reaction_blocks_confirmation(self):
        bundle = self.bundle(reaction=ReactionEvidence(state="UNRESOLVED"))
        decision = ERGShadowStateMachine().evaluate(bundle)
        self.assertEqual(decision.research_state, "CANDIDATE")
        self.assertEqual(decision.reason_code, "REACTION_UNRESOLVED")

    def test_positive_surprise_negative_reaction_is_disagreement_candidate(self):
        bundle = self.bundle(reaction=self.reaction(state="NEGATIVE_DISAGREEMENT"))
        decision = ERGShadowStateMachine().evaluate(bundle)
        self.assertEqual(decision.research_state, "CANDIDATE")
        self.assertEqual(decision.reason_code, "POSITIVE_SURPRISE_NEGATIVE_REACTION")

    def test_negative_surprise_positive_reaction_requires_reunderwrite(self):
        bundle = self.bundle(
            surprise=self.surprise(direction="NEGATIVE", actual=90.0, delta=-10.0, delta_pct=-0.10),
            reaction=self.reaction(state="POSITIVE_CONFIRMATION"),
        )
        decision = ERGShadowStateMachine().evaluate(bundle)
        self.assertEqual(decision.research_state, "CANDIDATE")
        self.assertEqual(decision.reason_code, "NEGATIVE_SURPRISE_POSITIVE_REACTION")

    def test_negative_surprise_negative_reaction_invalidates(self):
        bundle = self.bundle(
            surprise=self.surprise(direction="NEGATIVE", actual=90.0, delta=-10.0, delta_pct=-0.10),
            reaction=self.reaction(state="NEGATIVE_DISAGREEMENT"),
        )
        decision = ERGShadowStateMachine().evaluate(bundle)
        self.assertEqual(decision.research_state, "INVALIDATED")
        self.assertIsNone(decision.confirmation_basis)

    def test_resolved_reaction_requires_classification_contract(self):
        with self.assertRaisesRegex(ValueError, "resolved reaction requires classification_contract_id"):
            self.reaction(classification_contract_id=None).validate()

    def test_resolved_prepricing_requires_measurement_id(self):
        with self.assertRaisesRegex(ValueError, "resolved prepricing requires event_measurement_id"):
            self.prepricing(event_measurement_id=None).validate()

    def test_prepricing_and_reaction_must_share_event_measurement(self):
        with self.assertRaisesRegex(ValueError, "same event measurement"):
            self.bundle(
                reaction=self.reaction(event_measurement_id="different-measurement"),
            )

    def test_bundle_identity_changes_when_classification_contract_changes(self):
        first = self.bundle()
        second = self.bundle(
            reaction=self.reaction(classification_contract_id="reaction-classification-v2")
        )
        self.assertNotEqual(first.evidence_bundle_id, second.evidence_bundle_id)

    def test_long_sleeve_is_rejected(self):
        with self.assertRaisesRegex(ValueError, "strategy context mismatch"):
            ERGEvidenceBundle.build(
                event_id="x",
                event_family="EARNINGS",
                security_id="601600",
                as_of=AS_OF,
                information_timestamp=INFO,
                first_tradable_timestamp=TRADABLE,
                primary_source_tier="TIER1",
                eligibility=EligibilityEvidence(status="PASS"),
                expectation=self.expectation(),
                surprise=self.surprise(),
                materiality=self.materiality(),
                prepricing=self.prepricing(),
                reaction=self.reaction(),
                strategy_id="a_share_long_retirement",
                sleeve="long",
            )

    def test_roundtrip_from_dict(self):
        first = self.bundle()
        restored = ERGEvidenceBundle.from_dict(first.to_dict())
        restored.validate()
        self.assertEqual(first.to_dict(), restored.to_dict())


if __name__ == "__main__":
    unittest.main()
