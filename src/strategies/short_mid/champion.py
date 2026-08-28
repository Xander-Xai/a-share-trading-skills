from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Mapping

from src.core.strategy_boundary import (
    SHORT_MID_SLEEVE,
    SHORT_MID_STRATEGY_ID,
    require_strategy_context,
)
from src.features.snapshot import FeatureSnapshot, FeatureValue


VALID_DATA_CONFIDENCE = {"HIGH", "MEDIUM", "LOW"}


class ChampionInputError(ValueError):
    """Raised when Champion inputs are incomplete or violate the frozen contract."""


@dataclass(frozen=True)
class ChampionConfig:
    config_version: str
    strategy_id: str
    sleeve: str
    section_caps: dict[str, float]
    base_sections: dict[str, dict[str, float]]
    hard_veto_flags: tuple[str, ...]
    penalty_caps: dict[str, float]
    thresholds: dict[str, float]
    risk_off_regimes: tuple[str, ...]
    score_floor: float
    score_ceiling: float

    def validate(self) -> None:
        require_strategy_context(
            strategy_id=self.strategy_id,
            sleeve=self.sleeve,
            expected_strategy_id=SHORT_MID_STRATEGY_ID,
            expected_sleeve=SHORT_MID_SLEEVE,
        )
        if not self.config_version.strip():
            raise ValueError("config_version is required")
        if not self.base_sections or not self.section_caps:
            raise ValueError("section_caps and base_sections cannot be empty")
        if set(self.section_caps) != set(self.base_sections):
            raise ValueError("section_caps must exactly match base_sections")

        section_cap_total = 0.0
        for section, section_cap in self.section_caps.items():
            if not isinstance(section_cap, (int, float)) or section_cap <= 0:
                raise ValueError(f"invalid section cap: {section}={section_cap!r}")
            criteria = self.base_sections[section]
            if not section or not criteria:
                raise ValueError("section names and criteria are required")
            criterion_total = 0.0
            for criterion, cap in criteria.items():
                if not criterion or not isinstance(cap, (int, float)) or cap <= 0:
                    raise ValueError(f"invalid score cap: {section}.{criterion}={cap!r}")
                criterion_total += float(cap)
            if abs(criterion_total - float(section_cap)) > 1e-9:
                raise ValueError(
                    f"section cap mismatch for {section}: criteria={criterion_total}, section_cap={section_cap}"
                )
            section_cap_total += float(section_cap)
        if abs(section_cap_total - 100.0) > 1e-9:
            raise ValueError(
                f"Champion section caps must sum to 100, got {section_cap_total}"
            )

        if not self.hard_veto_flags:
            raise ValueError("hard_veto_flags cannot be empty")
        if len(set(self.hard_veto_flags)) != len(self.hard_veto_flags):
            raise ValueError("hard_veto_flags must be unique")
        for flag in self.hard_veto_flags:
            if not isinstance(flag, str) or not flag.strip():
                raise ValueError("hard_veto_flags must contain non-empty strings")

        for name, cap in self.penalty_caps.items():
            if not name or not isinstance(cap, (int, float)) or cap < 0:
                raise ValueError(f"invalid penalty cap: {name}={cap!r}")

        required_thresholds = {
            "high_priority",
            "trigger_candidate",
            "watch",
            "practical_entry_base",
            "risk_off_entry_buffer",
        }
        if set(self.thresholds) != required_thresholds:
            raise ValueError(
                f"threshold keys must be exactly {sorted(required_thresholds)}"
            )
        high = float(self.thresholds["high_priority"])
        trigger = float(self.thresholds["trigger_candidate"])
        watch = float(self.thresholds["watch"])
        if not (self.score_floor <= watch <= trigger <= high <= self.score_ceiling):
            raise ValueError("Champion thresholds must be monotonic within score bounds")
        if self.thresholds["risk_off_entry_buffer"] < 0:
            raise ValueError("risk_off_entry_buffer cannot be negative")
        if self.score_floor > self.score_ceiling:
            raise ValueError("score_floor cannot exceed score_ceiling")

    @classmethod
    def from_mapping(cls, row: Mapping[str, Any]) -> "ChampionConfig":
        config = cls(
            config_version=str(row["config_version"]),
            strategy_id=str(row["strategy_id"]),
            sleeve=str(row["sleeve"]),
            section_caps={
                str(section): float(cap)
                for section, cap in row["section_caps"].items()
            },
            base_sections={
                str(section): {
                    str(name): float(cap) for name, cap in criteria.items()
                }
                for section, criteria in row["base_sections"].items()
            },
            hard_veto_flags=tuple(str(v) for v in row["hard_veto_flags"]),
            penalty_caps={
                str(name): float(cap) for name, cap in row["penalty_caps"].items()
            },
            thresholds={
                str(name): float(value) for name, value in row["thresholds"].items()
            },
            risk_off_regimes=tuple(str(v).upper() for v in row["risk_off_regimes"]),
            score_floor=float(row["score_floor"]),
            score_ceiling=float(row["score_ceiling"]),
        )
        config.validate()
        return config


def load_champion_config(path: str | Path) -> ChampionConfig:
    row = json.loads(Path(path).read_text(encoding="utf-8"))
    return ChampionConfig.from_mapping(row)


@dataclass(frozen=True)
class ChampionScoreInput:
    strategy_id: str
    sleeve: str
    feature_snapshot_id: str
    section_scores: dict[str, dict[str, float]]
    penalties: dict[str, float]
    hard_veto_checked: bool
    hard_veto_flags: dict[str, bool]
    data_confidence: str
    market_regime: str

    def validate(self, config: ChampionConfig) -> None:
        require_strategy_context(
            strategy_id=self.strategy_id,
            sleeve=self.sleeve,
            expected_strategy_id=SHORT_MID_STRATEGY_ID,
            expected_sleeve=SHORT_MID_SLEEVE,
        )
        if not self.feature_snapshot_id.strip():
            raise ChampionInputError("feature_snapshot_id is required")
        if not self.hard_veto_checked:
            raise ChampionInputError("hard-veto checks must be completed before scoring")
        if set(self.hard_veto_flags) != set(config.hard_veto_flags):
            raise ChampionInputError(
                "all frozen hard-veto flags must be explicitly evaluated"
            )
        if any(type(value) is not bool for value in self.hard_veto_flags.values()):
            raise ChampionInputError("hard-veto flag values must be booleans")
        if self.data_confidence not in VALID_DATA_CONFIDENCE:
            raise ChampionInputError(
                f"invalid data_confidence: {self.data_confidence!r}"
            )
        if not self.market_regime.strip():
            raise ChampionInputError("market_regime is required")

        if set(self.section_scores) != set(config.base_sections):
            raise ChampionInputError("Champion section set does not match frozen config")
        for section, criteria in config.base_sections.items():
            actual = self.section_scores[section]
            if set(actual) != set(criteria):
                raise ChampionInputError(
                    f"Champion criteria mismatch for section {section!r}"
                )
            for name, cap in criteria.items():
                value = actual[name]
                if isinstance(value, bool) or not isinstance(value, (int, float)):
                    raise ChampionInputError(
                        f"score must be numeric: {section}.{name}"
                    )
                if value < 0 or value > cap:
                    raise ChampionInputError(
                        f"score outside cap: {section}.{name}={value}, cap={cap}"
                    )

        if set(self.penalties) != set(config.penalty_caps):
            raise ChampionInputError("Champion penalty set does not match frozen config")
        for name, cap in config.penalty_caps.items():
            value = self.penalties[name]
            if isinstance(value, bool) or not isinstance(value, (int, float)):
                raise ChampionInputError(f"penalty must be numeric: {name}")
            if value < 0 or value > cap:
                raise ChampionInputError(
                    f"penalty outside cap: {name}={value}, cap={cap}"
                )


@dataclass(frozen=True)
class ChampionScoreResult:
    config_version: str
    feature_snapshot_id: str
    section_totals: dict[str, float]
    base_score: float
    total_penalty: float
    final_score: float
    ranking_status: str
    hard_veto: bool
    hard_veto_reasons: tuple[str, ...]
    market_regime: str
    practical_entry_threshold: float
    score_threshold_passed: bool
    research_eligible: bool
    data_confidence: str
    execution_authorized: bool = False

    def to_dict(self) -> dict[str, Any]:
        return {
            "config_version": self.config_version,
            "feature_snapshot_id": self.feature_snapshot_id,
            "section_totals": dict(self.section_totals),
            "base_score": self.base_score,
            "total_penalty": self.total_penalty,
            "final_score": self.final_score,
            "ranking_status": self.ranking_status,
            "hard_veto": self.hard_veto,
            "hard_veto_reasons": list(self.hard_veto_reasons),
            "market_regime": self.market_regime,
            "practical_entry_threshold": self.practical_entry_threshold,
            "score_threshold_passed": self.score_threshold_passed,
            "research_eligible": self.research_eligible,
            "data_confidence": self.data_confidence,
            "execution_authorized": self.execution_authorized,
        }


class ChampionScorer:
    """Deterministic aggregator for the frozen Short/Mid Champion.

    This v0 scorer does **not** infer qualitative sub-scores from market or filing
    data. It consumes an explicit, versioned feature snapshot and applies frozen
    score, penalty, confidence and veto mechanics. It never authorizes broker
    execution.
    """

    def __init__(self, config: ChampionConfig):
        config.validate()
        self.config = config

    def score(self, inputs: ChampionScoreInput) -> ChampionScoreResult:
        inputs.validate(self.config)

        section_totals = {
            section: float(sum(criteria.values()))
            for section, criteria in inputs.section_scores.items()
        }
        base_score = float(sum(section_totals.values()))
        total_penalty = float(sum(inputs.penalties.values()))
        raw_score = base_score - total_penalty
        final_score = min(
            self.config.score_ceiling,
            max(self.config.score_floor, raw_score),
        )

        hard_veto_reasons = tuple(
            flag for flag in self.config.hard_veto_flags if inputs.hard_veto_flags[flag]
        )
        hard_veto = bool(hard_veto_reasons)
        if hard_veto:
            ranking_status = "REJECT_HARD_VETO"
        elif final_score >= self.config.thresholds["high_priority"]:
            ranking_status = "HIGH_PRIORITY"
        elif final_score >= self.config.thresholds["trigger_candidate"]:
            ranking_status = "TRIGGER_CANDIDATE"
        elif final_score >= self.config.thresholds["watch"]:
            ranking_status = "WATCH"
        else:
            ranking_status = "NO_NEW_POSITION"

        regime = inputs.market_regime.upper()
        entry_threshold = self.config.thresholds["practical_entry_base"]
        if regime in self.config.risk_off_regimes:
            entry_threshold += self.config.thresholds["risk_off_entry_buffer"]

        score_threshold_passed = final_score >= entry_threshold
        research_eligible = (
            (not hard_veto)
            and inputs.data_confidence != "LOW"
            and score_threshold_passed
        )

        return ChampionScoreResult(
            config_version=self.config.config_version,
            feature_snapshot_id=inputs.feature_snapshot_id,
            section_totals=section_totals,
            base_score=base_score,
            total_penalty=total_penalty,
            final_score=final_score,
            ranking_status=ranking_status,
            hard_veto=hard_veto,
            hard_veto_reasons=hard_veto_reasons,
            market_regime=regime,
            practical_entry_threshold=float(entry_threshold),
            score_threshold_passed=score_threshold_passed,
            research_eligible=research_eligible,
            data_confidence=inputs.data_confidence,
            execution_authorized=False,
        )

    def from_feature_snapshot(self, snapshot: FeatureSnapshot) -> ChampionScoreInput:
        require_strategy_context(
            strategy_id=snapshot.strategy_id,
            sleeve=snapshot.sleeve,
            expected_strategy_id=SHORT_MID_STRATEGY_ID,
            expected_sleeve=SHORT_MID_SLEEVE,
        )
        snapshot.validate()
        if snapshot.config_version != self.config.config_version:
            raise ChampionInputError(
                "feature snapshot config_version does not match Champion config"
            )

        feature_map = snapshot.feature_map()

        def required(name: str) -> FeatureValue:
            feature = feature_map.get(name)
            if feature is None:
                raise ChampionInputError(f"missing required Champion feature: {name}")
            if feature.status != "AVAILABLE":
                raise ChampionInputError(
                    f"Champion feature is not AVAILABLE: {name}={feature.status}"
                )
            return feature

        def numeric(name: str) -> float:
            feature = required(name)
            value = feature.value
            if isinstance(value, bool) or not isinstance(value, (int, float)):
                raise ChampionInputError(f"Champion feature must be numeric: {name}")
            return float(value)

        section_scores: dict[str, dict[str, float]] = {}
        for section, criteria in self.config.base_sections.items():
            section_scores[section] = {
                criterion: numeric(f"champion.{section}.{criterion}")
                for criterion in criteria
            }

        penalties = {
            name: numeric(f"champion.penalty.{name}")
            for name in self.config.penalty_caps
        }

        checked = required("champion.hard_veto_checked").value
        if checked is not True:
            raise ChampionInputError("champion.hard_veto_checked must be true")

        hard_veto_flags: dict[str, bool] = {}
        for flag in self.config.hard_veto_flags:
            value = required(f"champion.hard_veto.{flag}").value
            if type(value) is not bool:
                raise ChampionInputError(
                    f"champion.hard_veto.{flag} must be a boolean"
                )
            hard_veto_flags[flag] = value

        data_confidence_value = required("champion.data_confidence").value
        if not isinstance(data_confidence_value, str):
            raise ChampionInputError("champion.data_confidence must be a string")
        data_confidence = data_confidence_value.upper()

        regime_value = required("market.regime").value
        if not isinstance(regime_value, str):
            raise ChampionInputError("market.regime must be a string")

        inputs = ChampionScoreInput(
            strategy_id=snapshot.strategy_id,
            sleeve=snapshot.sleeve,
            feature_snapshot_id=snapshot.feature_snapshot_id,
            section_scores=section_scores,
            penalties=penalties,
            hard_veto_checked=True,
            hard_veto_flags=hard_veto_flags,
            data_confidence=data_confidence,
            market_regime=regime_value,
        )
        inputs.validate(self.config)
        return inputs

    def score_feature_snapshot(self, snapshot: FeatureSnapshot) -> ChampionScoreResult:
        return self.score(self.from_feature_snapshot(snapshot))
