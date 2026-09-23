import sys
import unittest
from pathlib import Path


RUNTIME_DIR = Path(__file__).resolve().parents[1]
if str(RUNTIME_DIR) not in sys.path:
    sys.path.insert(0, str(RUNTIME_DIR))

from monitor import (
    DecisionInput,
    calculate_sentiment,
    decide_short_mid_monitor_state,
    normalize_stock_code,
)
from src.core.strategy_boundary import LONG_SLEEVE, LONG_STRATEGY_ID


class CodeNormalizationTests(unittest.TestCase):
    def test_eastmoney_numeric_code(self):
        self.assertEqual(normalize_stock_code("600000"), "600000")

    def test_sina_prefixed_codes(self):
        self.assertEqual(normalize_stock_code("sh600000"), "600000")
        self.assertEqual(normalize_stock_code("sz000001"), "000001")
        self.assertEqual(normalize_stock_code("bj430017"), "430017")

    def test_empty_code(self):
        self.assertEqual(normalize_stock_code(None), "")
        self.assertEqual(normalize_stock_code(""), "")


class SentimentTests(unittest.TestCase):
    def test_balanced_market_is_near_neutral(self):
        result = calculate_sentiment(
            {
                "advance_count": 2000,
                "decline_count": 2000,
                "limit_up_count": 30,
                "limit_down_count": 30,
                "broken_limit_count": 10,
                "strong_count": 100,
                "weak_count": 100,
                "median_return_pct": 0.0,
                "total_turnover": 1.0e12,
                "turnover_20d_median": 1.0e12,
            }
        )
        self.assertIsNotNone(result["sentiment_score"])
        self.assertIn(result["regime"], {"NEUTRAL", "RISK_ON"})

    def test_missing_core_data_fails_closed(self):
        result = calculate_sentiment(
            {
                "advance_count": None,
                "decline_count": None,
                "limit_up_count": None,
                "limit_down_count": None,
                "broken_limit_count": None,
                "strong_count": None,
                "weak_count": None,
                "median_return_pct": 0.5,
                "total_turnover": None,
                "turnover_20d_median": None,
            }
        )
        self.assertEqual(result["regime"], "DATA_INSUFFICIENT")
        self.assertIsNone(result["sentiment_score"])

    def test_strong_broad_market_scores_high(self):
        result = calculate_sentiment(
            {
                "advance_count": 4000,
                "decline_count": 500,
                "limit_up_count": 120,
                "limit_down_count": 5,
                "broken_limit_count": 15,
                "strong_count": 500,
                "weak_count": 30,
                "median_return_pct": 1.8,
                "total_turnover": 1.5e12,
                "turnover_20d_median": 1.0e12,
            }
        )
        self.assertGreater(result["sentiment_score"], 60)
        self.assertIn(result["regime"], {"RISK_ON", "EUPHORIA"})


class ActionEngineTests(unittest.TestCase):
    def test_long_sleeve_cannot_enter_short_mid_engine(self):
        state = DecisionInput(
            strategy_id=LONG_STRATEGY_ID,
            sleeve=LONG_SLEEVE,
            data_complete=True,
            entry_gate_pass=True,
            score_gate_pass=True,
            reward_risk_pass=True,
            risk_budget_pass=True,
        )
        self.assertEqual(
            decide_short_mid_monitor_state(state),
            "NO_ACTION_STRATEGY_MISMATCH",
        )

    def test_incomplete_data_never_trades(self):
        self.assertEqual(
            decide_short_mid_monitor_state(DecisionInput(data_complete=False)),
            "NO_ACTION",
        )

    def test_panic_blocks_new_entry(self):
        state = DecisionInput(
            data_complete=True,
            has_position=False,
            market_regime="PANIC",
            entry_gate_pass=True,
            score_gate_pass=True,
            reward_risk_pass=True,
            risk_budget_pass=True,
        )
        self.assertEqual(decide_short_mid_monitor_state(state), "WAIT")

    def test_risk_off_is_not_automatic_veto_when_stricter_gates_pass(self):
        state = DecisionInput(
            data_complete=True,
            has_position=False,
            market_regime="RISK_OFF",
            entry_gate_pass=True,
            score_gate_pass=True,
            reward_risk_pass=True,
            risk_budget_pass=True,
        )
        self.assertEqual(decide_short_mid_monitor_state(state), "READY")

    def test_risk_off_without_tight_entry_gate_stays_watch(self):
        state = DecisionInput(
            data_complete=True,
            has_position=False,
            market_regime="RISK_OFF",
            entry_gate_pass=False,
            score_gate_pass=True,
            reward_risk_pass=True,
            risk_budget_pass=True,
        )
        self.assertEqual(decide_short_mid_monitor_state(state), "WATCH")

    def test_ready_requires_all_entry_gates(self):
        state = DecisionInput(
            data_complete=True,
            has_position=False,
            market_regime="RISK_ON",
            entry_gate_pass=True,
            score_gate_pass=True,
            reward_risk_pass=True,
            risk_budget_pass=True,
        )
        self.assertEqual(decide_short_mid_monitor_state(state), "READY")

    def test_invalidated_position_exits(self):
        state = DecisionInput(
            data_complete=True,
            has_position=True,
            thesis_invalidated=True,
        )
        self.assertEqual(decide_short_mid_monitor_state(state), "EXIT_REVIEW")

    def test_monitor_engine_never_emits_position_mutation_states(self):
        for state in (
            DecisionInput(data_complete=True, has_position=False, entry_gate_pass=True, score_gate_pass=True, reward_risk_pass=True, risk_budget_pass=True),
            DecisionInput(data_complete=True, has_position=True, add_confirmation=True, add_gate_pass=True, risk_budget_pass=True),
            DecisionInput(data_complete=True, has_position=True),
        ):
            result = decide_short_mid_monitor_state(state)
            self.assertNotIn(result, {"ENTRY", "ADD", "HOLD", "TRIM", "EXIT"})


if __name__ == "__main__":
    unittest.main()
