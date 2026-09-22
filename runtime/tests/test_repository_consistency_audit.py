import subprocess
import unittest
from unittest.mock import patch

from runtime import repository_consistency_audit as audit


class RepositoryConsistencyAuditTests(unittest.TestCase):
    def test_git_enumeration_failure_is_not_a_privacy_pass(self):
        with patch.object(audit.subprocess, "run", side_effect=FileNotFoundError("git")):
            checks = audit.run_audit()
        by_name = {check.name: check for check in checks}
        self.assertFalse(by_name["tracked_file_enumeration"].ok)
        self.assertFalse(by_name["no_tracked_personal_instances"].ok)

    def test_git_enumeration_called_process_error_is_not_a_privacy_pass(self):
        error = subprocess.CalledProcessError(128, ["git", "ls-files"], stderr="bad repo")
        with patch.object(audit.subprocess, "run", side_effect=error):
            checks = audit.run_audit()
        by_name = {check.name: check for check in checks}
        self.assertFalse(by_name["tracked_file_enumeration"].ok)
        self.assertFalse(by_name["no_tracked_personal_instances"].ok)

    def test_declared_private_directories_fail_when_tracked(self):
        for tracked in (
            {"runtime/pretrade_authorizations/test.json"},
            {"runtime/private/account.json"},
            {"runtime/state/private/state.json"},
            {"reports/private/report.md"},
            {"runtime/portfolio_instances.json"},
        ):
            with patch.object(audit, "_git_tracked_paths", return_value=tracked):
                checks = audit.run_audit()
            self.assertFalse(next(c for c in checks if c.name == "private_tracked_paths").ok)

    def test_public_example_path_is_not_private(self):
        with patch.object(audit, "_git_tracked_paths", return_value={"runtime/portfolio_instances.example.json"}):
            checks = audit.run_audit()
        self.assertTrue(next(c for c in checks if c.name == "private_tracked_paths").ok)

    def test_internal_links_use_tracked_markdown_only(self):
        self.assertTrue(audit._internal_links_exist({"README.md"}).ok)
        self.assertFalse(audit._internal_links_exist({"docs/public.md"}).ok)


if __name__ == "__main__":
    unittest.main()
