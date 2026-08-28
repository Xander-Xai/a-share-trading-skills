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
from src.features.erg_shadow import EvidenceRef, ExpectationEvidence, SurpriseEvidence


EXPECTATION_SURPRISE_SCHEMA_VERSION = "1.0"
VALID_BASELINE_TYPES = {"COMPANY_GUIDANCE", "CONSENSUS_RECENT"}
VALID_CONFIDENCE = {"HIGH", "MEDIUM", "LOW"}
VALID_SURPRISE_METHODS = {"POINT_DELTA", "RANGE_BREAK"}
VALID_POLARITY = {"HIGHER_IS_POSITIVE", "LOWER_IS_POSITIVE"}
SUPPORTED_EXPECTATION_UNITS = {
    "CNY": 1.0,
    "CNY_YUAN": 1.0,
    "CNY_THOUSAND": 1_000.0,
    "CNY_10K": 10_000.0,
    "CNY_MILLION": 1_000_000.0,
    "CNY_100M": 100_000_000.0,
}


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


def _normalize_expectation_value(value: float | int | None, unit: str) -> float | None:
    if value is None:
        return None
    _finite(value, "expectation value")
    factor = SUPPORTED_EXPECTATION_UNITS.get(unit)
    if factor is None:
        raise ValueError(
            "unsupported expectation unit for monetary v1 adapter: "
            f"{unit!r}; use an explicit future unit adapter rather than guessing"
        )
    return float(value) * factor


def _record_ref(record: StoredPITRecord, *, note: str) -> EvidenceRef:
    return EvidenceRef(
        ref=f"{record.metadata.record_id}@{record.metadata.revision_id}",
        source_tier=record.metadata.source_tier,
        source_snapshot_id=record.metadata.source_snapshot_id,
        note=note,
    )


@dataclass(frozen=True)
class ExpectationSurpriseContract:
    contract_id: str
    schema_version: str
    baseline_type: str
    expectation_record_id: str
    actual_record_id: str
    security_id: str
    fiscal_period: str
    actual_period_end: str
    metric: str
    confidence: str
    normalized_unit: str
    surprise_method: str
    metric_polarity: str
    neutral_tolerance_abs: float = 0.0

    def identity_payload(self) -> dict[str, Any]:
        return {
            "schema_version": self.schema_version,
            "baseline_type": self.baseline_type,
            "expectation_record_id": self.expectation_record_id,
            "actual_record_id": self.actual_record_id,
            "security_id": self.security_id,
            "fiscal_period": self.fiscal_period,
            "actual_period_end": self.actual_period_end,
            "metric": self.metric,
            "confidence": self.confidence,
            "normalized_unit": self.normalized_unit,
            "surprise_method": self.surprise_method,
            "metric_polarity": self.metric_polarity,
            "neutral_tolerance_abs": self.neutral_tolerance_abs,
        }

    def validate(self) -> None:
        if self.schema_version != EXPECTATION_SURPRISE_SCHEMA_VERSION:
            raise ValueError("unsupported expectation/surprise contract schema")
        if self.baseline_type not in VALID_BASELINE_TYPES:
            raise ValueError(f"unsupported source-backed baseline_type: {self.baseline_type}")
        for value, field_name in (
            (self.expectation_record_id, "expectation_record_id"),
            (self.actual_record_id, "actual_record_id"),
            (self.security_id, "security_id"),
            (self.fiscal_period, "fiscal_period"),
            (self.actual_period_end, "actual_period_end"),
            (self.metric, "metric"),
            (self.normalized_unit, "normalized_unit"),
        ):
            _require_text(value, field_name)
        if self.confidence not in VALID_CONFIDENCE:
            raise ValueError(f"invalid confidence: {self.confidence}")
        if self.normalized_unit != "CNY":
            raise ValueError("v1 source-backed adapter only normalizes monetary totals to CNY")
        if self.surprise_method not in VALID_SURPRISE_METHODS:
            raise ValueError(f"invalid surprise_method: {self.surprise_method}")
        if self.metric_polarity not in VALID_POLARITY:
            raise ValueError(f"invalid metric_polarity: {self.metric_polarity}")
        _finite(self.neutral_tolerance_abs, "neutral_tolerance_abs")
        if self.neutral_tolerance_abs < 0:
            raise ValueError("neutral_tolerance_abs cannot be negative")
        if self.baseline_type == "CONSENSUS_RECENT" and self.surprise_method != "POINT_DELTA":
            raise ValueError("CONSENSUS_RECENT v1 requires POINT_DELTA")
        if _sha256(self.identity_payload()) != self.contract_id:
            raise ValueError("contract_id does not match contract content")

    def to_dict(self) -> dict[str, Any]:
        return {**self.identity_payload(), "contract_id": self.contract_id}

    @classmethod
    def build(
        cls,
        *,
        baseline_type: str,
        expectation_record_id: str,
        actual_record_id: str,
        security_id: str,
        fiscal_period: str,
        actual_period_end: str,
        metric: str,
        confidence: str,
        surprise_method: str,
        metric_polarity: str,
        neutral_tolerance_abs: float = 0.0,
        normalized_unit: str = "CNY",
    ) -> "ExpectationSurpriseContract":
        provisional = cls(
            contract_id="pending",
            schema_version=EXPECTATION_SURPRISE_SCHEMA_VERSION,
            baseline_type=baseline_type,
            expectation_record_id=expectation_record_id,
            actual_record_id=actual_record_id,
            security_id=security_id,
            fiscal_period=fiscal_period,
            actual_period_end=actual_period_end,
            metric=metric,
            confidence=confidence,
            normalized_unit=normalized_unit,
            surprise_method=surprise_method,
            metric_polarity=metric_polarity,
            neutral_tolerance_abs=float(neutral_tolerance_abs),
        )
        result = cls(**{**provisional.__dict__, "contract_id": _sha256(provisional.identity_payload())})
        result.validate()
        return result

    @classmethod
    def from_dict(cls, payload: Mapping[str, Any]) -> "ExpectationSurpriseContract":
        result = cls(
            contract_id=str(payload["contract_id"]),
            schema_version=str(payload["schema_version"]),
            baseline_type=str(payload["baseline_type"]),
            expectation_record_id=str(payload["expectation_record_id"]),
            actual_record_id=str(payload["actual_record_id"]),
            security_id=str(payload["security_id"]),
            fiscal_period=str(payload["fiscal_period"]),
            actual_period_end=str(payload["actual_period_end"]),
            metric=str(payload["metric"]),
            confidence=str(payload["confidence"]),
            normalized_unit=str(payload["normalized_unit"]),
            surprise_method=str(payload["surprise_method"]),
            metric_polarity=str(payload["metric_polarity"]),
            neutral_tolerance_abs=float(payload.get("neutral_tolerance_abs", 0.0)),
        )
        result.validate()
        return result


@dataclass(frozen=True)
class ExpectationSurpriseResult:
    result_id: str
    schema_version: str
    contract_id: str
    strategy_id: str
    sleeve: str
    as_of: str
    information_timestamp: str
    expectation: ExpectationEvidence
    surprise: SurpriseEvidence

    def identity_payload(self) -> dict[str, Any]:
        return {
            "schema_version": self.schema_version,
            "contract_id": self.contract_id,
            "strategy_id": self.strategy_id,
            "sleeve": self.sleeve,
            "as_of": self.as_of,
            "information_timestamp": self.information_timestamp,
            "expectation": self.expectation.to_dict(),
            "surprise": self.surprise.to_dict(),
        }

    def validate(self) -> None:
        if self.schema_version != EXPECTATION_SURPRISE_SCHEMA_VERSION:
            raise ValueError("unsupported expectation/surprise result schema")
        require_strategy_context(
            strategy_id=self.strategy_id,
            sleeve=self.sleeve,
            expected_strategy_id=SHORT_MID_STRATEGY_ID,
            expected_sleeve=SHORT_MID_SLEEVE,
        )
        _require_text(self.contract_id, "contract_id")
        as_of = _parse_aware(self.as_of, "as_of")
        info = _parse_aware(self.information_timestamp, "information_timestamp")
        if as_of < info:
            raise ValueError("as_of cannot precede information_timestamp")
        self.expectation.validate()
        self.surprise.validate()
        if self.surprise.verified and not self.expectation.eligible_for_verified_surprise():
            raise ValueError("verified surprise requires eligible expectation evidence")
        if _sha256(self.identity_payload()) != self.result_id:
            raise ValueError("result_id does not match result content")

    def to_dict(self) -> dict[str, Any]:
        return {**self.identity_payload(), "result_id": self.result_id}


class PITExpectationSurpriseAdapter:
    """Build source-backed ERG expectation/surprise evidence from a PIT snapshot.

    The adapter never searches for the most favorable baseline. A frozen contract
    names the exact expectation and actual record ids. This avoids ex-post source
    substitution and keeps the baseline-selection decision auditable.

    v1 supports monetary earnings-style metrics only. It intentionally does not
    auto-label GUIDANCE as EARNINGS_PREANNOUNCEMENT because the current canonical
    GUIDANCE entity has no source-backed subtype field.
    """

    def build(
        self,
        records: Iterable[StoredPITRecord],
        *,
        contract: ExpectationSurpriseContract,
        as_of: str,
        information_timestamp: str,
        strategy_id: str = SHORT_MID_STRATEGY_ID,
        sleeve: str = SHORT_MID_SLEEVE,
    ) -> ExpectationSurpriseResult:
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
        expectation_record = self._exact_record(rows, contract.expectation_record_id)
        actual_record = self._exact_record(rows, contract.actual_record_id)

        self._validate_record_clock(
            expectation_record,
            actual_record,
            as_of=as_of_dt,
            information_timestamp=info_dt,
        )
        expectation = self._build_expectation(expectation_record, contract)
        surprise = self._build_surprise(
            expectation,
            actual_record,
            contract,
            expectation_record=expectation_record,
        )

        provisional = ExpectationSurpriseResult(
            result_id="pending",
            schema_version=EXPECTATION_SURPRISE_SCHEMA_VERSION,
            contract_id=contract.contract_id,
            strategy_id=strategy_id,
            sleeve=sleeve,
            as_of=as_of_dt.isoformat(),
            information_timestamp=info_dt.isoformat(),
            expectation=expectation,
            surprise=surprise,
        )
        result = ExpectationSurpriseResult(
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
        record = matches[0]
        record.validate()
        return record

    @staticmethod
    def _validate_record_clock(
        expectation_record: StoredPITRecord,
        actual_record: StoredPITRecord,
        *,
        as_of: datetime,
        information_timestamp: datetime,
    ) -> None:
        expectation_available = _parse_aware(
            expectation_record.metadata.available_at,
            "expectation.available_at",
        )
        actual_available = _parse_aware(actual_record.metadata.available_at, "actual.available_at")
        if expectation_available >= information_timestamp:
            raise ValueError(
                "expectation baseline must be observable strictly before information_timestamp"
            )
        if actual_available < information_timestamp:
            raise ValueError(
                "actual result became observable before information_timestamp; event clock is inconsistent"
            )
        if actual_available > as_of:
            raise ValueError("actual result is not observable by as_of")

    def _build_expectation(
        self,
        record: StoredPITRecord,
        contract: ExpectationSurpriseContract,
    ) -> ExpectationEvidence:
        if record.metadata.security_id != contract.security_id:
            raise ValueError("expectation record security_id does not match frozen contract")
        if contract.baseline_type == "COMPANY_GUIDANCE":
            return self._from_guidance(record, contract)
        if contract.baseline_type == "CONSENSUS_RECENT":
            return self._from_consensus(record, contract)
        raise AssertionError("validated baseline_type became unsupported")

    @staticmethod
    def _from_guidance(
        record: StoredPITRecord,
        contract: ExpectationSurpriseContract,
    ) -> ExpectationEvidence:
        if record.metadata.entity_type != "GUIDANCE":
            raise ValueError("COMPANY_GUIDANCE contract requires GUIDANCE record")
        payload = record.payload
        if payload.get("fiscal_period") != contract.fiscal_period:
            raise ValueError("guidance fiscal_period does not match frozen contract")
        if payload.get("metric") != contract.metric:
            raise ValueError("guidance metric does not match frozen contract")
        unit = str(payload.get("unit"))
        low = _normalize_expectation_value(payload.get("lower"), unit)
        high = _normalize_expectation_value(payload.get("upper"), unit)
        point = _normalize_expectation_value(payload.get("point_estimate"), unit)
        center = point
        if center is None and low is not None and high is not None:
            center = (low + high) / 2.0
        evidence = ExpectationEvidence(
            baseline_type="COMPANY_GUIDANCE",
            confidence=contract.confidence,
            center=center,
            low=low,
            high=high,
            dispersion=None,
            coverage_count=None,
            coverage_flag=True,
            fiscal_period=contract.fiscal_period,
            metric=contract.metric,
            unit=contract.normalized_unit,
            evidence_refs=(
                _record_ref(record, note=f"expectation_contract={contract.contract_id}"),
            ),
        )
        evidence.validate()
        return evidence

    @staticmethod
    def _from_consensus(
        record: StoredPITRecord,
        contract: ExpectationSurpriseContract,
    ) -> ExpectationEvidence:
        if record.metadata.entity_type != "CONSENSUS_EXPECTATION":
            raise ValueError("CONSENSUS_RECENT contract requires CONSENSUS_EXPECTATION record")
        payload = record.payload
        if payload.get("fiscal_period") != contract.fiscal_period:
            raise ValueError("consensus fiscal_period does not match frozen contract")
        if payload.get("metric") != contract.metric:
            raise ValueError("consensus metric does not match frozen contract")
        source_baseline_type = str(payload.get("baseline_type"))
        if source_baseline_type not in {"SELL_SIDE_CONSENSUS", "CONSENSUS_RECENT"}:
            raise ValueError("consensus source record is not a supported sell-side consensus baseline")
        coverage_count = payload.get("coverage_count")
        if not isinstance(coverage_count, int) or isinstance(coverage_count, bool) or coverage_count < 2:
            raise ValueError("CONSENSUS_RECENT requires source coverage_count >= 2")
        unit = str(payload.get("unit"))
        center = _normalize_expectation_value(payload.get("value"), unit)
        dispersion = _normalize_expectation_value(payload.get("dispersion"), unit)
        evidence = ExpectationEvidence(
            baseline_type="CONSENSUS_RECENT",
            confidence=contract.confidence,
            center=center,
            low=None,
            high=None,
            dispersion=dispersion,
            coverage_count=coverage_count,
            coverage_flag=True,
            fiscal_period=contract.fiscal_period,
            metric=contract.metric,
            unit=contract.normalized_unit,
            evidence_refs=(
                _record_ref(record, note=f"expectation_contract={contract.contract_id}"),
            ),
        )
        evidence.validate()
        return evidence

    def _build_surprise(
        self,
        expectation: ExpectationEvidence,
        actual_record: StoredPITRecord,
        contract: ExpectationSurpriseContract,
        *,
        expectation_record: StoredPITRecord,
    ) -> SurpriseEvidence:
        if actual_record.metadata.entity_type != "FINANCIAL_STATEMENT":
            raise ValueError("actual_record_id must reference FINANCIAL_STATEMENT")
        if actual_record.metadata.security_id != contract.security_id:
            raise ValueError("actual financial statement security_id does not match frozen contract")
        payload = actual_record.payload
        if payload.get("period_end") != contract.actual_period_end:
            raise ValueError("financial-statement period_end does not match frozen contract")
        metrics = payload.get("metrics")
        if not isinstance(metrics, Mapping) or contract.metric not in metrics:
            raise ValueError(f"actual financial statement is missing metric: {contract.metric}")
        raw_actual = metrics[contract.metric]
        if raw_actual is None:
            raise ValueError(f"actual financial metric is unresolved: {contract.metric}")
        _finite(raw_actual, "actual metric")
        currency = str(payload.get("currency"))
        if currency != "CNY":
            raise ValueError("v1 actual monetary adapter requires FINANCIAL_STATEMENT currency=CNY")
        unit_scale = payload.get("unit_scale")
        _finite(unit_scale, "financial_statement.unit_scale")
        if float(unit_scale) <= 0:
            raise ValueError("financial_statement.unit_scale must be > 0")
        actual = float(raw_actual) * float(unit_scale)

        diagnostic_center = expectation.center
        delta = None if diagnostic_center is None else actual - diagnostic_center
        delta_pct = None
        if diagnostic_center is not None and diagnostic_center != 0:
            delta_pct = delta / abs(diagnostic_center)

        refs = (
            _record_ref(
                expectation_record,
                note=f"expectation_contract={contract.contract_id}",
            ),
            _record_ref(
                actual_record,
                note=f"actual_for_expectation_contract={contract.contract_id}",
            ),
        )

        if not expectation.eligible_for_verified_surprise():
            evidence = SurpriseEvidence(
                direction="UNRESOLVED",
                verified=False,
                metric=contract.metric,
                actual=actual,
                expected_center=diagnostic_center,
                delta=delta,
                delta_pct=delta_pct,
                calculation_method=f"SOURCE_BACKED_{contract.surprise_method}_V1",
                classification_contract_id=contract.contract_id,
                evidence_refs=refs,
            )
            evidence.validate()
            return evidence

        direction = self._classify_direction(actual, expectation, contract)
        if direction == "UNRESOLVED":
            verified = False
        else:
            verified = True
        evidence = SurpriseEvidence(
            direction=direction,
            verified=verified,
            metric=contract.metric,
            actual=actual,
            expected_center=diagnostic_center,
            delta=delta,
            delta_pct=delta_pct,
            calculation_method=f"SOURCE_BACKED_{contract.surprise_method}_V1",
            classification_contract_id=contract.contract_id,
            evidence_refs=refs,
        )
        evidence.validate()
        return evidence

    @staticmethod
    def _classify_direction(
        actual: float,
        expectation: ExpectationEvidence,
        contract: ExpectationSurpriseContract,
    ) -> str:
        tolerance = contract.neutral_tolerance_abs
        polarity = contract.metric_polarity

        if contract.surprise_method == "POINT_DELTA":
            if expectation.center is None:
                return "UNRESOLVED"
            delta = actual - expectation.center
            if abs(delta) <= tolerance:
                return "NEUTRAL"
            economically_higher = delta > 0
        elif contract.surprise_method == "RANGE_BREAK":
            if expectation.low is None or expectation.high is None:
                return "UNRESOLVED"
            if expectation.low - tolerance <= actual <= expectation.high + tolerance:
                return "NEUTRAL"
            economically_higher = actual > expectation.high + tolerance
        else:
            raise AssertionError("validated surprise_method became unsupported")

        if polarity == "HIGHER_IS_POSITIVE":
            return "POSITIVE" if economically_higher else "NEGATIVE"
        if polarity == "LOWER_IS_POSITIVE":
            return "NEGATIVE" if economically_higher else "POSITIVE"
        raise AssertionError("validated metric_polarity became unsupported")
