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


if __name__ == "__main__":
    unittest.main()
