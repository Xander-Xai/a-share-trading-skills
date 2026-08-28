import json
import tempfile
import unittest
from pathlib import Path

from src.core.pit import PITMetadata
from src.core.pit_store import PITStore
from src.core.strategy_boundary import SHORT_MID_STRATEGY_ID


class PITStoreTests(unittest.TestCase):
    def build_metadata(self, **overrides):
        data = {
            "record_id": "disclosure-601600-h1",
            "entity_type": "DISCLOSURE",
            "source": "exchange",
            "source_tier": "TIER1",
            "source_snapshot_id": "source-snap-1",
            "revision_id": "rev-1",
            "available_at": "2026-08-28T16:23:05+08:00",
            "ingested_at": "2026-08-28T16:24:00+08:00",
            "published_at": "2026-08-28T16:23:00+08:00",
            "security_id": "601600",
            "strategy_visibility": ("long", "short_mid"),
            "permitted_use": "RESEARCH_ONLY",
        }
        data.update(overrides)
        return PITMetadata(**data)

    def test_append_is_idempotent_for_same_identity_and_payload(self):
        with tempfile.TemporaryDirectory() as tmp:
            store = PITStore(tmp)
            metadata = self.build_metadata()
            first = store.append(metadata, {"net_profit": 118.71})
            second = store.append(metadata, {"net_profit": 118.71})

            self.assertEqual(first.metadata.payload_hash, second.metadata.payload_hash)
            self.assertEqual(len(store.read_all()), 1)

    def test_same_identity_with_different_payload_is_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            store = PITStore(tmp)
            metadata = self.build_metadata()
            store.append(metadata, {"net_profit": 118.71})
            with self.assertRaises(ValueError):
                store.append(metadata, {"net_profit": 119.00})

    def test_superseded_revision_must_exist(self):
        with tempfile.TemporaryDirectory() as tmp:
            store = PITStore(tmp)
            metadata = self.build_metadata(
                revision_id="rev-2",
                supersedes_revision_id="rev-missing",
            )
            with self.assertRaises(ValueError):
                store.append(metadata, {"net_profit": 119.00})

    def test_snapshot_uses_latest_revision_visible_at_as_of(self):
        with tempfile.TemporaryDirectory() as tmp:
            store = PITStore(tmp)
            rev1 = self.build_metadata()
            store.append(rev1, {"net_profit": 118.71})

            rev2 = self.build_metadata(
                revision_id="rev-2",
                supersedes_revision_id="rev-1",
                source_snapshot_id="source-snap-2",
                published_at="2026-08-29T09:00:00+08:00",
                available_at="2026-08-29T09:00:05+08:00",
                ingested_at="2026-08-29T09:01:00+08:00",
            )
            store.append(rev2, {"net_profit": 119.00})

            before = store.create_snapshot(
                strategy_id=SHORT_MID_STRATEGY_ID,
                sleeve="short_mid",
                as_of="2026-08-28T18:00:00+08:00",
            )
            after = store.create_snapshot(
                strategy_id=SHORT_MID_STRATEGY_ID,
                sleeve="short_mid",
                as_of="2026-08-29T10:00:00+08:00",
            )

            self.assertEqual(before["records"][0]["revision_id"], "rev-1")
            self.assertEqual(after["records"][0]["revision_id"], "rev-2")

    def test_snapshot_id_is_deterministic_for_same_selection(self):
        with tempfile.TemporaryDirectory() as tmp:
            store = PITStore(tmp)
            store.append(self.build_metadata(), {"net_profit": 118.71})

            first = store.create_snapshot(
                strategy_id=SHORT_MID_STRATEGY_ID,
                sleeve="short_mid",
                as_of="2026-08-28T18:00:00+08:00",
            )
            second = store.create_snapshot(
                strategy_id=SHORT_MID_STRATEGY_ID,
                sleeve="short_mid",
                as_of="2026-08-28T18:00:00+08:00",
            )

            self.assertEqual(first["snapshot_id"], second["snapshot_id"])
            self.assertEqual(first["created_at"], second["created_at"])

    def test_strategy_visibility_is_respected(self):
        with tempfile.TemporaryDirectory() as tmp:
            store = PITStore(tmp)
            metadata = self.build_metadata(strategy_visibility=("long",))
            store.append(metadata, {"net_profit": 118.71})

            snapshot = store.create_snapshot(
                strategy_id=SHORT_MID_STRATEGY_ID,
                sleeve="short_mid",
                as_of="2026-08-28T18:00:00+08:00",
            )
            self.assertEqual(snapshot["record_count"], 0)

    def test_internal_production_blocks_research_only_record(self):
        with tempfile.TemporaryDirectory() as tmp:
            store = PITStore(tmp)
            store.append(self.build_metadata(), {"net_profit": 118.71})

            with self.assertRaises(ValueError):
                store.create_snapshot(
                    strategy_id=SHORT_MID_STRATEGY_ID,
                    sleeve="short_mid",
                    as_of="2026-08-28T18:00:00+08:00",
                    intended_use="INTERNAL_PRODUCTION",
                )

    def test_internal_production_allows_explicitly_permitted_record(self):
        with tempfile.TemporaryDirectory() as tmp:
            store = PITStore(tmp)
            metadata = self.build_metadata(
                permitted_use="INTERNAL_PRODUCTION_ALLOWED"
            )
            store.append(metadata, {"net_profit": 118.71})

            snapshot = store.create_snapshot(
                strategy_id=SHORT_MID_STRATEGY_ID,
                sleeve="short_mid",
                as_of="2026-08-28T18:00:00+08:00",
                intended_use="INTERNAL_PRODUCTION",
            )
            self.assertEqual(snapshot["record_count"], 1)

    def test_old_research_only_revision_does_not_block_new_permitted_revision(self):
        with tempfile.TemporaryDirectory() as tmp:
            store = PITStore(tmp)
            store.append(self.build_metadata(), {"net_profit": 118.71})
            rev2 = self.build_metadata(
                revision_id="rev-2",
                supersedes_revision_id="rev-1",
                source_snapshot_id="source-snap-2",
                published_at="2026-08-29T09:00:00+08:00",
                available_at="2026-08-29T09:00:05+08:00",
                ingested_at="2026-08-29T09:01:00+08:00",
                permitted_use="INTERNAL_PRODUCTION_ALLOWED",
            )
            store.append(rev2, {"net_profit": 119.00})

            snapshot = store.create_snapshot(
                strategy_id=SHORT_MID_STRATEGY_ID,
                sleeve="short_mid",
                as_of="2026-08-29T10:00:00+08:00",
                intended_use="INTERNAL_PRODUCTION",
            )
            self.assertEqual(snapshot["record_count"], 1)
            self.assertEqual(snapshot["records"][0]["revision_id"], "rev-2")

    def test_materialize_snapshot_detects_missing_record(self):
        with tempfile.TemporaryDirectory() as tmp:
            store = PITStore(tmp)
            store.append(self.build_metadata(), {"net_profit": 118.71})
            snapshot = store.create_snapshot(
                strategy_id=SHORT_MID_STRATEGY_ID,
                sleeve="short_mid",
                as_of="2026-08-28T18:00:00+08:00",
            )

            Path(store.records_path).write_text("", encoding="utf-8")
            with self.assertRaises(ValueError):
                store.materialize_snapshot(snapshot["snapshot_id"])

    def test_load_snapshot_detects_manifest_tampering(self):
        with tempfile.TemporaryDirectory() as tmp:
            store = PITStore(tmp)
            store.append(self.build_metadata(), {"net_profit": 118.71})
            snapshot = store.create_snapshot(
                strategy_id=SHORT_MID_STRATEGY_ID,
                sleeve="short_mid",
                as_of="2026-08-28T18:00:00+08:00",
            )
            path = store.snapshots_dir / f"{snapshot['snapshot_id']}.json"
            manifest = json.loads(path.read_text(encoding="utf-8"))
            manifest["as_of"] = "2026-08-28T19:00:00+08:00"
            path.write_text(json.dumps(manifest), encoding="utf-8")

            with self.assertRaises(ValueError):
                store.load_snapshot(snapshot["snapshot_id"])


if __name__ == "__main__":
    unittest.main()
