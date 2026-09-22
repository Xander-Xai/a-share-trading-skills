import unittest
import math

from src.core.account_snapshot import CanonicalAccountSnapshot


def snapshot(**overrides):
    data = dict(
        as_of="2026-09-22T07:00:00+08:00",
        execution_mode="PAPER",
        cash=100000.0,
        stock_account_equity=100000.0,
        positions={},
        strategy_virtual_positions={},
        symbol_exposure={},
        cluster_exposure={},
        short_mid_nav=50000.0,
        open_initial_risk=0.0,
        factor_initial_risk=0.0,
        trade_planned_risk=0.0,
        data_source="synthetic-test",
        reconciliation_state="RECONCILED",
        staleness_state="FRESH",
    )
    data.update(overrides)
    return CanonicalAccountSnapshot(**data)


class AccountSnapshotTests(unittest.TestCase):
    def test_fresh_reconciled_snapshot_allows_entry_and_add(self):
        current = snapshot()
        self.assertEqual(current.authorization_gate("ENTRY"), "AUTHORIZED")
        self.assertEqual(current.authorization_gate("ADD"), "AUTHORIZED")

    def test_missing_or_stale_blocks_entry_but_allows_exit(self):
        for state in ("MISSING", "STALE", "CONFLICT", "UNRECONCILED"):
            current = snapshot(reconciliation_state=state)
            self.assertEqual(current.authorization_gate("ENTRY"), "BLOCKED")
            self.assertEqual(current.authorization_gate("EXIT"), "AUTHORIZED_RISK_REDUCTION")
        current = snapshot(staleness_state="STALE")
        self.assertEqual(current.authorization_gate("ADD"), "BLOCKED")

    def test_unknown_governance_state_rejected(self):
        with self.assertRaises(ValueError):
            snapshot(reconciliation_state="GUESS")

    def test_incomplete_or_invalid_fields_block_entry_and_add(self):
        for field, value in (("cash", None), ("stock_account_equity", None), ("open_initial_risk", None), ("factor_initial_risk", math.nan), ("trade_planned_risk", -1.0), ("positions", None)):
            current = snapshot(**{field: value})
            self.assertFalse(current.is_complete_and_valid)
            self.assertEqual(current.authorization_gate("ENTRY"), "BLOCKED")
            self.assertEqual(current.authorization_gate("ADD"), "BLOCKED")

    def test_empty_exposure_mappings_are_valid_and_exit_survives_incomplete(self):
        current = snapshot()
        self.assertTrue(current.is_complete_and_valid)
        self.assertEqual(current.authorization_gate("EXIT"), "AUTHORIZED_RISK_REDUCTION")
        self.assertEqual(snapshot(cash=None).authorization_gate("EXIT"), "AUTHORIZED_RISK_REDUCTION")

    def test_unknown_actions_fail_closed(self):
        current = snapshot()
        for action in ("BUY", "SELL", "OPEN", "CLOSE", "FOO", "", None):
            self.assertEqual(current.authorization_gate(action), "BLOCKED")


if __name__ == "__main__":
    unittest.main()
