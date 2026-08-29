from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from datetime import datetime
from typing import Any, Iterable, Mapping
from zoneinfo import ZoneInfo

from src.core.pit_store import StoredPITRecord
from src.core.strategy_boundary import (
    SHORT_MID_SLEEVE,
    SHORT_MID_STRATEGY_ID,
    require_strategy_context,
)
from src.features.erg_earnings_materiality import (
    EarningsMaterialityContract,
    EarningsMaterialityResult,
    PITEarningsMaterialityProducer,
)
from src.features.erg_expectation_surprise import (
    ExpectationSurpriseContract,
    ExpectationSurpriseResult,
    PITExpectationSurpriseAdapter,
)
from src.features.erg_shadow import (
    ERGEvidenceBundle,
    ERGShadowDecision,
    ERGShadowStateMachine,
    EligibilityEvidence,
    PrepricingEvidence,
    ReactionEvidence,
)
from src.features.event_reaction import EventReactionMeasurement, EventWindowMetric


EARNINGS_ERG_PIPELINE_SCHEMA_VERSION = "1.0"
EARNINGS_ERG_PIPELINE_VERSION = "EARNINGS_ERG_E2E_V1"
SHANGHAI = ZoneInfo("Asia/Shanghai")
VALID_ELIGIBILITY_STATUS = {"PASS", "FAIL", "UNRESOLVED"}
VALID_PREPRICING_STATES = {
    "UNDERPRICED",
    "PARTIALLY_PRICED",
    "HEAVILY_PRICED",
    "UNRESOLVED",
}
VALID_REACTION_STATES = {
    "POSITIVE_CONFIRMATION",
    "MIXED",
    "NEGATIVE_DISAGREEMENT",
    "UNRESOLVED",
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


def _validate_sha256(value: str, field_name: str) -> None:
    _require_text(value, field_name)
    if len(value) != 64:
        raise ValueError(f"{field_name} must be a 64-character SHA-256 hex id")
    try:
        int(value, 16)
    except ValueError as exc:
        raise ValueError(f"{field_name} must be hexadecimal") from exc


def _window_metrics(metric: EventWindowMetric) -> dict[str, float]:
    return {
        "window_sessions": float(metric.sessions),
        "stock_return": float(metric.stock_return),
        "benchmark_return": float(metric.benchmark_return),
        "excess_return": float(metric.excess_return),
        "cumulative_abnormal_return": float(metric.cumulative_abnormal_return),
    }


def event_reaction_measurement_from_dict(payload: Mapping[str, Any]) -> EventReactionMeasurement:
    """Parse and validate a serialized EventReactionMeasurement artifact."""

    result = EventReactionMeasurement(
        event_measurement_id=str(payload["event_measurement_id"]),
        schema_version=str(payload["schema_version"]),
        measurement_basis=str(payload["measurement_basis"]),
        strategy_id=str(payload["strategy_id"]),
        sleeve=str(payload["sleeve"]),
        event_id=str(payload["event_id"]),
        event_family=str(payload["event_family"]),
        security_id=str(payload["security_id"]),
        information_timestamp=str(payload["information_timestamp"]),
        first_tradable_timestamp=str(payload["first_tradable_timestamp"]),
        full_session_anchor_date=str(payload["full_session_anchor_date"]),
        partial_session_reaction_omitted=bool(payload["partial_session_reaction_omitted"]),
        reaction_window_contract_id=str(payload["reaction_window_contract_id"]),
        primary_reaction_window_sessions=(
            None
            if payload.get("primary_reaction_window_sessions") is None
            else int(payload["primary_reaction_window_sessions"])
        ),
        primary_window_status=str(payload["primary_window_status"]),
        relative_performance_id=str(payload["relative_performance_id"]),
        benchmark_id=str(payload["benchmark_id"]),
        benchmark_selection_contract_id=str(payload["benchmark_selection_contract_id"]),
        prepricing_metrics=tuple(
            EventWindowMetric(**dict(item)) for item in payload.get("prepricing_metrics", ())
        ),
        reaction_metrics=tuple(
            EventWindowMetric(**dict(item)) for item in payload.get("reaction_metrics", ())
        ),
    )
    result.validate()
    return result


@dataclass(frozen=True)
class EarningsERGAssemblyContract:
    contract_id: str
    schema_version: str
    event_id: str
    security_id: str
    information_timestamp: str
    first_tradable_timestamp: str
    expectation_surprise_contract_id: str
    earnings_materiality_contract_id: str
    event_measurement_id: str
    eligibility_status: str
    eligibility_reasons: tuple[str, ...] = ()
    prepricing_state: str = "UNRESOLVED"
    prepricing_window_sessions: int | None = None
    prepricing_classification_contract_id: str | None = None
    reaction_state: str = "UNRESOLVED"
    reaction_classification_contract_id: str | None = None

    def identity_payload(self) -> dict[str, Any]:
        return {
            "schema_version": self.schema_version,
            "event_id": self.event_id,
            "event_family": "EARNINGS",
            "security_id": self.security_id,
            "information_timestamp": self.information_timestamp,
            "first_tradable_timestamp": self.first_tradable_timestamp,
            "expectation_surprise_contract_id": self.expectation_surprise_contract_id,
            "earnings_materiality_contract_id": self.earnings_materiality_contract_id,
            "event_measurement_id": self.event_measurement_id,
            "eligibility_status": self.eligibility_status,
            "eligibility_reasons": list(self.eligibility_reasons),
            "prepricing_state": self.prepricing_state,
            "prepricing_window_sessions": self.prepricing_window_sessions,
            "prepricing_classification_contract_id": self.prepricing_classification_contract_id,
            "reaction_state": self.reaction_state,
            "reaction_classification_contract_id": self.reaction_classification_contract_id,
        }

    def validate(self) -> None:
        if self.schema_version != EARNINGS_ERG_PIPELINE_SCHEMA_VERSION:
            raise ValueError("unsupported earnings ERG assembly contract schema")
        for value, field_name in (
            (self.event_id, "event_id"),
            (self.security_id, "security_id"),
            (self.expectation_surprise_contract_id, "expectation_surprise_contract_id"),
            (self.earnings_materiality_contract_id, "earnings_materiality_contract_id"),
            (self.event_measurement_id, "event_measurement_id"),
        ):
            _require_text(value, field_name)
        info = _parse_aware(self.information_timestamp, "information_timestamp")
        tradable = _parse_aware(self.first_tradable_timestamp, "first_tradable_timestamp")
        if tradable < info:
            raise ValueError("first_tradable_timestamp cannot precede information_timestamp")
        if self.eligibility_status not in VALID_ELIGIBILITY_STATUS:
            raise ValueError(f"invalid eligibility_status: {self.eligibility_status}")
        for reason in self.eligibility_reasons:
            _require_text(reason, "eligibility_reason")
        if self.eligibility_status == "PASS" and self.eligibility_reasons:
            raise ValueError("PASS eligibility must not carry failure reasons")
        if self.eligibility_status != "PASS" and not self.eligibility_reasons:
            raise ValueError("non-PASS eligibility requires reasons")
        if self.prepricing_state not in VALID_PREPRICING_STATES:
            raise ValueError(f"invalid prepricing_state: {self.prepricing_state}")
        if self.prepricing_window_sessions is not None:
            if (
                isinstance(self.prepricing_window_sessions, bool)
                or not isinstance(self.prepricing_window_sessions, int)
                or self.prepricing_window_sessions <= 0
            ):
                raise ValueError("prepricing_window_sessions must be a positive integer")
        if self.prepricing_classification_contract_id is not None:
            _require_text(
                self.prepricing_classification_contract_id,
                "prepricing_classification_contract_id",
            )
        if self.prepricing_state != "UNRESOLVED":
            if self.prepricing_window_sessions is None:
                raise ValueError("resolved prepricing requires prepricing_window_sessions")
            if self.prepricing_classification_contract_id is None:
                raise ValueError("resolved prepricing requires a classification contract id")
        if self.reaction_state not in VALID_REACTION_STATES:
            raise ValueError(f"invalid reaction_state: {self.reaction_state}")
        if self.reaction_classification_contract_id is not None:
            _require_text(
                self.reaction_classification_contract_id,
                "reaction_classification_contract_id",
            )
        if self.reaction_state != "UNRESOLVED" and self.reaction_classification_contract_id is None:
            raise ValueError("resolved reaction requires a classification contract id")
        if _sha256(self.identity_payload()) != self.contract_id:
            raise ValueError("contract_id does not match assembly contract content")

    def to_dict(self) -> dict[str, Any]:
        return {**self.identity_payload(), "contract_id": self.contract_id}

    @classmethod
    def build(
        cls,
        *,
        event_id: str,
        security_id: str,
        information_timestamp: str,
        first_tradable_timestamp: str,
        expectation_surprise_contract_id: str,
        earnings_materiality_contract_id: str,
        event_measurement_id: str,
        eligibility_status: str,
        eligibility_reasons: Iterable[str] = (),
        prepricing_state: str = "UNRESOLVED",
        prepricing_window_sessions: int | None = None,
        prepricing_classification_contract_id: str | None = None,
        reaction_state: str = "UNRESOLVED",
        reaction_classification_contract_id: str | None = None,
    ) -> "EarningsERGAssemblyContract":
        provisional = cls(
            contract_id="pending",
            schema_version=EARNINGS_ERG_PIPELINE_SCHEMA_VERSION,
            event_id=event_id,
            security_id=security_id,
            information_timestamp=information_timestamp,
            first_tradable_timestamp=first_tradable_timestamp,
            expectation_surprise_contract_id=expectation_surprise_contract_id,
            earnings_materiality_contract_id=earnings_materiality_contract_id,
            event_measurement_id=event_measurement_id,
            eligibility_status=eligibility_status,
            eligibility_reasons=tuple(eligibility_reasons),
            prepricing_state=prepricing_state,
            prepricing_window_sessions=prepricing_window_sessions,
            prepricing_classification_contract_id=prepricing_classification_contract_id,
            reaction_state=reaction_state,
            reaction_classification_contract_id=reaction_classification_contract_id,
        )
        result = cls(**{**provisional.__dict__, "contract_id": _sha256(provisional.identity_payload())})
        result.validate()
        return result

    @classmethod
    def from_dict(cls, payload: Mapping[str, Any]) -> "EarningsERGAssemblyContract":
        result = cls(
            contract_id=str(payload["contract_id"]),
            schema_version=str(payload["schema_version"]),
            event_id=str(payload["event_id"]),
            security_id=str(payload["security_id"]),
            information_timestamp=str(payload["information_timestamp"]),
            first_tradable_timestamp=str(payload["first_tradable_timestamp"]),
            expectation_surprise_contract_id=str(payload["expectation_surprise_contract_id"]),
            earnings_materiality_contract_id=str(payload["earnings_materiality_contract_id"]),
            event_measurement_id=str(payload["event_measurement_id"]),
            eligibility_status=str(payload["eligibility_status"]),
            eligibility_reasons=tuple(payload.get("eligibility_reasons", ())),
            prepricing_state=str(payload.get("prepricing_state", "UNRESOLVED")),
            prepricing_window_sessions=(
                None
                if payload.get("prepricing_window_sessions") is None
                else int(payload["prepricing_window_sessions"])
            ),
            prepricing_classification_contract_id=(
                None
                if payload.get("prepricing_classification_contract_id") is None
                else str(payload["prepricing_classification_contract_id"])
            ),
            reaction_state=str(payload.get("reaction_state", "UNRESOLVED")),
            reaction_classification_contract_id=(
                None
                if payload.get("reaction_classification_contract_id") is None
                else str(payload["reaction_classification_contract_id"])
            ),
        )
        result.validate()
        return result


@dataclass(frozen=True)
class EarningsERGRun:
    run_id: str
    schema_version: str
    pipeline_version: str
    strategy_id: str
    sleeve: str
    data_snapshot_id: str
    as_of: str
    assembly_contract_id: str
    expectation_surprise_result_id: str
    earnings_materiality_result_id: str
    event_measurement_id: str
    evidence_bundle_id: str
    shadow_decision_id: str
    evidence_bundle: ERGEvidenceBundle
    shadow_decision: ERGShadowDecision

    def identity_payload(self) -> dict[str, Any]:
        return {
            "schema_version": self.schema_version,
            "pipeline_version": self.pipeline_version,
            "strategy_id": self.strategy_id,
            "sleeve": self.sleeve,
            "data_snapshot_id": self.data_snapshot_id,
            "as_of": self.as_of,
            "assembly_contract_id": self.assembly_contract_id,
            "expectation_surprise_result_id": self.expectation_surprise_result_id,
            "earnings_materiality_result_id": self.earnings_materiality_result_id,
            "event_measurement_id": self.event_measurement_id,
            "evidence_bundle_id": self.evidence_bundle_id,
            "shadow_decision_id": self.shadow_decision_id,
            "evidence_bundle": self.evidence_bundle.to_dict(),
            "shadow_decision": self.shadow_decision.to_dict(),
        }

    def validate(self) -> None:
        if self.schema_version != EARNINGS_ERG_PIPELINE_SCHEMA_VERSION:
            raise ValueError("unsupported earnings ERG run schema")
        if self.pipeline_version != EARNINGS_ERG_PIPELINE_VERSION:
            raise ValueError("unsupported earnings ERG pipeline version")
        require_strategy_context(
            strategy_id=self.strategy_id,
            sleeve=self.sleeve,
            expected_strategy_id=SHORT_MID_STRATEGY_ID,
            expected_sleeve=SHORT_MID_SLEEVE,
        )
        _validate_sha256(self.data_snapshot_id, "data_snapshot_id")
        _parse_aware(self.as_of, "as_of")
        for value, field_name in (
            (self.assembly_contract_id, "assembly_contract_id"),
            (self.expectation_surprise_result_id, "expectation_surprise_result_id"),
            (self.earnings_materiality_result_id, "earnings_materiality_result_id"),
            (self.event_measurement_id, "event_measurement_id"),
            (self.evidence_bundle_id, "evidence_bundle_id"),
            (self.shadow_decision_id, "shadow_decision_id"),
        ):
            _require_text(value, field_name)
        self.evidence_bundle.validate()
        self.shadow_decision.validate()
        if self.evidence_bundle.evidence_bundle_id != self.evidence_bundle_id:
            raise ValueError("evidence_bundle_id lineage mismatch")
        if self.shadow_decision.decision_id != self.shadow_decision_id:
            raise ValueError("shadow_decision_id lineage mismatch")
        if self.shadow_decision.evidence_bundle_id != self.evidence_bundle_id:
            raise ValueError("shadow decision must consume this evidence bundle")
        if _sha256(self.identity_payload()) != self.run_id:
            raise ValueError("run_id does not match run content")

    def to_dict(self) -> dict[str, Any]:
        return {**self.identity_payload(), "run_id": self.run_id}


@dataclass(frozen=True)
class EarningsERGRunArtifacts:
    run: EarningsERGRun
    expectation_surprise: ExpectationSurpriseResult
    earnings_materiality: EarningsMaterialityResult
    event_measurement: EventReactionMeasurement

    def to_dict(self) -> dict[str, Any]:
        self.run.validate()
        self.expectation_surprise.validate()
        self.earnings_materiality.validate()
        self.event_measurement.validate()
        if self.run.expectation_surprise_result_id != self.expectation_surprise.result_id:
            raise ValueError("expectation/surprise artifact lineage mismatch")
        if self.run.earnings_materiality_result_id != self.earnings_materiality.result_id:
            raise ValueError("earnings materiality artifact lineage mismatch")
        if self.run.event_measurement_id != self.event_measurement.event_measurement_id:
            raise ValueError("event measurement artifact lineage mismatch")
        payload = {
            "artifact_schema_version": EARNINGS_ERG_PIPELINE_SCHEMA_VERSION,
            "run": self.run.to_dict(),
            "expectation_surprise": self.expectation_surprise.to_dict(),
            "earnings_materiality": self.earnings_materiality.to_dict(),
            "event_measurement": self.event_measurement.to_dict(),
        }
        return {**payload, "artifact_id": _sha256(payload)}


class EarningsERGEndToEndPipeline:
    """Assemble one auditable EARNINGS ERG Shadow run from frozen artifacts.

    The pipeline orchestrates already-governed components. It does not invent
    Materiality, Prepricing or Reaction thresholds. Resolved categorical market
    states must be supplied under explicit classification-contract ids.

    Research and execution remain separated: the downstream v0 state machine is
    Shadow-only, always FLAT and never executable.
    """

    def run(
        self,
        records: Iterable[StoredPITRecord],
        *,
        data_snapshot_id: str,
        as_of: str,
        expectation_contract: ExpectationSurpriseContract,
        materiality_contract: EarningsMaterialityContract,
        event_measurement: EventReactionMeasurement,
        assembly_contract: EarningsERGAssemblyContract,
        strategy_id: str = SHORT_MID_STRATEGY_ID,
        sleeve: str = SHORT_MID_SLEEVE,
    ) -> EarningsERGRunArtifacts:
        _validate_sha256(data_snapshot_id, "data_snapshot_id")
        as_of_dt = _parse_aware(as_of, "as_of")
        require_strategy_context(
            strategy_id=strategy_id,
            sleeve=sleeve,
            expected_strategy_id=SHORT_MID_STRATEGY_ID,
            expected_sleeve=SHORT_MID_SLEEVE,
        )
        expectation_contract.validate()
        materiality_contract.validate()
        event_measurement.validate()
        assembly_contract.validate()

        if assembly_contract.expectation_surprise_contract_id != expectation_contract.contract_id:
            raise ValueError("assembly contract does not reference supplied expectation contract")
        if assembly_contract.earnings_materiality_contract_id != materiality_contract.contract_id:
            raise ValueError("assembly contract does not reference supplied materiality contract")
        if assembly_contract.event_measurement_id != event_measurement.event_measurement_id:
            raise ValueError("assembly contract does not reference supplied event measurement")
        if assembly_contract.event_id != event_measurement.event_id:
            raise ValueError("event_id mismatch between assembly contract and event measurement")
        if event_measurement.event_family != "EARNINGS":
            raise ValueError("EarningsERGEndToEndPipeline requires event_family=EARNINGS")
        if event_measurement.strategy_id != strategy_id or event_measurement.sleeve != sleeve:
            raise ValueError("event measurement strategy context mismatch")
        if assembly_contract.security_id != event_measurement.security_id:
            raise ValueError("security_id mismatch between assembly contract and event measurement")
        if expectation_contract.security_id != assembly_contract.security_id:
            raise ValueError("expectation contract security_id mismatch")
        if materiality_contract.security_id != assembly_contract.security_id:
            raise ValueError("materiality contract security_id mismatch")
        if expectation_contract.actual_record_id != materiality_contract.current_record_id:
            raise ValueError(
                "v1 requires Surprise actual and Materiality current statement to be the same PIT record"
            )
        if expectation_contract.metric != materiality_contract.primary_metric:
            raise ValueError(
                "v1 requires Surprise metric and Materiality primary_metric to match"
            )
        if assembly_contract.information_timestamp != event_measurement.information_timestamp:
            raise ValueError("information_timestamp mismatch with event measurement")
        if assembly_contract.first_tradable_timestamp != event_measurement.first_tradable_timestamp:
            raise ValueError("first_tradable_timestamp mismatch with event measurement")

        self._validate_measurement_as_of(event_measurement, as_of_dt)
        materialized = tuple(records)
        expectation_surprise = PITExpectationSurpriseAdapter().build(
            materialized,
            contract=expectation_contract,
            as_of=as_of_dt.isoformat(),
            information_timestamp=assembly_contract.information_timestamp,
            strategy_id=strategy_id,
            sleeve=sleeve,
        )
        earnings_materiality = PITEarningsMaterialityProducer().build(
            materialized,
            contract=materiality_contract,
            as_of=as_of_dt.isoformat(),
            information_timestamp=assembly_contract.information_timestamp,
            strategy_id=strategy_id,
            sleeve=sleeve,
        )
        actual_record = self._exact_record(materialized, expectation_contract.actual_record_id)

        prepricing = self._prepricing_evidence(event_measurement, assembly_contract)
        reaction = self._reaction_evidence(event_measurement, assembly_contract)
        eligibility = EligibilityEvidence(
            status=assembly_contract.eligibility_status,
            reasons=assembly_contract.eligibility_reasons,
        )
        eligibility.validate()

        bundle = ERGEvidenceBundle.build(
            event_id=assembly_contract.event_id,
            event_family="EARNINGS",
            security_id=assembly_contract.security_id,
            as_of=as_of_dt.isoformat(),
            information_timestamp=assembly_contract.information_timestamp,
            first_tradable_timestamp=assembly_contract.first_tradable_timestamp,
            primary_source_tier=actual_record.metadata.source_tier,
            eligibility=eligibility,
            expectation=expectation_surprise.expectation,
            surprise=expectation_surprise.surprise,
            materiality=earnings_materiality.materiality,
            prepricing=prepricing,
            reaction=reaction,
            strategy_id=strategy_id,
            sleeve=sleeve,
        )
        decision = ERGShadowStateMachine().evaluate(bundle)

        provisional = EarningsERGRun(
            run_id="pending",
            schema_version=EARNINGS_ERG_PIPELINE_SCHEMA_VERSION,
            pipeline_version=EARNINGS_ERG_PIPELINE_VERSION,
            strategy_id=strategy_id,
            sleeve=sleeve,
            data_snapshot_id=data_snapshot_id,
            as_of=as_of_dt.isoformat(),
            assembly_contract_id=assembly_contract.contract_id,
            expectation_surprise_result_id=expectation_surprise.result_id,
            earnings_materiality_result_id=earnings_materiality.result_id,
            event_measurement_id=event_measurement.event_measurement_id,
            evidence_bundle_id=bundle.evidence_bundle_id,
            shadow_decision_id=decision.decision_id,
            evidence_bundle=bundle,
            shadow_decision=decision,
        )
        run = EarningsERGRun(
            **{**provisional.__dict__, "run_id": _sha256(provisional.identity_payload())}
        )
        run.validate()
        return EarningsERGRunArtifacts(
            run=run,
            expectation_surprise=expectation_surprise,
            earnings_materiality=earnings_materiality,
            event_measurement=event_measurement,
        )

    @staticmethod
    def _exact_record(records: tuple[StoredPITRecord, ...], record_id: str) -> StoredPITRecord:
        matches = [record for record in records if record.metadata.record_id == record_id]
        if len(matches) != 1:
            raise ValueError(
                f"required logical PIT record must appear exactly once in snapshot: {record_id}"
            )
        matches[0].validate()
        return matches[0]

    @staticmethod
    def _validate_measurement_as_of(
        measurement: EventReactionMeasurement,
        as_of: datetime,
    ) -> None:
        as_of_date = as_of.astimezone(SHANGHAI).date().isoformat()
        future = [
            metric.end_date
            for metric in measurement.reaction_metrics
            if metric.end_date > as_of_date
        ]
        if future:
            raise ValueError(
                "event measurement contains post-as_of reaction data; "
                f"future_end_dates={sorted(set(future))}"
            )

    @staticmethod
    def _prepricing_evidence(
        measurement: EventReactionMeasurement,
        contract: EarningsERGAssemblyContract,
    ) -> PrepricingEvidence:
        selected: EventWindowMetric | None = None
        if contract.prepricing_window_sessions is not None:
            matches = [
                metric
                for metric in measurement.prepricing_metrics
                if metric.sessions == contract.prepricing_window_sessions
            ]
            if len(matches) != 1:
                raise ValueError(
                    "frozen prepricing window must appear exactly once in event measurement"
                )
            selected = matches[0]
        evidence = PrepricingEvidence(
            state=contract.prepricing_state,
            event_measurement_id=measurement.event_measurement_id,
            classification_contract_id=contract.prepricing_classification_contract_id,
            metrics=None if selected is None else _window_metrics(selected),
        )
        evidence.validate()
        return evidence

    @staticmethod
    def _reaction_evidence(
        measurement: EventReactionMeasurement,
        contract: EarningsERGAssemblyContract,
    ) -> ReactionEvidence:
        primary = measurement.primary_reaction_window_sessions
        selected: EventWindowMetric | None = None
        if primary is not None:
            matches = [metric for metric in measurement.reaction_metrics if metric.sessions == primary]
            if len(matches) != 1:
                raise ValueError("primary reaction window must appear exactly once")
            selected = matches[0]
        if contract.reaction_state != "UNRESOLVED" and primary is None:
            raise ValueError(
                "resolved reaction state requires a primary reaction window frozen by the measurement contract"
            )
        evidence = ReactionEvidence(
            state=contract.reaction_state,
            event_measurement_id=measurement.event_measurement_id,
            classification_contract_id=contract.reaction_classification_contract_id,
            primary_reaction_window_sessions=primary,
            benchmark_id=measurement.benchmark_id,
            benchmark_selection_contract_id=measurement.benchmark_selection_contract_id,
            metrics=None if selected is None else _window_metrics(selected),
        )
        evidence.validate()
        return evidence
