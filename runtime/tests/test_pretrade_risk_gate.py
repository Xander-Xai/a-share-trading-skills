import unittest

from src.core.pretrade_risk_gate import (
    CapitalSafetyInput,
    LongPreTradeInput,
    ShortMidPreTradeInput,
    evaluate_long_pretrade,
    evaluate_short_mid_pretrade,
)


def good_capital(idle=20_000, equity=100_000):
    return CapitalSafetyInput(
        available_idle_cash_rmb=idle,
        stock_account_equity_rmb=equity,
        capital_eligibility="PASS",
        cash_need_gate="PASS",
        emergency_reserve_gate="PASS",
        debt_leverage_gate="PASS",
        risk_capacity="MEDIUM",
        risk_willingness="MEDIUM",
    )


class TestPreTradeRiskGate(unittest.TestCase):
    def base_short(self, **overrides):
        data = dict(
            capital=good_capital(),
            position_state="ENTRY",
            entry_price=20.0,
            invalidation_price=19.0,
            strategy_nav_rmb=50_000,
            user_max_loss_this_trade_rmb=300,
            trigger_confirmed=True,
            current_account_symbol_exposure_rmb=0,
            current_account_cluster_exposure_rmb=0,
            current_total_short_exposure_rmb=0,
            current_short_symbol_exposure_rmb=0,
            current_short_cluster_exposure_rmb=0,
            current_open_initial_risk_rmb=0,
            current_factor_initial_risk_rmb=0,
            final_short_cap_rmb=20_000,
        )
        data.update(overrides)
        return ShortMidPreTradeInput(**data)

    def test_missing_idle_cash_fails_closed(self):
        cap = CapitalSafetyInput(
            available_idle_cash_rmb=None,
            stock_account_equity_rmb=100_000,
            capital_eligibility="UNKNOWN",
            cash_need_gate="PASS",
            emergency_reserve_gate="PASS",
            debt_leverage_gate="PASS",
            risk_capacity="MEDIUM",
            risk_willingness="MEDIUM",
        )
        d = evaluate_short_mid_pretrade(self.base_short(capital=cap))
        self.assertEqual(d.authorization_state, "NEED_USER_INPUT")
        self.assertEqual(d.max_executable_shares, 0)
        self.assertIn("available_idle_cash_rmb", d.missing_fields)

    def test_cash_need_gate_blocks_buy(self):
        cap = CapitalSafetyInput(
            available_idle_cash_rmb=20_000,
            stock_account_equity_rmb=100_000,
            capital_eligibility="FAIL",
            cash_need_gate="FAIL",
            emergency_reserve_gate="PASS",
            debt_leverage_gate="PASS",
            risk_capacity="MEDIUM",
            risk_willingness="MEDIUM",
        )
        d = evaluate_short_mid_pretrade(self.base_short(capital=cap))
        self.assertEqual(d.authorization_state, "BLOCKED")
        self.assertEqual(d.max_executable_shares, 0)

    def test_borrowed_money_blocks_buy(self):
        cap = CapitalSafetyInput(
            available_idle_cash_rmb=20_000,
            stock_account_equity_rmb=100_000,
            capital_eligibility="FAIL",
            cash_need_gate="PASS",
            emergency_reserve_gate="PASS",
            debt_leverage_gate="FAIL",
            risk_capacity="HIGH",
            risk_willingness="HIGH",
        )
        d = evaluate_short_mid_pretrade(self.base_short(capital=cap))
        self.assertEqual(d.authorization_state, "BLOCKED")

    def test_unconfirmed_entry_has_zero_shares(self):
        d = evaluate_short_mid_pretrade(self.base_short(trigger_confirmed=False))
        self.assertEqual(d.authorization_state, "BLOCKED")
        self.assertEqual(d.max_executable_shares, 0)

    def test_add_requires_positive_confirmation(self):
        d = evaluate_short_mid_pretrade(self.base_short(
            position_state="ADD",
            positive_add_confirmation=False,
        ))
        self.assertEqual(d.authorization_state, "BLOCKED")
        self.assertIn("ADD requires positive confirmation", d.blocking_reasons)

    def test_short_position_is_risk_sized_and_board_lot_rounded(self):
        d = evaluate_short_mid_pretrade(self.base_short())
        # NAV 50k => operating per-trade risk 250; stop distance 1 => risk cap 200 shares after lot rounding.
        # ENTRY uses 50% setup tranche => 100 shares.
        self.assertEqual(d.authorization_state, "AUTHORIZED")
        self.assertEqual(d.max_executable_shares, 200)
        self.assertEqual(d.planned_entry_shares, 100)
        self.assertEqual(d.allowed_new_loss_rmb, 250.0)
        self.assertEqual(d.worst_case_planned_loss_rmb, 100.0)

    def test_zero_remaining_heat_blocks_trade(self):
        d = evaluate_short_mid_pretrade(self.base_short(current_open_initial_risk_rmb=1_000))
        self.assertEqual(d.authorization_state, "NO_TRADE_POSITION_TOO_SMALL_FOR_RISK_BUDGET")
        self.assertEqual(d.max_executable_shares, 0)

    def test_final_short_cap_can_bind(self):
        d = evaluate_short_mid_pretrade(self.base_short(
            entry_price=10.0,
            invalidation_price=9.5,
            final_short_cap_rmb=1_500,
        ))
        self.assertEqual(d.authorization_state, "NO_TRADE_TRANCHE_ROUNDS_BELOW_BOARD_LOT")
        self.assertIn("final_short_cap", d.binding_constraints)

    def test_long_requires_all_gates(self):
        d = evaluate_long_pretrade(LongPreTradeInput(
            capital=good_capital(),
            position_state="ENTRY",
            entry_price=20.0,
            long_target_total_position_rmb=10_000,
            current_account_symbol_exposure_rmb=0,
            current_account_cluster_exposure_rmb=0,
            valuation_gate="PASS",
            portfolio_gate="PASS",
            thesis_gate="PASS",
            balance_gate="UNKNOWN",
            planned_tranche_fraction=0.40,
        ))
        self.assertEqual(d.authorization_state, "NEED_USER_INPUT")
        self.assertEqual(d.max_executable_shares, 0)

    def test_long_sizing_respects_tranche(self):
        d = evaluate_long_pretrade(LongPreTradeInput(
            capital=good_capital(idle=20_000, equity=100_000),
            position_state="ENTRY",
            entry_price=20.0,
            long_target_total_position_rmb=10_000,
            current_account_symbol_exposure_rmb=0,
            current_account_cluster_exposure_rmb=0,
            valuation_gate="PASS",
            portfolio_gate="PASS",
            thesis_gate="PASS",
            balance_gate="PASS",
            planned_tranche_fraction=0.40,
        ))
        self.assertEqual(d.authorization_state, "AUTHORIZED")
        self.assertEqual(d.planned_entry_shares, 200)
        self.assertEqual(d.planned_notional_rmb, 4_000.0)


if __name__ == "__main__":
    unittest.main()
