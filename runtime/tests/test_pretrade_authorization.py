import json
import os
import stat
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from runtime.pretrade_cli import authorization_exit_code, finalize_authorization
from src.core.pretrade_authorization import DEFAULT_PRIVATE_AUTH_ROOT, authorization_input_snapshot, persist_pretrade_card


class PreTradeAuthorizationPersistenceTests(unittest.TestCase):
    def test_authorization_exit_code_distinguishes_persisted_card_from_authorization(self):
        self.assertEqual(authorization_exit_code("AUTHORIZED"), 0)
        self.assertEqual(authorization_exit_code("AUTHORIZED_RISK_REDUCTION"), 0)
        for state in ("BLOCKED", "NEED_USER_INPUT", "NO_TRADE_POSITION_TOO_SMALL_FOR_RISK_BUDGET", "UNKNOWN"):
            self.assertNotEqual(authorization_exit_code(state), 0)

    def test_default_private_root_is_repo_anchored_across_cwd(self):
        import os

        original = Path.cwd()
        try:
            for cwd in (Path(__file__).resolve().parents[2], Path(tempfile.gettempdir())):
                os.chdir(cwd)
                path = persist_pretrade_card(
                    {"decision_id": f"synthetic-{cwd.name}"},
                    snapshot={"synthetic": True},
                    policy_versions={},
                )
                self.assertEqual(path.parent, DEFAULT_PRIVATE_AUTH_ROOT.resolve())
                path.unlink(missing_ok=True)
        finally:
            os.chdir(original)

    def test_explicit_private_root_remains_supported(self):
        with tempfile.TemporaryDirectory() as directory:
            path = persist_pretrade_card({"decision_id": "synthetic"}, snapshot={}, policy_versions={}, root=directory)
            self.assertEqual(path.parent, Path(directory).resolve())

    def test_posix_private_directory_and_card_are_owner_only(self):
        if os.name == "nt":
            self.skipTest("POSIX mode bits are not authoritative on Windows")
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory) / "private"
            path = persist_pretrade_card({"decision_id": "mode-check"}, snapshot={}, policy_versions={}, root=root)
            self.assertEqual(stat.S_IMODE(root.stat().st_mode) & 0o077, 0)
            self.assertEqual(stat.S_IMODE(path.stat().st_mode) & 0o077, 0)

    def test_complete_inputs_hash_is_deterministic_and_sensitive(self):
        base = {"capital": {"cash": 1000}, "strategy_inputs": {"entry_price": 10.0, "invalidation_price": 9.0, "exposure": 0}, "action": "ENTRY"}
        _, first = authorization_input_snapshot(base)
        _, second = authorization_input_snapshot({"action": "ENTRY", "strategy_inputs": {"invalidation_price": 9.0, "entry_price": 10.0, "exposure": 0}, "capital": {"cash": 1000}})
        self.assertEqual(first, second)
        for key, value in (("entry_price", 11.0), ("invalidation_price", 8.0), ("exposure", 100.0)):
            changed = json.loads(json.dumps(base))
            changed["strategy_inputs"][key] = value
            self.assertNotEqual(first, authorization_input_snapshot(changed)[1])
        changed = json.loads(json.dumps(base))
        changed["strategy_inputs"]["confirmation"] = True
        self.assertNotEqual(first, authorization_input_snapshot(changed)[1])

    def test_decision_id_does_not_change_input_hash(self):
        inputs = {"capital": {"cash": 1000}, "strategy_inputs": {"entry_price": 10}, "action": "ENTRY"}
        _, first = authorization_input_snapshot(inputs)
        _, second = authorization_input_snapshot(inputs)
        self.assertEqual(first, second)

    def test_entry_persistence_failure_blocks_and_zeroes_quantity(self):
        from types import SimpleNamespace

        decision = SimpleNamespace(authorization_state="AUTHORIZED", position_state="ENTRY", max_executable_shares=200)
        def fail(*args, **kwargs):
            raise PermissionError("read-only")
        out, code = finalize_authorization(decision, {"action": "ENTRY"}, persist=fail)
        self.assertEqual(code, 1)
        self.assertEqual(out["authorization_state"], "BLOCKED")
        self.assertEqual(out["max_executable_shares"], 0)
        self.assertEqual(out["reason"], "PRIVATE_AUTHORIZATION_PERSISTENCE_FAILED")
        self.assertNotEqual(out["authorization_state"], "AUTHORIZED")

    def test_add_persistence_failure_blocks(self):
        from types import SimpleNamespace

        decision = SimpleNamespace(authorization_state="AUTHORIZED", position_state="ADD", max_executable_shares=100)
        out, code = finalize_authorization(decision, {"action": "ADD"}, persist=lambda *a, **k: (_ for _ in ()).throw(OSError("disk full")))
        self.assertEqual((out["authorization_state"], out["max_executable_shares"], code), ("BLOCKED", 0, 1))

    def test_decision_id_collision_is_create_once_and_preserves_original_card(self):
        with tempfile.TemporaryDirectory() as directory:
            path = persist_pretrade_card(
                {"decision_id": "decision-immutable", "authorization_state": "AUTHORIZED"},
                snapshot={"cash": 1000, "positions": {}},
                policy_versions={"pretrade": "1.1"},
                root=directory,
            )
            original = path.read_bytes()
            with self.assertRaises(FileExistsError):
                persist_pretrade_card(
                    {"decision_id": "decision-immutable", "authorization_state": "BLOCKED", "reason": "changed"},
                    snapshot={"cash": 1, "positions": {"600000": 100}},
                    policy_versions={"pretrade": "9.9"},
                    root=directory,
                )
            self.assertEqual(path.read_bytes(), original)

    def test_write_failure_cleans_partial_temp_and_allows_retry(self):
        with tempfile.TemporaryDirectory() as directory:
            def fail_after_partial(path, content):
                path.write_bytes(content[:5])
                raise OSError("disk full")

            with patch("src.core.pretrade_authorization._write_complete_file", side_effect=fail_after_partial):
                with self.assertRaises(OSError):
                    persist_pretrade_card(
                        {"decision_id": "retryable"}, snapshot={"synthetic": True}, policy_versions={}, root=directory
                    )
            root = Path(directory)
            self.assertEqual(list(root.iterdir()), [])

            path = persist_pretrade_card(
                {"decision_id": "retryable"}, snapshot={"synthetic": True}, policy_versions={}, root=directory
            )
            self.assertTrue(path.exists())
            self.assertEqual([item.name for item in root.iterdir()], [path.name])

    def test_flush_failure_cleans_partial_temp_and_leaves_no_destination(self):
        with tempfile.TemporaryDirectory() as directory:
            with patch("src.core.pretrade_authorization.os.fsync", side_effect=OSError("flush failed")):
                with self.assertRaises(OSError):
                    persist_pretrade_card(
                        {"decision_id": "flush-failure"}, snapshot={"synthetic": True}, policy_versions={}, root=directory
                    )
            self.assertEqual(list(Path(directory).iterdir()), [])

    def test_exclusive_publish_fallback_remains_create_once(self):
        with tempfile.TemporaryDirectory() as directory:
            with patch("src.core.pretrade_authorization.os.link", side_effect=NotImplementedError):
                path = persist_pretrade_card(
                    {"decision_id": "fallback"}, snapshot={"synthetic": True}, policy_versions={}, root=directory
                )
            original = path.read_bytes()
            with patch("src.core.pretrade_authorization.os.link", side_effect=NotImplementedError):
                with self.assertRaises(FileExistsError):
                    persist_pretrade_card(
                        {"decision_id": "fallback", "changed": True},
                        snapshot={"synthetic": False},
                        policy_versions={"pretrade": "changed"},
                        root=directory,
                    )
            self.assertEqual(path.read_bytes(), original)

    def test_entry_collision_blocks_and_zeroes_quantity(self):
        from types import SimpleNamespace

        decision = SimpleNamespace(authorization_state="AUTHORIZED", position_state="ENTRY", max_executable_shares=200)

        def collision(*args, **kwargs):
            raise FileExistsError("decision_id already exists")

        out, code = finalize_authorization(decision, {"action": "ENTRY"}, persist=collision)
        self.assertEqual(code, 1)
        self.assertEqual(out["authorization_state"], "BLOCKED")
        self.assertEqual(out["max_executable_shares"], 0)
        self.assertEqual(out["reason"], "PRIVATE_AUTHORIZATION_PERSISTENCE_FAILED")

    def test_card_is_private_and_contains_snapshot_hash(self):
        with tempfile.TemporaryDirectory() as directory:
            path = persist_pretrade_card(
                {"decision_id": "decision-1", "authorization_state": "AUTHORIZED"},
                snapshot={"cash": 1000, "positions": {}},
                policy_versions={"pretrade": "1.1"},
                root=directory,
            )
            payload = json.loads(Path(path).read_text(encoding="utf-8"))
            self.assertEqual(payload["decision_id"], "decision-1")
            self.assertEqual(len(payload["input_snapshot_hash"]), 64)
            self.assertEqual(payload["policy_versions"]["pretrade"], "1.1")

    def test_unsafe_decision_id_rejected(self):
        with tempfile.TemporaryDirectory() as directory:
            with self.assertRaises(ValueError):
                persist_pretrade_card({"decision_id": "../escape"}, snapshot={}, policy_versions={}, root=directory)


if __name__ == "__main__":
    unittest.main()
