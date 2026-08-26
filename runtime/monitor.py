from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Any, Dict, Optional


SENTIMENT_WEIGHTS = {
    "breadth_score": 25.0,
    "limit_balance_score": 20.0,
    "board_quality_score": 15.0,
    "tail_score": 15.0,
    "median_score": 10.0,
    "turnover_score": 15.0,
}


def clip(value: float, lower: float = 0.0, upper: float = 100.0) -> float:
    return max(lower, min(upper, value))


def regime_from_score(score: float) -> str:
    if score < 20:
        return "PANIC"
    if score < 40:
        return "RISK_OFF"
    if score < 60:
        return "NEUTRAL"
    if score < 80:
        return "RISK_ON"
    return "EUPHORIA"


def calculate_sentiment(metrics: Dict[str, Optional[float]]) -> Dict[str, Any]:
    """Calculate the repository's A-share Sentiment Regime Index.

    Missing components are reweighted only when at least 70% of the original
    component weight is available. Otherwise the result is fail-closed as
    DATA_INSUFFICIENT.
    """
    advance = metrics.get("advance_count")
    decline = metrics.get("decline_count")
    up = metrics.get("limit_up_count")
    down = metrics.get("limit_down_count")
    broken = metrics.get("broken_limit_count")
    strong = metrics.get("strong_count")
    weak = metrics.get("weak_count")
    median_return = metrics.get("median_return_pct")
    turnover = metrics.get("total_turnover")
    turnover_20d = metrics.get("turnover_20d_median")

    components: Dict[str, Optional[float]] = {
        "breadth_score": None,
        "limit_balance_score": None,
        "board_quality_score": None,
        "tail_score": None,
        "median_score": None,
        "turnover_score": None,
    }

    if advance is not None and decline is not None and (advance + decline) > 0:
        components["breadth_score"] = 100.0 * advance / (advance + decline)

    if up is not None and down is not None:
        components["limit_balance_score"] = clip(
            50.0 + 50.0 * (up - down) / (up + down + 10.0)
        )

    if up is not None and broken is not None:
        components["board_quality_score"] = clip(
            100.0 * (1.0 - broken / (up + broken + 1.0))
        )

    if strong is not None and weak is not None:
        components["tail_score"] = clip(
            50.0 + 50.0 * (strong - weak) / (strong + weak + 20.0)
        )

    if median_return is not None:
        components["median_score"] = clip(50.0 + 12.5 * median_return)

    if turnover is not None:
        if turnover_20d is None or turnover_20d <= 0:
            components["turnover_score"] = 50.0
        else:
            components["turnover_score"] = clip(
                50.0 + 25.0 * math.log(max(turnover, 1.0) / turnover_20d)
            )

    available_weight = sum(
        SENTIMENT_WEIGHTS[k]
        for k, value in components.items()
        if value is not None
    )

    if available_weight < 70.0:
        return {
            **components,
            "sentiment_score": None,
            "regime": "DATA_INSUFFICIENT",
            "crowding_flag": False,
            "available_weight": available_weight,
            "data_confidence": "LOW",
        }

    weighted = sum(
        float(value) * SENTIMENT_WEIGHTS[k]
        for k, value in components.items()
        if value is not None
    )
    score = weighted / available_weight
    regime = regime_from_score(score)

    broken_rate = None
    if up is not None and broken is not None and (up + broken) > 0:
        broken_rate = broken / (up + broken)

    crowding_flag = bool(
        score >= 80.0
        and (
            (broken_rate is not None and broken_rate >= 0.30)
            or (median_return is not None and median_return >= 2.5)
        )
    )

    confidence = "HIGH" if available_weight >= 100.0 else "MEDIUM"

    return {
        **components,
        "sentiment_score": round(score, 2),
        "regime": regime,
        "crowding_flag": crowding_flag,
        "available_weight": available_weight,
        "data_confidence": confidence,
    }


@dataclass
class DecisionInput:
    """Normalized inputs for a deterministic short/mid-term action state."""

    data_complete: bool = True
    hard_veto: bool = False
    has_position: bool = False
    market_regime: str = "NEUTRAL"
    crowding_flag: bool = False
    entry_gate_pass: bool = False
    score_gate_pass: bool = False
    reward_risk_pass: bool = False
    risk_budget_pass: bool = False
    thesis_invalidated: bool = False
    invalidation_hit: bool = False
    hard_risk_breach: bool = False
    cap_breach: bool = False
    thesis_weakening: bool = False
    time_review_failed: bool = False
    add_confirmation: bool = False
    add_gate_pass: bool = False


def decide_short_mid_action(s: DecisionInput) -> str:
    """Return a deterministic research/action state.

    This engine never bypasses broker or capital-policy gates. It is deliberately
    conservative: incomplete data always produces NO_ACTION.
    """
    if not s.data_complete:
        return "NO_ACTION"

    if s.hard_veto:
        return "REJECT" if not s.has_position else "EXIT_REVIEW"

    if not s.has_position:
        if s.market_regime in {"PANIC", "RISK_OFF", "DATA_INSUFFICIENT"}:
            return "WAIT"
        if s.market_regime == "EUPHORIA" and s.crowding_flag:
            return "WAIT_NO_CHASE"
        if not s.entry_gate_pass:
            return "WATCH"
        if s.score_gate_pass and s.reward_risk_pass and s.risk_budget_pass:
            return "READY"
        return "WATCH"

    if s.thesis_invalidated or s.invalidation_hit:
        return "EXIT"

    if s.hard_risk_breach:
        return "RISK_EXIT_REVIEW"

    if s.cap_breach or s.thesis_weakening or s.time_review_failed:
        return "TRIM_REVIEW"

    if s.add_confirmation and s.add_gate_pass and s.risk_budget_pass:
        return "ADD"

    return "HOLD"
