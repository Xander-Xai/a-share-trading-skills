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
            {"reports/trades/private/report.md"},
            {"runtime/portfolio_instances.json"},
        ):
            with patch.object(audit, "_git_tracked_paths", return_value=tracked):
                checks = audit.run_audit()
            self.assertFalse(next(c for c in checks if c.name == "private_tracked_paths").ok)

    def test_public_example_path_is_not_private(self):
        with patch.object(audit, "_git_tracked_paths", return_value={"runtime/portfolio_instances.example.json"}):
            checks = audit.run_audit()
        self.assertTrue(next(c for c in checks if c.name == "private_tracked_paths").ok)

    def test_every_declared_private_prefix_is_required_in_gitignore(self):
        complete = "\n".join(audit.PRIVATE_PATH_PREFIXES)
        self.assertTrue(audit._private_paths_ignored(complete).ok)
        for missing in audit.PRIVATE_PATH_PREFIXES:
            synthetic = "\n".join(prefix for prefix in audit.PRIVATE_PATH_PREFIXES if prefix != missing)
            result = audit._private_paths_ignored(synthetic)
            self.assertFalse(result.ok)
            self.assertIn(missing, result.detail)

    def test_effective_git_ignore_rules_are_used(self):
        calls = []

        def fake_run(args, **kwargs):
            calls.append(args)
            return subprocess.CompletedProcess(args, 0, "", "")

        with patch.object(audit.subprocess, "run", side_effect=fake_run):
            result = audit._private_paths_ignored()
        self.assertTrue(result.ok)
        self.assertTrue(calls)
        self.assertTrue(all("check-ignore" in call for call in calls))

    def test_effective_git_ignore_missing_rule_fails(self):
        def fake_run(args, **kwargs):
            path = args[-1]
            code = 1 if path.startswith("runtime/private/") else 0
            return subprocess.CompletedProcess(args, code, "", "")

        with patch.object(audit.subprocess, "run", side_effect=fake_run):
            result = audit._private_paths_ignored()
        self.assertFalse(result.ok)
        self.assertIn("runtime/private/", result.detail)

    def test_effective_git_ignore_command_failure_is_not_privacy_pass(self):
        error = subprocess.CalledProcessError(128, ["git", "check-ignore"], stderr="bad repo")

        def fake_run(*args, **kwargs):
            raise error

        with patch.object(audit.subprocess, "run", side_effect=fake_run):
            result = audit._private_paths_ignored()
        self.assertFalse(result.ok)
        self.assertIn("NOT_EVALUATED", result.detail)

    def test_dotfile_rule_does_not_cover_regular_private_probe(self):
        self.assertFalse(audit._private_paths_ignored(".*\n").ok)

    def test_commented_private_rule_fails(self):
        self.assertFalse(audit._private_paths_ignored("# runtime/private/\n").ok)

    def test_later_negation_fails_effective_ignore_check(self):
        self.assertFalse(audit._private_paths_ignored("runtime/private/\n!runtime/private/**\n").ok)

    def test_broader_effective_rule_passes(self):
        self.assertTrue(audit._private_paths_ignored("runtime/**\nreports/**\n").ok)

    def test_internal_links_use_tracked_markdown_only(self):
        self.assertTrue(audit._internal_links_exist({"README.md"}).ok)
        self.assertFalse(audit._internal_links_exist({"docs/public.md"}).ok)


if __name__ == "__main__":
    unittest.main()
