import json
import tempfile
import unittest
from pathlib import Path

from src.data.raw_archive import RawEvidenceArchive


class RawEvidenceArchiveTests(unittest.TestCase):
    def archive(self, store: RawEvidenceArchive, **overrides):
        data = {
            "source": "Shanghai Stock Exchange",
            "locator": "https://www.sse.com.cn/disclosure/listedinfo/announcement/",
            "observed_at": "2026-08-28T16:24:00+08:00",
            "content": b"<html>official-index-snapshot</html>",
            "content_type": "text/html",
            "permitted_use": "UNRESOLVED_LICENSE",
            "source_tier": "TIER1",
            "encoding": "utf-8",
            "status_code": 200,
            "headers": {"content-type": "text/html"},
        }
        data.update(overrides)
        return store.archive_bytes(**data)

    def test_same_observation_is_deterministic(self):
        with tempfile.TemporaryDirectory() as tmp:
            store = RawEvidenceArchive(tmp)
            first = self.archive(store)
            second = self.archive(store)
            self.assertEqual(first.raw_snapshot_id, second.raw_snapshot_id)
            self.assertEqual(store.read_bytes(first.raw_snapshot_id), b"<html>official-index-snapshot</html>")

    def test_same_content_observed_at_different_time_has_distinct_snapshot(self):
        with tempfile.TemporaryDirectory() as tmp:
            store = RawEvidenceArchive(tmp)
            first = self.archive(store)
            second = self.archive(store, observed_at="2026-08-28T16:25:00+08:00")
            self.assertNotEqual(first.raw_snapshot_id, second.raw_snapshot_id)
            self.assertEqual(first.content_hash, second.content_hash)

    def test_content_is_deduplicated_by_hash(self):
        with tempfile.TemporaryDirectory() as tmp:
            store = RawEvidenceArchive(tmp)
            first = self.archive(store)
            self.archive(store, observed_at="2026-08-28T16:25:00+08:00")
            object_path = store.objects_dir / first.content_hash[:2] / first.content_hash
            self.assertTrue(object_path.exists())
            self.assertEqual(len(list(store.objects_dir.rglob(first.content_hash))), 1)

    def test_naive_observed_timestamp_is_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            store = RawEvidenceArchive(tmp)
            with self.assertRaises(ValueError):
                self.archive(store, observed_at="2026-08-28T16:24:00")

    def test_empty_content_is_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            store = RawEvidenceArchive(tmp)
            with self.assertRaises(ValueError):
                self.archive(store, content=b"")

    def test_manifest_tampering_is_detected(self):
        with tempfile.TemporaryDirectory() as tmp:
            store = RawEvidenceArchive(tmp)
            manifest = self.archive(store)
            path = store.manifests_dir / f"{manifest.raw_snapshot_id}.json"
            row = json.loads(path.read_text(encoding="utf-8"))
            row["locator"] = "https://example.com/tampered"
            path.write_text(json.dumps(row), encoding="utf-8")
            with self.assertRaises(ValueError):
                store.load_manifest(manifest.raw_snapshot_id)

    def test_object_tampering_is_detected(self):
        with tempfile.TemporaryDirectory() as tmp:
            store = RawEvidenceArchive(tmp)
            manifest = self.archive(store)
            path = store.objects_dir / manifest.content_hash[:2] / manifest.content_hash
            path.write_bytes(b"tampered")
            with self.assertRaises(ValueError):
                store.read_bytes(manifest.raw_snapshot_id)

    def test_permitted_use_is_part_of_snapshot_identity(self):
        with tempfile.TemporaryDirectory() as tmp:
            store = RawEvidenceArchive(tmp)
            first = self.archive(store, permitted_use="UNRESOLVED_LICENSE")
            second = self.archive(store, permitted_use="RESEARCH_ONLY")
            self.assertNotEqual(first.raw_snapshot_id, second.raw_snapshot_id)
            self.assertEqual(first.content_hash, second.content_hash)

    def test_invalid_http_status_is_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            store = RawEvidenceArchive(tmp)
            with self.assertRaises(ValueError):
                self.archive(store, status_code=999)


if __name__ == "__main__":
    unittest.main()
