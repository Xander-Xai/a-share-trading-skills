from __future__ import annotations

import tempfile
import unittest

from src.core.pit_store import PITStore
from src.data.adapters import NormalizedRecordCandidate
from src.data.entities import FinancialStatement
from src.data.ingest import ingest_candidates
from src.features.erg_earnings_materiality import (
    EarningsMaterialityContract,
    PITEarningsMaterialityProducer,
)


AS_OF = "2026-08-28T18:00:00+08:00"
INFO = "2026-08-28T16:23:00+08:00"
CURRENT_AVAILABLE = "2026-08-28T16:24:00+08:00"
COMPARATOR_AVAILABLE = "2025-08-29T16:00:00+08:00"
SECURITY = "601600"
CURRENT_PERIOD = "2026-06-30"
COMPARATOR_PERIOD = "2025-06-30"
PRIMARY = "ATTRIBUTABLE_NET_PROFIT"
ADJUSTED = "ADJUSTED_NET_PROFIT"
REVENUE = "REVENUE"
OCF = "OPERATING_CASH_FLOW"


class ERGEarningsMaterialityTests(unittest.TestCase):
    def statement(
        self,
        *,
        period_end,
        primary,
        adjusted=None,
        revenue=None,
        ocf=None,
        report_type="H1",
        statement_scope="CONSOLIDATED",
        currency="CNY",
        unit_scale=1_000_000.0,
    ):
        metrics = {PRIMARY: primary}
        if adjusted is not None:
            metrics[ADJUSTED] = adjusted
        if revenue is not None:
            metrics[REVENUE] = revenue
        if ocf is not None:
            metrics[OCF] = ocf
        return FinancialStatement(
            security_id=SECURITY,
            period_end=period_end,
            report_type=report_type,
            statement_scope=statement_scope,
            metrics=metrics,
            currency=currency,
            unit_scale=unit_scale,
            audit_status="UNAUDITED",
        )

    def candidate(self, entity, *, revision_id, available_at):
        return NormalizedRecordCandidate.from_entity(
            entity=entity,
            source="erg-materiality-fixture",
            source_tier="TIER1",
            source_snapshot_id=("a" if "current" in revision_id else "b") * 64,
            revision_id=revision_id,
            available_at=available_at,
            ingested_at=available_at,
            strategy_visibility=("short_mid",),
            permitted_use="RESEARCH_ONLY",
            is_current_revision=True,
        )

    def materialize(self, current, comparator, *, current_available=CURRENT_AVAILABLE, comparator_available=COMPARATOR_AVAILABLE):
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        store = PITStore(tmp.name)
        ingest_candidates(
            store,
            [
                self.candidate(current, revision_id="current-rev", available_at=current_available),
                self.candidate(
                    comparator,
                    revision_id="comparator-rev",
                    available_at=comparator_available,
                ),
            ],
        )
        snapshot = store.create_snapshot(
            strategy_id="a_share_short_mid",
            sleeve="short_mid",
            as_of=AS_OF,
            intended_use="RESEARCH",
            entity_types=["FINANCIAL_STATEMENT"],
            security_ids=[SECURITY],
        )
        return tuple(store.materialize_snapshot(snapshot["snapshot_id"]))

    def contract(self, current, comparator, **overrides):
        values = dict(
            current_record_id=current.record_id(),
            comparator_record_id=comparator.record_id(),
            security_id=SECURITY,
            current_period_end=CURRENT_PERIOD,
            comparator_period_end=COMPARATOR_PERIOD,
            statement_scope="CONSOLIDATED",
            report_type="H1",
            primary_metric=PRIMARY,
            transmission_path=(
                "reported attributable profit change -> normalized earnings significance -> valuation expectation"
            ),
            rule_mode="EVIDENCE_ONLY",
            classification_basis="PRIMARY_CHANGE_ONLY",
            low_base_floor_abs=0.0,
        )
        values.update(overrides)
        return EarningsMaterialityContract.build(**values)

    def build(self, current, comparator, *, contract=None, **clock_overrides):
        records = self.materialize(
            current,
            comparator,
            current_available=clock_overrides.get("current_available", CURRENT_AVAILABLE),
            comparator_available=clock_overrides.get(
                "comparator_available", COMPARATOR_AVAILABLE
            ),
        )
        contract = contract or self.contract(current, comparator)
        return PITEarningsMaterialityProducer().build(
            records,
            contract=contract,
            as_of=clock_overrides.get("as_of", AS_OF),
            information_timestamp=clock_overrides.get("information_timestamp", INFO),
        )

    def test_evidence_only_stays_unresolved_but_computes_diagnostics(self):
        comparator = self.statement(period_end=COMPARATOR_PERIOD, primary=100.0)
        current = self.statement(period_end=CURRENT_PERIOD, primary=130.0)
        result = self.build(current, comparator)
        self.assertEqual(result.materiality.state, "UNRESOLVED")
        self.assertAlmostEqual(result.diagnostics.primary_current, 130_000_000.0)
        self.assertAlmostEqual(result.diagnostics.primary_comparator, 100_000_000.0)
        self.assertAlmostEqual(result.diagnostics.primary_change_pct, 0.30)
        self.assertEqual(result.materiality.assessment_contract_id, result.contract_id)
        self.assertEqual(len(result.materiality.evidence_refs), 2)

    def test_threshold_rule_can_classify_material(self):
        comparator = self.statement(period_end=COMPARATOR_PERIOD, primary=100.0)
        current = self.statement(period_end=CURRENT_PERIOD, primary=130.0)
        contract = self.contract(
            current,
            comparator,
            rule_mode="THRESHOLD_RULE_V1",
            min_primary_change_abs_pct=0.20,
        )
        result = self.build(current, comparator, contract=contract)
        self.assertEqual(result.materiality.state, "MATERIAL")

    def test_threshold_rule_can_classify_low_materiality(self):
        comparator = self.statement(period_end=COMPARATOR_PERIOD, primary=100.0)
        current = self.statement(period_end=CURRENT_PERIOD, primary=110.0)
        contract = self.contract(
            current,
            comparator,
            rule_mode="THRESHOLD_RULE_V1",
            min_primary_change_abs_pct=0.20,
        )
        result = self.build(current, comparator, contract=contract)
        self.assertEqual(result.materiality.state, "LOW_MATERIALITY")

    def test_large_negative_change_is_still_material(self):
        comparator = self.statement(period_end=COMPARATOR_PERIOD, primary=100.0)
        current = self.statement(period_end=CURRENT_PERIOD, primary=70.0)
        contract = self.contract(
            current,
            comparator,
            rule_mode="THRESHOLD_RULE_V1",
            min_primary_change_abs_pct=0.20,
        )
        result = self.build(current, comparator, contract=contract)
        self.assertAlmostEqual(result.diagnostics.primary_change_pct, -0.30)
        self.assertEqual(result.materiality.state, "MATERIAL")

    def test_low_base_fails_closed_instead_of_exploding_growth(self):
        comparator = self.statement(period_end=COMPARATOR_PERIOD, primary=10.0)
        current = self.statement(period_end=CURRENT_PERIOD, primary=30.0)
        contract = self.contract(
            current,
            comparator,
            rule_mode="THRESHOLD_RULE_V1",
            min_primary_change_abs_pct=0.20,
            low_base_floor_abs=20_000_000.0,
        )
        result = self.build(current, comparator, contract=contract)
        self.assertTrue(result.diagnostics.primary_low_base)
        self.assertIsNone(result.diagnostics.primary_change_pct)
        self.assertEqual(result.materiality.state, "UNRESOLVED")

    def test_adjusted_confirmation_can_be_frozen_as_required(self):
        comparator = self.statement(
            period_end=COMPARATOR_PERIOD,
            primary=100.0,
            adjusted=100.0,
        )
        current = self.statement(
            period_end=CURRENT_PERIOD,
            primary=130.0,
            adjusted=105.0,
        )
        contract = self.contract(
            current,
            comparator,
            rule_mode="THRESHOLD_RULE_V1",
            classification_basis="PRIMARY_AND_ADJUSTED_CHANGE",
            min_primary_change_abs_pct=0.20,
            adjusted_metric=ADJUSTED,
            min_adjusted_change_abs_pct=0.20,
        )
        result = self.build(current, comparator, contract=contract)
        self.assertAlmostEqual(result.diagnostics.primary_change_pct, 0.30)
        self.assertAlmostEqual(result.diagnostics.adjusted_change_pct, 0.05)
        self.assertEqual(result.materiality.state, "LOW_MATERIALITY")

    def test_adjusted_confirmation_can_support_material_state(self):
        comparator = self.statement(
            period_end=COMPARATOR_PERIOD,
            primary=100.0,
            adjusted=90.0,
        )
        current = self.statement(
            period_end=CURRENT_PERIOD,
            primary=130.0,
            adjusted=120.0,
        )
        contract = self.contract(
            current,
            comparator,
            rule_mode="THRESHOLD_RULE_V1",
            classification_basis="PRIMARY_AND_ADJUSTED_CHANGE",
            min_primary_change_abs_pct=0.20,
            adjusted_metric=ADJUSTED,
            min_adjusted_change_abs_pct=0.20,
        )
        result = self.build(current, comparator, contract=contract)
        self.assertEqual(result.materiality.state, "MATERIAL")

    def test_revenue_cash_and_one_off_are_diagnostics_not_hidden_gates(self):
        comparator = self.statement(
            period_end=COMPARATOR_PERIOD,
            primary=100.0,
            adjusted=90.0,
            revenue=1000.0,
            ocf=80.0,
        )
        current = self.statement(
            period_end=CURRENT_PERIOD,
            primary=130.0,
            adjusted=110.0,
            revenue=1150.0,
            ocf=104.0,
        )
        contract = self.contract(
            current,
            comparator,
            adjusted_metric=ADJUSTED,
            revenue_metric=REVENUE,
            cash_flow_metric=OCF,
        )
        result = self.build(current, comparator, contract=contract)
        self.assertEqual(result.materiality.state, "UNRESOLVED")
        self.assertAlmostEqual(result.diagnostics.revenue_change_pct, 0.15)
        self.assertAlmostEqual(result.diagnostics.current_cash_conversion_ratio, 0.8)
        self.assertAlmostEqual(
            result.diagnostics.current_one_off_gap_ratio,
            (130.0 - 110.0) / 130.0,
        )

    def test_current_statement_cannot_precede_event_clock(self):
        comparator = self.statement(period_end=COMPARATOR_PERIOD, primary=100.0)
        current = self.statement(period_end=CURRENT_PERIOD, primary=130.0)
        with self.assertRaisesRegex(ValueError, "before information_timestamp"):
            self.build(
                current,
                comparator,
                current_available="2026-08-28T16:00:00+08:00",
            )

    def test_comparator_must_be_pre_event(self):
        comparator = self.statement(period_end=COMPARATOR_PERIOD, primary=100.0)
        current = self.statement(period_end=CURRENT_PERIOD, primary=130.0)
        with self.assertRaisesRegex(ValueError, "strictly before information_timestamp"):
            self.build(
                current,
                comparator,
                comparator_available="2026-08-28T16:30:00+08:00",
            )

    def test_current_statement_must_be_visible_by_as_of(self):
        comparator = self.statement(period_end=COMPARATOR_PERIOD, primary=100.0)
        current = self.statement(period_end=CURRENT_PERIOD, primary=130.0)
        records = self.materialize(
            current,
            comparator,
            current_available="2026-08-28T19:00:00+08:00",
        )
        contract = self.contract(current, comparator)
        with self.assertRaisesRegex(ValueError, "not present|not observable"):
            PITEarningsMaterialityProducer().build(
                records,
                contract=contract,
                as_of=AS_OF,
                information_timestamp=INFO,
            )

    def test_scope_mismatch_is_rejected(self):
        comparator = self.statement(period_end=COMPARATOR_PERIOD, primary=100.0)
        current = self.statement(
            period_end=CURRENT_PERIOD,
            primary=130.0,
            statement_scope="PARENT_ONLY",
        )
        contract = self.contract(current, comparator)
        with self.assertRaisesRegex(ValueError, "statement_scope"):
            self.build(current, comparator, contract=contract)

    def test_missing_frozen_optional_metric_fails_closed(self):
        comparator = self.statement(period_end=COMPARATOR_PERIOD, primary=100.0)
        current = self.statement(period_end=CURRENT_PERIOD, primary=130.0)
        contract = self.contract(
            current,
            comparator,
            adjusted_metric=ADJUSTED,
        )
        with self.assertRaisesRegex(ValueError, "missing required metric"):
            self.build(current, comparator, contract=contract)

    def test_thresholds_are_not_allowed_in_evidence_only_mode(self):
        comparator = self.statement(period_end=COMPARATOR_PERIOD, primary=100.0)
        current = self.statement(period_end=CURRENT_PERIOD, primary=130.0)
        with self.assertRaisesRegex(ValueError, "EVIDENCE_ONLY"):
            self.contract(
                current,
                comparator,
                min_primary_change_abs_pct=0.20,
            )

    def test_rule_based_mode_requires_explicit_threshold(self):
        comparator = self.statement(period_end=COMPARATOR_PERIOD, primary=100.0)
        current = self.statement(period_end=CURRENT_PERIOD, primary=130.0)
        with self.assertRaisesRegex(ValueError, "requires min_primary_change_abs_pct"):
            self.contract(current, comparator, rule_mode="THRESHOLD_RULE_V1")

    def test_contract_and_result_ids_are_deterministic(self):
        comparator = self.statement(period_end=COMPARATOR_PERIOD, primary=100.0)
        current = self.statement(period_end=CURRENT_PERIOD, primary=130.0)
        first_contract = self.contract(current, comparator)
        second_contract = self.contract(current, comparator)
        self.assertEqual(first_contract.contract_id, second_contract.contract_id)
        first = self.build(current, comparator, contract=first_contract)
        second = self.build(current, comparator, contract=second_contract)
        self.assertEqual(first.result_id, second.result_id)
        self.assertEqual(first.to_dict(), second.to_dict())

    def test_contract_identity_changes_when_threshold_changes(self):
        comparator = self.statement(period_end=COMPARATOR_PERIOD, primary=100.0)
        current = self.statement(period_end=CURRENT_PERIOD, primary=130.0)
        first = self.contract(
            current,
            comparator,
            rule_mode="THRESHOLD_RULE_V1",
            min_primary_change_abs_pct=0.20,
        )
        second = self.contract(
            current,
            comparator,
            rule_mode="THRESHOLD_RULE_V1",
            min_primary_change_abs_pct=0.25,
        )
        self.assertNotEqual(first.contract_id, second.contract_id)

    def test_long_sleeve_is_rejected(self):
        comparator = self.statement(period_end=COMPARATOR_PERIOD, primary=100.0)
        current = self.statement(period_end=CURRENT_PERIOD, primary=130.0)
        records = self.materialize(current, comparator)
        contract = self.contract(current, comparator)
        with self.assertRaisesRegex(ValueError, "strategy context mismatch"):
            PITEarningsMaterialityProducer().build(
                records,
                contract=contract,
                as_of=AS_OF,
                information_timestamp=INFO,
                strategy_id="a_share_long_retirement",
                sleeve="long",
            )

    def test_contract_roundtrip(self):
        comparator = self.statement(period_end=COMPARATOR_PERIOD, primary=100.0)
        current = self.statement(period_end=CURRENT_PERIOD, primary=130.0)
        first = self.contract(
            current,
            comparator,
            rule_mode="THRESHOLD_RULE_V1",
            min_primary_change_abs_pct=0.20,
            revenue_metric=REVENUE,
        )
        restored = EarningsMaterialityContract.from_dict(first.to_dict())
        self.assertEqual(first.to_dict(), restored.to_dict())


if __name__ == "__main__":
    unittest.main()
