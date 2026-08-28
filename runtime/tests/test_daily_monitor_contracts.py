import json
import sys
import tempfile
import unittest
from pathlib import Path


RUNTIME_DIR = Path(__file__).resolve().parents[1]
if str(RUNTIME_DIR) not in sys.path:
    sys.path.insert(0, str(RUNTIME_DIR))

from daily_monitor import DEFAULT_UNIVERSE, load_universe


class RuntimeUniverseContractTests(unittest.TestCase):
    def test_default_universe_is_not_a_level4_example(self):
        normalized = DEFAULT_UNIVERSE.as_posix()
        self.assertTrue(normalized.startswith("runtime/config/"))
        self.assertNotIn("/examples/", normalized)

    def test_valid_short_mid_universe_loads(self):
        payload = {
            "strategy_id": "a_share_short_mid",
            "sleeve": "short_mid",
            "runtime_universe_version": "test-v1",
            "as_of": "2026-08-28T18:10:00+08:00",
            "source_type": "TEST",
            "stocks": [{"code": "601600", "name": "中国铝业"}],
        }
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "universe.json"
            path.write_text(json.dumps(payload, ensure_ascii=False), encoding="utf-8")
            stocks, meta = load_universe(path)

        self.assertEqual(len(stocks), 1)
        self.assertEqual(meta["runtime_universe_version"], "test-v1")

    def test_long_universe_is_rejected_by_short_mid_monitor(self):
        payload = {
            "strategy_id": "a_share_long_retirement",
            "sleeve": "long",
            "runtime_universe_version": "test-v1",
            "as_of": "2026-08-28T18:10:00+08:00",
            "source_type": "TEST",
            "stocks": [],
        }
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "universe.json"
            path.write_text(json.dumps(payload, ensure_ascii=False), encoding="utf-8")
            with self.assertRaises(ValueError):
                load_universe(path)


if __name__ == "__main__":
    unittest.main()
