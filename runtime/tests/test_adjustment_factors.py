from __future__ import annotations

import tempfile
import unittest

from src.core.pit_store import PITStore
from src.data.adapters import NormalizedRecordCandidate
from src.data.adjustments import AdjustmentFactorBuilder
from src.data.coverage import DatasetCoverage
from src.data.entities import CorporateAction, DailyBar
from src.data.ingest import ingest_candidates


AS_OF = "2026-08-28T18:00:00+08:00"
SOURCE_SNAPSHOT = "fixture-adjustment-v1"


class AdjustmentFactorTests(unittest.TestCase):
    def candidate(self, entity, *, exchange="SSE", revision_id="rev-1"):
        return NormalizedRecordCandidate.from_entity(
            entity=entity,
            source="fixture",
            source_tier="TIER1",
            source_snapshot_id=SOURCE_SNAPSHOT,
            revision_id=revision_id,
            available_at="2026-08-28T17:00:00+08:00",
            ingested_at="2026-08-28T17:00:00+08:00",
            strategy_visibility=("long", "short_mid"),
            permitted_use="RESEARCH_ONLY",
            exchange=exchange,
            is_current_revision=True,
        )

    def bar(self, trade_date, *, close, open_=None, high=None, low=None, prev_close=10.0):
        open_ = close if open_ is None else open_
        high = max(open_, close) if high is None else high
        low = min(open_, close) if low is None else low
        return DailyBar(
            security_id="601600",
            trade_date=trade_date,
            open=open_,
            high=high,
            low=low,
            close=close,
            prev_close=prev_close,
            volume=1000,
            turnover=10000,
        )

    def coverage(self, family, *, start="2026-08-26", end="2026-08-28"):
        method = (
            "TRADING_CALENDAR_RECONCILED"
            if family == "DAILY_BAR"
            else "OFFICIAL_SOURCE_ENUMERATION"
        )
        return DatasetCoverage(
            coverage_id=f"{family.lower()}-coverage",
            dataset_family=family,
            scope_type="SECURITY",
            security_id="601600",
            exchange="SSE",
            start_date=start,
            end_date=end,
            completeness_status="CONFIRMED_COMPLETE",
            verification_method=method,
            expected_count=None,
            observed_count=None,
        )

    def build_records(self, *, action=None, include_action_coverage=True, extra_actions=()):
        candidates = [
            self.candidate(self.bar("2026-08-26", close=10.0)),
            self.candidate(self.bar("2026-08-27", close=10.0)),
            self.candidate(
                self.bar(
                    "2026-08-28",
                    close=9.2,
                    open_=9.0,
                    high=9.3,
                    low=8.9,
                    prev_close=9.0,
                )
            ),
            self.candidate(self.coverage("DAILY_BAR")),
        ]
        if include_action_coverage:
            candidates.append(self.candidate(self.coverage("CORPORATE_ACTION")))
        if action is not None:
            candidates.append(self.candidate(action))
        for index, extra in enumerate(extra_actions, start=2):
            candidates.append(self.candidate(extra, revision_id=f"rev-{index}"))

        with tempfile.TemporaryDirectory() as tmp:
            store = PITStore(tmp)
            ingest_candidates(store, candidates)
            snapshot = store.create_snapshot(
                strategy_id="a_share_short_mid",
                sleeve="short_mid",
                as_of=AS_OF,
                intended_use="RESEARCH",
                entity_types=["DAILY_BAR", "CORPORATE_ACTION", "DATASET_COVERAGE"],
                security_ids=["601600"],
            )
            return tuple(store.materialize_snapshot(snapshot["snapshot_id"]))

    def action(self, **kwargs):
        defaults = dict(
            security_id="601600",
            action_id="action-1",
            action_type="DISTRIBUTION",
            announcement_date="2026-08-20",
            record_date="2026-08-27",
            ex_date="2026-08-28",
        )
        defaults.update(kwargs)
        return CorporateAction(**defaults)

    def test_cash_dividend_uses_exchange_reference_formula(self):
        records = self.build_records(action=self.action(cash_per_share=1.0))
        series = AdjustmentFactorBuilder().build(records, security_id="601600")
        self.assertEqual(len(series.events), 1)
        event = series.events[0]
        self.assertAlmostEqual(event.reference_price, 9.0)
        self.assertAlmostEqual(event.event_factor, 0.9)
        self.assertAlmostEqual(series.points[1].adjusted_close, 9.0)
        self.assertAlmostEqual(series.points[-1].adjustment_factor, 1.0)
        self.assertAlmostEqual(series.points[-1].adjusted_close, 9.2)

    def test_bonus_and_transfer_change_denominator(self):
        records = self.build_records(
            action=self.action(bonus_ratio=0.1, transfer_ratio=0.1)
        )
        series = AdjustmentFactorBuilder().build(records, security_id="601600")
        event = series.events[0]
        self.assertAlmostEqual(event.total_share_change_ratio, 0.2)
        self.assertAlmostEqual(event.reference_price, 10.0 / 1.2)
        self.assertAlmostEqual(event.event_factor, 1.0 / 1.2)

    def test_rights_issue_uses_subscription_value_in_numerator(self):
        records = self.build_records(
            action=self.action(rights_ratio=0.2, rights_price=5.0)
        )
        series = AdjustmentFactorBuilder().build(records, security_id="601600")
        event = series.events[0]
        self.assertAlmostEqual(event.rights_value_component, 1.0)
        self.assertAlmostEqual(event.reference_price, 11.0 / 1.2)

    def test_combined_event_uses_all_explicit_terms(self):
        records = self.build_records(
            action=self.action(
                cash_per_share=0.5,
                bonus_ratio=0.1,
                rights_ratio=0.2,
                rights_price=4.0,
            )
        )
        series = AdjustmentFactorBuilder().build(records, security_id="601600")
        event = series.events[0]
        self.assertAlmostEqual(event.reference_price, (10.0 - 0.5 + 0.8) / 1.3)
        self.assertAlmostEqual(event.total_share_change_ratio, 0.3)

    def test_effective_reference_cash_can_differ_from_holder_cash(self):
        records = self.build_records(
            action=self.action(cash_per_share=0.5, reference_cash_per_share=0.4)
        )
        series = AdjustmentFactorBuilder().build(records, security_id="601600")
        self.assertAlmostEqual(series.events[0].reference_cash_per_share, 0.4)
        self.assertAlmostEqual(series.events[0].reference_price, 9.6)

    def test_reference_share_change_override_supports_effective_terms(self):
        records = self.build_records(
            action=self.action(
                bonus_ratio=0.4,
                reference_total_share_change_ratio=0.3861,
                reference_cash_per_share=0.4827,
            )
        )
        series = AdjustmentFactorBuilder().build(records, security_id="601600")
        event = series.events[0]
        self.assertAlmostEqual(event.total_share_change_ratio, 0.3861)
        self.assertAlmostEqual(event.reference_price, (10.0 - 0.4827) / 1.3861)

    def test_legacy_ratio_is_rejected_by_adjustment_engine(self):
        records = self.build_records(action=self.action(ratio=0.1))
        with self.assertRaisesRegex(ValueError, "legacy ambiguous ratio"):
            AdjustmentFactorBuilder().build(records, security_id="601600")

    def test_missing_corporate_action_coverage_fails_closed(self):
        records = self.build_records(
            action=self.action(cash_per_share=1.0),
            include_action_coverage=False,
        )
        with self.assertRaisesRegex(ValueError, "CORPORATE_ACTION coverage not confirmed"):
            AdjustmentFactorBuilder().build(records, security_id="601600")

    def test_multiple_standard_rows_same_ex_date_are_aggregated(self):
        cash = self.action(action_id="cash", cash_per_share=0.5)
        bonus = self.action(action_id="bonus", bonus_ratio=0.1)
        records = self.build_records(action=cash, extra_actions=(bonus,))
        series = AdjustmentFactorBuilder().build(records, security_id="601600")
        event = series.events[0]
        self.assertEqual(len(event.action_refs), 2)
        self.assertAlmostEqual(event.reference_price, (10.0 - 0.5) / 1.1)

    def test_override_requires_one_consolidated_row_per_ex_date(self):
        special = self.action(
            action_id="special",
            reference_total_share_change_ratio=0.1,
        )
        extra = self.action(action_id="cash", cash_per_share=0.1)
        records = self.build_records(action=special, extra_actions=(extra,))
        with self.assertRaisesRegex(ValueError, "one consolidated action row"):
            AdjustmentFactorBuilder().build(records, security_id="601600")

    def test_series_identity_is_deterministic(self):
        records = self.build_records(action=self.action(cash_per_share=1.0))
        first = AdjustmentFactorBuilder().build(records, security_id="601600")
        second = AdjustmentFactorBuilder().build(records, security_id="601600")
        self.assertEqual(first.adjustment_series_id, second.adjustment_series_id)
        self.assertEqual(first.to_dict(), second.to_dict())


if __name__ == "__main__":
    unittest.main()
