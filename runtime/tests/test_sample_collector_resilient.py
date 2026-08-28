import json
import tempfile
import unittest
from datetime import date
from pathlib import Path
from unittest.mock import patch

import pandas as pd

from runtime import sample_collector_resilient as resilient


class ResilientSampleCollectorTests(unittest.TestCase):
    def test_tencent_stock_fallback_normalizes_units(self):
        tx = pd.DataFrame(
            {
                "date": ["2026-08-27", "2026-08-28"],
                "open": [19.0, 19.2],
                "close": [19.2, 19.01],
                "high": [19.3, 19.37],
                "low": [18.8, 18.99],
                "volume": [1000000.0, 17681600.0],
                "turnover": [0.001, 0.0127],
                "amount": [19000000.0, 338440000.0],
            }
        )
        errors = []
        with patch.object(resilient, "_primary_stock_history", return_value=None), patch.object(
            resilient.core, "safe_call", return_value=tx
        ):
            out = resilient.fetch_stock_history_resilient(
                "600699", date(2026, 8, 1), date(2026, 8, 29), errors
            )
        self.assertIsNotNone(out)
        self.assertAlmostEqual(float(out.iloc[-1]["成交量"]), 176816.0)
        self.assertAlmostEqual(float(out.iloc[-1]["换手率"]), 1.27)
        self.assertEqual(out.attrs["sample_source"], "AKShare stock_zh_a_hist_tx / Tencent fallback")

    def test_lower_quality_revision_is_not_appended(self):
        with tempfile.TemporaryDirectory() as td:
            path = Path(td) / "2026-08-28.jsonl"
            prior = {
                "record_key": "s1:2026-08-28",
                "revision_number": 1,
                "payload_hash": "old",
                "data_quality": {"price_complete": True, "benchmark_complete": True},
                "price_and_path": {"x": 1},
            }
            path.write_text(json.dumps(prior) + "\n", encoding="utf-8")
            worse = {
                "record_key": "s1:2026-08-28",
                "data_quality": {"price_complete": False, "benchmark_complete": False},
                "price_and_path": None,
                "available_at": "2026-08-29T04:00:00+08:00",
                "ingested_at": "2026-08-29T04:00:00+08:00",
            }
            self.assertFalse(resilient.append_revisioned_daily_resilient(path, worse))
            self.assertEqual(len(path.read_text(encoding="utf-8").splitlines()), 1)


if __name__ == "__main__":
    unittest.main()
