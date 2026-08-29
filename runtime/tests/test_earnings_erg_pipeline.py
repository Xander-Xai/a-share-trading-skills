from __future__ import annotations

import hashlib
import json
import tempfile
import unittest

from src.core.pit_store import PITStore
from src.data.adapters import NormalizedRecordCandidate
from src.data.entities import CompanyGuidance, FinancialStatement
from src.data.ingest import ingest_candidates
from src.features.earnings_erg_pipeline import (
    EarningsERGAssemblyContract,
    EarningsERGEndToEndPipeline,
    event_reaction_measurement_from_dict,
)
from src.features.erg_earnings_materiality import EarningsMaterialityContract
from src.features.erg_expectation_surprise import ExpectationSurpriseContract


SECURITY = "601600"
METRIC = "ATTRIBUTABLE_NET_PROFIT"
INFO = "2026-08-28T16:23:00+08:00"
FIRST_TRADABLE = "2026-08-31T09:30:00+08:00"
AS_OF = "2026-08-31T18:00:00+08:00"
EVENT_ID = "earnings-601600-2026h1"


def canonical_hash(payload):
    text = json.dumps(
        payload,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
        allow_nan=False,
    )
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


class EarningsERGEndToEndTests(unittest.TestCase):
    def candidate(self, entity, *, available_at, revision_id, source_tier="TIER1"):
        return NormalizedRecordCandidate.from_entity(
            entity=entity,
            source="e2e-fixture",
            source_tier=source_tier,
            source_snapshot_id=("a" if source_tier == "TIER1" else "b") * 64,
            revision_id=revision_id,
            available_at=available_at,
            ingested_at=available_at,
            strategy_visibility=("short_mid",),
            permitted_use="RESEARCH_ONLY",
            is_current_revision=True,
        )

    def build_snapshot(self):
        guidance = CompanyGuidance(
            security_id=SECURITY,
            guidance_id="guidance-2026-h1",
            fiscal_period="2026-H1",
            metric=METRIC,
            lower=95.0,
            upper=105.0,
            unit="CNY_MILLION",
        )
        current = FinancialStatement(
            security_id=SECURITY,
            period_end="2026-06-30",
            report_type="H1",
            statement_scope="CONSOLIDATED",
            metrics={METRIC: 110.0},
            currency="CNY",
            unit_scale=1_000_000.0,
            audit_status="UNAUDITED",
        )
        comparator = FinancialStatement(
            security_id=SECURITY,
            period_end="2025-06-30",
            report_type="H1",
            statement_scope="CONSOLIDATED",
            metrics={METRIC: 80.0},
            currency="CNY",
            unit_scale=1_000_000.0,
            audit_status="AUDITED",
        )
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        store = PITStore(tmp.name)
        ingest_candidates(
            store,
            [
                self.candidate(
                    guidance,
                    available_at="2026-08-20T10:00:00+08:00",
                    revision_id="g1",
                ),
                self.candidate(
                    comparator,
                    available_at="2025-08-29T16:00:00+08:00",
                    revision_id="c1",
                ),
                self.candidate(
                    current,
                    available_at="2026-08-28T16:24:00+08:00",
                    revision_id="a1",
                ),
            ],
        )
        snapshot = store.create_snapshot(
            strategy_id="a_share_short_mid",
            sleeve="short_mid",
            as_of=AS_OF,
            intended_use="RESEARCH",
            entity_types=["GUIDANCE", "FINANCIAL_STATEMENT"],
            security_ids=[SECURITY],
        )
        records = tuple(store.materialize_snapshot(snapshot["snapshot_id"]))
        return snapshot, records, guidance, current, comparator

    def measurement_payload(self, *, reaction_end="2026-08-31", primary=1):
        payload = {
            "schema_version": "1.0",
            "measurement_basis": "DAILY_CLOSE_TO_CLOSE_FIRST_FULL_SESSION_V1",
            "strategy_id": "a_share_short_mid",
            "sleeve": "short_mid",
            "event_id": EVENT_ID,
            "event_family": "EARNINGS",
            "security_id": SECURITY,
            "information_timestamp": INFO,
            "first_tradable_timestamp": FIRST_TRADABLE,
            "full_session_anchor_date": "2026-08-31",
            "partial_session_reaction_omitted": True,
            "reaction_window_contract_id": "earnings-rwc-v1",
            "primary_reaction_window_sessions": primary,
            "primary_window_status": "FROZEN_BY_CONTRACT" if primary is not None else "UNRESOLVED_RESEARCH",
            "relative_performance_id": "relative-performance-fixture",
            "benchmark_id": "000300.SH",
            "benchmark_selection_contract_id": "bmk-primary-v1",
            "prepricing_metrics": [
                {
                    "window_kind": "PREPRICING",
                    "sessions": 20,
                    "start_date": "2026-07-31",
                    "end_date": "2026-08-28",
                    "stock_return": 0.08,
                    "benchmark_return": 0.03,
                    "excess_return": 0.05,
                    "cumulative_abnormal_return": 0.049,
                }
            ],
            "reaction_metrics": [
                {
                    "window_kind": "REACTION",
                    "sessions": 1,
                    "start_date": "2026-08-28",
                    "end_date": reaction_end,
                    "stock_return": 0.04,
                    "benchmark_return": 0.01,
                    "excess_return": 0.03,
                    "cumulative_abnormal_return": 0.03,
                }
            ],
        }
        identity = dict(payload)
        payload["event_measurement_id"] = canonical_hash(identity)
        return payload

    def contracts(self, guidance, current, comparator, measurement, *, materiality_mode="THRESHOLD_RULE_V1"):
        expectation = ExpectationSurpriseContract.build(
            baseline_type="COMPANY_GUIDANCE",
            expectation_record_id=guidance.record_id(),
            actual_record_id=current.record_id(),
            security_id=SECURITY,
            fiscal_period="2026-H1",
            actual_period_end="2026-06-30",
            metric=METRIC,
            confidence="HIGH",
            surprise_method="RANGE_BREAK",
            metric_polarity="HIGHER_IS_POSITIVE",
        )
        materiality_kwargs = dict(
            current_record_id=current.record_id(),
            comparator_record_id=comparator.record_id(),
            security_id=SECURITY,
            current_period_end="2026-06-30",
            comparator_period_end="2025-06-30",
            statement_scope="CONSOLIDATED",
            report_type="H1",
            primary_metric=METRIC,
            transmission_path="reported earnings -> normalized profit expectation -> valuation input",
            rule_mode=materiality_mode,
        )
        if materiality_mode == "THRESHOLD_RULE_V1":
            materiality_kwargs["min_primary_change_abs_pct"] = 0.20
        materiality = EarningsMaterialityContract.build(**materiality_kwargs)
        assembly = EarningsERGAssemblyContract.build(
            event_id=EVENT_ID,
            security_id=SECURITY,
            information_timestamp=INFO,
            first_tradable_timestamp=FIRST_TRADABLE,
            expectation_surprise_contract_id=expectation.contract_id,
            earnings_materiality_contract_id=materiality.contract_id,
            event_measurement_id=measurement.event_measurement_id,
            eligibility_status="PASS",
            prepricing_state="PARTIALLY_PRICED",
            prepricing_window_sessions=20,
            prepricing_classification_contract_id="prepricing-classifier-frozen-v1",
            reaction_state="POSITIVE_CONFIRMATION",
            reaction_classification_contract_id="reaction-classifier-frozen-v1",
        )
        return expectation, materiality, assembly

    def build_run(self, *, materiality_mode="THRESHOLD_RULE_V1"):
        snapshot, records, guidance, current, comparator = self.build_snapshot()
        measurement = event_reaction_measurement_from_dict(self.measurement_payload())
        expectation, materiality, assembly = self.contracts(
            guidance,
            current,
            comparator,
            measurement,
            materiality_mode=materiality_mode,
        )
        artifacts = EarningsERGEndToEndPipeline().run(
            records,
            data_snapshot_id=snapshot["snapshot_id"],
            as_of=AS_OF,
            expectation_contract=expectation,
            materiality_contract=materiality,
            event_measurement=measurement,
            assembly_contract=assembly,
        )
        return artifacts

    def test_positive_earnings_path_reaches_shadow_confirmed(self):
        artifacts = self.build_run()
        self.assertEqual(artifacts.expectation_surprise.surprise.direction, "POSITIVE")
        self.assertTrue(artifacts.expectation_surprise.surprise.verified)
        self.assertEqual(artifacts.earnings_materiality.materiality.state, "MATERIAL")
        self.assertEqual(artifacts.run.evidence_bundle.prepricing.state, "PARTIALLY_PRICED")
        self.assertEqual(artifacts.run.evidence_bundle.reaction.state, "POSITIVE_CONFIRMATION")
        self.assertEqual(artifacts.run.shadow_decision.research_state, "CONFIRMED")
        self.assertEqual(artifacts.run.shadow_decision.position_state, "FLAT")
        self.assertFalse(artifacts.run.shadow_decision.executable)

    def test_evidence_only_materiality_keeps_pipeline_watch(self):
        artifacts = self.build_run(materiality_mode="EVIDENCE_ONLY")
        self.assertEqual(artifacts.earnings_materiality.materiality.state, "UNRESOLVED")
        self.assertEqual(artifacts.run.shadow_decision.research_state, "WATCH")
        self.assertEqual(artifacts.run.shadow_decision.reason_code, "MATERIALITY_UNRESOLVED")

    def test_run_and_artifact_identity_are_deterministic(self):
        first = self.build_run()
        second = self.build_run()
        self.assertEqual(first.run.run_id, second.run.run_id)
        self.assertEqual(first.to_dict()["artifact_id"], second.to_dict()["artifact_id"])

    def test_future_reaction_data_is_rejected(self):
        snapshot, records, guidance, current, comparator = self.build_snapshot()
        measurement = event_reaction_measurement_from_dict(
            self.measurement_payload(reaction_end="2026-09-01")
        )
        expectation, materiality, assembly = self.contracts(
            guidance, current, comparator, measurement
        )
        with self.assertRaisesRegex(ValueError, "post-as_of reaction data"):
            EarningsERGEndToEndPipeline().run(
                records,
                data_snapshot_id=snapshot["snapshot_id"],
                as_of=AS_OF,
                expectation_contract=expectation,
                materiality_contract=materiality,
                event_measurement=measurement,
                assembly_contract=assembly,
            )

    def test_resolved_reaction_requires_frozen_primary_window(self):
        snapshot, records, guidance, current, comparator = self.build_snapshot()
        measurement = event_reaction_measurement_from_dict(
            self.measurement_payload(primary=None)
        )
        expectation, materiality, _ = self.contracts(
            guidance, current, comparator, measurement
        )
        assembly = EarningsERGAssemblyContract.build(
            event_id=EVENT_ID,
            security_id=SECURITY,
            information_timestamp=INFO,
            first_tradable_timestamp=FIRST_TRADABLE,
            expectation_surprise_contract_id=expectation.contract_id,
            earnings_materiality_contract_id=materiality.contract_id,
            event_measurement_id=measurement.event_measurement_id,
            eligibility_status="PASS",
            prepricing_state="PARTIALLY_PRICED",
            prepricing_window_sessions=20,
            prepricing_classification_contract_id="prepricing-classifier-frozen-v1",
            reaction_state="POSITIVE_CONFIRMATION",
            reaction_classification_contract_id="reaction-classifier-frozen-v1",
        )
        with self.assertRaisesRegex(ValueError, "primary reaction window"):
            EarningsERGEndToEndPipeline().run(
                records,
                data_snapshot_id=snapshot["snapshot_id"],
                as_of=AS_OF,
                expectation_contract=expectation,
                materiality_contract=materiality,
                event_measurement=measurement,
                assembly_contract=assembly,
            )

    def test_surprise_and_materiality_must_use_same_current_statement(self):
        snapshot, records, guidance, current, comparator = self.build_snapshot()
        measurement = event_reaction_measurement_from_dict(self.measurement_payload())
        expectation, materiality, _ = self.contracts(
            guidance, current, comparator, measurement
        )
        wrong_materiality = EarningsMaterialityContract.build(
            current_record_id=comparator.record_id(),
            comparator_record_id=current.record_id(),
            security_id=SECURITY,
            current_period_end="2025-06-30",
            comparator_period_end="2026-06-30",
            statement_scope="CONSOLIDATED",
            report_type="H1",
            primary_metric=METRIC,
            transmission_path="wrong comparator test",
            rule_mode="THRESHOLD_RULE_V1",
            min_primary_change_abs_pct=0.20,
        )
        assembly = EarningsERGAssemblyContract.build(
            event_id=EVENT_ID,
            security_id=SECURITY,
            information_timestamp=INFO,
            first_tradable_timestamp=FIRST_TRADABLE,
            expectation_surprise_contract_id=expectation.contract_id,
            earnings_materiality_contract_id=wrong_materiality.contract_id,
            event_measurement_id=measurement.event_measurement_id,
            eligibility_status="PASS",
        )
        with self.assertRaisesRegex(ValueError, "same PIT record"):
            EarningsERGEndToEndPipeline().run(
                records,
                data_snapshot_id=snapshot["snapshot_id"],
                as_of=AS_OF,
                expectation_contract=expectation,
                materiality_contract=wrong_materiality,
                event_measurement=measurement,
                assembly_contract=assembly,
            )

    def test_hard_gate_failure_rejects_but_never_executes(self):
        snapshot, records, guidance, current, comparator = self.build_snapshot()
        measurement = event_reaction_measurement_from_dict(self.measurement_payload())
        expectation, materiality, _ = self.contracts(
            guidance, current, comparator, measurement
        )
        assembly = EarningsERGAssemblyContract.build(
            event_id=EVENT_ID,
            security_id=SECURITY,
            information_timestamp=INFO,
            first_tradable_timestamp=FIRST_TRADABLE,
            expectation_surprise_contract_id=expectation.contract_id,
            earnings_materiality_contract_id=materiality.contract_id,
            event_measurement_id=measurement.event_measurement_id,
            eligibility_status="FAIL",
            eligibility_reasons=("execution availability unresolved",),
            prepricing_state="PARTIALLY_PRICED",
            prepricing_window_sessions=20,
            prepricing_classification_contract_id="prepricing-classifier-frozen-v1",
            reaction_state="POSITIVE_CONFIRMATION",
            reaction_classification_contract_id="reaction-classifier-frozen-v1",
        )
        artifacts = EarningsERGEndToEndPipeline().run(
            records,
            data_snapshot_id=snapshot["snapshot_id"],
            as_of=AS_OF,
            expectation_contract=expectation,
            materiality_contract=materiality,
            event_measurement=measurement,
            assembly_contract=assembly,
        )
        self.assertEqual(artifacts.run.shadow_decision.research_state, "REJECT")
        self.assertFalse(artifacts.run.shadow_decision.executable)

    def test_long_sleeve_is_rejected(self):
        snapshot, records, guidance, current, comparator = self.build_snapshot()
        measurement = event_reaction_measurement_from_dict(self.measurement_payload())
        expectation, materiality, assembly = self.contracts(
            guidance, current, comparator, measurement
        )
        with self.assertRaises(ValueError):
            EarningsERGEndToEndPipeline().run(
                records,
                data_snapshot_id=snapshot["snapshot_id"],
                as_of=AS_OF,
                expectation_contract=expectation,
                materiality_contract=materiality,
                event_measurement=measurement,
                assembly_contract=assembly,
                strategy_id="a_share_long_retirement",
                sleeve="long",
            )

    def test_event_measurement_tampering_is_rejected(self):
        payload = self.measurement_payload()
        payload["benchmark_id"] = "000905.SH"
        with self.assertRaisesRegex(ValueError, "event_measurement_id"):
            event_reaction_measurement_from_dict(payload)


if __name__ == "__main__":
    unittest.main()
