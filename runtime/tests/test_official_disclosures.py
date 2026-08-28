import tempfile
import unittest

from src.core.pit_store import PITStore
from src.core.strategy_boundary import SHORT_MID_STRATEGY_ID
from src.data.ingest import run_adapter
from src.data.official_disclosures import (
    OfficialDisclosureRow,
    StaticOfficialDisclosureTransport,
    TimestampResolutionError,
    build_sse_disclosure_adapter,
    build_szse_disclosure_adapter,
)


class OfficialDisclosureAdapterTests(unittest.TestCase):
    def sse_row(self, **overrides):
        data = {
            "security_id": "601600",
            "announcement_id": "601600_20240829_79TR",
            "title": "2024年半年度报告",
            "category": "PERIODIC_REPORT",
            "document_url": "https://www.sse.com.cn/disclosure/listedinfo/announcement/c/new/2024-08-29/601600_20240829_79TR.pdf",
            "observed_at": "2024-08-29T08:05:00+08:00",
            "period_end": "2024-06-30",
        }
        data.update(overrides)
        return OfficialDisclosureRow(**data)

    def test_first_observed_basis_never_invents_published_time(self):
        row = self.sse_row()
        adapter = build_sse_disclosure_adapter(
            StaticOfficialDisclosureTransport((row,))
        )
        candidate = adapter.normalize(row)

        self.assertIsNone(candidate.metadata.published_at)
        self.assertEqual(
            candidate.metadata.available_at,
            "2024-08-29T08:05:00+08:00",
        )
        self.assertEqual(candidate.metadata.source_tier, "TIER1")
        self.assertEqual(candidate.metadata.permitted_use, "UNRESOLVED_LICENSE")

    def test_official_timestamp_basis_requires_exact_published_at(self):
        row = self.sse_row()
        adapter = build_sse_disclosure_adapter(
            StaticOfficialDisclosureTransport((row,)),
            visibility_basis="OFFICIAL_TIMESTAMP",
        )
        with self.assertRaises(TimestampResolutionError):
            adapter.normalize(row)

    def test_official_timestamp_can_be_used_when_exact_time_is_known(self):
        row = self.sse_row(
            published_at="2024-08-29T07:55:00+08:00",
            observed_at="2024-08-29T08:05:00+08:00",
        )
        adapter = build_sse_disclosure_adapter(
            StaticOfficialDisclosureTransport((row,)),
            visibility_basis="OFFICIAL_TIMESTAMP",
        )
        candidate = adapter.normalize(row)
        self.assertEqual(
            candidate.metadata.available_at,
            "2024-08-29T07:55:00+08:00",
        )
        self.assertEqual(
            candidate.metadata.ingested_at,
            "2024-08-29T08:05:00+08:00",
        )

    def test_observed_at_cannot_precede_published_at(self):
        row = self.sse_row(
            published_at="2024-08-29T08:10:00+08:00",
            observed_at="2024-08-29T08:05:00+08:00",
        )
        adapter = build_sse_disclosure_adapter(
            StaticOfficialDisclosureTransport((row,))
        )
        with self.assertRaises(ValueError):
            adapter.normalize(row)

    def test_non_official_document_host_is_rejected(self):
        row = self.sse_row(document_url="https://example.com/fake.pdf")
        adapter = build_sse_disclosure_adapter(
            StaticOfficialDisclosureTransport((row,))
        )
        with self.assertRaises(ValueError):
            adapter.normalize(row)

    def test_szse_static_document_host_is_allowed(self):
        row = OfficialDisclosureRow(
            security_id="002602",
            announcement_id="f3597cda-d7f6-4dc7-8a2f-cff71524ed37",
            title="2025年度业绩预告",
            category="EARNINGS_GUIDANCE",
            document_url="https://disc.static.szse.cn/disc/disk03/finalpage/2026-01-30/f3597cda-d7f6-4dc7-8a2f-cff71524ed37.PDF",
            observed_at="2026-01-30T08:00:00+08:00",
        )
        adapter = build_szse_disclosure_adapter(
            StaticOfficialDisclosureTransport((row,))
        )
        candidate = adapter.normalize(row)
        self.assertEqual(candidate.metadata.exchange, "SZSE")
        self.assertEqual(candidate.metadata.security_id, "002602")

    def test_static_transport_does_not_emit_future_observations(self):
        row = self.sse_row(observed_at="2024-08-29T08:05:00+08:00")
        transport = StaticOfficialDisclosureTransport((row,))
        adapter = build_sse_disclosure_adapter(transport)
        candidates = list(adapter.collect(as_of="2024-08-29T08:00:00+08:00"))
        self.assertEqual(candidates, [])

    def test_adapter_can_ingest_and_replay_research_snapshot(self):
        row = self.sse_row()
        adapter = build_sse_disclosure_adapter(
            StaticOfficialDisclosureTransport((row,))
        )
        with tempfile.TemporaryDirectory() as tmp:
            store = PITStore(tmp)
            result = run_adapter(
                store,
                adapter,
                as_of="2024-08-29T08:10:00+08:00",
            )
            self.assertEqual(result.received, 1)

            snapshot = store.create_snapshot(
                strategy_id=SHORT_MID_STRATEGY_ID,
                sleeve="short_mid",
                as_of="2024-08-29T08:10:00+08:00",
                intended_use="RESEARCH",
                entity_types=["DISCLOSURE"],
                security_ids=["601600"],
            )
            self.assertEqual(snapshot["record_count"], 1)

    def test_default_unresolved_license_blocks_internal_production(self):
        row = self.sse_row()
        adapter = build_sse_disclosure_adapter(
            StaticOfficialDisclosureTransport((row,))
        )
        with tempfile.TemporaryDirectory() as tmp:
            store = PITStore(tmp)
            run_adapter(store, adapter, as_of="2024-08-29T08:10:00+08:00")
            with self.assertRaises(ValueError):
                store.create_snapshot(
                    strategy_id=SHORT_MID_STRATEGY_ID,
                    sleeve="short_mid",
                    as_of="2024-08-29T08:10:00+08:00",
                    intended_use="INTERNAL_PRODUCTION",
                    entity_types=["DISCLOSURE"],
                    security_ids=["601600"],
                )


if __name__ == "__main__":
    unittest.main()
