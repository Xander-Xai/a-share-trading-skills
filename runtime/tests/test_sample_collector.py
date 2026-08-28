import json
import tempfile
import unittest
from datetime import datetime
from pathlib import Path

import pandas as pd

from runtime.sample_collector import (
    append_revisioned_daily,
    checkpoint_metrics,
    derive_price_features,
)


class SampleCollectorTests(unittest.TestCase):
    def _hist(self):
        return pd.DataFrame(
            {
                "trade_date": pd.to_datetime(
                    ["2026-08-05", "2026-08-06", "2026-08-07", "2026-08-10", "2026-08-11", "2026-08-12"]
                ),
                "开盘": [10.0, 10.2, 10.1, 10.3, 10.4, 10.5],
                "收盘": [10.1, 10.3, 10.2, 10.4, 10.5, 10.6],
                "最高": [30.0, 11.0, 10.5, 10.7, 10.8, 10.9],
                "最低": [9.0, 9.8, 9.7, 10.0, 10.1, 10.2],
                "成交量": [100, 120, 90, 130, 110, 140],
                "成交额": [1000, 1200, 900, 1300, 1100, 1400],
                "换手率": [1, 1, 1, 1, 1, 1],
                "涨跌幅": [1, 2, -1, 2, 1, 1],
            }
        )

    def _benchmark(self):
        return pd.DataFrame(
            {
                "trade_date": pd.to_datetime(
                    ["2026-08-05", "2026-08-06", "2026-08-07", "2026-08-10", "2026-08-11", "2026-08-12"]
                ),
                "close": [100, 101, 100, 102, 103, 104],
            }
        )

    def test_entry_day_high_low_not_counted_as_post_fill_mfe_mae(self):
        sample = {
            "entry_date": "2026-08-05",
            "actual_average_cost": 10.0,
        }
        result = derive_price_features(self._hist(), self._benchmark(), sample)
        path = result["sample_path"]
        self.assertEqual(path["entry_day_excursion_status"], "UNRESOLVED_WITH_DAILY_BARS_UNLESS_INTRADAY_FILL_DATA_EXISTS")
        self.assertEqual(path["MFE_price"], 11.0)
        self.assertEqual(path["MAE_price"], 9.7)
        self.assertNotEqual(path["MFE_price"], 30.0)
        self.assertNotEqual(path["MAE_price"], 9.0)

    def test_checkpoint_is_frozen_to_requested_sessions(self):
        result = checkpoint_metrics(
            self._hist(),
            self._benchmark(),
            datetime.strptime("2026-08-05", "%Y-%m-%d").date(),
            10.0,
            3,
        )
        self.assertIsNotNone(result)
        self.assertEqual(result["checkpoint"], "D3")
        self.assertEqual(result["checkpoint_date"], "2026-08-07")
        self.assertEqual(result["follow_through_classification"], "UNCLASSIFIED_CHALLENGER")

    def test_daily_revision_is_idempotent_for_same_payload(self):
        with tempfile.TemporaryDirectory() as td:
            path = Path(td) / "2026-08-05.jsonl"
            record = {
                "record_key": "sample:2026-08-05",
                "ingested_at": "2026-08-05T15:40:00+08:00",
                "value": 1,
            }
            self.assertTrue(append_revisioned_daily(path, record))
            self.assertFalse(append_revisioned_daily(path, {**record, "ingested_at": "2026-08-05T16:00:00+08:00"}))
            rows = [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]
            self.assertEqual(len(rows), 1)
            self.assertEqual(rows[0]["revision_number"], 1)

    def test_daily_revision_appends_when_evidence_changes(self):
        with tempfile.TemporaryDirectory() as td:
            path = Path(td) / "2026-08-05.jsonl"
            base = {
                "record_key": "sample:2026-08-05",
                "ingested_at": "2026-08-05T15:40:00+08:00",
                "value": 1,
            }
            self.assertTrue(append_revisioned_daily(path, base))
            self.assertTrue(append_revisioned_daily(path, {**base, "ingested_at": "2026-08-05T17:00:00+08:00", "value": 2}))
            rows = [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]
            self.assertEqual(len(rows), 2)
            self.assertEqual(rows[-1]["revision_number"], 2)
            self.assertEqual(rows[-1]["supersedes_payload_hash"], rows[0]["payload_hash"])


if __name__ == "__main__":
    unittest.main()
