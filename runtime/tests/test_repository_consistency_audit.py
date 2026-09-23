import json
import subprocess
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from runtime import repository_consistency_audit as audit


class RepositoryConsistencyAuditTests(unittest.TestCase):
    def _current_state(self):
        state, result = audit._load_current_state()
        self.assertTrue(result.ok, result.detail)
        return json.loads(json.dumps(state))

    def _semantic_check(self, state, name):
        return next(check for check in audit._state_semantics_checks(state) if check.name == name)

    def test_registry_policy_version_drift_fails(self):
        state = self._current_state()
        original_read = audit._read

        def drifted_read(path):
            if path == state["policy_versions"]["capital_allocation"]["path"]:
                return "# Capital Allocation Contract v99\n"
            return original_read(path)

        with patch.object(audit, "_read", side_effect=drifted_read):
            check = next(c for c in audit._registry_version_checks(state) if c.name == "registry_policy_versions")
        self.assertFalse(check.ok)

    def test_registry_skill_version_drift_fails(self):
        state = self._current_state()
        state["skill_versions"]["short_midterm_stock_selection"]["version"] = "99.0"
        check = next(c for c in audit._registry_version_checks(state) if c.name == "registry_skill_versions")
        self.assertFalse(check.ok)

    def test_missing_readme_repository_map_target_fails(self):
        state = self._current_state()
        missing = "docs/not-a-real-repository-target.md"
        state["repository_map_paths"].append(missing)
        readme = audit._read("README.md").replace("## Rule precedence", f"| `{missing}` | invalid target |\n\n## Rule precedence")
        result = audit._repository_map_consistency(readme, state, audit._git_tracked_paths())
        self.assertFalse(result.ok)
        self.assertIn(missing, result.detail)

    def test_registry_auto_order_drift_fails(self):
        state = self._current_state()
        state["runtime"]["auto_order"] = True
        self.assertFalse(self._semantic_check(state, "runtime_order_safety").ok)

    def test_scheduled_evidence_allowlist_drift_fails(self):
        state = self._current_state()
        state["scheduled_evidence_allowlist"].append("reports/private/daily/")
        self.assertFalse(self._semantic_check(state, "daily_workflow_write_model").ok)

    def test_actions_pull_request_setting_must_be_documented(self):
        state = self._current_state()
        state["github_actions_permissions"]["allow_create_and_approve_pull_requests"] = False
        self.assertFalse(self._semantic_check(state, "daily_workflow_write_model").ok)

    def test_daily_workflow_direct_main_push_fails(self):
        state = self._current_state()
        workflow = audit._read(".github/workflows/a-share-daily-monitor.yml")
        for direct_push in ("git push origin HEAD:main", "git push --force origin main"):
            with self.subTest(direct_push=direct_push):
                unsafe_workflow = workflow.replace('git push origin "$branch"', direct_push)
                check = audit._daily_workflow_write_model_check(state, unsafe_workflow)
                self.assertFalse(check.ok)

    def test_daily_workflow_must_not_submit_pr_approvals(self):
        state = self._current_state()
        workflow = audit._read(".github/workflows/a-share-daily-monitor.yml")
        workflow = workflow.replace("gh pr create", "gh pr review --approve")
        self.assertFalse(audit._daily_workflow_write_model_check(state, workflow).ok)

    def test_daily_workflow_dispatches_required_governance_for_bot_pr(self):
        state = self._current_state()
        workflow = audit._read(".github/workflows/a-share-daily-monitor.yml")
        self.assertFalse(audit._daily_workflow_write_model_check(state, workflow.replace("gh workflow run repository-governance.yml", "gh workflow run other.yml")).ok)

    def test_existing_evidence_branch_is_pushed_after_optional_commit(self):
        state = self._current_state()
        workflow = audit._read(".github/workflows/a-share-daily-monitor.yml")
        unsafe = workflow.replace(
            '            git commit -m "chore: update public market evidence"\n          fi\n          # This also fast-forwards a previously behind evidence branch when\n          # the new artifact itself has no staged data delta.\n          git push origin "$branch"',
            '            git commit -m "chore: update public market evidence"\n            git push origin "$branch"\n          fi',
        )
        self.assertNotEqual(unsafe, workflow)
        self.assertFalse(audit._daily_workflow_write_model_check(state, unsafe).ok)

    def test_champion_drift_fails(self):
        state = self._current_state()
        state["models"]["champion"]["status"] = "SHADOW_ONLY"
        self.assertFalse(self._semantic_check(state, "model_governance").ok)

    def test_erg_silent_promotion_fails(self):
        state = self._current_state()
        state["models"]["erg"]["status"] = "ACTIVE"
        self.assertFalse(self._semantic_check(state, "model_governance").ok)

    def test_strategy_id_mismatch_fails(self):
        state = self._current_state()
        state["strategies"]["short_mid"]["strategy_id"] = "wrong_strategy"
        self.assertFalse(self._semantic_check(state, "strategy_context").ok)

    def test_sleeve_mismatch_fails(self):
        state = self._current_state()
        state["strategies"]["long"]["sleeve"] = "short_mid"
        self.assertFalse(self._semantic_check(state, "strategy_context").ok)

    def test_historical_document_cannot_be_marked_as_current(self):
        state = self._current_state()
        state["historical_document_policy"]["current_authority"] = True
        self.assertFalse(self._semantic_check(state, "historical_document_classification").ok)

    def test_invalid_state_namespace_fails(self):
        state = self._current_state()
        state["state_namespaces"]["position_state"].append("READY")
        self.assertFalse(self._semantic_check(state, "state_namespaces").ok)

    def test_broken_internal_markdown_link_fails(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            source = root / "docs" / "source.md"
            source.parent.mkdir(parents=True)
            source.write_text("[missing](not-present.md)\n", encoding="utf-8")
            with patch.object(audit, "ROOT", root):
                result = audit._internal_links_exist({"docs/source.md"})
        self.assertFalse(result.ok)

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

    def test_git_tracked_paths_uses_nul_framing_for_unicode_and_spaces(self):
        raw = "reports/测试文件.json\0reports/file with spaces.txt\0".encode("utf-8")
        completed = subprocess.CompletedProcess(["git", "ls-files", "-z"], 0, raw, b"")
        with patch.object(audit.subprocess, "run", return_value=completed) as run:
            paths = audit._git_tracked_paths()
        self.assertEqual(paths, {"reports/测试文件.json", "reports/file with spaces.txt"})
        self.assertIn("-z", run.call_args.args[0])

    def test_private_unicode_tracked_path_is_detected(self):
        with patch.object(audit, "_git_tracked_paths", return_value={"runtime/private/账户测试.json"}):
            checks = audit.run_audit()
        self.assertFalse(next(c for c in checks if c.name == "private_tracked_paths").ok)

    def test_declared_private_directories_fail_when_tracked(self):
        for tracked in (
            {"runtime/pretrade_authorizations/test.json"},
            {"runtime/private/account.json"},
            {"runtime/state/private/state.json"},
            {"runtime/state/sample_evidence/daily/sample.jsonl"},
            {"reports/private/report.md"},
            {"reports/daily/report.md"},
            {"reports/trades/private/report.md"},
            {"runtime/portfolio_instances.json"},
            {"runtime/config/short_mid_universe.json"},
            {"runtime/config/sample_registry.json"},
        ):
            with patch.object(audit, "_git_tracked_paths", return_value=tracked):
                checks = audit.run_audit()
            self.assertFalse(next(c for c in checks if c.name == "private_tracked_paths").ok)

    def test_public_example_path_is_not_private(self):
        with patch.object(audit, "_git_tracked_paths", return_value={"runtime/portfolio_instances.example.json"}):
            checks = audit.run_audit()
        self.assertTrue(next(c for c in checks if c.name == "private_tracked_paths").ok)

    def test_every_declared_private_prefix_is_required_in_gitignore(self):
        complete = "\n".join((*audit.PRIVATE_PATH_PREFIXES, *audit.PRIVATE_EXACT_PATHS))
        self.assertTrue(audit._private_paths_ignored(complete).ok)
        for missing in (*audit.PRIVATE_PATH_PREFIXES, *audit.PRIVATE_EXACT_PATHS):
            synthetic = "\n".join((
                *(prefix for prefix in audit.PRIVATE_PATH_PREFIXES if prefix != missing),
                *(path for path in audit.PRIVATE_EXACT_PATHS if path != missing),
            ))
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

    def test_narrow_json_only_rule_fails_probe_matrix(self):
        self.assertFalse(audit._private_paths_ignored("runtime/private/*.json\n").ok)

    def test_single_filename_rule_fails_probe_matrix(self):
        self.assertFalse(audit._private_paths_ignored("runtime/private/__governance_probe__.json\n").ok)

    def test_internal_links_use_tracked_markdown_only(self):
        self.assertTrue(audit._internal_links_exist({"README.md"}).ok)
        self.assertFalse(audit._internal_links_exist({"docs/public.md"}).ok)

    def test_public_case_fixtures_require_explicit_synthetic_marker(self):
        with patch.object(audit, "_read", return_value=audit.SYNTHETIC_MARKER):
            self.assertTrue(audit._public_synthetic_fixtures(set(audit.PUBLIC_SYNTHETIC_FIXTURES)).ok)
        with patch.object(audit, "_read", return_value="fixture without declaration"):
            result = audit._public_synthetic_fixtures(set(audit.PUBLIC_SYNTHETIC_FIXTURES))
        self.assertFalse(result.ok)


if __name__ == "__main__":
    unittest.main()
