import unittest

from src.core.pretrade_risk_gate import (
    CapitalSafetyInput,
    LongPreTradeInput,
    ShortMidPreTradeInput,
    evaluate_long_pretrade,
    evaluate_short_mid_pretrade,
    validate_manual_requested_shares,
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
            current_trade_planned_risk_rmb=0,
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
        self.assertEqual(d.authorization_state, "NO_TRADE_TRANCHE_ROUNDS_BELOW_MINIMUM")
        self.assertIn("final_short_cap", d.binding_constraints)

    def test_long_requires_all_gates(self):
        d = evaluate_long_pretrade(LongPreTradeInput(
            capital=good_capital(),
            position_state="ENTRY",
            entry_price=20.0,
            long_target_total_position_rmb=10_000,
            current_account_symbol_exposure_rmb=0,
            current_account_cluster_exposure_rmb=0,
            current_long_symbol_exposure_rmb=0,
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
            current_long_symbol_exposure_rmb=0,
            valuation_gate="PASS",
            portfolio_gate="PASS",
            thesis_gate="PASS",
            balance_gate="PASS",
            planned_tranche_fraction=0.40,
        ))
        self.assertEqual(d.authorization_state, "AUTHORIZED")
        self.assertEqual(d.planned_entry_shares, 200)
        self.assertEqual(d.planned_notional_rmb, 4_000.0)

    def test_manual_buy_above_planned_tranche_requires_reauthorization(self):
        d = evaluate_short_mid_pretrade(self.base_short())
        self.assertEqual(d.authorization_state, "AUTHORIZED")
        ok, reason = validate_manual_requested_shares(d, 200)
        self.assertFalse(ok)
        self.assertEqual(reason, "REAUTHORIZATION_REQUIRED_ABOVE_PLANNED_TRANCHE")

    def test_manual_buy_fewer_than_planned_is_allowed(self):
        d = evaluate_short_mid_pretrade(self.base_short(
            strategy_nav_rmb=100_000,
            user_max_loss_this_trade_rmb=1_000,
        ))
        self.assertEqual(d.authorization_state, "AUTHORIZED")
        self.assertGreaterEqual(d.planned_entry_shares, 100)
        ok, reason = validate_manual_requested_shares(d, 100)
        self.assertTrue(ok)
        self.assertEqual(reason, "AUTHORIZED_MANUAL_QUANTITY")


    def test_add_cannot_reset_per_trade_operating_risk(self):
        d = evaluate_short_mid_pretrade(self.base_short(
            position_state="ADD",
            positive_add_confirmation=True,
            current_short_symbol_exposure_rmb=2_000,
            current_trade_planned_risk_rmb=200,
        ))
        # NAV 50k => 0.5% per-trade target = 250. Existing planned risk 200 leaves only 50.
        # Main-board minimum buy quantity is 100 shares, so no ADD is authorized.
        self.assertEqual(d.authorization_state, "NO_TRADE_POSITION_TOO_SMALL_FOR_RISK_BUDGET")
        self.assertEqual(d.allowed_new_loss_rmb, 50.0)
        self.assertEqual(d.max_executable_shares, 0)

    def test_user_trade_loss_limit_is_cumulative_across_tranches(self):
        d = evaluate_short_mid_pretrade(self.base_short(
            position_state="ADD",
            positive_add_confirmation=True,
            strategy_nav_rmb=100_000,
            user_max_loss_this_trade_rmb=300,
            current_short_symbol_exposure_rmb=2_000,
            current_trade_planned_risk_rmb=250,
        ))
        self.assertEqual(d.authorization_state, "NO_TRADE_POSITION_TOO_SMALL_FOR_RISK_BUDGET")
        self.assertEqual(d.allowed_new_loss_rmb, 50.0)

    def test_unknown_buy_quantity_rule_fails_closed(self):
        d = evaluate_short_mid_pretrade(self.base_short(
            min_buy_shares=0,
            buy_increment_shares=0,
        ))
        self.assertEqual(d.authorization_state, "NEED_USER_INPUT")
        self.assertIn("buy_quantity_rule", d.missing_fields)

    def test_star_market_add_supports_one_share_increment_above_200(self):
        d = evaluate_short_mid_pretrade(self.base_short(
            position_state="ADD",
            positive_add_confirmation=True,
            current_short_symbol_exposure_rmb=2_000,
            min_buy_shares=200,
            buy_increment_shares=1,
        ))
        self.assertEqual(d.authorization_state, "AUTHORIZED")
        self.assertEqual(d.max_executable_shares, 250)
        self.assertEqual(d.planned_entry_shares, 250)
        ok, reason = validate_manual_requested_shares(d, 201)
        self.assertTrue(ok)
        self.assertEqual(reason, "AUTHORIZED_MANUAL_QUANTITY")

    def test_bse_entry_supports_one_share_increment_above_100(self):
        d = evaluate_short_mid_pretrade(self.base_short(
            min_buy_shares=100,
            buy_increment_shares=1,
        ))
        self.assertEqual(d.authorization_state, "AUTHORIZED")
        self.assertEqual(d.max_executable_shares, 250)
        self.assertEqual(d.planned_entry_shares, 125)

    def test_main_board_manual_odd_quantity_is_rejected(self):
        d = evaluate_short_mid_pretrade(self.base_short())
        self.assertEqual(d.authorization_state, "AUTHORIZED")
        ok, reason = validate_manual_requested_shares(d, 101)
        self.assertFalse(ok)
        self.assertEqual(reason, "INVALID_BUY_QUANTITY")

    def test_long_target_uses_long_sleeve_not_total_account_symbol_exposure(self):
        d = evaluate_long_pretrade(LongPreTradeInput(
            capital=good_capital(idle=20_000, equity=100_000),
            position_state="ENTRY",
            entry_price=20.0,
            long_target_total_position_rmb=10_000,
            current_account_symbol_exposure_rmb=9_000,
            current_account_cluster_exposure_rmb=9_000,
            current_long_symbol_exposure_rmb=0,
            valuation_gate="PASS",
            portfolio_gate="PASS",
            thesis_gate="PASS",
            balance_gate="PASS",
            planned_tranche_fraction=0.40,
        ))
        # Account concentration still sees all sleeves, but the long target is reduced only by long-sleeve holdings.
        self.assertEqual(d.authorization_state, "AUTHORIZED")
        self.assertEqual(d.planned_entry_shares, 200)
        self.assertEqual(d.planned_notional_rmb, 4_000.0)

    def test_short_invalidation_must_be_below_entry(self):
        d = evaluate_short_mid_pretrade(self.base_short(
            entry_price=20.0,
            invalidation_price=20.5,
        ))
        self.assertEqual(d.authorization_state, "BLOCKED")
        self.assertEqual(d.max_executable_shares, 0)
        self.assertTrue(any("invalidation_price < entry_price" in x for x in d.blocking_reasons))

    def test_short_entry_tranche_fraction_cannot_exceed_one(self):
        d = evaluate_short_mid_pretrade(self.base_short(entry_tranche_fraction=1.5))
        self.assertEqual(d.authorization_state, "BLOCKED")
        self.assertIn("entry_tranche_fraction must be > 0 and <= 1", d.blocking_reasons)

    def test_entry_rejected_when_short_mid_position_already_exists(self):
        d = evaluate_short_mid_pretrade(self.base_short(
            current_short_symbol_exposure_rmb=2_000,
            current_trade_planned_risk_rmb=100,
        ))
        self.assertEqual(d.authorization_state, "BLOCKED")
        self.assertIn("ENTRY requires no existing short-mid position/risk in this symbol", d.blocking_reasons)

    def test_add_rejected_without_existing_short_mid_position(self):
        d = evaluate_short_mid_pretrade(self.base_short(
            position_state="ADD",
            current_short_symbol_exposure_rmb=0,
            current_trade_planned_risk_rmb=0,
            positive_add_confirmation=True,
        ))
        self.assertEqual(d.authorization_state, "BLOCKED")
        self.assertIn("ADD requires an existing short-mid position", d.blocking_reasons)

    def test_long_tranche_fraction_cannot_exceed_one(self):
        d = evaluate_long_pretrade(LongPreTradeInput(
            capital=good_capital(),
            position_state="ENTRY",
            entry_price=20.0,
            long_target_total_position_rmb=10_000,
            current_account_symbol_exposure_rmb=0,
            current_account_cluster_exposure_rmb=0,
            current_long_symbol_exposure_rmb=0,
            valuation_gate="PASS",
            portfolio_gate="PASS",
            thesis_gate="PASS",
            balance_gate="PASS",
            planned_tranche_fraction=1.5,
        ))
        self.assertEqual(d.authorization_state, "BLOCKED")
        self.assertIn("planned_tranche_fraction must be > 0 and <= 1", d.blocking_reasons)

    def test_long_add_requires_existing_long_position(self):
        d = evaluate_long_pretrade(LongPreTradeInput(
            capital=good_capital(),
            position_state="ADD",
            entry_price=20.0,
            long_target_total_position_rmb=10_000,
            current_account_symbol_exposure_rmb=0,
            current_account_cluster_exposure_rmb=0,
            current_long_symbol_exposure_rmb=0,
            valuation_gate="PASS",
            portfolio_gate="PASS",
            thesis_gate="PASS",
            balance_gate="PASS",
            planned_tranche_fraction=0.30,
        ))
        self.assertEqual(d.authorization_state, "BLOCKED")
        self.assertIn("ADD requires an existing long-sleeve position", d.blocking_reasons)


if __name__ == "__main__":
    unittest.main()
