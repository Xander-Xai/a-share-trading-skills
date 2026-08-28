from __future__ import annotations

import tempfile
import unittest

from src.core.pit_store import PITStore
from src.data.adapters import NormalizedRecordCandidate
from src.data.adjustments import AdjustmentFactorBuilder
from src.data.benchmarks import BenchmarkDailyBar, BenchmarkSeriesBuilder
from src.data.coverage import DatasetCoverage
from src.data.entities import DailyBar
from src.data.ingest import ingest_candidates
from src.features.relative_performance import RelativePerformanceBuilder


AS_OF = "2026-08-28T18:00:00+08:00"
DATES = ("2026-08-25", "2026-08-26", "2026-08-27", "2026-08-28")


class RelativePerformanceTests(unittest.TestCase):
    def candidate(self, entity, *, revision_id="rev-1", exchange=None):
        return NormalizedRecordCandidate.from_entity(
            entity=entity,
            source="relative-performance-fixture",
            source_tier="TIER2",
            source_snapshot_id="relative-performance-fixture",
            revision_id=revision_id,
            available_at="2026-08-28T17:00:00+08:00",
            ingested_at="2026-08-28T17:00:00+08:00",
            strategy_visibility=("long", "short_mid"),
            permitted_use="RESEARCH_ONLY",
            exchange=exchange,
            is_current_revision=True,
        )

    def stock_bar(self, trade_date, close, prev_close=None):
        return DailyBar(
            security_id="601600",
            trade_date=trade_date,
            open=close,
            high=close,
            low=close,
            close=close,
            prev_close=prev_close,
            volume=1000,
            turnover=10000,
        )

    def stock_coverage(self, family):
        return DatasetCoverage(
            coverage_id=f"{family.lower()}-coverage",
            dataset_family=family,
            scope_type="SECURITY",
            security_id="601600",
            exchange="SSE",
            start_date=DATES[0],
            end_date=DATES[-1],
            completeness_status="CONFIRMED_COMPLETE",
            verification_method=(
                "TRADING_CALENDAR_RECONCILED"
                if family == "DAILY_BAR"
                else "OFFICIAL_SOURCE_ENUMERATION"
            ),
        )

    def benchmark_coverage(self, benchmark_id="CSI300"):
        return DatasetCoverage(
            coverage_id=f"{benchmark_id}-coverage",
            dataset_family="BENCHMARK_DAILY_BAR",
            dataset_key=benchmark_id,
            scope_type="GLOBAL",
            start_date=DATES[0],
            end_date=DATES[-1],
            completeness_status="CONFIRMED_COMPLETE",
            verification_method="OFFICIAL_INDEX_SERIES_RECONCILED",
            expected_count=4,
            observed_count=4,
        )

    def build_inputs(self, *, benchmark_dates=DATES):
        stock_closes = (10.0, 10.5, 10.3, 10.8)
        benchmark_closes = (100.0, 101.0, 100.5, 102.0)
        candidates = []
        for index, (trade_date, close) in enumerate(zip(DATES, stock_closes, strict=True)):
            candidates.append(
                self.candidate(
                    self.stock_bar(
                        trade_date,
                        close,
                        None if index == 0 else stock_closes[index - 1],
                    ),
                    revision_id=f"stock-{index}",
                    exchange="SSE",
                )
            )
        candidates.extend(
            [
                self.candidate(self.stock_coverage("DAILY_BAR"), revision_id="daily-cov"),
                self.candidate(
                    self.stock_coverage("CORPORATE_ACTION"),
                    revision_id="action-cov",
                ),
            ]
        )
        for index, (trade_date, close) in enumerate(
            zip(benchmark_dates, benchmark_closes[: len(benchmark_dates)], strict=True)
        ):
            candidates.append(
                self.candidate(
                    BenchmarkDailyBar(
                        benchmark_id="CSI300",
                        trade_date=trade_date,
                        open=close,
                        high=close,
                        low=close,
                        close=close,
                        prev_close=None if index == 0 else benchmark_closes[index - 1],
                    ),
                    revision_id=f"bench-{index}",
                )
            )
        candidates.append(
            self.candidate(
                DatasetCoverage(
                    coverage_id="CSI300-coverage",
                    dataset_family="BENCHMARK_DAILY_BAR",
                    dataset_key="CSI300",
                    scope_type="GLOBAL",
                    start_date=benchmark_dates[0],
                    end_date=benchmark_dates[-1],
                    completeness_status="CONFIRMED_COMPLETE",
                    verification_method="OFFICIAL_INDEX_SERIES_RECONCILED",
                    expected_count=len(benchmark_dates),
                    observed_count=len(benchmark_dates),
                ),
                revision_id="bench-cov",
            )
        )

        with tempfile.TemporaryDirectory() as tmp:
            store = PITStore(tmp)
            ingest_candidates(store, candidates)
            snapshot = store.create_snapshot(
                strategy_id="a_share_short_mid",
                sleeve="short_mid",
                as_of=AS_OF,
                intended_use="RESEARCH",
                entity_types=[
                    "DAILY_BAR",
                    "CORPORATE_ACTION",
                    "BENCHMARK_DAILY_BAR",
                    "DATASET_COVERAGE",
                ],
                security_ids=["601600"],
            )
            # Benchmark bars have no security_id and are excluded by a security filter,
            # so create a second all-entity snapshot for the benchmark facts.
            all_snapshot = store.create_snapshot(
                strategy_id="a_share_short_mid",
                sleeve="short_mid",
                as_of=AS_OF,
                intended_use="RESEARCH",
                entity_types=[
                    "DAILY_BAR",
                    "CORPORATE_ACTION",
                    "BENCHMARK_DAILY_BAR",
                    "DATASET_COVERAGE",
                ],
            )
            stock_records = tuple(store.materialize_snapshot(snapshot["snapshot_id"]))
            all_records = tuple(store.materialize_snapshot(all_snapshot["snapshot_id"]))
            stock = AdjustmentFactorBuilder().build(stock_records, security_id="601600")
            benchmark = BenchmarkSeriesBuilder().build(all_records, benchmark_id="CSI300")
            return stock, benchmark

    def test_builds_daily_abnormal_returns_and_explicit_windows(self):
        stock, benchmark = self.build_inputs()
        result = RelativePerformanceBuilder().build(
            stock,
            benchmark,
            benchmark_selection_contract_id="benchmark-contract-test-v1",
            benchmark_role="PRIMARY",
            diagnostic_windows=(1, 3),
        )
        self.assertEqual(result.strategy_id, "a_share_short_mid")
        self.assertEqual(result.sleeve, "short_mid")
        self.assertEqual(result.benchmark_id, "CSI300")
        self.assertEqual(len(result.points), 4)
        self.assertIsNone(result.points[0].abnormal_return_1d)
        expected_stock_1d = (10.5 / 10.0) - 1.0
        expected_benchmark_1d = (101.0 / 100.0) - 1.0
        self.assertAlmostEqual(
            result.points[1].abnormal_return_1d,
            expected_stock_1d - expected_benchmark_1d,
        )
        self.assertEqual(tuple(window.sessions for window in result.windows), (1, 3))
        full = result.windows[-1]
        self.assertAlmostEqual(full.stock_return, 0.08)
        self.assertAlmostEqual(full.benchmark_return, 0.02)
        self.assertAlmostEqual(full.excess_return, 0.06)

    def test_identity_is_deterministic(self):
        stock, benchmark = self.build_inputs()
        first = RelativePerformanceBuilder().build(
            stock,
            benchmark,
            benchmark_selection_contract_id="contract-v1",
            diagnostic_windows=(1, 3),
        )
        second = RelativePerformanceBuilder().build(
            stock,
            benchmark,
            benchmark_selection_contract_id="contract-v1",
            diagnostic_windows=(3, 1),
        )
        self.assertEqual(first.relative_performance_id, second.relative_performance_id)
        self.assertEqual(first.to_dict(), second.to_dict())

    def test_selection_contract_is_part_of_identity(self):
        stock, benchmark = self.build_inputs()
        first = RelativePerformanceBuilder().build(
            stock,
            benchmark,
            benchmark_selection_contract_id="contract-v1",
        )
        second = RelativePerformanceBuilder().build(
            stock,
            benchmark,
            benchmark_selection_contract_id="contract-v2",
        )
        self.assertNotEqual(first.relative_performance_id, second.relative_performance_id)

    def test_long_strategy_context_is_rejected(self):
        stock, benchmark = self.build_inputs()
        with self.assertRaisesRegex(ValueError, "strategy context mismatch"):
            RelativePerformanceBuilder().build(
                stock,
                benchmark,
                benchmark_selection_contract_id="contract-v1",
                strategy_id="a_share_long_retirement",
                sleeve="long",
            )

    def test_insufficient_history_for_requested_window_fails_closed(self):
        stock, benchmark = self.build_inputs()
        with self.assertRaisesRegex(ValueError, "insufficient aligned history"):
            RelativePerformanceBuilder().build(
                stock,
                benchmark,
                benchmark_selection_contract_id="contract-v1",
                diagnostic_windows=(4,),
            )

    def test_stock_and_benchmark_dates_must_align_exactly(self):
        stock, benchmark = self.build_inputs(
            benchmark_dates=("2026-08-25", "2026-08-26", "2026-08-28")
        )
        with self.assertRaisesRegex(ValueError, "dates must align exactly"):
            RelativePerformanceBuilder().build(
                stock,
                benchmark,
                benchmark_selection_contract_id="contract-v1",
            )

    def test_benchmark_selection_contract_is_required(self):
        stock, benchmark = self.build_inputs()
        with self.assertRaises(ValueError):
            RelativePerformanceBuilder().build(
                stock,
                benchmark,
                benchmark_selection_contract_id="",
            )

    def test_duplicate_windows_are_rejected(self):
        stock, benchmark = self.build_inputs()
        with self.assertRaisesRegex(ValueError, "must be unique"):
            RelativePerformanceBuilder().build(
                stock,
                benchmark,
                benchmark_selection_contract_id="contract-v1",
                diagnostic_windows=(1, 1),
            )


if __name__ == "__main__":
    unittest.main()
