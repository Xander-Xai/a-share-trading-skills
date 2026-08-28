from __future__ import annotations

from dataclasses import dataclass


LONG_STRATEGY_ID = "a_share_long_retirement"
LONG_SLEEVE = "long"
SHORT_MID_STRATEGY_ID = "a_share_short_mid"
SHORT_MID_SLEEVE = "short_mid"

VALID_CONTEXTS = {
    (LONG_STRATEGY_ID, LONG_SLEEVE),
    (SHORT_MID_STRATEGY_ID, SHORT_MID_SLEEVE),
}


@dataclass(frozen=True)
class StrategyContext:
    strategy_id: str
    sleeve: str

    def validate(self) -> None:
        if (self.strategy_id, self.sleeve) not in VALID_CONTEXTS:
            raise ValueError(
                f"invalid strategy context: strategy_id={self.strategy_id!r}, sleeve={self.sleeve!r}"
            )


def require_strategy_context(
    *,
    strategy_id: str,
    sleeve: str,
    expected_strategy_id: str,
    expected_sleeve: str,
) -> None:
    """Fail closed when a strategy engine is invoked with the wrong sleeve.

    This is an implementation guard. It does not make a market decision and
    must never be interpreted as a strategy signal.
    """
    context = StrategyContext(strategy_id=strategy_id, sleeve=sleeve)
    context.validate()

    if strategy_id != expected_strategy_id or sleeve != expected_sleeve:
        raise ValueError(
            "strategy context mismatch: "
            f"expected=({expected_strategy_id},{expected_sleeve}) "
            f"actual=({strategy_id},{sleeve})"
        )
