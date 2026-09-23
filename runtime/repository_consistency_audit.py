from __future__ import annotations

import json
import re
import os
import subprocess
import sys
import tempfile
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterable


ROOT = Path(__file__).resolve().parents[1]

PRIVATE_PATH_PREFIXES = (
    "runtime/private/",
    "runtime/state/private/",
    "runtime/state/sample_evidence/",
    "runtime/pretrade_authorizations/",
    "reports/private/",
    "reports/daily/",
    "reports/trades/private/",
)
PRIVATE_PATH_PROBES = (
    "__governance_probe__.json",
    "governance_probe.txt",
    "governance_probe",
    "nested/governance_probe.yaml",
)
PRIVATE_EXACT_PATHS = (
    "runtime/portfolio_instances.json",
    "runtime/portfolio_instances.local.json",
    "runtime/config/short_mid_universe.json",
    "runtime/config/sample_registry.json",
)
PUBLIC_SYNTHETIC_FIXTURES = (
    "skills/a-share-short-midterm-stock-selection/examples/synthetic-watchlist-case-study.md",
    "skills/a-share-short-midterm-stock-selection/examples/synthetic-watchlist.json",
    "skills/a-share-short-midterm-stock-selection/examples/synthetic-forward-cohort.md",
    "skills/a-share-short-midterm-stock-selection/examples/synthetic-forward-cohort.json",
    "skills/a-share-short-midterm-stock-selection/references/synthetic-core-pool-case.md",
    "skills/a-share-retirement-investing/examples/synthetic-retirement-allocation.md",
    "skills/a-share-retirement-investing/references/synthetic-seed-watchlist.md",
)
SYNTHETIC_MARKER = "SYNTHETIC EXAMPLE / NOT REAL USER DATA"
CURRENT_STATE_PATH = "configs/governance/current-state.json"
EXPECTED_GOVERNANCE_MODE = "SOLO_MAINTAINER"
POSITION_STATES = {"FLAT", "ENTRY", "ADD", "HOLD", "TRIM", "EXIT", "COOLDOWN"}
POSITION_INTENTS = {"ENTRY", "ADD", "TRIM", "EXIT"}
EXECUTION_SIDES = {"BUY", "SELL"}
RESEARCH_STATES = {"REJECT", "WATCH", "CANDIDATE", "CONFIRMED", "INVALIDATED"}
AUTHORIZATION_STATES = {
    "AUTHORIZED", "AUTHORIZED_RISK_REDUCTION", "NEED_USER_INPUT", "BLOCKED",
    "NO_TRADE_POSITION_TOO_SMALL_FOR_RISK_BUDGET",
    "NO_TRADE_TRANCHE_ROUNDS_BELOW_MINIMUM",
    "NO_TRADE_POSITION_TOO_SMALL_FOR_CAPS", "UNKNOWN",
}
MONITOR_STATES = {
    "NO_ACTION", "NO_ACTION_STRATEGY_MISMATCH", "NO_ACTION_DATA_MISSING", "REJECT",
    "WAIT", "WAIT_NO_CHASE", "WATCH", "READY", "EXIT_REVIEW", "RISK_EXIT_REVIEW",
    "TRIM_REVIEW", "ADD_REVIEW", "HOLD_REVIEW", "NO_NEW_ENTRY", "EVENT_REVIEW",
    "REFRESH_FULL_GATES", "REFRESH_SETUP", "RISK_REVIEW",
}


@dataclass(frozen=True)
class CheckResult:
    name: str
    ok: bool
    detail: str


class GitEnumerationError(RuntimeError):
    pass


def _read(path: str) -> str:
    target = ROOT / path
    if not target.exists():
        raise FileNotFoundError(path)
    return target.read_text(encoding="utf-8")


def _contains_all(path: str, needles: Iterable[str]) -> CheckResult:
    text = _read(path)
    missing = [needle for needle in needles if needle not in text]
    return CheckResult(
        name=f"contains:{path}",
        ok=not missing,
        detail="ok" if not missing else f"missing: {missing}",
    )


def _private_paths_ignored(gitignore_text: str | None = None) -> CheckResult:
    """Verify effective Git ignore behavior, including overrides and negations.

    The optional text argument is retained for small unit-test fixtures. The
    production audit always evaluates the repository's effective rules via
    ``git check-ignore``; a failed invocation is never treated as a privacy
    pass.
    """
    temporary_root = None
    check_root = ROOT
    if gitignore_text is not None:
        temporary_root = tempfile.TemporaryDirectory()
        check_root = Path(temporary_root.name)
        (check_root / ".gitignore").write_text(gitignore_text, encoding="utf-8")
        try:
            subprocess.run(
                ["git", "init", "-q"], cwd=check_root, check=True,
                capture_output=True, text=True,
            )
        except (OSError, subprocess.CalledProcessError) as exc:
            temporary_root.cleanup()
            return CheckResult("private_paths_ignored", False, f"NOT_EVALUATED: git init failure: {exc}")

    failures: list[str] = []
    errors: list[str] = []
    candidates = [f"{prefix}{probe}" for prefix in PRIVATE_PATH_PREFIXES for probe in PRIVATE_PATH_PROBES]
    candidates.extend(PRIVATE_EXACT_PATHS)
    for candidate in candidates:
        prefix_failed = False
        try:
            result = subprocess.run(
                ["git", "check-ignore", "-v", "--no-index", "--", candidate],
                cwd=check_root,
                capture_output=True,
            )
        except (OSError, subprocess.CalledProcessError) as exc:
            errors.append(f"{candidate}: {exc}")
            continue
        if result.returncode == 0:
            continue
        if result.returncode == 1:
            failures.append(candidate)
            continue
        raw_detail = result.stderr or result.stdout or b"git check-ignore failed"
        detail = os.fsdecode(raw_detail).strip() if isinstance(raw_detail, bytes) else str(raw_detail).strip()
        errors.append(f"{candidate}: {detail}")

    result = CheckResult(
            name="private_paths_ignored",
            ok=not errors and not failures,
            detail=(f"NOT_EVALUATED: git check-ignore failure: {errors}" if errors
                    else "private runtime paths are effectively ignored" if not failures
                    else f"not ignored: {failures}"),
        )
    if temporary_root is not None:
        temporary_root.cleanup()
    return result


def _public_synthetic_fixtures(tracked_paths: set[str] | None) -> CheckResult:
    if tracked_paths is None:
        return CheckResult("public_synthetic_fixtures", False, "NOT_EVALUATED: tracked file enumeration failed")
    missing = [path for path in PUBLIC_SYNTHETIC_FIXTURES if path not in tracked_paths]
    invalid = []
    for path in PUBLIC_SYNTHETIC_FIXTURES:
        if path not in tracked_paths:
            continue
        try:
            if SYNTHETIC_MARKER not in _read(path):
                invalid.append(path)
        except (OSError, UnicodeError) as exc:
            invalid.append(f"{path}: {type(exc).__name__}")
    ok = not missing and not invalid
    return CheckResult(
        "public_synthetic_fixtures",
        ok,
        "all tracked case fixtures carry the synthetic marker" if ok else f"missing={missing}; marker_missing_or_unreadable={invalid}",
    )


def _not_contains(path: str, needles: Iterable[str]) -> CheckResult:
    text = _read(path)
    found = [needle for needle in needles if needle in text]
    return CheckResult(
        name=f"not_contains:{path}",
        ok=not found,
        detail="ok" if not found else f"stale/conflicting text: {found}",
    )


def _header_version(path: str, pattern: str, expected: str) -> CheckResult:
    first = _read(path).splitlines()[0]
    match = re.search(pattern, first)
    actual = match.group(1) if match else None
    return CheckResult(
        name=f"version:{path}",
        ok=actual == expected,
        detail=f"expected={expected}, actual={actual}",
    )


def _yaml_skill_version(path: str, expected: str) -> CheckResult:
    text = _read(path)
    match = re.search(r"(?m)^\s*version:\s*[\"']?([^\"'\n]+)[\"']?\s*$", text)
    actual = match.group(1).strip() if match else None
    return CheckResult(
        name=f"skill_version:{path}",
        ok=actual == expected,
        detail=f"expected={expected}, actual={actual}",
    )


def _load_current_state() -> tuple[dict[str, Any] | None, CheckResult]:
    try:
        state = json.loads(_read(CURRENT_STATE_PATH))
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        return None, CheckResult("current_state_registry", False, f"NOT_EVALUATED: {type(exc).__name__}: {exc}")
    if not isinstance(state, dict):
        return None, CheckResult("current_state_registry", False, "registry root must be a JSON object")
    required = {
        "schema_version", "governance_mode", "branch_protection", "policy_versions", "skill_versions",
        "strategies", "runtime", "models", "storage_namespaces", "historical_document_policy",
        "state_namespaces", "privacy_boundary_version", "repository_map_paths",
    }
    missing = sorted(required - set(state))
    return state, CheckResult(
        "current_state_registry", not missing and state.get("schema_version") == "1.0",
        "schema 1.0 present" if not missing and state.get("schema_version") == "1.0" else f"missing={missing}; schema_version={state.get('schema_version')!r}",
    )


def _registry_version_checks(state: dict[str, Any] | None) -> list[CheckResult]:
    if state is None:
        return [CheckResult("registry_policy_versions", False, "NOT_EVALUATED: current-state registry unavailable"),
                CheckResult("registry_skill_versions", False, "NOT_EVALUATED: current-state registry unavailable"),
                CheckResult("registry_document_versions", False, "NOT_EVALUATED: current-state registry unavailable")]
    results: list[CheckResult] = []
    policy_versions = state.get("policy_versions")
    policy_failures: list[str] = []
    if not isinstance(policy_versions, dict) or not policy_versions:
        policy_failures.append("policy_versions missing/invalid")
    else:
        for key, item in policy_versions.items():
            if not isinstance(item, dict) or not isinstance(item.get("path"), str) or not isinstance(item.get("version"), str):
                policy_failures.append(f"{key}: invalid registry entry")
                continue
            path = item["path"]
            try:
                first = _read(path).splitlines()[0]
            except (OSError, UnicodeError, IndexError):
                policy_failures.append(f"{key}: missing/empty {path}")
                continue
            match = re.search(r"\bv(\d+(?:\.\d+)*)\s*$", first)
            actual = None if match is None else match.group(1)
            if actual != item["version"]:
                policy_failures.append(f"{path}: registry={item['version']}, actual={actual}")
    results.append(CheckResult("registry_policy_versions", not policy_failures, "ok" if not policy_failures else str(policy_failures)))

    skill_versions = state.get("skill_versions")
    skill_failures: list[str] = []
    if not isinstance(skill_versions, dict) or not skill_versions:
        skill_failures.append("skill_versions missing/invalid")
    else:
        for key, item in skill_versions.items():
            if not isinstance(item, dict) or not isinstance(item.get("path"), str) or not isinstance(item.get("version"), str):
                skill_failures.append(f"{key}: invalid registry entry")
                continue
            try:
                text = _read(item["path"])
            except (OSError, UnicodeError) as exc:
                skill_failures.append(f"{item['path']}: {type(exc).__name__}")
                continue
            match = re.search(r"(?m)^\s*version:\s*[\"']?([^\"'\n]+)[\"']?\s*$", text)
            actual = None if match is None else match.group(1).strip()
            if actual != item["version"]:
                skill_failures.append(f"{item['path']}: registry={item['version']}, actual={actual}")
    results.append(CheckResult("registry_skill_versions", not skill_failures, "ok" if not skill_failures else str(skill_failures)))

    docs = {
        "README.md": ("capital_eligibility", "pre_trade_authorization", "capital_allocation", "automation_execution", "research_model", "canonical_pit_data"),
        "skills/a-share-retirement-investing/README.md": ("capital_allocation", "automation_execution"),
        "skills/a-share-short-midterm-stock-selection/README.md": ("capital_allocation", "automation_execution"),
    }
    labels = {
        "capital_eligibility": "Capital Eligibility",
        "pre_trade_authorization": "Pre-Trade Authorization",
        "capital_allocation": "Capital / Risk",
        "automation_execution": "Automation / Execution",
        "research_model": "Research / Model",
        "canonical_pit_data": "Canonical PIT Data",
    }
    document_failures: list[str] = []
    versions = state.get("policy_versions")
    for path, keys in docs.items():
        try:
            text = _read(path)
        except (OSError, UnicodeError) as exc:
            document_failures.append(f"{path}: {type(exc).__name__}")
            continue
        if not isinstance(versions, dict):
            document_failures.append(f"{path}: registry policy versions unavailable")
            continue
        for key in keys:
            label = labels[key]
            item = versions.get(key)
            if not isinstance(item, dict):
                continue
            match = re.search(rf"(?m)^{re.escape(label)}:\s*v?(\d+(?:\.\d+)*)(?:\s+[^\n]+)?\s*$", text)
            actual = None if match is None else match.group(1)
            if actual != item.get("version"):
                document_failures.append(f"{path}: {label} registry={item.get('version')}, actual={actual}")
    for path, skill_key, label in (
        ("skills/a-share-retirement-investing/README.md", "retirement_investing", "Long Skill"),
        ("skills/a-share-short-midterm-stock-selection/README.md", "short_midterm_stock_selection", "Short/Mid Skill"),
    ):
        item = (state.get("skill_versions") or {}).get(skill_key)
        text = _read(path)
        match = re.search(rf"(?m)^{re.escape(label)}:\s*v?(\d+(?:\.\d+)*)(?:\s+[^\n]+)?\s*$", text)
        actual = None if match is None else match.group(1)
        expected = item.get("version") if isinstance(item, dict) else None
        if actual != expected:
            document_failures.append(f"{path}: {label} registry={expected}, actual={actual}")
    results.append(CheckResult("registry_document_versions", not document_failures, "ok" if not document_failures else str(document_failures)))
    return results


def _state_semantics_checks(state: dict[str, Any] | None) -> list[CheckResult]:
    if state is None:
        return [CheckResult(name, False, "NOT_EVALUATED: current-state registry unavailable") for name in (
            "governance_mode", "branch_protection_contract", "runtime_order_safety", "model_governance",
            "strategy_context", "state_namespaces", "historical_document_classification",
            "daily_workflow_write_model")]
    checks: list[CheckResult] = []
    checks.append(CheckResult("governance_mode", state.get("governance_mode") == EXPECTED_GOVERNANCE_MODE,
                              str(state.get("governance_mode"))))
    protection = state.get("branch_protection")
    required_protection = {
        "pull_request_required": True, "required_approvals": 0, "required_checks": ["governance"],
        "conversation_resolution_required": True, "force_push_allowed": False,
        "deletion_allowed": False, "admin_enforcement": True, "bypass_actors": [],
    }
    checks.append(CheckResult("branch_protection_contract", protection == required_protection,
                              "matches solo-maintainer protected-main policy" if protection == required_protection else f"actual={protection}"))

    runtime = state.get("runtime")
    runtime_source = _read("runtime/daily_monitor.py")
    safe = isinstance(runtime, dict) and runtime.get("auto_monitor") is True and runtime.get("auto_order") is False
    safe = safe and '"auto_order": False' in runtime_source
    safe = safe and "--market-only" in runtime_source
    checks.append(CheckResult("runtime_order_safety", bool(safe), "AUTO_ORDER=false; market-only mode declared" if safe else f"runtime={runtime}"))
    checks.append(_daily_workflow_write_model_check(state))

    models = state.get("models")
    model_ok = isinstance(models, dict)
    if model_ok:
        model_ok = (models.get("champion", {}).get("status") == "ACTIVE"
                    and models.get("erg", {}).get("status") == "SHADOW_ONLY"
                    and models.get("causal_challenger", {}).get("status") == "SHADOW_ONLY")
        champion_path = models.get("champion", {}).get("config_path")
        try:
            champion = json.loads(_read(champion_path))
        except (OSError, UnicodeError, json.JSONDecodeError, TypeError):
            champion = {}
            model_ok = False
        short = (state.get("strategies") or {}).get("short_mid", {})
        model_ok = model_ok and champion.get("strategy_id") == short.get("strategy_id") and champion.get("sleeve") == short.get("sleeve")
    checks.append(CheckResult("model_governance", bool(model_ok), "Champion ACTIVE; ERG and Causal Challenger SHADOW_ONLY" if model_ok else f"models={models}"))

    strategies = state.get("strategies")
    try:
        boundary = _read("src/core/strategy_boundary.py")
        identities = {
            "long": ("LONG_STRATEGY_ID", "LONG_SLEEVE"),
            "short_mid": ("SHORT_MID_STRATEGY_ID", "SHORT_MID_SLEEVE"),
        }
        strategy_errors: list[str] = []
        for key, (id_name, sleeve_name) in identities.items():
            declared = strategies.get(key, {}) if isinstance(strategies, dict) else {}
            actual_id = re.search(rf"(?m)^{id_name}\s*=\s*['\"]([^'\"]+)['\"]", boundary)
            actual_sleeve = re.search(rf"(?m)^{sleeve_name}\s*=\s*['\"]([^'\"]+)['\"]", boundary)
            pair = (None if actual_id is None else actual_id.group(1), None if actual_sleeve is None else actual_sleeve.group(1))
            if pair != (declared.get("strategy_id"), declared.get("sleeve")):
                strategy_errors.append(f"{key}: registry={(declared.get('strategy_id'), declared.get('sleeve'))}, implementation={pair}")
    except (OSError, UnicodeError):
        strategy_errors = ["strategy boundary source missing"]
    checks.append(CheckResult("strategy_context", not strategy_errors, "strategy_id/sleeve pairs match" if not strategy_errors else str(strategy_errors)))

    namespaces = state.get("state_namespaces")
    required_sets = {
        "execution_side": EXECUTION_SIDES,
        "position_intent": POSITION_INTENTS,
        "position_state": POSITION_STATES,
        "authorization_state": AUTHORIZATION_STATES,
        "research_state": RESEARCH_STATES,
        "monitor_state": MONITOR_STATES,
    }
    namespace_errors: list[str] = []
    if not isinstance(namespaces, dict):
        namespace_errors.append("state_namespaces missing/invalid")
    else:
        for key, required in required_sets.items():
            values = namespaces.get(key)
            if not isinstance(values, list) or set(values) != required or len(values) != len(set(values)):
                namespace_errors.append(f"{key}: expected={sorted(required)}, actual={values}")
    sample_contract = _read("skills/a-share-short-midterm-stock-selection/references/sample-data-acquisition-contract.md")
    if "execution_side: BUY | SELL" not in sample_contract or "position_intent: ENTRY | ADD | TRIM | EXIT" not in sample_contract:
        namespace_errors.append("sample-data contract does not distinguish execution_side from position_intent")
    monitor_source = _read("runtime/monitor.py")
    literal = re.search(r"MonitorState\s*=\s*Literal\[(.*?)\]", monitor_source, re.S)
    actual_monitor = set(re.findall(r"[\"']([A-Z_]+)[\"']", literal.group(1))) if literal else set()
    if actual_monitor != MONITOR_STATES or "def decide_short_mid_monitor_state" not in monitor_source:
        namespace_errors.append(f"monitor state API mismatch: {sorted(actual_monitor)}")
    checks.append(CheckResult("state_namespaces", not namespace_errors, "typed state namespaces agree" if not namespace_errors else str(namespace_errors)))

    history_policy = state.get("historical_document_policy")
    history_ok = isinstance(history_policy, dict) and history_policy.get("classification") == "HISTORICAL_SNAPSHOT" and history_policy.get("current_authority") is False
    if history_ok:
        try:
            history_text = _read(history_policy["path"])
            history_ok = history_policy.get("required_banner") in "\n".join(history_text.splitlines()[:8])
        except (OSError, UnicodeError, TypeError):
            history_ok = False
    checks.append(CheckResult("historical_document_classification", bool(history_ok), "dated implementation report is labelled historical" if history_ok else f"policy={history_policy}"))
    return checks


def _daily_workflow_write_model_check(state: dict[str, Any] | None, workflow_text: str | None = None) -> CheckResult:
    if state is None:
        return CheckResult("daily_workflow_write_model", False, "NOT_EVALUATED: current-state registry unavailable")
    text = _read(".github/workflows/a-share-daily-monitor.yml") if workflow_text is None else workflow_text
    allowed = ["runtime/state/market_history.csv"]
    publisher = text.split("  publish-evidence:", 1)[1] if "  publish-evidence:" in text else ""
    required = (
        "actions/upload-artifact@v4",
        "actions/download-artifact@v4",
        "path: runtime/state/market_history.csv",
        'artifact_path="$RUNNER_TEMP/public-market-history/market_history.csv"',
        'root.rglob("*")',
        "contents: read",
        "pull-requests: write",
        "automation/public-market-evidence",
        '"diff", "--name-only", "-z"',
        '"ls-files", "--others", "--exclude-standard", "-z"',
        '"diff", "--cached", "--name-only", "-z"',
        "gh pr list",
        "gh pr create",
        'git push origin "$branch"',
        "if ! git diff --cached --quiet; then",
    )
    missing = [item for item in required if item not in text]
    valid = state.get("scheduled_evidence_allowlist") == allowed
    valid = valid and bool(publisher) and "contents: write" in publisher and "pull-requests: write" in publisher
    valid = valid and "if: github.event_name != 'pull_request'" in publisher
    action_permissions = state.get("github_actions_permissions")
    valid = valid and action_permissions == {
        "default_workflow_permissions": "read",
        "allow_create_and_approve_pull_requests": True,
        "workflow_submits_approvals": False,
    }
    direct_main_push = bool(re.search(r"git\s+push(?:\s+--[^\s]+)*\s+origin\s+(?:HEAD:)?main\b", text))
    valid = valid and not direct_main_push
    valid = valid and not re.search(r"\bgh\s+pr\s+review\b", publisher)
    valid = valid and not missing
    detail = "isolated write-permission publisher opens a PR for the registry allowlist only" if valid else (
        f"allowlist={state.get('scheduled_evidence_allowlist')}; publisher_present={bool(publisher)}; "
        f"actions_permissions={action_permissions}; missing={missing}; direct_main_push={direct_main_push}"
    )
    return CheckResult("daily_workflow_write_model", bool(valid), detail)


def _repository_map_consistency(
    readme_text: str | None = None,
    state: dict[str, Any] | None = None,
    tracked_paths: set[str] | None = None,
) -> CheckResult:
    if state is None or tracked_paths is None:
        return CheckResult("repository_map", False, "NOT_EVALUATED: registry or Git tracked paths unavailable")
    text = _read("README.md") if readme_text is None else readme_text
    match = re.search(r"(?ms)^## Repository map\s*(.*?)(?=^## |\Z)", text)
    if match is None:
        return CheckResult("repository_map", False, "README repository map section missing")
    documented = set(re.findall(r"`([^`]+)`", match.group(1)))
    declared = set(state.get("repository_map_paths", []))
    missing_from_docs = sorted(declared - documented)
    undeclared_in_docs = sorted(documented - declared)
    missing_from_tree = []
    for path in declared:
        normalized = path.rstrip("/")
        exists = normalized in tracked_paths or any(item.startswith(normalized + "/") for item in tracked_paths)
        if not exists:
            missing_from_tree.append(path)
    ok = not missing_from_docs and not undeclared_in_docs and not missing_from_tree
    detail = "registry map matches README and tracked tree" if ok else f"missing_from_docs={missing_from_docs}; undeclared_in_docs={undeclared_in_docs}; missing_from_tree={sorted(missing_from_tree)}"
    return CheckResult("repository_map", ok, detail)


def _optional_path_documentation(state: dict[str, Any] | None) -> CheckResult:
    if state is None:
        return CheckResult("optional_generated_paths", False, "NOT_EVALUATED: current-state registry unavailable")
    declared = state.get("documented_optional_or_generated_paths")
    if not isinstance(declared, dict):
        return CheckResult("optional_generated_paths", False, "documented_optional_or_generated_paths missing")
    docs = _read("README.md") + "\n" + _read("runtime/README.md")
    errors = []
    for path, classification in declared.items():
        if classification not in {"PRIVATE_OPTIONAL", "GENERATED_PRIVATE"}:
            errors.append(f"{path}: invalid classification={classification}")
            continue
        normalized = path.rstrip("/")
        matches = [line for line in docs.splitlines() if normalized in line]
        if not matches or not any(classification in line for line in matches):
            errors.append(f"{path}: missing explicit {classification} documentation")
    return CheckResult("optional_generated_paths", not errors, "all non-tracked paths are explicitly classified" if not errors else str(errors))


def _storage_namespace_check(state: dict[str, Any] | None, tracked_paths: set[str] | None) -> CheckResult:
    if state is None or tracked_paths is None:
        return CheckResult("storage_namespaces", False, "NOT_EVALUATED: registry or tracked paths unavailable")
    namespaces = state.get("storage_namespaces")
    if not isinstance(namespaces, dict):
        return CheckResult("storage_namespaces", False, "storage_namespaces missing/invalid")
    private = namespaces.get("private_execution_truth", {})
    if not isinstance(private, dict):
        return CheckResult("storage_namespaces", False, "private_execution_truth missing/invalid")
    private_paths = private.get("paths") if isinstance(private, dict) else None
    normalized = set(private_paths) if isinstance(private_paths, list) else set()
    declared_prefixes = {p for p in normalized if p.endswith("/")}
    declared_exact = normalized - declared_prefixes
    expected = set(PRIVATE_PATH_PREFIXES) | set(PRIVATE_EXACT_PATHS)
    errors = []
    if private.get("tracking") != "IGNORED_PRIVATE_OPTIONAL" or normalized != expected:
        errors.append(f"private namespace mismatch: tracking={private.get('tracking')}; paths={sorted(normalized)}")
    if declared_prefixes != set(PRIVATE_PATH_PREFIXES) or declared_exact != set(PRIVATE_EXACT_PATHS):
        errors.append("private path rules do not match the effective-ignore audit contract")
    tracked_private = sorted(path for path in tracked_paths if path in declared_exact or path.startswith(tuple(declared_prefixes)))
    if tracked_private:
        errors.append(f"private paths tracked: {tracked_private}")
    for key, tracking in (("public_market_truth", "PUBLIC_TRACKED"),
                          ("strategy_configuration_truth", "PUBLIC_TRACKED"),
                          ("synthetic_public_fixtures", "PUBLIC_TRACKED")):
        item = namespaces.get(key)
        paths = item.get("paths") if isinstance(item, dict) else None
        if not isinstance(paths, list) or item.get("tracking") != tracking:
            errors.append(f"{key}: invalid tracking declaration")
            continue
        for path in paths:
            target = str(path).rstrip("/")
            if not (target in tracked_paths or any(p.startswith(target + "/") for p in tracked_paths)):
                errors.append(f"{key}: declared tracked path missing from Git: {path}")
    synthetic = namespaces.get("synthetic_public_fixtures", {})
    if not isinstance(synthetic, dict):
        errors.append("synthetic_public_fixtures missing/invalid")
        synthetic = {}
    registry_synthetic = set(synthetic.get("paths", [])) if isinstance(synthetic, dict) else set()
    if registry_synthetic != set(PUBLIC_SYNTHETIC_FIXTURES) or synthetic.get("required_marker") != SYNTHETIC_MARKER:
        errors.append("synthetic fixture registry paths/marker do not match the structural privacy audit")
    return CheckResult("storage_namespaces", not errors, "public/private storage classes match tracked and ignored paths" if not errors else str(errors))


def _git_tracked_paths() -> set[str]:
    try:
        result = subprocess.run(
            ["git", "ls-files", "-z"], cwd=ROOT, check=True, capture_output=True
        )
    except (OSError, subprocess.CalledProcessError) as exc:
        raise GitEnumerationError(f"git ls-files failed: {exc}") from exc
    raw = result.stdout
    if not isinstance(raw, bytes):
        raise GitEnumerationError("git ls-files -z returned non-byte output")
    try:
        entries = raw.split(b"\0")
        if entries and entries[-1] == b"":
            entries.pop()
        return {os.fsdecode(entry).replace("\\", "/") for entry in entries}
    except (UnicodeError, ValueError) as exc:
        raise GitEnumerationError(f"git ls-files -z path decoding failed: {exc}") from exc


def _internal_links_exist(tracked_paths: set[str] | None) -> CheckResult:
    if tracked_paths is None:
        return CheckResult("internal_links", False, "NOT_EVALUATED: tracked file enumeration failed")
    missing: list[str] = []
    markdown_files = [ROOT / path for path in tracked_paths if path.lower().endswith(".md")]
    for source in markdown_files:
        if not source.exists():
            missing.append(f"{source.relative_to(ROOT)} -> tracked file missing")
            continue
        text = source.read_text(encoding="utf-8")
        for raw in re.findall(r"\[[^\]]+\]\(([^)#]+)", text):
            target = raw.strip().strip("<>")
            if not target or "://" in target or target.startswith("mailto:"):
                continue
            candidate = (source.parent / target).resolve()
            if not candidate.exists():
                missing.append(f"{source.relative_to(ROOT)} -> {target}")
    return CheckResult("internal_links", not missing, "ok" if not missing else f"missing={missing[:10]}")


def run_audit() -> list[CheckResult]:
    checks: list[CheckResult] = []

    expected_files = [
        "shared/policy-precedence.md",
        "shared/capital-eligibility-and-investor-risk-philosophy.md",
        "shared/pre-trade-order-authorization-contract.md",
        "shared/capital-allocation-and-entry-policy.md",
        "shared/automation-execution-governance.md",
        "shared/research-model-governance.md",
        "skills/a-share-multi-asset-allocation/SKILL.md",
        "skills/a-share-retirement-investing/SKILL.md",
        "skills/a-share-short-midterm-stock-selection/SKILL.md",
        "src/core/pretrade_risk_gate.py",
        "runtime/pretrade_cli.py",
        CURRENT_STATE_PATH,
    ]
    missing_files = [path for path in expected_files if not (ROOT / path).exists()]
    checks.append(CheckResult("required_files", not missing_files, f"missing={missing_files}"))

    if missing_files:
        return checks

    state, state_check = _load_current_state()
    checks.append(state_check)

    try:
        tracked_paths = _git_tracked_paths()
        checks.append(CheckResult("tracked_file_enumeration", True, "ok"))
    except GitEnumerationError as exc:
        checks.append(CheckResult("tracked_file_enumeration", False, str(exc)))
        tracked_paths = None

    checks.extend(_registry_version_checks(state))
    checks.extend(_state_semantics_checks(state))
    checks.append(_repository_map_consistency(state=state, tracked_paths=tracked_paths))
    checks.append(_optional_path_documentation(state))
    checks.append(_storage_namespace_check(state, tracked_paths))

    level0_refs = [
        "capital-eligibility-and-investor-risk-philosophy.md",
        "pre-trade-order-authorization-contract.md",
    ]
    for path in (
        "skills/a-share-retirement-investing/SKILL.md",
        "skills/a-share-short-midterm-stock-selection/SKILL.md",
        "skills/a-share-retirement-investing/README.md",
        "skills/a-share-short-midterm-stock-selection/README.md",
        "runtime/README.md",
    ):
        checks.append(_contains_all(path, level0_refs))

    checks.extend([
        _contains_all(
            "src/core/pretrade_risk_gate.py",
            [
                "current_trade_planned_risk_rmb",
                "remaining_trade_risk",
                "remaining_user_trade_risk",
                "min_buy_shares",
                "buy_increment_shares",
                "current_long_symbol_exposure_rmb",
            ],
        ),
        _contains_all(
            "runtime/pretrade_cli.py",
            [
                "MAIN",
                "CHINEXT",
                "STAR",
                "BSE",
                "current_trade_planned_risk_rmb",
                "current_long_symbol_exposure_rmb",
            ],
        ),
        _not_contains(
            "skills/a-share-retirement-investing/references/methodology.md",
            ["### Level 0：数据可信性"],
        ),
        _not_contains(
            "skills/a-share-short-midterm-stock-selection/references/paper-live-automation-roadmap.md",
            ["100股单位", "尊重100股单位"],
        ),
        _not_contains(
            "skills/a-share-short-midterm-stock-selection/references/validation-metrics-and-trade-ledger.md",
            ["100股单位"],
        ),
        _contains_all(
            "runtime/README.md",
            ["runtime/private/short_mid_universe.json", "ignored local private paths"],
        ),
        _contains_all(
            "skills/a-share-short-midterm-stock-selection/references/sample-data-acquisition-contract.md",
            ["PUBLIC / TRACKED EVIDENCE", "PRIVATE EXECUTION STATE", "runtime/state/private/sample_evidence/"],
        ),
    ])

    checks.extend([
        CheckResult(
            name="privacy_boundary",
            ok=not (ROOT / "runtime/portfolio_instances.json").exists()
               and (ROOT / ".gitignore").exists()
               and (ROOT / "runtime/PRIVATE_STATE.md").exists(),
            detail="personal portfolio/trade artifacts must not be tracked in public source",
        ),
        _private_paths_ignored(),
        CheckResult(
            name="private_tracked_paths",
            ok=tracked_paths is not None and not any(
                path in PRIVATE_EXACT_PATHS or path.startswith(PRIVATE_PATH_PREFIXES)
                for path in tracked_paths
            ),
            detail=("tracked tree contains no declared private paths"
                    if tracked_paths is not None else "NOT_EVALUATED: tracked file enumeration failed"),
        ),
        CheckResult(
            name="no_tracked_personal_instances",
            ok=tracked_paths is not None and not any(
                path in PRIVATE_EXACT_PATHS or path.startswith(PRIVATE_PATH_PREFIXES)
                for path in tracked_paths
            ),
            detail=("public tracked tree excludes personal portfolio/trade artifacts"
                    if tracked_paths is not None else "NOT_EVALUATED: tracked file enumeration failed"),
        ),
        _public_synthetic_fixtures(tracked_paths),
        _contains_all(
            "src/core/account_snapshot.py",
            ["CanonicalAccountSnapshot", "reconciliation_state", "staleness_state", "ENTRY", "ADD", "TRIM", "EXIT"],
        ),
        _contains_all(
            "src/core/pretrade_authorization.py",
            ["input_snapshot_hash", "policy_versions", "DEFAULT_PRIVATE_AUTH_ROOT"],
        ),
        _contains_all(
            "runtime/tests/test_account_snapshot.py",
            ["MISSING", "STALE", "CONFLICT", "UNRECONCILED", "EXIT"],
        ),
        _contains_all(
            "runtime/tests/test_pretrade_risk_gate.py",
            ["invalidation", "tranche", "ADD", "ENTRY"],
        ),
        _internal_links_exist(tracked_paths),
    ])

    workflow = ".github/workflows/a-share-daily-monitor.yml"
    checks.append(_contains_all(
        workflow,
        [
            '"shared/**"',
            '"skills/**"',
            '"README.md"',
            "python runtime/repository_consistency_audit.py",
        ],
    ))

    governance_workflow = ".github/workflows/repository-governance.yml"
    checks.append(CheckResult(
        name="governance_workflow_exists",
        ok=(ROOT / governance_workflow).exists(),
        detail=governance_workflow,
    ))
    if (ROOT / governance_workflow).exists():
        checks.append(_contains_all(
            governance_workflow,
            [
                '"shared/**"',
                '"skills/**"',
                '"src/**"',
                '"runtime/**"',
                '"README.md"',
                '"configs/**"',
                "python runtime/repository_consistency_audit.py",
                "python -m unittest discover -s runtime/tests -v",
            ],
        ))

    return checks


def main() -> int:
    checks = run_audit()
    failures = [item for item in checks if not item.ok]
    for item in checks:
        status = "PASS" if item.ok else "FAIL"
        print(f"[{status}] {item.name}: {item.detail}")
    if failures:
        print(f"\nRepository consistency audit failed: {len(failures)} issue(s).")
        return 1
    print(f"\nRepository consistency audit passed: {len(checks)} checks.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
