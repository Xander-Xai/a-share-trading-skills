import json
import tempfile
import unittest
from datetime import date, datetime
from pathlib import Path
from unittest.mock import patch

import pandas as pd

from runtime.sample_collector import (
    DEFAULT_MARKET_REPORT_DIR,
    append_revisioned_daily,
    build_sample_record,
    checkpoint_metrics,
    derive_price_features,
    load_market_report,
    main,
)


class SampleCollectorTests(unittest.TestCase):
    def test_default_market_report_dir_matches_daily_monitor(self):
        self.assertEqual(DEFAULT_MARKET_REPORT_DIR.as_posix(), "reports/private/daily")

    def test_build_sample_record_loads_private_daily_market_report(self):
        with tempfile.TemporaryDirectory() as td:
            report_dir = Path(td) / "reports" / "private" / "daily"
            report_dir.mkdir(parents=True)
            market_report = {
                "market_metrics": {"advance_count": 1200, "decline_count": 900},
                "sentiment": {"sentiment_score": 61.25, "regime": "RISK_ON"},
                "spot_provider": "EASTMONEY_PRIMARY",
            }
            (report_dir / "2026-09-22-market-monitor.json").write_text(
                json.dumps(market_report), encoding="utf-8"
            )
            with patch("runtime.sample_collector.fetch_stock_history", return_value=pd.DataFrame({"x": [1]})), \
                 patch("runtime.sample_collector.fetch_benchmark_history", return_value=pd.DataFrame({"x": [1]})), \
                 patch("runtime.sample_collector.derive_price_features", return_value={"trade_date": "2026-09-22"}), \
                 patch("runtime.sample_collector.fetch_vendor_flow", return_value={"status": "AVAILABLE"}), \
                 patch("runtime.sample_collector.fetch_latest_margin", return_value={"status": "AVAILABLE"}), \
                 patch("runtime.sample_collector.fetch_disclosures", return_value=[]):
                record, _, _, _ = build_sample_record(
                    {"sample_id": "synthetic-1", "code": "999999", "entry_date": "2026-09-01", "actual_average_cost": 10.0},
                    date.fromisoformat("2026-09-23"),
                    "2026-09-23T09:00:00+08:00",
                    Path(td) / "state",
                    report_dir,
                )

            self.assertEqual(load_market_report(report_dir, "2026-09-22"), market_report)
            self.assertEqual(record["market_state"]["status"], "AVAILABLE")
            self.assertTrue(record["data_quality"]["market_complete"])
            self.assertEqual(record["market_state"]["sentiment"]["sentiment_score"], 61.25)

    def test_build_sample_record_fails_closed_when_market_report_is_missing(self):
        with tempfile.TemporaryDirectory() as td:
            missing_report_dir = Path(td) / "reports" / "private" / "daily"
            with patch("runtime.sample_collector.fetch_stock_history", return_value=pd.DataFrame({"x": [1]})), \
                 patch("runtime.sample_collector.fetch_benchmark_history", return_value=pd.DataFrame({"x": [1]})), \
                 patch("runtime.sample_collector.derive_price_features", return_value={"trade_date": "2026-09-22"}), \
                 patch("runtime.sample_collector.fetch_vendor_flow", return_value={"status": "AVAILABLE"}), \
                 patch("runtime.sample_collector.fetch_latest_margin", return_value={"status": "AVAILABLE"}), \
                 patch("runtime.sample_collector.fetch_disclosures", return_value=[]):
                record, _, _, _ = build_sample_record(
                    {"sample_id": "synthetic-1", "code": "999999", "entry_date": "2026-09-01", "actual_average_cost": 10.0},
                    date.fromisoformat("2026-09-23"),
                    "2026-09-23T09:00:00+08:00",
                    Path(td) / "state",
                    missing_report_dir,
                )

            self.assertFalse(record["data_quality"]["market_complete"])
            self.assertEqual(record["market_state"]["status"], "PROVIDER_ERROR")

    def test_missing_registry_is_deterministic_fail_closed(self):
        with tempfile.TemporaryDirectory() as td:
            state_dir = Path(td) / "state"
            report_dir = Path(td) / "reports"
            argv = [
                "sample_collector",
                "--registry",
                str(Path(td) / "missing-registry.json"),
                "--state-dir",
                str(state_dir),
                "--report-dir",
                str(report_dir),
                "--as-of-date",
                "2026-09-22",
            ]
            with patch("sys.argv", argv):
                self.assertEqual(main(), 0)
            summary = json.loads((state_dir / "latest-run.json").read_text(encoding="utf-8"))
            self.assertEqual(summary["registry_status"], "ABSENT_NO_FORWARD_SAMPLES")
            self.assertEqual(summary["data_status"], "DATA_INSUFFICIENT")
            self.assertEqual(summary["sample_count_registered"], 0)

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
