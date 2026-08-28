from __future__ import annotations

import tempfile
import unittest

from src.core.pit_store import PITStore
from src.data.coverage import CoverageResolver
from src.data.ingest import ingest_candidates
from src.data.official_corporate_actions import (
    OfficialCorporateActionBatch,
    OfficialCorporateActionRow,
)


SSE_SOURCE = "https://www.sse.com.cn/market/stockdata/dividends/dividend/"
RAW_ID = "a" * 64
OBSERVED_AT = "2026-08-28T23:26:00+08:00"


class OfficialCorporateActionTests(unittest.TestCase):
    def make_row(self, *, ex_date="2026-08-28", security_id="601600"):
        return OfficialCorporateActionRow(
            security_id=security_id,
            action_id=f"cash-div-{ex_date}",
            action_type="CASH_DIVIDEND",
            announcement_date="2026-08-20",
            record_date="2026-08-27",
            ex_date=ex_date,
            pay_date="2026-08-28",
            cash_per_share=0.1,
            source_locator=SSE_SOURCE,
            published_at="2026-08-20T16:00:00+08:00",
        )

    def make_batch(
        self,
        *,
        rows=(),
        source_row_count=None,
        scope_type="SECURITY",
        security_id="601600",
        source_snapshot_id=RAW_ID,
        source_url=SSE_SOURCE,
        completeness_status="CONFIRMED_COMPLETE",
    ):
        rows = tuple(rows)
        if source_row_count is None:
            source_row_count = len(rows)
        return OfficialCorporateActionBatch(
            exchange="SSE",
            source_name="Shanghai Stock Exchange",
            source_url=source_url,
            source_snapshot_id=source_snapshot_id,
            observed_at=OBSERVED_AT,
            start_date="2026-08-01",
            end_date="2026-08-28",
            scope_type=scope_type,
            security_id=security_id if scope_type == "SECURITY" else None,
            source_row_count=source_row_count,
            rows=rows,
            completeness_status=completeness_status,
        )

    def test_complete_empty_security_enumeration_proves_absence(self):
        batch = self.make_batch(rows=())
        rows = list(batch.collect(as_of=OBSERVED_AT))
        self.assertEqual(len(rows), 1)
        self.assertEqual(rows[0].metadata.entity_type, "DATASET_COVERAGE")
        self.assertEqual(rows[0].payload["dataset_family"], "CORPORATE_ACTION")
        self.assertEqual(rows[0].payload["completeness_status"], "CONFIRMED_COMPLETE")
        self.assertEqual(rows[0].payload["expected_count"], 0)
        self.assertEqual(rows[0].payload["observed_count"], 0)

    def test_complete_batch_emits_action_and_coverage(self):
        batch = self.make_batch(rows=(self.make_row(),))
        rows = list(batch.collect(as_of=OBSERVED_AT))
        self.assertEqual(len(rows), 2)
        action = next(row for row in rows if row.metadata.entity_type == "CORPORATE_ACTION")
        coverage = next(row for row in rows if row.metadata.entity_type == "DATASET_COVERAGE")
        self.assertEqual(action.payload["security_id"], "601600")
        self.assertEqual(action.payload["ex_date"], "2026-08-28")
        self.assertEqual(action.metadata.available_at, "2026-08-20T16:00:00+08:00")
        self.assertEqual(action.metadata.ingested_at, OBSERVED_AT)
        self.assertEqual(coverage.payload["verification_method"], "OFFICIAL_SOURCE_ENUMERATION")

    def test_pit_coverage_resolver_accepts_security_level_official_enumeration(self):
        with tempfile.TemporaryDirectory() as tmp:
            store = PITStore(tmp)
            batch = self.make_batch(rows=())
            ingest_candidates(
                store,
                batch.collect(as_of=OBSERVED_AT),
                adapter_id="SSE_OFFICIAL_CORPORATE_ACTION_ENUMERATION_V1",
            )
            snapshot = store.create_snapshot(
                strategy_id="a_share_short_mid",
                sleeve="short_mid",
                as_of=OBSERVED_AT,
                intended_use="RESEARCH",
                entity_types=["CORPORATE_ACTION", "DATASET_COVERAGE"],
                security_ids=["601600"],
            )
            records = store.materialize_snapshot(snapshot["snapshot_id"])
            resolution = CoverageResolver().resolve(
                records,
                dataset_family="CORPORATE_ACTION",
                requested_start="2026-08-01",
                requested_end="2026-08-28",
                security_id="601600",
                exchange="SSE",
                accepted_methods={"OFFICIAL_SOURCE_ENUMERATION"},
            )
            self.assertTrue(resolution.confirmed)
            self.assertEqual(resolution.scope_type, "SECURITY")

    def test_exchange_batch_can_prove_coverage_for_any_security_in_exchange(self):
        with tempfile.TemporaryDirectory() as tmp:
            store = PITStore(tmp)
            batch = self.make_batch(
                scope_type="EXCHANGE",
                security_id=None,
                rows=(self.make_row(),),
            )
            ingest_candidates(store, batch.collect(as_of=OBSERVED_AT))
            snapshot = store.create_snapshot(
                strategy_id="a_share_short_mid",
                sleeve="short_mid",
                as_of=OBSERVED_AT,
                intended_use="RESEARCH",
                entity_types=["CORPORATE_ACTION", "DATASET_COVERAGE"],
            )
            records = store.materialize_snapshot(snapshot["snapshot_id"])
            resolution = CoverageResolver().resolve(
                records,
                dataset_family="CORPORATE_ACTION",
                requested_start="2026-08-01",
                requested_end="2026-08-28",
                security_id="600000",
                exchange="SSE",
                accepted_methods={"OFFICIAL_SOURCE_ENUMERATION"},
            )
            self.assertTrue(resolution.confirmed)
            self.assertEqual(resolution.scope_type, "EXCHANGE")

    def test_complete_batch_requires_raw_archive_sha256_id(self):
        with self.assertRaises(ValueError):
            self.make_batch(source_snapshot_id="curated-not-raw").validate()

    def test_complete_batch_rejects_source_row_count_mismatch(self):
        with self.assertRaises(ValueError):
            self.make_batch(rows=(self.make_row(),), source_row_count=2).validate()

    def test_non_official_source_host_is_rejected(self):
        with self.assertRaises(ValueError):
            self.make_batch(source_url="https://example.com/actions").validate()

    def test_security_batch_rejects_row_for_another_security(self):
        with self.assertRaises(ValueError):
            self.make_batch(rows=(self.make_row(security_id="600000"),)).validate()

    def test_row_outside_coverage_range_is_rejected(self):
        with self.assertRaises(ValueError):
            self.make_batch(rows=(self.make_row(ex_date="2026-07-31"),)).validate()

    def test_batch_is_not_visible_before_first_observation(self):
        batch = self.make_batch(rows=())
        rows = list(batch.collect(as_of="2026-08-28T23:25:59+08:00"))
        self.assertEqual(rows, [])


if __name__ == "__main__":
    unittest.main()
