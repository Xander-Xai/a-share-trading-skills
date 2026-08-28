from __future__ import annotations

import hashlib
import json
import math
from dataclasses import asdict, dataclass
from datetime import datetime
from typing import Any, Iterable, Mapping

from src.core.pit_store import StoredPITRecord
from src.core.strategy_boundary import (
    SHORT_MID_SLEEVE,
    SHORT_MID_STRATEGY_ID,
    require_strategy_context,
)
from src.features.erg_shadow import EvidenceRef, MaterialityEvidence


EARNINGS_MATERIALITY_SCHEMA_VERSION = "1.0"
VALID_RULE_MODES = {"EVIDENCE_ONLY", "THRESHOLD_RULE_V1"}
VALID_CLASSIFICATION_BASES = {"PRIMARY_CHANGE_ONLY", "PRIMARY_AND_ADJUSTED_CHANGE"}


def _canonical_json(value: Any) -> str:
    return json.dumps(
        value,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
        allow_nan=False,
    )


def _sha256(value: Any) -> str:
    return hashlib.sha256(_canonical_json(value).encode("utf-8")).hexdigest()


def _require_text(value: str, field_name: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{field_name} is required")
    return value.strip()


def _parse_aware(value: str, field_name: str) -> datetime:
    try:
        parsed = datetime.fromisoformat(value)
    except Exception as exc:
        raise ValueError(f"{field_name} must be ISO-8601") from exc
    if parsed.tzinfo is None or parsed.utcoffset() is None:
        raise ValueError(f"{field_name} must be timezone-aware")
    return parsed


def _finite(value: float | int | None, field_name: str, *, allow_none: bool = False) -> None:
    if value is None:
        if allow_none:
            return
        raise ValueError(f"{field_name} is required")
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise ValueError(f"{field_name} must be numeric")
    if not math.isfinite(float(value)):
        raise ValueError(f"{field_name} must be finite")


def _record_ref(record: StoredPITRecord, *, note: str) -> EvidenceRef:
    return EvidenceRef(
        ref=f"{record.metadata.record_id}@{record.metadata.revision_id}",
        source_tier=record.metadata.source_tier,
        source_snapshot_id=record.metadata.source_snapshot_id,
        note=note,
    )


def _normalized_metric(record: StoredPITRecord, metric: str) -> float:
    if record.metadata.entity_type != "FINANCIAL_STATEMENT":
        raise ValueError("earnings materiality records must be FINANCIAL_STATEMENT")
    payload = record.payload
    metrics = payload.get("metrics")
    if not isinstance(metrics, Mapping) or metric not in metrics:
        raise ValueError(f"financial statement is missing required metric: {metric}")
    raw = metrics[metric]
    if raw is None:
        raise ValueError(f"financial metric is unresolved: {metric}")
    _finite(raw, f"metrics[{metric}]")
    if payload.get("currency") != "CNY":
        raise ValueError("earnings materiality v1 requires FINANCIAL_STATEMENT currency=CNY")
    unit_scale = payload.get("unit_scale")
    _finite(unit_scale, "financial_statement.unit_scale")
    if float(unit_scale) <= 0:
        raise ValueError("financial_statement.unit_scale must be > 0")
    return float(raw) * float(unit_scale)


def _growth(current: float, comparator: float, *, low_base_floor_abs: float) -> tuple[float | None, bool]:
    low_base = abs(comparator) < low_base_floor_abs
    if low_base or comparator == 0:
        return None, True
    return (current - comparator) / abs(comparator), False


@dataclass(frozen=True)
class EarningsMaterialityContract:
    contract_id: str
    schema_version: str
    current_record_id: str
    comparator_record_id: str
    security_id: str
    current_period_end: str
    comparator_period_end: str
    statement_scope: str
    report_type: str
    primary_metric: str
    transmission_path: str
    rule_mode: str = "EVIDENCE_ONLY"
    classification_basis: str = "PRIMARY_CHANGE_ONLY"
    min_primary_change_abs_pct: float | None = None
    adjusted_metric: str | None = None
    min_adjusted_change_abs_pct: float | None = None
    revenue_metric: str | None = None
    cash_flow_metric: str | None = None
    low_base_floor_abs: float = 0.0

    def identity_payload(self) -> dict[str, Any]:
        return {
            "schema_version": self.schema_version,
            "current_record_id": self.current_record_id,
            "comparator_record_id": self.comparator_record_id,
            "security_id": self.security_id,
            "current_period_end": self.current_period_end,
            "comparator_period_end": self.comparator_period_end,
            "statement_scope": self.statement_scope,
            "report_type": self.report_type,
            "primary_metric": self.primary_metric,
            "transmission_path": self.transmission_path,
            "rule_mode": self.rule_mode,
            "classification_basis": self.classification_basis,
            "min_primary_change_abs_pct": self.min_primary_change_abs_pct,
            "adjusted_metric": self.adjusted_metric,
            "min_adjusted_change_abs_pct": self.min_adjusted_change_abs_pct,
            "revenue_metric": self.revenue_metric,
            "cash_flow_metric": self.cash_flow_metric,
            "low_base_floor_abs": self.low_base_floor_abs,
        }

    def validate(self) -> None:
        if self.schema_version != EARNINGS_MATERIALITY_SCHEMA_VERSION:
            raise ValueError("unsupported earnings materiality contract schema")
        for value, field_name in (
            (self.current_record_id, "current_record_id"),
            (self.comparator_record_id, "comparator_record_id"),
            (self.security_id, "security_id"),
            (self.current_period_end, "current_period_end"),
            (self.comparator_period_end, "comparator_period_end"),
            (self.statement_scope, "statement_scope"),
            (self.report_type, "report_type"),
            (self.primary_metric, "primary_metric"),
            (self.transmission_path, "transmission_path"),
        ):
            _require_text(value, field_name)
        if self.current_record_id == self.comparator_record_id:
            raise ValueError("current_record_id and comparator_record_id must differ")
        if self.rule_mode not in VALID_RULE_MODES:
            raise ValueError(f"invalid rule_mode: {self.rule_mode}")
        if self.classification_basis not in VALID_CLASSIFICATION_BASES:
            raise ValueError(f"invalid classification_basis: {self.classification_basis}")
        for value, field_name in (
            (self.adjusted_metric, "adjusted_metric"),
            (self.revenue_metric, "revenue_metric"),
            (self.cash_flow_metric, "cash_flow_metric"),
        ):
            if value is not None:
                _require_text(value, field_name)
        for value, field_name in (
            (self.min_primary_change_abs_pct, "min_primary_change_abs_pct"),
            (self.min_adjusted_change_abs_pct, "min_adjusted_change_abs_pct"),
        ):
            _finite(value, field_name, allow_none=True)
            if value is not None and value < 0:
                raise ValueError(f"{field_name} cannot be negative")
        _finite(self.low_base_floor_abs, "low_base_floor_abs")
        if self.low_base_floor_abs < 0:
            raise ValueError("low_base_floor_abs cannot be negative")

        if self.rule_mode == "EVIDENCE_ONLY":
            if self.min_primary_change_abs_pct is not None or self.min_adjusted_change_abs_pct is not None:
                raise ValueError("EVIDENCE_ONLY must not carry classification thresholds")
        else:
            if self.min_primary_change_abs_pct is None:
                raise ValueError("THRESHOLD_RULE_V1 requires min_primary_change_abs_pct")
            if self.classification_basis == "PRIMARY_AND_ADJUSTED_CHANGE":
                if self.adjusted_metric is None:
                    raise ValueError("PRIMARY_AND_ADJUSTED_CHANGE requires adjusted_metric")
                if self.min_adjusted_change_abs_pct is None:
                    raise ValueError(
                        "PRIMARY_AND_ADJUSTED_CHANGE requires min_adjusted_change_abs_pct"
                    )
            elif self.min_adjusted_change_abs_pct is not None:
                raise ValueError(
                    "min_adjusted_change_abs_pct is only valid with PRIMARY_AND_ADJUSTED_CHANGE"
                )

        if _sha256(self.identity_payload()) != self.contract_id:
            raise ValueError("contract_id does not match contract content")

    def to_dict(self) -> dict[str, Any]:
        return {**self.identity_payload(), "contract_id": self.contract_id}

    @classmethod
    def build(
        cls,
        *,
        current_record_id: str,
        comparator_record_id: str,
        security_id: str,
        current_period_end: str,
        comparator_period_end: str,
        statement_scope: str,
        report_type: str,
        primary_metric: str,
        transmission_path: str,
        rule_mode: str = "EVIDENCE_ONLY",
        classification_basis: str = "PRIMARY_CHANGE_ONLY",
        min_primary_change_abs_pct: float | None = None,
        adjusted_metric: str | None = None,
        min_adjusted_change_abs_pct: float | None = None,
        revenue_metric: str | None = None,
        cash_flow_metric: str | None = None,
        low_base_floor_abs: float = 0.0,
    ) -> "EarningsMaterialityContract":
        provisional = cls(
            contract_id="pending",
            schema_version=EARNINGS_MATERIALITY_SCHEMA_VERSION,
            current_record_id=current_record_id,
            comparator_record_id=comparator_record_id,
            security_id=security_id,
            current_period_end=current_period_end,
            comparator_period_end=comparator_period_end,
            statement_scope=statement_scope,
            report_type=report_type,
            primary_metric=primary_metric,
            transmission_path=transmission_path,
            rule_mode=rule_mode,
            classification_basis=classification_basis,
            min_primary_change_abs_pct=min_primary_change_abs_pct,
            adjusted_metric=adjusted_metric,
            min_adjusted_change_abs_pct=min_adjusted_change_abs_pct,
            revenue_metric=revenue_metric,
            cash_flow_metric=cash_flow_metric,
            low_base_floor_abs=float(low_base_floor_abs),
        )
        result = cls(
            **{**provisional.__dict__, "contract_id": _sha256(provisional.identity_payload())}
        )
        result.validate()
        return result

    @classmethod
    def from_dict(cls, payload: Mapping[str, Any]) -> "EarningsMaterialityContract":
        result = cls(
            contract_id=str(payload["contract_id"]),
            schema_version=str(payload["schema_version"]),
            current_record_id=str(payload["current_record_id"]),
            comparator_record_id=str(payload["comparator_record_id"]),
            security_id=str(payload["security_id"]),
            current_period_end=str(payload["current_period_end"]),
            comparator_period_end=str(payload["comparator_period_end"]),
            statement_scope=str(payload["statement_scope"]),
            report_type=str(payload["report_type"]),
            primary_metric=str(payload["primary_metric"]),
            transmission_path=str(payload["transmission_path"]),
            rule_mode=str(payload.get("rule_mode", "EVIDENCE_ONLY")),
            classification_basis=str(payload.get("classification_basis", "PRIMARY_CHANGE_ONLY")),
            min_primary_change_abs_pct=(
                None
                if payload.get("min_primary_change_abs_pct") is None
                else float(payload["min_primary_change_abs_pct"])
            ),
            adjusted_metric=(None if payload.get("adjusted_metric") is None else str(payload["adjusted_metric"])),
            min_adjusted_change_abs_pct=(
                None
                if payload.get("min_adjusted_change_abs_pct") is None
                else float(payload["min_adjusted_change_abs_pct"])
            ),
            revenue_metric=(None if payload.get("revenue_metric") is None else str(payload["revenue_metric"])),
            cash_flow_metric=(
                None if payload.get("cash_flow_metric") is None else str(payload["cash_flow_metric"])
            ),
            low_base_floor_abs=float(payload.get("low_base_floor_abs", 0.0)),
        )
        result.validate()
        return result


@dataclass(frozen=True)
class EarningsMaterialityDiagnostics:
    primary_current: float
    primary_comparator: float
    primary_delta: float
    primary_change_pct: float | None
    primary_low_base: bool
    adjusted_current: float | None = None
    adjusted_comparator: float | None = None
    adjusted_change_pct: float | None = None
    adjusted_low_base: bool | None = None
    revenue_current: float | None = None
    revenue_comparator: float | None = None
    revenue_change_pct: float | None = None
    cash_flow_current: float | None = None
    cash_flow_comparator: float | None = None
    current_cash_conversion_ratio: float | None = None
    comparator_cash_conversion_ratio: float | None = None
    current_one_off_gap_ratio: float | None = None

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class EarningsMaterialityResult:
    result_id: str
    schema_version: str
    contract_id: str
    strategy_id: str
    sleeve: str
    as_of: str
    information_timestamp: str
    current_record_ref: str
    comparator_record_ref: str
    diagnostics: EarningsMaterialityDiagnostics
    materiality: MaterialityEvidence

    def identity_payload(self) -> dict[str, Any]:
        return {
            "schema_version": self.schema_version,
            "contract_id": self.contract_id,
            "strategy_id": self.strategy_id,
            "sleeve": self.sleeve,
            "as_of": self.as_of,
            "information_timestamp": self.information_timestamp,
            "current_record_ref": self.current_record_ref,
            "comparator_record_ref": self.comparator_record_ref,
            "diagnostics": self.diagnostics.to_dict(),
            "materiality": self.materiality.to_dict(),
        }

    def validate(self) -> None:
        if self.schema_version != EARNINGS_MATERIALITY_SCHEMA_VERSION:
            raise ValueError("unsupported earnings materiality result schema")
        require_strategy_context(
            strategy_id=self.strategy_id,
            sleeve=self.sleeve,
            expected_strategy_id=SHORT_MID_STRATEGY_ID,
            expected_sleeve=SHORT_MID_SLEEVE,
        )
        _require_text(self.contract_id, "contract_id")
        _require_text(self.current_record_ref, "current_record_ref")
        _require_text(self.comparator_record_ref, "comparator_record_ref")
        as_of = _parse_aware(self.as_of, "as_of")
        info = _parse_aware(self.information_timestamp, "information_timestamp")
        if as_of < info:
            raise ValueError("as_of cannot precede information_timestamp")
        self.materiality.validate()
        if self.materiality.assessment_contract_id != self.contract_id:
            raise ValueError("materiality assessment_contract_id must match contract_id")
        if _sha256(self.identity_payload()) != self.result_id:
            raise ValueError("result_id does not match result content")

    def to_dict(self) -> dict[str, Any]:
        return {**self.identity_payload(), "result_id": self.result_id}


class PITEarningsMaterialityProducer:
    """Build source-backed EARNINGS MaterialityEvidence from PIT statements.

    v1 deliberately separates evidence production from model-selection claims:

    - EVIDENCE_ONLY computes diagnostics and returns UNRESOLVED.
    - THRESHOLD_RULE_V1 may classify MATERIAL/LOW_MATERIALITY only when all
      thresholds are explicitly frozen in the content-addressed contract.

    No default percentage threshold is embedded in code. Large positive and large
    negative changes are both potentially material; direction belongs to Surprise,
    not Materiality.
    """

    def build(
        self,
        records: Iterable[StoredPITRecord],
        *,
        contract: EarningsMaterialityContract,
        as_of: str,
        information_timestamp: str,
        strategy_id: str = SHORT_MID_STRATEGY_ID,
        sleeve: str = SHORT_MID_SLEEVE,
    ) -> EarningsMaterialityResult:
        contract.validate()
        require_strategy_context(
            strategy_id=strategy_id,
            sleeve=sleeve,
            expected_strategy_id=SHORT_MID_STRATEGY_ID,
            expected_sleeve=SHORT_MID_SLEEVE,
        )
        as_of_dt = _parse_aware(as_of, "as_of")
        info_dt = _parse_aware(information_timestamp, "information_timestamp")
        if as_of_dt < info_dt:
            raise ValueError("as_of cannot precede information_timestamp")

        rows = tuple(records)
        current = self._exact_record(rows, contract.current_record_id)
        comparator = self._exact_record(rows, contract.comparator_record_id)
        self._validate_records(current, comparator, contract, as_of_dt, info_dt)
        diagnostics = self._diagnostics(current, comparator, contract)
        state = self._classify(diagnostics, contract)

        refs = (
            _record_ref(current, note=f"earnings_materiality_contract={contract.contract_id};role=current"),
            _record_ref(
                comparator,
                note=f"earnings_materiality_contract={contract.contract_id};role=comparator",
            ),
        )
        impact_metrics = self._impact_metrics(diagnostics)
        materiality = MaterialityEvidence(
            state=state,
            transmission_path=contract.transmission_path,
            assessment_contract_id=contract.contract_id,
            impact_metrics=impact_metrics,
            evidence_refs=refs,
        )
        materiality.validate()

        provisional = EarningsMaterialityResult(
            result_id="pending",
            schema_version=EARNINGS_MATERIALITY_SCHEMA_VERSION,
            contract_id=contract.contract_id,
            strategy_id=strategy_id,
            sleeve=sleeve,
            as_of=as_of_dt.isoformat(),
            information_timestamp=info_dt.isoformat(),
            current_record_ref=f"{current.metadata.record_id}@{current.metadata.revision_id}",
            comparator_record_ref=f"{comparator.metadata.record_id}@{comparator.metadata.revision_id}",
            diagnostics=diagnostics,
            materiality=materiality,
        )
        result = EarningsMaterialityResult(
            **{**provisional.__dict__, "result_id": _sha256(provisional.identity_payload())}
        )
        result.validate()
        return result

    @staticmethod
    def _exact_record(records: tuple[StoredPITRecord, ...], record_id: str) -> StoredPITRecord:
        matches = [record for record in records if record.metadata.record_id == record_id]
        if not matches:
            raise ValueError(f"required PIT record not present in snapshot: {record_id}")
        if len(matches) != 1:
            raise ValueError(f"snapshot contains duplicate logical record id: {record_id}")
        matches[0].validate()
        return matches[0]

    @staticmethod
    def _validate_records(
        current: StoredPITRecord,
        comparator: StoredPITRecord,
        contract: EarningsMaterialityContract,
        as_of: datetime,
        information_timestamp: datetime,
    ) -> None:
        for record, role in ((current, "current"), (comparator, "comparator")):
            if record.metadata.entity_type != "FINANCIAL_STATEMENT":
                raise ValueError(f"{role} materiality record must be FINANCIAL_STATEMENT")
            if record.metadata.security_id != contract.security_id:
                raise ValueError(f"{role} security_id does not match contract")
            payload = record.payload
            if payload.get("statement_scope") != contract.statement_scope:
                raise ValueError(f"{role} statement_scope does not match contract")
            if payload.get("report_type") != contract.report_type:
                raise ValueError(f"{role} report_type does not match contract")

        if current.payload.get("period_end") != contract.current_period_end:
            raise ValueError("current period_end does not match contract")
        if comparator.payload.get("period_end") != contract.comparator_period_end:
            raise ValueError("comparator period_end does not match contract")

        current_available = _parse_aware(current.metadata.available_at, "current.available_at")
        comparator_available = _parse_aware(
            comparator.metadata.available_at,
            "comparator.available_at",
        )
        if current_available < information_timestamp:
            raise ValueError(
                "current financial statement became observable before information_timestamp; event clock is inconsistent"
            )
        if current_available > as_of:
            raise ValueError("current financial statement is not observable by as_of")
        if comparator_available >= information_timestamp:
            raise ValueError("comparator must be observable strictly before information_timestamp")

    @staticmethod
    def _diagnostics(
        current: StoredPITRecord,
        comparator: StoredPITRecord,
        contract: EarningsMaterialityContract,
    ) -> EarningsMaterialityDiagnostics:
        primary_current = _normalized_metric(current, contract.primary_metric)
        primary_comparator = _normalized_metric(comparator, contract.primary_metric)
        primary_change_pct, primary_low_base = _growth(
            primary_current,
            primary_comparator,
            low_base_floor_abs=contract.low_base_floor_abs,
        )

        adjusted_current = adjusted_comparator = adjusted_change_pct = None
        adjusted_low_base = None
        if contract.adjusted_metric is not None:
            adjusted_current = _normalized_metric(current, contract.adjusted_metric)
            adjusted_comparator = _normalized_metric(comparator, contract.adjusted_metric)
            adjusted_change_pct, adjusted_low_base = _growth(
                adjusted_current,
                adjusted_comparator,
                low_base_floor_abs=contract.low_base_floor_abs,
            )

        revenue_current = revenue_comparator = revenue_change_pct = None
        if contract.revenue_metric is not None:
            revenue_current = _normalized_metric(current, contract.revenue_metric)
            revenue_comparator = _normalized_metric(comparator, contract.revenue_metric)
            revenue_change_pct, _ = _growth(
                revenue_current,
                revenue_comparator,
                low_base_floor_abs=contract.low_base_floor_abs,
            )

        cash_current = cash_comparator = None
        current_cash_conversion = comparator_cash_conversion = None
        if contract.cash_flow_metric is not None:
            cash_current = _normalized_metric(current, contract.cash_flow_metric)
            cash_comparator = _normalized_metric(comparator, contract.cash_flow_metric)
            if primary_current != 0:
                current_cash_conversion = cash_current / abs(primary_current)
            if primary_comparator != 0:
                comparator_cash_conversion = cash_comparator / abs(primary_comparator)

        one_off_gap = None
        if adjusted_current is not None and primary_current != 0:
            one_off_gap = (primary_current - adjusted_current) / abs(primary_current)

        return EarningsMaterialityDiagnostics(
            primary_current=primary_current,
            primary_comparator=primary_comparator,
            primary_delta=primary_current - primary_comparator,
            primary_change_pct=primary_change_pct,
            primary_low_base=primary_low_base,
            adjusted_current=adjusted_current,
            adjusted_comparator=adjusted_comparator,
            adjusted_change_pct=adjusted_change_pct,
            adjusted_low_base=adjusted_low_base,
            revenue_current=revenue_current,
            revenue_comparator=revenue_comparator,
            revenue_change_pct=revenue_change_pct,
            cash_flow_current=cash_current,
            cash_flow_comparator=cash_comparator,
            current_cash_conversion_ratio=current_cash_conversion,
            comparator_cash_conversion_ratio=comparator_cash_conversion,
            current_one_off_gap_ratio=one_off_gap,
        )

    @staticmethod
    def _classify(
        diagnostics: EarningsMaterialityDiagnostics,
        contract: EarningsMaterialityContract,
    ) -> str:
        if contract.rule_mode == "EVIDENCE_ONLY":
            return "UNRESOLVED"

        if diagnostics.primary_low_base or diagnostics.primary_change_pct is None:
            return "UNRESOLVED"
        if abs(diagnostics.primary_change_pct) < float(contract.min_primary_change_abs_pct):
            return "LOW_MATERIALITY"

        if contract.classification_basis == "PRIMARY_AND_ADJUSTED_CHANGE":
            if diagnostics.adjusted_low_base or diagnostics.adjusted_change_pct is None:
                return "UNRESOLVED"
            if abs(diagnostics.adjusted_change_pct) < float(contract.min_adjusted_change_abs_pct):
                return "LOW_MATERIALITY"

        return "MATERIAL"

    @staticmethod
    def _impact_metrics(d: EarningsMaterialityDiagnostics) -> dict[str, float]:
        metrics: dict[str, float] = {
            "primary_current": d.primary_current,
            "primary_comparator": d.primary_comparator,
            "primary_delta": d.primary_delta,
            "primary_low_base": 1.0 if d.primary_low_base else 0.0,
        }
        optional = {
            "primary_change_pct": d.primary_change_pct,
            "adjusted_current": d.adjusted_current,
            "adjusted_comparator": d.adjusted_comparator,
            "adjusted_change_pct": d.adjusted_change_pct,
            "adjusted_low_base": (
                None if d.adjusted_low_base is None else (1.0 if d.adjusted_low_base else 0.0)
            ),
            "revenue_current": d.revenue_current,
            "revenue_comparator": d.revenue_comparator,
            "revenue_change_pct": d.revenue_change_pct,
            "cash_flow_current": d.cash_flow_current,
            "cash_flow_comparator": d.cash_flow_comparator,
            "current_cash_conversion_ratio": d.current_cash_conversion_ratio,
            "comparator_cash_conversion_ratio": d.comparator_cash_conversion_ratio,
            "current_one_off_gap_ratio": d.current_one_off_gap_ratio,
        }
        for key, value in optional.items():
            if value is not None:
                metrics[key] = float(value)
        return metrics
