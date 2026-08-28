from __future__ import annotations

from dataclasses import dataclass
from datetime import date

from src.data.entities import EntityMixin


@dataclass(frozen=True)
class TradingSession(EntityMixin):
    """Canonical exchange trading-calendar fact.

    This is shared market infrastructure. It contains no Long/Short-Mid signal
    semantics and no broker execution authorization.
    """

    entity_type = "TRADING_SESSION"

    exchange: str
    trade_date: str
    is_open: bool
    session_rule_version: str

    def validate(self) -> None:
        if not isinstance(self.exchange, str) or not self.exchange.strip():
            raise ValueError("exchange is required")
        try:
            date.fromisoformat(self.trade_date)
        except Exception as exc:
            raise ValueError("trade_date must be YYYY-MM-DD") from exc
        if type(self.is_open) is not bool:
            raise ValueError("is_open must be boolean")
        if not isinstance(self.session_rule_version, str) or not self.session_rule_version.strip():
            raise ValueError("session_rule_version is required")

    def record_id(self) -> str:
        self.validate()
        return f"TRADING_SESSION:{self.exchange}:{self.trade_date}"
