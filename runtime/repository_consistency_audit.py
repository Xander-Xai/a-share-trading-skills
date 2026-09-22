from __future__ import annotations

import re
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable


ROOT = Path(__file__).resolve().parents[1]


@dataclass(frozen=True)
class CheckResult:
    name: str
    ok: bool
    detail: str


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
    match = re.search(r"(?m)^version:\s*[\"']?([^\"'\n]+)[\"']?\s*$", text)
    actual = match.group(1).strip() if match else None
    return CheckResult(
        name=f"skill_version:{path}",
        ok=actual == expected,
        detail=f"expected={expected}, actual={actual}",
    )


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
    ]
    missing_files = [path for path in expected_files if not (ROOT / path).exists()]
    checks.append(CheckResult("required_files", not missing_files, f"missing={missing_files}"))

    if missing_files:
        return checks

    checks.extend([
        _header_version(
            "shared/capital-eligibility-and-investor-risk-philosophy.md",
            r"v(\d+(?:\.\d+)*)$",
            "2",
        ),
        _header_version(
            "shared/pre-trade-order-authorization-contract.md",
            r"v(\d+(?:\.\d+)*)$",
            "1.1",
        ),
        _header_version(
            "shared/capital-allocation-and-entry-policy.md",
            r"v(\d+(?:\.\d+)*)$",
            "2.6",
        ),
        _header_version(
            "shared/automation-execution-governance.md",
            r"v(\d+(?:\.\d+)*)$",
            "1.5",
        ),
        _header_version(
            "shared/research-model-governance.md",
            r"v(\d+(?:\.\d+)*)$",
            "3.2",
        ),
        _header_version(
            "shared/canonical-pit-data-contract.md",
            r"v(\d+(?:\.\d+)*)$",
            "1.2",
        ),
        _yaml_skill_version("skills/a-share-multi-asset-allocation/SKILL.md", "1.1.1"),
        _yaml_skill_version("skills/a-share-retirement-investing/SKILL.md", "2.2.2"),
        _yaml_skill_version("skills/a-share-short-midterm-stock-selection/SKILL.md", "1.7.3"),
    ])

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
            "README.md",
            [
                "Capital Eligibility:    v2",
                "Pre-Trade Authorization: v1.1",
                "Capital / Risk:          v2.6",
                "Automation / Execution: v1.5",
                "Research / Model:        v3.2",
                "Canonical PIT Data:      v1.2",
            ],
        ),
        _contains_all(
            "skills/a-share-retirement-investing/README.md",
            [
                "Capital / Risk:           v2.6",
                "Automation / Execution:  v1.5",
                "Long Skill:               v2.2.2",
            ],
        ),
        _contains_all(
            "skills/a-share-short-midterm-stock-selection/README.md",
            [
                "Capital / Risk:           v2.6",
                "Automation / Execution:  v1.5",
                "Short/Mid Skill:          v1.7.3",
            ],
        ),
    ])

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
                "python runtime/repository_consistency_audit.py",
                "python -m unittest runtime.tests.test_pretrade_risk_gate -v",
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
