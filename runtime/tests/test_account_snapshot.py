import unittest
import math
import json
import tempfile
from pathlib import Path

from src.core.account_snapshot import CanonicalAccountSnapshot, LocalAccountSnapshotAdapter


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

    def test_exposure_mapping_values_must_be_finite_nonnegative_numbers(self):
        invalid_values = (None, "100", math.nan, math.inf, -1.0, True)
        for field in ("symbol_exposure", "cluster_exposure"):
            for value in invalid_values:
                with self.subTest(field=field, value=value):
                    current = snapshot(**{field: {"synthetic-key": value}})
                    self.assertFalse(current.is_complete_and_valid)
                    self.assertEqual(current.authorization_gate("ENTRY"), "BLOCKED")
                    self.assertEqual(current.authorization_gate("ADD"), "BLOCKED")
                    self.assertEqual(current.authorization_gate("EXIT"), "AUTHORIZED_RISK_REDUCTION")

    def test_nonempty_valid_exposure_mappings_allow_entry(self):
        current = snapshot(
            symbol_exposure={"600000": 1000.0},
            cluster_exposure={"synthetic-cluster": 2000},
        )
        self.assertTrue(current.is_complete_and_valid)
        self.assertEqual(current.authorization_gate("ENTRY"), "AUTHORIZED")

    def test_oversized_integer_from_json_fails_closed_without_crashing(self):
        payload = {
            "as_of": "2026-09-22T07:00:00+08:00",
            "execution_mode": "PAPER",
            "cash": 10**1000,
            "stock_account_equity": 100000.0,
            "positions": {},
            "strategy_virtual_positions": {},
            "symbol_exposure": {},
            "cluster_exposure": {},
            "short_mid_nav": 50000.0,
            "open_initial_risk": 0.0,
            "factor_initial_risk": 0.0,
            "trade_planned_risk": 0.0,
            "data_source": "synthetic-test",
            "reconciliation_state": "RECONCILED",
            "staleness_state": "FRESH",
        }
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "snapshot.json"
            path.write_text(json.dumps(payload), encoding="utf-8")
            loaded = LocalAccountSnapshotAdapter(path).read_snapshot()

        for action in ("ENTRY", "ADD"):
            with self.subTest(action=action):
                self.assertEqual(loaded.authorization_gate(action), "BLOCKED")
        self.assertEqual(loaded.authorization_gate("EXIT"), "AUTHORIZED_RISK_REDUCTION")

    def test_numeric_contract_preserves_supported_ints_and_rejects_bool_nonfinite(self):
        for value in (0, 10**100, 100.0):
            with self.subTest(value_type=type(value).__name__):
                self.assertEqual(snapshot(cash=value).authorization_gate("ENTRY"), "AUTHORIZED")
        for value in (True, False, math.nan, math.inf, -math.inf, 10**1000):
            with self.subTest(value=repr(value)[:32]):
                self.assertEqual(snapshot(cash=value).authorization_gate("ENTRY"), "BLOCKED")

    def test_unknown_actions_fail_closed(self):
        current = snapshot()
        for action in ("BUY", "SELL", "OPEN", "CLOSE", "FOO", "", None):
            self.assertEqual(current.authorization_gate(action), "BLOCKED")


if __name__ == "__main__":
    unittest.main()
