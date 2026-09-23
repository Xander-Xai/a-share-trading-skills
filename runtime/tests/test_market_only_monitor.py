import contextlib
import csv
import io
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

import pandas as pd

RUNTIME_DIR = Path(__file__).resolve().parents[1]
if str(RUNTIME_DIR) not in sys.path:
    sys.path.insert(0, str(RUNTIME_DIR))

from runtime import daily_monitor


class MarketOnlyMonitorTests(unittest.TestCase):
    def test_daily_monitor_supports_module_and_script_entrypoints(self):
        repo_root = Path(__file__).resolve().parents[2]
        for command in (
            [sys.executable, "-m", "runtime.daily_monitor", "--help"],
            [sys.executable, "runtime/daily_monitor.py", "--help"],
        ):
            with self.subTest(command=command):
                result = subprocess.run(command, cwd=repo_root, capture_output=True, text=True, check=False)
                self.assertEqual(result.returncode, 0, result.stderr)
                self.assertIn("--market-only", result.stdout)

    def _spot(self):
        return pd.DataFrame(
            {
                "代码": ["999999", "000001", "000002", "000003"],
                "名称": ["Synthetic A", "Synthetic B", "Synthetic C", "Synthetic D"],
                "涨跌幅": [1.0, 0.5, -0.5, -1.0],
                "成交额": [100.0, 200.0, 300.0, 400.0],
                "最新价": [10.0, 20.0, 30.0, 40.0],
            }
        )

    def _run(self, tmp, *, market_only, universe, spot_available=True, fresh_checkout=False):
        history = Path(tmp) / "state" / "market_history.csv"
        output = Path(tmp) / "candidate-reports"
        argv = ["daily_monitor"]
        if universe is not None:
            argv.extend(["--watchlist", str(universe)])
        argv.extend(["--history", str(history), "--output-dir", str(output)])
        if market_only:
            argv.append("--market-only")

        def fake_safe_call(errors, label, func, *args, **kwargs):
            if label == "load_universe":
                selected = universe or daily_monitor.DEFAULT_UNIVERSE
                return None if not selected.exists() else daily_monitor.load_universe(selected)
            return pd.DataFrame()

        with contextlib.ExitStack() as stack:
            if fresh_checkout:
                stack.enter_context(contextlib.chdir(tmp))
            stack.enter_context(patch.object(daily_monitor, "is_trade_date", return_value=True))
            stack.enter_context(patch.object(daily_monitor, "fetch_spot_with_fallback", return_value=(self._spot(), "EASTMONEY_PRIMARY") if spot_available else (None, "UNAVAILABLE")))
            stack.enter_context(patch.object(daily_monitor, "load_turnover_median", return_value=1.0e12))
            safe_call = stack.enter_context(patch.object(daily_monitor, "safe_call", side_effect=fake_safe_call))
            stack.enter_context(patch.object(sys, "argv", argv))
            with contextlib.redirect_stdout(io.StringIO()):
                status = daily_monitor.main()
        return status, history, output, safe_call

    def test_market_only_without_private_universe_persists_public_state(self):
        with tempfile.TemporaryDirectory() as tmp:
            absent = Path(tmp) / daily_monitor.DEFAULT_UNIVERSE
            status, history, output, safe_call = self._run(
                tmp, market_only=True, universe=None, fresh_checkout=True
            )

            self.assertEqual(status, 0)
            self.assertFalse(absent.exists())
            self.assertNotIn("load_universe", [call.args[1] for call in safe_call.call_args_list])
            self.assertFalse(output.exists())
            with history.open(newline="", encoding="utf-8") as stream:
                row = next(csv.DictReader(stream))
            self.assertTrue(float(row["sentiment_score"]) > 0)
            self.assertNotEqual(row["regime"], "DATA_INSUFFICIENT")
            self.assertEqual(float(row["total_turnover"]), 1000.0)

    def test_normal_mode_missing_universe_blocks_candidates_not_public_state(self):
        with tempfile.TemporaryDirectory() as tmp:
            absent = Path(tmp) / "private" / "short_mid_universe.json"
            status, history, output, safe_call = self._run(tmp, market_only=False, universe=absent)

            self.assertEqual(status, 0)
            self.assertIn("load_universe", [call.args[1] for call in safe_call.call_args_list])
            report = json.loads(next(output.glob("*-market-monitor.json")).read_text(encoding="utf-8"))
            self.assertEqual(report["universe"]["status"], "UNRESOLVED")
            self.assertEqual(report["sentiment"]["strategy_context_gate"], "BLOCKED")
            self.assertIsNotNone(report["sentiment"]["sentiment_score"])
            self.assertNotEqual(report["sentiment"]["regime"], "DATA_INSUFFICIENT")
            self.assertEqual(report["candidates"], [])
            self.assertTrue(history.exists())

    def test_private_universe_still_enables_candidate_monitoring(self):
        with tempfile.TemporaryDirectory() as tmp:
            universe = Path(tmp) / "private" / "short_mid_universe.json"
            universe.parent.mkdir(parents=True)
            universe.write_text(json.dumps({
                "strategy_id": "a_share_short_mid",
                "sleeve": "short_mid",
                "stocks": [{"code": "999999", "name": "Synthetic A", "status": "priority_scan"}],
            }), encoding="utf-8")
            status, _, output, _ = self._run(tmp, market_only=False, universe=universe)

            self.assertEqual(status, 0)
            report = json.loads(next(output.glob("*-market-monitor.json")).read_text(encoding="utf-8"))
            self.assertEqual(report["universe"]["status"], "LOADED")
            self.assertEqual(len(report["candidates"]), 1)

    def test_market_only_provider_failure_is_not_success(self):
        with tempfile.TemporaryDirectory() as tmp:
            absent = Path(tmp) / "private" / "short_mid_universe.json"
            status, history, output, _ = self._run(
                tmp, market_only=True, universe=absent, spot_available=False
            )

            self.assertEqual(status, 1)
            self.assertFalse(history.exists())
            self.assertFalse(output.exists())


if __name__ == "__main__":
    unittest.main()
