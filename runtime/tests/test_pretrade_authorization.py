import json
import tempfile
import unittest
from pathlib import Path

from src.core.pretrade_authorization import persist_pretrade_card


class PreTradeAuthorizationPersistenceTests(unittest.TestCase):
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
