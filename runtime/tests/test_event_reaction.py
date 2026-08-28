from __future__ import annotations

import hashlib
import json
import unittest

from src.features.event_reaction import EventReactionMeasurementBuilder
from src.features.relative_performance import (
    RELATIVE_PERFORMANCE_SCHEMA_VERSION,
    RelativePerformancePoint,
    RelativePerformanceSeries,
)


DATES = (
    "2026-08-20",
    "2026-08-21",
    "2026-08-24",
    "2026-08-25",
    "2026-08-26",
    "2026-08-27",
    "2026-08-28",
    "2026-08-31",
    "2026-09-01",
)


def canonical_hash(value) -> str:
    payload = json.dumps(
        value,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
        allow_nan=False,
    )
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


class EventReactionMeasurementTests(unittest.TestCase):
    def relative(self) -> RelativePerformanceSeries:
        stock = 10.0
        benchmark = 100.0
        points = []
        previous_stock = None
        previous_benchmark = None
        for index, trade_date in enumerate(DATES):
            if index > 0:
                stock *= 1.01
                benchmark *= 1.002
            stock_return = None if previous_stock is None else (stock / previous_stock) - 1.0
            benchmark_return = (
                None
                if previous_benchmark is None
                else (benchmark / previous_benchmark) - 1.0
            )
            abnormal = (
                None
                if stock_return is None
                else stock_return - benchmark_return
            )
            points.append(
                RelativePerformancePoint(
                    trade_date=trade_date,
                    stock_adjusted_close=stock,
                    benchmark_close=benchmark,
                    stock_return_1d=stock_return,
                    benchmark_return_1d=benchmark_return,
                    abnormal_return_1d=abnormal,
                )
            )
            previous_stock = stock
            previous_benchmark = benchmark

        provisional = RelativePerformanceSeries(
            relative_performance_id="pending",
            schema_version=RELATIVE_PERFORMANCE_SCHEMA_VERSION,
            strategy_id="a_share_short_mid",
            sleeve="short_mid",
            security_id="601600",
            benchmark_id="CSI300",
            benchmark_role="PRIMARY",
            benchmark_selection_contract_id="benchmark-contract-v1",
            adjustment_series_id="adjustment-series-fixture",
            benchmark_series_id="benchmark-series-fixture",
            start_date=DATES[0],
            end_date=DATES[-1],
            points=tuple(points),
            windows=(),
        )
        result = RelativePerformanceSeries(
            relative_performance_id=canonical_hash(provisional.identity_payload()),
            schema_version=provisional.schema_version,
            strategy_id=provisional.strategy_id,
            sleeve=provisional.sleeve,
            security_id=provisional.security_id,
            benchmark_id=provisional.benchmark_id,
            benchmark_role=provisional.benchmark_role,
            benchmark_selection_contract_id=provisional.benchmark_selection_contract_id,
            adjustment_series_id=provisional.adjustment_series_id,
            benchmark_series_id=provisional.benchmark_series_id,
            start_date=provisional.start_date,
            end_date=provisional.end_date,
            points=provisional.points,
            windows=provisional.windows,
        )
        result.validate()
        return result

    def build(self, **overrides):
        kwargs = dict(
            event_id="event-1",
            event_family="EARNINGS",
            information_timestamp="2026-08-27T16:20:00+08:00",
            first_tradable_timestamp="2026-08-27T16:23:00+08:00",
            reaction_window_contract_id="reaction-contract-v1",
            prepricing_windows=(1, 3),
            reaction_windows=(1, 2),
            primary_reaction_window_sessions=None,
        )
        kwargs.update(overrides)
        return EventReactionMeasurementBuilder().build(self.relative(), **kwargs)

    def test_after_close_event_anchors_next_full_session(self):
        result = self.build()
        self.assertEqual(result.full_session_anchor_date, "2026-08-28")
        self.assertTrue(result.partial_session_reaction_omitted)
        self.assertEqual(result.primary_window_status, "UNRESOLVED_RESEARCH")
        self.assertEqual(tuple(row.sessions for row in result.prepricing_metrics), (1, 3))
        self.assertEqual(tuple(row.sessions for row in result.reaction_metrics), (1, 2))
        self.assertEqual(result.reaction_metrics[0].start_date, "2026-08-27")
        self.assertEqual(result.reaction_metrics[0].end_date, "2026-08-28")

    def test_before_open_tradable_time_can_use_same_full_session(self):
        result = self.build(
            information_timestamp="2026-08-28T08:50:00+08:00",
            first_tradable_timestamp="2026-08-28T09:20:00+08:00",
        )
        self.assertEqual(result.full_session_anchor_date, "2026-08-28")
        self.assertFalse(result.partial_session_reaction_omitted)

    def test_intraday_first_tradable_time_skips_to_next_full_session(self):
        result = self.build(
            information_timestamp="2026-08-28T09:50:00+08:00",
            first_tradable_timestamp="2026-08-28T10:00:00+08:00",
            reaction_windows=(1,),
        )
        self.assertEqual(result.full_session_anchor_date, "2026-08-31")
        self.assertTrue(result.partial_session_reaction_omitted)
        self.assertEqual(result.reaction_metrics[0].start_date, "2026-08-28")
        self.assertEqual(result.reaction_metrics[0].end_date, "2026-08-31")

    def test_prepricing_window_excludes_anchor_session(self):
        result = self.build(prepricing_windows=(3,), reaction_windows=(1,))
        metric = result.prepricing_metrics[0]
        self.assertEqual(metric.start_date, "2026-08-24")
        self.assertEqual(metric.end_date, "2026-08-27")
        self.assertEqual(metric.sessions, 3)

    def test_primary_window_must_be_predeclared(self):
        with self.assertRaisesRegex(ValueError, "predeclared"):
            self.build(
                reaction_windows=(1, 2),
                primary_reaction_window_sessions=3,
            )

    def test_resolved_primary_window_is_marked_frozen(self):
        result = self.build(primary_reaction_window_sessions=2)
        self.assertEqual(result.primary_reaction_window_sessions, 2)
        self.assertEqual(result.primary_window_status, "FROZEN_BY_CONTRACT")

    def test_first_tradable_cannot_precede_information(self):
        with self.assertRaisesRegex(ValueError, "cannot precede"):
            self.build(
                information_timestamp="2026-08-27T16:20:00+08:00",
                first_tradable_timestamp="2026-08-27T16:19:59+08:00",
            )

    def test_insufficient_post_event_history_fails_closed(self):
        with self.assertRaisesRegex(ValueError, "insufficient post-event history"):
            self.build(
                information_timestamp="2026-08-31T16:00:00+08:00",
                first_tradable_timestamp="2026-08-31T16:01:00+08:00",
                reaction_windows=(2,),
                prepricing_windows=(),
            )

    def test_insufficient_pre_event_history_fails_closed(self):
        with self.assertRaisesRegex(ValueError, "insufficient pre-event history"):
            self.build(
                information_timestamp="2026-08-24T08:00:00+08:00",
                first_tradable_timestamp="2026-08-24T09:00:00+08:00",
                prepricing_windows=(3,),
                reaction_windows=(1,),
            )

    def test_long_strategy_context_is_rejected(self):
        with self.assertRaisesRegex(ValueError, "strategy context mismatch"):
            self.build(
                strategy_id="a_share_long_retirement",
                sleeve="long",
            )

    def test_identity_is_deterministic(self):
        first = self.build()
        second = self.build()
        self.assertEqual(first.event_measurement_id, second.event_measurement_id)
        self.assertEqual(first.to_dict(), second.to_dict())

    def test_contract_id_changes_measurement_identity(self):
        first = self.build(reaction_window_contract_id="reaction-contract-v1")
        second = self.build(reaction_window_contract_id="reaction-contract-v2")
        self.assertNotEqual(first.event_measurement_id, second.event_measurement_id)


if __name__ == "__main__":
    unittest.main()
