from __future__ import annotations

import tempfile
import unittest

from src.core.pit_store import PITStore
from src.data.adapters import NormalizedRecordCandidate
from src.data.benchmarks import (
    BenchmarkDailyBar,
    BenchmarkMaster,
    BenchmarkSeriesBuilder,
)
from src.data.coverage import CoverageResolver, DatasetCoverage
from src.data.ingest import ingest_candidates


AS_OF = "2026-08-28T18:00:00+08:00"


class BenchmarkSeriesTests(unittest.TestCase):
    def candidate(self, entity, *, revision_id="rev-1"):
        return NormalizedRecordCandidate.from_entity(
            entity=entity,
            source="benchmark-fixture",
            source_tier="TIER2",
            source_snapshot_id="benchmark-fixture-snapshot",
            revision_id=revision_id,
            available_at="2026-08-28T17:00:00+08:00",
            ingested_at="2026-08-28T17:00:00+08:00",
            strategy_visibility=("long", "short_mid"),
            permitted_use="RESEARCH_ONLY",
            is_current_revision=True,
        )

    def bar(self, benchmark_id, trade_date, close, prev_close=None):
        return BenchmarkDailyBar(
            benchmark_id=benchmark_id,
            trade_date=trade_date,
            open=close,
            high=close,
            low=close,
            close=close,
            prev_close=prev_close,
        )

    def coverage(self, benchmark_id, *, keyed=True, status="CONFIRMED_COMPLETE"):
        return DatasetCoverage(
            coverage_id=f"{benchmark_id}-coverage",
            dataset_family="BENCHMARK_DAILY_BAR",
            dataset_key=benchmark_id if keyed else None,
            scope_type="GLOBAL",
            start_date="2026-08-26",
            end_date="2026-08-28",
            completeness_status=status,
            verification_method="OFFICIAL_INDEX_SERIES_RECONCILED",
            expected_count=3 if status == "CONFIRMED_COMPLETE" else None,
            observed_count=3 if status == "CONFIRMED_COMPLETE" else None,
        )

    def materialize(self, candidates):
        with tempfile.TemporaryDirectory() as tmp:
            store = PITStore(tmp)
            ingest_candidates(store, candidates)
            snapshot = store.create_snapshot(
                strategy_id="a_share_short_mid",
                sleeve="short_mid",
                as_of=AS_OF,
                intended_use="RESEARCH",
                entity_types=["BENCHMARK_MASTER", "BENCHMARK_DAILY_BAR", "DATASET_COVERAGE"],
            )
            return tuple(store.materialize_snapshot(snapshot["snapshot_id"]))

    def standard_candidates(self, benchmark_id="CSI300"):
        return [
            self.candidate(
                BenchmarkMaster(
                    benchmark_id=benchmark_id,
                    benchmark_type="BROAD_INDEX",
                    name="Fixture Broad Index",
                    methodology_version="fixture-v1",
                )
            ),
            self.candidate(self.bar(benchmark_id, "2026-08-26", 4000.0)),
            self.candidate(self.bar(benchmark_id, "2026-08-27", 4040.0, 4000.0)),
            self.candidate(self.bar(benchmark_id, "2026-08-28", 4020.0, 4040.0)),
            self.candidate(self.coverage(benchmark_id)),
        ]

    def test_master_validates_type(self):
        with self.assertRaises(ValueError):
            BenchmarkMaster(
                benchmark_id="X",
                benchmark_type="UNKNOWN",
                name="Unknown",
            ).validate()

    def test_series_builds_deterministically(self):
        records = self.materialize(self.standard_candidates())
        first = BenchmarkSeriesBuilder().build(records, benchmark_id="CSI300")
        second = BenchmarkSeriesBuilder().build(records, benchmark_id="CSI300")
        self.assertEqual(first.benchmark_series_id, second.benchmark_series_id)
        self.assertEqual(first.to_dict(), second.to_dict())
        self.assertEqual(len(first.points), 3)
        self.assertIsNone(first.points[0].return_1d)
        self.assertAlmostEqual(first.points[1].return_1d, 0.01)
        self.assertAlmostEqual(first.points[2].return_1d, (4020.0 / 4040.0) - 1.0)

    def test_keyed_coverage_does_not_cross_benchmark_ids(self):
        candidates = self.standard_candidates("CSI300")
        candidates.extend(
            [
                self.candidate(self.bar("SECTOR-X", "2026-08-26", 1000.0), revision_id="s1"),
                self.candidate(self.bar("SECTOR-X", "2026-08-27", 1005.0), revision_id="s2"),
                self.candidate(self.bar("SECTOR-X", "2026-08-28", 1010.0), revision_id="s3"),
            ]
        )
        records = self.materialize(candidates)
        with self.assertRaisesRegex(ValueError, "benchmark coverage not confirmed"):
            BenchmarkSeriesBuilder().build(records, benchmark_id="SECTOR-X")

    def test_unkeyed_coverage_cannot_prove_specific_benchmark(self):
        candidates = self.standard_candidates()
        candidates[-1] = self.candidate(self.coverage("CSI300", keyed=False))
        records = self.materialize(candidates)
        resolution = CoverageResolver().resolve(
            records,
            dataset_family="BENCHMARK_DAILY_BAR",
            dataset_key="CSI300",
            requested_start="2026-08-26",
            requested_end="2026-08-28",
            accepted_methods={"OFFICIAL_INDEX_SERIES_RECONCILED"},
        )
        self.assertFalse(resolution.confirmed)
        self.assertEqual(resolution.reason, "NO_APPLICABLE_COVERAGE_ASSERTION")

    def test_unkeyed_legacy_coverage_still_resolves_for_unkeyed_requests(self):
        coverage = DatasetCoverage(
            coverage_id="legacy",
            dataset_family="DAILY_BAR",
            scope_type="GLOBAL",
            start_date="2026-08-26",
            end_date="2026-08-28",
            completeness_status="CONFIRMED_COMPLETE",
            verification_method="TRADING_CALENDAR_RECONCILED",
        )
        old_id = "DATASET_COVERAGE:DAILY_BAR:GLOBAL:GLOBAL:legacy:2026-08-26:2026-08-28"
        self.assertEqual(coverage.record_id(), old_id)
        records = self.materialize([self.candidate(coverage)])
        resolution = CoverageResolver().resolve(
            records,
            dataset_family="DAILY_BAR",
            requested_start="2026-08-26",
            requested_end="2026-08-28",
            accepted_methods={"TRADING_CALENDAR_RECONCILED"},
        )
        self.assertTrue(resolution.confirmed)

    def test_partial_benchmark_coverage_fails_closed(self):
        candidates = self.standard_candidates()
        candidates[-1] = self.candidate(self.coverage("CSI300", status="PARTIAL"))
        records = self.materialize(candidates)
        with self.assertRaisesRegex(ValueError, "benchmark coverage not confirmed"):
            BenchmarkSeriesBuilder().build(records, benchmark_id="CSI300")

    def test_duplicate_benchmark_date_is_rejected(self):
        candidates = self.standard_candidates()
        candidates.insert(
            3,
            self.candidate(self.bar("CSI300", "2026-08-27", 4041.0), revision_id="dup"),
        )
        records = self.materialize(candidates)
        with self.assertRaisesRegex(ValueError, "duplicate benchmark trade_date"):
            BenchmarkSeriesBuilder().build(records, benchmark_id="CSI300")


if __name__ == "__main__":
    unittest.main()
