"""Canonical, private account-state contract for Level-0 authorization.

The public repository contains only the schema and a local JSON adapter.  A
broker adapter may implement :class:`AccountSnapshotProvider` later, but this
module deliberately never stores credentials or real account data in Git.
"""
from __future__ import annotations

import json
import math
from collections.abc import Mapping as MappingABC
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any, Mapping, Protocol


BLOCKING_RECONCILIATION_STATES = {"MISSING", "STALE", "CONFLICT", "UNRECONCILED"}
RISK_INCREASING_ACTIONS = {"ENTRY", "ADD"}
RISK_REDUCING_ACTIONS = {"TRIM", "EXIT"}
SUPPORTED_ACTIONS = RISK_INCREASING_ACTIONS | RISK_REDUCING_ACTIONS


def _is_nonnegative_finite_number(value: Any) -> bool:
    """Return whether a snapshot amount is a real, finite non-negative number."""
    return (
        isinstance(value, (int, float))
        and not isinstance(value, bool)
        and math.isfinite(value)
        and value >= 0
    )


@dataclass(frozen=True)
class CanonicalAccountSnapshot:
    as_of: str
    execution_mode: str
    cash: float | None
    stock_account_equity: float | None
    positions: Mapping[str, Any]
    strategy_virtual_positions: Mapping[str, Any]
    symbol_exposure: Mapping[str, float]
    cluster_exposure: Mapping[str, float]
    short_mid_nav: float | None
    open_initial_risk: float | None
    factor_initial_risk: float | None
    trade_planned_risk: float | None
    data_source: str
    reconciliation_state: str
    staleness_state: str

    def __post_init__(self) -> None:
        if not self.as_of or not self.execution_mode or not self.data_source:
            raise ValueError("as_of, execution_mode and data_source are required")
        if self.reconciliation_state not in {"RECONCILED", *BLOCKING_RECONCILIATION_STATES}:
            raise ValueError("unknown reconciliation_state")
        if self.staleness_state not in {"FRESH", "STALE", "UNKNOWN"}:
            raise ValueError("unknown staleness_state")

    @property
    def entry_add_allowed(self) -> bool:
        return (
            self.reconciliation_state == "RECONCILED"
            and self.staleness_state == "FRESH"
            and self.is_complete_and_valid
        )

    @property
    def is_complete_and_valid(self) -> bool:
        numeric_fields = (
            "cash", "stock_account_equity", "short_mid_nav", "open_initial_risk",
            "factor_initial_risk", "trade_planned_risk",
        )
        for name in numeric_fields:
            value = getattr(self, name)
            if not _is_nonnegative_finite_number(value):
                return False
            if name in {"stock_account_equity", "short_mid_nav"} and value <= 0:
                return False
        for name in ("positions", "strategy_virtual_positions"):
            if not isinstance(getattr(self, name), MappingABC):
                return False
        for name in ("symbol_exposure", "cluster_exposure"):
            exposure = getattr(self, name)
            if not isinstance(exposure, MappingABC):
                return False
            if any(not _is_nonnegative_finite_number(value) for value in exposure.values()):
                return False
        return True

    def authorization_gate(self, action: str) -> str:
        """Return BLOCKED for risky opens, while preserving risk reduction."""
        if not isinstance(action, str):
            return "BLOCKED"
        action = action.upper()
        if action not in SUPPORTED_ACTIONS:
            return "BLOCKED"
        if action in RISK_REDUCING_ACTIONS:
            return "AUTHORIZED_RISK_REDUCTION"
        if action in RISK_INCREASING_ACTIONS and not self.entry_add_allowed:
            return "BLOCKED"
        return "AUTHORIZED"

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_mapping(cls, value: Mapping[str, Any]) -> "CanonicalAccountSnapshot":
        return cls(**dict(value))


class AccountSnapshotProvider(Protocol):
    def read_snapshot(self) -> CanonicalAccountSnapshot: ...


class LocalAccountSnapshotAdapter:
    """Read a snapshot from a private path; no broker integration is implied."""

    def __init__(self, path: str | Path):
        self.path = Path(path)

    def read_snapshot(self) -> CanonicalAccountSnapshot:
        if not self.path.exists():
            raise FileNotFoundError(self.path)
        with self.path.open("r", encoding="utf-8") as handle:
            payload = json.load(handle)
        return CanonicalAccountSnapshot.from_mapping(payload)


class MockAccountSnapshotAdapter:
    def __init__(self, snapshot: CanonicalAccountSnapshot):
        self.snapshot = snapshot

    def read_snapshot(self) -> CanonicalAccountSnapshot:
        return self.snapshot
