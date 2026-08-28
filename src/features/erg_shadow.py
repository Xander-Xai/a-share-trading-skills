from __future__ import annotations

import hashlib
import json
import math
from dataclasses import asdict, dataclass
from datetime import datetime
from typing import Any, Iterable, Mapping

from src.core.strategy_boundary import (
    SHORT_MID_SLEEVE,
    SHORT_MID_STRATEGY_ID,
    require_strategy_context,
)


ERG_EVIDENCE_SCHEMA_VERSION = "0.1"
ERG_STATE_MACHINE_VERSION = "ERG_SHADOW_STATE_V0"

VALID_EVENT_FAMILIES = {
    "EARNINGS",
    "EARNINGS_PREANNOUNCEMENT",
    "ORDER_CONTRACT",
    "COMMODITY_PRODUCT_PRICE",
    "POLICY",
    "CAPITAL_STRUCTURE",
    "OTHER",
}
VALID_SOURCE_TIERS = {"TIER1", "TIER2", "TIER3", "TIER4"}
VALID_HARD_GATE_STATUS = {"PASS", "FAIL", "UNRESOLVED"}
VALID_EXPECTATION_TYPES = {
    "CONSENSUS_RECENT",
    "COMPANY_GUIDANCE",
    "EARNINGS_PREANNOUNCEMENT",
    "BROKER_RANGE",
    "MODEL_BASELINE",
    "HISTORICAL_SEASONALITY",
    "NONE",
}
VALID_EXPECTATION_CONFIDENCE = {"HIGH", "MEDIUM", "LOW"}
VALID_SURPRISE_DIRECTIONS = {"POSITIVE", "NEUTRAL", "NEGATIVE", "UNRESOLVED"}
VALID_MATERIALITY_STATES = {"MATERIAL", "LOW_MATERIALITY", "UNRESOLVED"}
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
VALID_RESEARCH_STATES = {"REJECT", "WATCH", "CANDIDATE", "CONFIRMED", "INVALIDATED"}


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


def _finite(value: float | int | None, field_name: str, *, allow_none: bool = True) -> None:
    if value is None:
        if allow_none:
            return
        raise ValueError(f"{field_name} is required")
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise ValueError(f"{field_name} must be numeric")
    if not math.isfinite(float(value)):
        raise ValueError(f"{field_name} must be finite")


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


def _validate_string_tuple(values: Iterable[str], field_name: str) -> tuple[str, ...]:
    result = tuple(values)
    for value in result:
        _require_text(value, field_name)
    return result


@dataclass(frozen=True)
class EvidenceRef:
    ref: str
    source_tier: str
    source_snapshot_id: str | None = None
    note: str | None = None

    def validate(self) -> None:
        _require_text(self.ref, "evidence_ref.ref")
        if self.source_tier not in VALID_SOURCE_TIERS:
            raise ValueError(f"invalid source_tier: {self.source_tier}")
        if self.source_snapshot_id is not None:
            _require_text(self.source_snapshot_id, "source_snapshot_id")
        if self.note is not None:
            _require_text(self.note, "note")

    def to_dict(self) -> dict[str, Any]:
        self.validate()
        return asdict(self)


@dataclass(frozen=True)
class EligibilityEvidence:
    status: str
    reasons: tuple[str, ...] = ()

    def validate(self) -> None:
        if self.status not in VALID_HARD_GATE_STATUS:
            raise ValueError(f"invalid hard-gate status: {self.status}")
        _validate_string_tuple(self.reasons, "eligibility reason")
        if self.status == "PASS" and self.reasons:
            raise ValueError("PASS hard-gate evidence must not carry failure reasons")
        if self.status in {"FAIL", "UNRESOLVED"} and not self.reasons:
            raise ValueError(f"{self.status} hard-gate evidence requires reasons")

    def to_dict(self) -> dict[str, Any]:
        self.validate()
        return {"status": self.status, "reasons": list(self.reasons)}


@dataclass(frozen=True)
class ExpectationEvidence:
    baseline_type: str = "NONE"
    confidence: str = "LOW"
    center: float | None = None
    low: float | None = None
    high: float | None = None
    dispersion: float | None = None
    coverage_count: int | None = None
    coverage_flag: bool | None = None
    fiscal_period: str | None = None
    metric: str | None = None
    unit: str | None = None
    evidence_refs: tuple[EvidenceRef, ...] = ()

    def validate(self) -> None:
        if self.baseline_type not in VALID_EXPECTATION_TYPES:
            raise ValueError(f"invalid expectation baseline_type: {self.baseline_type}")
        if self.confidence not in VALID_EXPECTATION_CONFIDENCE:
            raise ValueError(f"invalid expectation confidence: {self.confidence}")
        for name in ("center", "low", "high", "dispersion"):
            _finite(getattr(self, name), f"expectation.{name}")
        if self.dispersion is not None and self.dispersion < 0:
            raise ValueError("expectation.dispersion cannot be negative")
        if self.low is not None and self.high is not None and self.low > self.high:
            raise ValueError("expectation.low cannot exceed expectation.high")
        if self.coverage_count is not None:
            if isinstance(self.coverage_count, bool) or not isinstance(self.coverage_count, int):
                raise ValueError("expectation.coverage_count must be an integer")
            if self.coverage_count < 0:
                raise ValueError("expectation.coverage_count cannot be negative")
        if self.baseline_type == "NONE":
            if self.confidence != "LOW":
                raise ValueError("NONE expectation baseline must remain LOW confidence")
            if self.coverage_flag is True:
                raise ValueError("NONE expectation baseline cannot claim coverage")
        if self.baseline_type == "CONSENSUS_RECENT" and self.coverage_count == 1:
            raise ValueError("a single analyst estimate cannot be labeled CONSENSUS_RECENT")
        for value, field_name in (
            (self.fiscal_period, "expectation.fiscal_period"),
            (self.metric, "expectation.metric"),
            (self.unit, "expectation.unit"),
        ):
            if value is not None:
                _require_text(value, field_name)
        for ref in self.evidence_refs:
            ref.validate()

    def eligible_for_verified_surprise(self) -> bool:
        self.validate()
        if self.baseline_type == "NONE" or self.confidence == "LOW":
            return False
        if self.coverage_flag is False:
            return False
        if self.baseline_type == "CONSENSUS_RECENT":
            return self.coverage_count is not None and self.coverage_count >= 2
        return True

    def to_dict(self) -> dict[str, Any]:
        self.validate()
        return {
            "baseline_type": self.baseline_type,
            "confidence": self.confidence,
            "center": self.center,
            "low": self.low,
            "high": self.high,
            "dispersion": self.dispersion,
            "coverage_count": self.coverage_count,
            "coverage_flag": self.coverage_flag,
            "fiscal_period": self.fiscal_period,
            "metric": self.metric,
            "unit": self.unit,
            "verified_surprise_eligible": self.eligible_for_verified_surprise(),
            "evidence_refs": [ref.to_dict() for ref in self.evidence_refs],
        }


@dataclass(frozen=True)
class SurpriseEvidence:
    direction: str = "UNRESOLVED"
    verified: bool = False
    metric: str | None = None
    actual: float | None = None
    expected_center: float | None = None
    delta: float | None = None
    delta_pct: float | None = None
    calculation_method: str | None = None
    classification_contract_id: str | None = None
    quarter_acceleration: float | None = None
    evidence_refs: tuple[EvidenceRef, ...] = ()

    def validate(self) -> None:
        if self.direction not in VALID_SURPRISE_DIRECTIONS:
            raise ValueError(f"invalid surprise direction: {self.direction}")
        for name in ("actual", "expected_center", "delta", "delta_pct", "quarter_acceleration"):
            _finite(getattr(self, name), f"surprise.{name}")
        for value, field_name in (
            (self.metric, "surprise.metric"),
            (self.calculation_method, "surprise.calculation_method"),
            (self.classification_contract_id, "surprise.classification_contract_id"),
        ):
            if value is not None:
                _require_text(value, field_name)
        for ref in self.evidence_refs:
            ref.validate()
        if self.verified:
            if self.direction == "UNRESOLVED":
                raise ValueError("verified surprise cannot be UNRESOLVED")
            if self.calculation_method is None:
                raise ValueError("verified surprise requires calculation_method")
            if not self.evidence_refs:
                raise ValueError("verified surprise requires evidence_refs")

    def to_dict(self) -> dict[str, Any]:
        self.validate()
        return {
            "direction": self.direction,
            "verified": self.verified,
            "metric": self.metric,
            "actual": self.actual,
            "expected_center": self.expected_center,
            "delta": self.delta,
            "delta_pct": self.delta_pct,
            "calculation_method": self.calculation_method,
            "classification_contract_id": self.classification_contract_id,
            "quarter_acceleration": self.quarter_acceleration,
            "evidence_refs": [ref.to_dict() for ref in self.evidence_refs],
        }


@dataclass(frozen=True)
class MaterialityEvidence:
    state: str = "UNRESOLVED"
    transmission_path: str | None = None
    assessment_contract_id: str | None = None
    impact_metrics: Mapping[str, float] | None = None
    evidence_refs: tuple[EvidenceRef, ...] = ()

    def validate(self) -> None:
        if self.state not in VALID_MATERIALITY_STATES:
            raise ValueError(f"invalid materiality state: {self.state}")
        if self.transmission_path is not None:
            _require_text(self.transmission_path, "materiality.transmission_path")
        if self.assessment_contract_id is not None:
            _require_text(self.assessment_contract_id, "materiality.assessment_contract_id")
        if self.impact_metrics is not None:
            for key, value in self.impact_metrics.items():
                _require_text(str(key), "materiality impact metric name")
                _finite(value, f"materiality.impact_metrics[{key}]", allow_none=False)
        for ref in self.evidence_refs:
            ref.validate()
        if self.state != "UNRESOLVED":
            if self.transmission_path is None:
                raise ValueError("resolved materiality requires transmission_path")
            if self.assessment_contract_id is None:
                raise ValueError("resolved materiality requires assessment_contract_id")
        if self.state == "MATERIAL" and not self.evidence_refs:
            raise ValueError("MATERIAL assessment requires evidence_refs")

    def to_dict(self) -> dict[str, Any]:
        self.validate()
        return {
            "state": self.state,
            "transmission_path": self.transmission_path,
            "assessment_contract_id": self.assessment_contract_id,
            "impact_metrics": None if self.impact_metrics is None else dict(self.impact_metrics),
            "evidence_refs": [ref.to_dict() for ref in self.evidence_refs],
        }


@dataclass(frozen=True)
class PrepricingEvidence:
    state: str = "UNRESOLVED"
    event_measurement_id: str | None = None
    classification_contract_id: str | None = None
    metrics: Mapping[str, float] | None = None

    def validate(self) -> None:
        if self.state not in VALID_PREPRICING_STATES:
            raise ValueError(f"invalid prepricing state: {self.state}")
        if self.event_measurement_id is not None:
            _require_text(self.event_measurement_id, "prepricing.event_measurement_id")
        if self.classification_contract_id is not None:
            _require_text(self.classification_contract_id, "prepricing.classification_contract_id")
        if self.metrics is not None:
            for key, value in self.metrics.items():
                _require_text(str(key), "prepricing metric name")
                _finite(value, f"prepricing.metrics[{key}]", allow_none=False)
        if self.state != "UNRESOLVED":
            if self.event_measurement_id is None:
                raise ValueError("resolved prepricing requires event_measurement_id")
            if self.classification_contract_id is None:
                raise ValueError("resolved prepricing requires classification_contract_id")

    def to_dict(self) -> dict[str, Any]:
        self.validate()
        return {
            "state": self.state,
            "event_measurement_id": self.event_measurement_id,
            "classification_contract_id": self.classification_contract_id,
            "metrics": None if self.metrics is None else dict(self.metrics),
        }


@dataclass(frozen=True)
class ReactionEvidence:
    state: str = "UNRESOLVED"
    event_measurement_id: str | None = None
    classification_contract_id: str | None = None
    primary_reaction_window_sessions: int | None = None
    benchmark_id: str | None = None
    benchmark_selection_contract_id: str | None = None
    metrics: Mapping[str, float] | None = None

    def validate(self) -> None:
        if self.state not in VALID_REACTION_STATES:
            raise ValueError(f"invalid reaction state: {self.state}")
        for value, field_name in (
            (self.event_measurement_id, "reaction.event_measurement_id"),
            (self.classification_contract_id, "reaction.classification_contract_id"),
            (self.benchmark_id, "reaction.benchmark_id"),
            (self.benchmark_selection_contract_id, "reaction.benchmark_selection_contract_id"),
        ):
            if value is not None:
                _require_text(value, field_name)
        if self.primary_reaction_window_sessions is not None:
            if (
                isinstance(self.primary_reaction_window_sessions, bool)
                or not isinstance(self.primary_reaction_window_sessions, int)
                or self.primary_reaction_window_sessions <= 0
            ):
                raise ValueError("primary_reaction_window_sessions must be a positive integer")
        if self.metrics is not None:
            for key, value in self.metrics.items():
                _require_text(str(key), "reaction metric name")
                _finite(value, f"reaction.metrics[{key}]", allow_none=False)
        if self.state != "UNRESOLVED":
            if self.event_measurement_id is None:
                raise ValueError("resolved reaction requires event_measurement_id")
            if self.classification_contract_id is None:
                raise ValueError("resolved reaction requires classification_contract_id")

    def to_dict(self) -> dict[str, Any]:
        self.validate()
        return {
            "state": self.state,
            "event_measurement_id": self.event_measurement_id,
            "classification_contract_id": self.classification_contract_id,
            "primary_reaction_window_sessions": self.primary_reaction_window_sessions,
            "benchmark_id": self.benchmark_id,
            "benchmark_selection_contract_id": self.benchmark_selection_contract_id,
            "metrics": None if self.metrics is None else dict(self.metrics),
        }


@dataclass(frozen=True)
class ERGEvidenceBundle:
    evidence_bundle_id: str
    schema_version: str
    strategy_id: str
    sleeve: str
    event_id: str
    event_family: str
    security_id: str
    as_of: str
    information_timestamp: str
    first_tradable_timestamp: str
    primary_source_tier: str
    eligibility: EligibilityEvidence
    expectation: ExpectationEvidence
    surprise: SurpriseEvidence
    materiality: MaterialityEvidence
    prepricing: PrepricingEvidence
    reaction: ReactionEvidence

    def identity_payload(self) -> dict[str, Any]:
        return {
            "schema_version": self.schema_version,
            "strategy_id": self.strategy_id,
            "sleeve": self.sleeve,
            "event_id": self.event_id,
            "event_family": self.event_family,
            "security_id": self.security_id,
            "as_of": self.as_of,
            "information_timestamp": self.information_timestamp,
            "first_tradable_timestamp": self.first_tradable_timestamp,
            "primary_source_tier": self.primary_source_tier,
            "eligibility": self.eligibility.to_dict(),
            "expectation": self.expectation.to_dict(),
            "surprise": self.surprise.to_dict(),
            "materiality": self.materiality.to_dict(),
            "prepricing": self.prepricing.to_dict(),
            "reaction": self.reaction.to_dict(),
        }

    def validate(self) -> None:
        if self.schema_version != ERG_EVIDENCE_SCHEMA_VERSION:
            raise ValueError("unsupported ERG evidence schema")
        require_strategy_context(
            strategy_id=self.strategy_id,
            sleeve=self.sleeve,
            expected_strategy_id=SHORT_MID_STRATEGY_ID,
            expected_sleeve=SHORT_MID_SLEEVE,
        )
        _require_text(self.event_id, "event_id")
        if self.event_family not in VALID_EVENT_FAMILIES:
            raise ValueError(f"invalid event_family: {self.event_family}")
        _require_text(self.security_id, "security_id")
        as_of = _parse_aware(self.as_of, "as_of")
        info = _parse_aware(self.information_timestamp, "information_timestamp")
        tradable = _parse_aware(self.first_tradable_timestamp, "first_tradable_timestamp")
        if tradable < info:
            raise ValueError("first_tradable_timestamp cannot precede information_timestamp")
        if as_of < info:
            raise ValueError("as_of cannot precede information_timestamp")
        if self.primary_source_tier not in VALID_SOURCE_TIERS:
            raise ValueError(f"invalid primary_source_tier: {self.primary_source_tier}")
        self.eligibility.validate()
        self.expectation.validate()
        self.surprise.validate()
        self.materiality.validate()
        self.prepricing.validate()
        self.reaction.validate()
        if self.surprise.verified and not self.expectation.eligible_for_verified_surprise():
            raise ValueError(
                "verified surprise requires a non-LOW, sufficiently covered expectation baseline"
            )
        pre_measurement = self.prepricing.event_measurement_id
        reaction_measurement = self.reaction.event_measurement_id
        if (
            pre_measurement is not None
            and reaction_measurement is not None
            and pre_measurement != reaction_measurement
        ):
            raise ValueError("prepricing and reaction must reference the same event measurement")
        if _sha256(self.identity_payload()) != self.evidence_bundle_id:
            raise ValueError("evidence_bundle_id does not match content")

    def to_dict(self) -> dict[str, Any]:
        return {**self.identity_payload(), "evidence_bundle_id": self.evidence_bundle_id}

    @classmethod
    def build(
        cls,
        *,
        event_id: str,
        event_family: str,
        security_id: str,
        as_of: str,
        information_timestamp: str,
        first_tradable_timestamp: str,
        primary_source_tier: str,
        eligibility: EligibilityEvidence,
        expectation: ExpectationEvidence,
        surprise: SurpriseEvidence,
        materiality: MaterialityEvidence,
        prepricing: PrepricingEvidence,
        reaction: ReactionEvidence,
        strategy_id: str = SHORT_MID_STRATEGY_ID,
        sleeve: str = SHORT_MID_SLEEVE,
    ) -> "ERGEvidenceBundle":
        provisional = cls(
            evidence_bundle_id="pending",
            schema_version=ERG_EVIDENCE_SCHEMA_VERSION,
            strategy_id=strategy_id,
            sleeve=sleeve,
            event_id=event_id,
            event_family=event_family,
            security_id=security_id,
            as_of=as_of,
            information_timestamp=information_timestamp,
            first_tradable_timestamp=first_tradable_timestamp,
            primary_source_tier=primary_source_tier,
            eligibility=eligibility,
            expectation=expectation,
            surprise=surprise,
            materiality=materiality,
            prepricing=prepricing,
            reaction=reaction,
        )
        identity = _sha256(provisional.identity_payload())
        result = cls(**{**provisional.__dict__, "evidence_bundle_id": identity})
        result.validate()
        return result

    @classmethod
    def from_dict(cls, payload: Mapping[str, Any]) -> "ERGEvidenceBundle":
        def refs(values: Iterable[Mapping[str, Any]]) -> tuple[EvidenceRef, ...]:
            return tuple(EvidenceRef(**dict(value)) for value in values)

        expectation_payload = dict(payload["expectation"])
        expectation_payload.pop("verified_surprise_eligible", None)
        expectation_payload["evidence_refs"] = refs(expectation_payload.get("evidence_refs", ()))

        surprise_payload = dict(payload["surprise"])
        surprise_payload["evidence_refs"] = refs(surprise_payload.get("evidence_refs", ()))

        materiality_payload = dict(payload["materiality"])
        materiality_payload["evidence_refs"] = refs(materiality_payload.get("evidence_refs", ()))

        return cls(
            evidence_bundle_id=str(payload["evidence_bundle_id"]),
            schema_version=str(payload["schema_version"]),
            strategy_id=str(payload["strategy_id"]),
            sleeve=str(payload["sleeve"]),
            event_id=str(payload["event_id"]),
            event_family=str(payload["event_family"]),
            security_id=str(payload["security_id"]),
            as_of=str(payload["as_of"]),
            information_timestamp=str(payload["information_timestamp"]),
            first_tradable_timestamp=str(payload["first_tradable_timestamp"]),
            primary_source_tier=str(payload["primary_source_tier"]),
            eligibility=EligibilityEvidence(
                status=str(payload["eligibility"]["status"]),
                reasons=tuple(payload["eligibility"].get("reasons", ())),
            ),
            expectation=ExpectationEvidence(**expectation_payload),
            surprise=SurpriseEvidence(**surprise_payload),
            materiality=MaterialityEvidence(**materiality_payload),
            prepricing=PrepricingEvidence(**dict(payload["prepricing"])),
            reaction=ReactionEvidence(**dict(payload["reaction"])),
        )


@dataclass(frozen=True)
class ERGShadowDecision:
    decision_id: str
    state_machine_version: str
    evidence_bundle_id: str
    strategy_id: str
    sleeve: str
    research_state: str
    reason_code: str
    reason: str
    confirmation_basis: str | None
    position_state: str = "FLAT"
    executable: bool = False

    def identity_payload(self) -> dict[str, Any]:
        return {
            "state_machine_version": self.state_machine_version,
            "evidence_bundle_id": self.evidence_bundle_id,
            "strategy_id": self.strategy_id,
            "sleeve": self.sleeve,
            "research_state": self.research_state,
            "reason_code": self.reason_code,
            "reason": self.reason,
            "confirmation_basis": self.confirmation_basis,
            "position_state": self.position_state,
            "executable": self.executable,
        }

    def validate(self) -> None:
        if self.state_machine_version != ERG_STATE_MACHINE_VERSION:
            raise ValueError("unsupported ERG state-machine version")
        require_strategy_context(
            strategy_id=self.strategy_id,
            sleeve=self.sleeve,
            expected_strategy_id=SHORT_MID_STRATEGY_ID,
            expected_sleeve=SHORT_MID_SLEEVE,
        )
        _require_text(self.evidence_bundle_id, "evidence_bundle_id")
        if self.research_state not in VALID_RESEARCH_STATES:
            raise ValueError(f"invalid research_state: {self.research_state}")
        _require_text(self.reason_code, "reason_code")
        _require_text(self.reason, "reason")
        if self.research_state == "CONFIRMED":
            if self.confirmation_basis != "EVENT_REACTION":
                raise ValueError("v0 ERG CONFIRMED requires EVENT_REACTION basis")
        elif self.confirmation_basis is not None:
            raise ValueError("non-CONFIRMED v0 ERG decision must not carry confirmation_basis")
        if self.position_state != "FLAT":
            raise ValueError("ERG shadow state machine cannot move position_state beyond FLAT")
        if self.executable:
            raise ValueError("ERG shadow state machine cannot authorize execution")
        if _sha256(self.identity_payload()) != self.decision_id:
            raise ValueError("decision_id does not match content")

    def to_dict(self) -> dict[str, Any]:
        return {**self.identity_payload(), "decision_id": self.decision_id}


class ERGShadowStateMachine:
    """Conservative v0 research-state resolver for event-driven ERG evidence.

    This state machine intentionally does not create price thresholds. Categorical
    Prepricing and Reaction states must already be supported by explicit frozen
    classification contracts before they can be treated as resolved evidence.

    It also never changes Position State or authorizes orders.
    """

    def evaluate(self, bundle: ERGEvidenceBundle) -> ERGShadowDecision:
        bundle.validate()

        if bundle.eligibility.status != "PASS":
            return self._decision(
                bundle,
                state="REJECT",
                reason_code="HARD_GATE_NOT_PASS",
                reason=(
                    "Eligibility / data / execution hard gate is not fully PASS: "
                    + "; ".join(bundle.eligibility.reasons)
                ),
            )

        if bundle.materiality.state == "LOW_MATERIALITY":
            return self._decision(
                bundle,
                state="WATCH",
                reason_code="LOW_MATERIALITY",
                reason="New information lacks a documented material earnings/cash-flow transmission path.",
            )

        if bundle.materiality.state == "UNRESOLVED":
            return self._decision(
                bundle,
                state="WATCH",
                reason_code="MATERIALITY_UNRESOLVED",
                reason="Economic materiality is unresolved; v0 does not promote the event to CANDIDATE.",
            )

        # From here materiality is MATERIAL.
        if not bundle.surprise.verified:
            return self._decision(
                bundle,
                state="CANDIDATE",
                reason_code="SURPRISE_NOT_VERIFIED",
                reason="Material event exists, but the expectation baseline does not support a verified beat/miss.",
            )

        if bundle.reaction.state == "UNRESOLVED":
            return self._decision(
                bundle,
                state="CANDIDATE",
                reason_code="REACTION_UNRESOLVED",
                reason="Material verified surprise exists, but post-event market reaction is unresolved.",
            )

        if bundle.prepricing.state == "UNRESOLVED":
            return self._decision(
                bundle,
                state="CANDIDATE",
                reason_code="PREPRICING_UNRESOLVED",
                reason="Material verified surprise and reaction evidence exist, but prepricing is unresolved.",
            )

        if (
            bundle.surprise.direction == "POSITIVE"
            and bundle.reaction.state == "POSITIVE_CONFIRMATION"
        ):
            return self._decision(
                bundle,
                state="CONFIRMED",
                reason_code="POSITIVE_SURPRISE_POSITIVE_REACTION",
                reason=(
                    "Verified positive surprise is economically material; prepricing is resolved and "
                    "the frozen event-reaction evidence positively confirms the thesis."
                ),
                confirmation_basis="EVENT_REACTION",
            )

        if (
            bundle.surprise.direction == "NEGATIVE"
            and bundle.reaction.state == "NEGATIVE_DISAGREEMENT"
        ):
            return self._decision(
                bundle,
                state="INVALIDATED",
                reason_code="NEGATIVE_SURPRISE_NEGATIVE_REACTION",
                reason="Verified negative surprise and negative market reaction materially contradict the active event thesis.",
            )

        if (
            bundle.surprise.direction == "POSITIVE"
            and bundle.reaction.state == "NEGATIVE_DISAGREEMENT"
        ):
            return self._decision(
                bundle,
                state="CANDIDATE",
                reason_code="POSITIVE_SURPRISE_NEGATIVE_REACTION",
                reason="Headline surprise is positive but the market disagrees or may have prepriced the event; re-underwrite rather than force confirmation.",
            )

        if (
            bundle.surprise.direction == "NEGATIVE"
            and bundle.reaction.state == "POSITIVE_CONFIRMATION"
        ):
            return self._decision(
                bundle,
                state="CANDIDATE",
                reason_code="NEGATIVE_SURPRISE_POSITIVE_REACTION",
                reason="Headline surprise is negative but market reaction is positive; expectations may have been worse and require re-underwriting.",
            )

        return self._decision(
            bundle,
            state="CANDIDATE",
            reason_code="MIXED_OR_NONCONFIRMING_EVIDENCE",
            reason="Material event evidence is resolved but does not satisfy the conservative v0 confirmation or invalidation matrix.",
        )

    @staticmethod
    def _decision(
        bundle: ERGEvidenceBundle,
        *,
        state: str,
        reason_code: str,
        reason: str,
        confirmation_basis: str | None = None,
    ) -> ERGShadowDecision:
        provisional = ERGShadowDecision(
            decision_id="pending",
            state_machine_version=ERG_STATE_MACHINE_VERSION,
            evidence_bundle_id=bundle.evidence_bundle_id,
            strategy_id=bundle.strategy_id,
            sleeve=bundle.sleeve,
            research_state=state,
            reason_code=reason_code,
            reason=reason,
            confirmation_basis=confirmation_basis,
            position_state="FLAT",
            executable=False,
        )
        result = ERGShadowDecision(
            decision_id=_sha256(provisional.identity_payload()),
            state_machine_version=provisional.state_machine_version,
            evidence_bundle_id=provisional.evidence_bundle_id,
            strategy_id=provisional.strategy_id,
            sleeve=provisional.sleeve,
            research_state=provisional.research_state,
            reason_code=provisional.reason_code,
            reason=provisional.reason,
            confirmation_basis=provisional.confirmation_basis,
            position_state=provisional.position_state,
            executable=provisional.executable,
        )
        result.validate()
        return result
