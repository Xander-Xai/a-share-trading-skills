from __future__ import annotations

from dataclasses import dataclass, field
from math import floor
from typing import Dict, List, Optional


PASS = "PASS"
UNKNOWN = "UNKNOWN"


@dataclass(frozen=True)
class CapitalSafetyInput:
    available_idle_cash_rmb: Optional[float]
    stock_account_equity_rmb: Optional[float]
    capital_eligibility: str = UNKNOWN
    cash_need_gate: str = UNKNOWN
    emergency_reserve_gate: str = UNKNOWN
    debt_leverage_gate: str = UNKNOWN
    risk_capacity: str = UNKNOWN
    risk_willingness: str = UNKNOWN


@dataclass(frozen=True)
class ShortMidPreTradeInput:
    capital: CapitalSafetyInput
    position_state: str
    entry_price: Optional[float]
    invalidation_price: Optional[float]
    strategy_nav_rmb: Optional[float]
    user_max_loss_this_trade_rmb: Optional[float]
    trigger_confirmed: Optional[bool]
    positive_add_confirmation: Optional[bool] = None
    current_account_symbol_exposure_rmb: Optional[float] = None
    current_account_cluster_exposure_rmb: Optional[float] = None
    current_total_short_exposure_rmb: Optional[float] = None
    current_short_symbol_exposure_rmb: Optional[float] = None
    current_short_cluster_exposure_rmb: Optional[float] = None
    current_open_initial_risk_rmb: Optional[float] = None
    current_factor_initial_risk_rmb: Optional[float] = None
    current_trade_planned_risk_rmb: Optional[float] = None
    final_short_cap_rmb: Optional[float] = None
    min_buy_shares: int = 100
    buy_increment_shares: int = 100
    entry_tranche_fraction: float = 0.50
    time_stop: str = "3-5 trading days if setup clearly fails; mandatory re-underwrite by 15 trading days"


@dataclass(frozen=True)
class LongPreTradeInput:
    capital: CapitalSafetyInput
    position_state: str
    entry_price: Optional[float]
    long_target_total_position_rmb: Optional[float]
    current_account_symbol_exposure_rmb: Optional[float]
    current_account_cluster_exposure_rmb: Optional[float]
    current_long_symbol_exposure_rmb: Optional[float]
    valuation_gate: str = UNKNOWN
    portfolio_gate: str = UNKNOWN
    thesis_gate: str = UNKNOWN
    balance_gate: str = UNKNOWN
    planned_tranche_fraction: Optional[float] = None
    min_buy_shares: int = 100
    buy_increment_shares: int = 100


@dataclass
class PreTradeDecision:
    authorization_state: str
    position_state: str
    max_executable_shares: int = 0
    planned_entry_shares: int = 0
    planned_notional_rmb: float = 0.0
    allowed_new_loss_rmb: Optional[float] = None
    worst_case_planned_loss_rmb: Optional[float] = None
    binding_constraints: List[str] = field(default_factory=list)
    missing_fields: List[str] = field(default_factory=list)
    blocking_reasons: List[str] = field(default_factory=list)
    cap_details: Dict[str, float] = field(default_factory=dict)
    min_buy_shares: int = 0
    buy_increment_shares: int = 0
    risk_warning: str = "股票可能盈利也可能亏损；本次股数是风险上限约束后的建议，不是收益保证。"


def _buy_quantity_floor(shares: float, min_buy_shares: int, buy_increment_shares: int) -> int:
    if min_buy_shares <= 0 or buy_increment_shares <= 0:
        raise ValueError("buy quantity rules must be positive")
    if shares < min_buy_shares:
        return 0
    return int(min_buy_shares + floor((shares - min_buy_shares) / buy_increment_shares) * buy_increment_shares)


def _is_valid_buy_quantity(quantity: int, min_buy_shares: int, buy_increment_shares: int) -> bool:
    if quantity == 0:
        return True
    if quantity < min_buy_shares:
        return False
    return (quantity - min_buy_shares) % buy_increment_shares == 0


def _positive_number(value: Optional[float]) -> bool:
    return value is not None and value > 0


def _nonnegative_number(value: Optional[float]) -> bool:
    return value is not None and value >= 0


def _account_cap_pcts(stock_account_equity_rmb: float) -> tuple[float, float]:
    if stock_account_equity_rmb <= 50_000:
        return 0.30, 0.40
    if stock_account_equity_rmb <= 300_000:
        return 0.20, 0.30
    if stock_account_equity_rmb < 2_000_000:
        return 0.15, 0.25
    return 0.10, 0.20


def _capital_gate_errors(capital: CapitalSafetyInput) -> tuple[List[str], List[str]]:
    missing: List[str] = []
    blocking: List[str] = []

    if not _positive_number(capital.available_idle_cash_rmb):
        missing.append("available_idle_cash_rmb")
    if not _positive_number(capital.stock_account_equity_rmb):
        missing.append("stock_account_equity_rmb")

    for name in (
        "capital_eligibility",
        "cash_need_gate",
        "emergency_reserve_gate",
        "debt_leverage_gate",
    ):
        value = getattr(capital, name)
        if value == UNKNOWN or not value:
            missing.append(name)
        elif value != PASS:
            blocking.append(f"{name}={value}")

    if capital.risk_capacity == UNKNOWN or not capital.risk_capacity:
        missing.append("risk_capacity")
    if capital.risk_willingness == UNKNOWN or not capital.risk_willingness:
        missing.append("risk_willingness")

    return missing, blocking


def evaluate_short_mid_pretrade(inp: ShortMidPreTradeInput) -> PreTradeDecision:
    state = (inp.position_state or "").upper()
    decision = PreTradeDecision(
        authorization_state="NEED_USER_INPUT",
        position_state=state or "UNKNOWN",
        min_buy_shares=inp.min_buy_shares,
        buy_increment_shares=inp.buy_increment_shares,
    )

    missing, blocking = _capital_gate_errors(inp.capital)

    required_nonnegative = {
        "current_account_symbol_exposure_rmb": inp.current_account_symbol_exposure_rmb,
        "current_account_cluster_exposure_rmb": inp.current_account_cluster_exposure_rmb,
        "current_total_short_exposure_rmb": inp.current_total_short_exposure_rmb,
        "current_short_symbol_exposure_rmb": inp.current_short_symbol_exposure_rmb,
        "current_short_cluster_exposure_rmb": inp.current_short_cluster_exposure_rmb,
        "current_open_initial_risk_rmb": inp.current_open_initial_risk_rmb,
        "current_factor_initial_risk_rmb": inp.current_factor_initial_risk_rmb,
        "current_trade_planned_risk_rmb": inp.current_trade_planned_risk_rmb,
    }
    for name, value in required_nonnegative.items():
        if not _nonnegative_number(value):
            missing.append(name)

    required_positive = {
        "entry_price": inp.entry_price,
        "invalidation_price": inp.invalidation_price,
        "strategy_nav_rmb": inp.strategy_nav_rmb,
        "user_max_loss_this_trade_rmb": inp.user_max_loss_this_trade_rmb,
        "final_short_cap_rmb": inp.final_short_cap_rmb,
    }
    for name, value in required_positive.items():
        if not _positive_number(value):
            missing.append(name)

    if inp.min_buy_shares <= 0 or inp.buy_increment_shares <= 0:
        missing.append("buy_quantity_rule")

    if not (0 < inp.entry_tranche_fraction <= 1):
        blocking.append("entry_tranche_fraction must be > 0 and <= 1")

    if state not in {"ENTRY", "ADD"}:
        blocking.append("position_state must be ENTRY or ADD")

    if inp.trigger_confirmed is None:
        missing.append("trigger_confirmed")
    elif not inp.trigger_confirmed:
        blocking.append("entry/add trigger not confirmed")

    if state == "ADD":
        if inp.positive_add_confirmation is None:
            missing.append("positive_add_confirmation")
        elif not inp.positive_add_confirmation:
            blocking.append("ADD requires positive confirmation")

    if _nonnegative_number(inp.current_short_symbol_exposure_rmb) and _nonnegative_number(inp.current_trade_planned_risk_rmb):
        if state == "ENTRY" and (
            float(inp.current_short_symbol_exposure_rmb) > 0
            or float(inp.current_trade_planned_risk_rmb) > 0
        ):
            blocking.append("ENTRY requires no existing short-mid position/risk in this symbol")
        if state == "ADD" and float(inp.current_short_symbol_exposure_rmb) <= 0:
            blocking.append("ADD requires an existing short-mid position")

    if missing:
        decision.missing_fields = sorted(set(missing))
        decision.blocking_reasons = blocking
        return decision

    if blocking:
        decision.authorization_state = "BLOCKED"
        decision.blocking_reasons = blocking
        return decision

    entry_price = float(inp.entry_price)
    invalidation_price = float(inp.invalidation_price)
    if invalidation_price >= entry_price:
        decision.authorization_state = "BLOCKED"
        decision.blocking_reasons = [
            "long-only short/mid ENTRY/ADD requires invalidation_price < entry_price"
        ]
        return decision
    stop_distance = entry_price - invalidation_price

    nav = float(inp.strategy_nav_rmb)
    per_trade_operating_risk = nav * 0.005
    current_trade_planned_risk = float(inp.current_trade_planned_risk_rmb)
    remaining_user_trade_risk = max(0.0, float(inp.user_max_loss_this_trade_rmb) - current_trade_planned_risk)
    remaining_trade_risk = max(0.0, per_trade_operating_risk - current_trade_planned_risk)
    remaining_portfolio_heat = max(0.0, nav * 0.02 - float(inp.current_open_initial_risk_rmb))
    remaining_factor_heat = max(0.0, nav * 0.01 - float(inp.current_factor_initial_risk_rmb))
    allowed_new_loss = min(
        remaining_user_trade_risk,
        remaining_trade_risk,
        remaining_portfolio_heat,
        remaining_factor_heat,
    )

    symbol_cap_pct, cluster_cap_pct = _account_cap_pcts(float(inp.capital.stock_account_equity_rmb))
    account_symbol_remaining = max(
        0.0,
        float(inp.capital.stock_account_equity_rmb) * symbol_cap_pct
        - float(inp.current_account_symbol_exposure_rmb),
    )
    account_cluster_remaining = max(
        0.0,
        float(inp.capital.stock_account_equity_rmb) * cluster_cap_pct
        - float(inp.current_account_cluster_exposure_rmb),
    )
    short_symbol_remaining = max(0.0, nav * 0.20 - float(inp.current_short_symbol_exposure_rmb))
    short_cluster_remaining = max(0.0, nav * 0.40 - float(inp.current_short_cluster_exposure_rmb))
    final_short_remaining = max(0.0, float(inp.final_short_cap_rmb) - float(inp.current_total_short_exposure_rmb))

    share_caps = {
        "risk_budget": allowed_new_loss / stop_distance,
        "idle_cash": float(inp.capital.available_idle_cash_rmb) / entry_price,
        "short_symbol_cap": short_symbol_remaining / entry_price,
        "short_cluster_cap": short_cluster_remaining / entry_price,
        "account_symbol_cap": account_symbol_remaining / entry_price,
        "account_cluster_cap": account_cluster_remaining / entry_price,
        "final_short_cap": final_short_remaining / entry_price,
    }

    floored_caps = {
        name: _buy_quantity_floor(value, inp.min_buy_shares, inp.buy_increment_shares)
        for name, value in share_caps.items()
    }
    max_shares = min(floored_caps.values()) if floored_caps else 0
    binding = sorted([name for name, value in floored_caps.items() if value == max_shares])

    if max_shares < inp.min_buy_shares:
        decision.authorization_state = "NO_TRADE_POSITION_TOO_SMALL_FOR_RISK_BUDGET"
        decision.allowed_new_loss_rmb = round(allowed_new_loss, 2)
        decision.binding_constraints = binding
        decision.cap_details = {k: float(v) for k, v in floored_caps.items()}
        return decision

    if state == "ENTRY":
        planned = _buy_quantity_floor(
            max_shares * inp.entry_tranche_fraction,
            inp.min_buy_shares,
            inp.buy_increment_shares,
        )
        if planned < inp.min_buy_shares:
            decision.authorization_state = "NO_TRADE_TRANCHE_ROUNDS_BELOW_MINIMUM"
            decision.allowed_new_loss_rmb = round(allowed_new_loss, 2)
            decision.binding_constraints = binding
            decision.cap_details = {k: float(v) for k, v in floored_caps.items()}
            return decision
    else:
        planned = max_shares

    decision.authorization_state = "AUTHORIZED"
    decision.max_executable_shares = int(max_shares)
    decision.planned_entry_shares = int(planned)
    decision.planned_notional_rmb = round(planned * entry_price, 2)
    decision.allowed_new_loss_rmb = round(allowed_new_loss, 2)
    decision.worst_case_planned_loss_rmb = round(planned * stop_distance, 2)
    decision.binding_constraints = binding
    decision.cap_details = {k: float(v) for k, v in floored_caps.items()}
    return decision


def evaluate_long_pretrade(inp: LongPreTradeInput) -> PreTradeDecision:
    state = (inp.position_state or "").upper()
    decision = PreTradeDecision(
        authorization_state="NEED_USER_INPUT",
        position_state=state or "UNKNOWN",
        min_buy_shares=inp.min_buy_shares,
        buy_increment_shares=inp.buy_increment_shares,
    )
    missing, blocking = _capital_gate_errors(inp.capital)

    required_positive = {
        "entry_price": inp.entry_price,
        "long_target_total_position_rmb": inp.long_target_total_position_rmb,
        "planned_tranche_fraction": inp.planned_tranche_fraction,
    }
    for name, value in required_positive.items():
        if not _positive_number(value):
            missing.append(name)

    if inp.min_buy_shares <= 0 or inp.buy_increment_shares <= 0:
        missing.append("buy_quantity_rule")

    if inp.planned_tranche_fraction is not None and not (0 < inp.planned_tranche_fraction <= 1):
        blocking.append("planned_tranche_fraction must be > 0 and <= 1")

    for name, value in {
        "current_account_symbol_exposure_rmb": inp.current_account_symbol_exposure_rmb,
        "current_account_cluster_exposure_rmb": inp.current_account_cluster_exposure_rmb,
        "current_long_symbol_exposure_rmb": inp.current_long_symbol_exposure_rmb,
    }.items():
        if not _nonnegative_number(value):
            missing.append(name)

    if state not in {"ENTRY", "ADD"}:
        blocking.append("position_state must be ENTRY or ADD")

    for name in ("valuation_gate", "portfolio_gate", "thesis_gate", "balance_gate"):
        value = getattr(inp, name)
        if value == UNKNOWN or not value:
            missing.append(name)
        elif value != PASS:
            blocking.append(f"{name}={value}")

    if _nonnegative_number(inp.current_long_symbol_exposure_rmb):
        if state == "ENTRY" and float(inp.current_long_symbol_exposure_rmb) > 0:
            blocking.append("ENTRY requires no existing long-sleeve position in this symbol")
        if state == "ADD" and float(inp.current_long_symbol_exposure_rmb) <= 0:
            blocking.append("ADD requires an existing long-sleeve position")

    if missing:
        decision.missing_fields = sorted(set(missing))
        decision.blocking_reasons = blocking
        return decision
    if blocking:
        decision.authorization_state = "BLOCKED"
        decision.blocking_reasons = blocking
        return decision

    entry_price = float(inp.entry_price)
    equity = float(inp.capital.stock_account_equity_rmb)
    symbol_cap_pct, cluster_cap_pct = _account_cap_pcts(equity)
    target_remaining = max(0.0, float(inp.long_target_total_position_rmb) - float(inp.current_long_symbol_exposure_rmb))
    account_symbol_remaining = max(0.0, equity * symbol_cap_pct - float(inp.current_account_symbol_exposure_rmb))
    account_cluster_remaining = max(0.0, equity * cluster_cap_pct - float(inp.current_account_cluster_exposure_rmb))
    tranche_value = float(inp.long_target_total_position_rmb) * float(inp.planned_tranche_fraction)

    value_caps = {
        "idle_cash": float(inp.capital.available_idle_cash_rmb),
        "target_position": target_remaining,
        "account_symbol_cap": account_symbol_remaining,
        "account_cluster_cap": account_cluster_remaining,
        "approved_tranche": tranche_value,
    }
    max_order_value = min(value_caps.values())
    planned = _buy_quantity_floor(max_order_value / entry_price, inp.min_buy_shares, inp.buy_increment_shares)
    binding = sorted([name for name, value in value_caps.items() if value == max_order_value])

    if planned < inp.min_buy_shares:
        decision.authorization_state = "NO_TRADE_POSITION_TOO_SMALL_FOR_CAPS"
        decision.binding_constraints = binding
        decision.cap_details = value_caps
        return decision

    decision.authorization_state = "AUTHORIZED"
    decision.max_executable_shares = planned
    decision.planned_entry_shares = planned
    decision.planned_notional_rmb = round(planned * entry_price, 2)
    decision.binding_constraints = binding
    decision.cap_details = value_caps
    return decision


def validate_manual_requested_shares(decision: PreTradeDecision, requested_shares: int) -> tuple[bool, str]:
    """Validate a user's manual buy quantity against the frozen authorization.

    Buying fewer shares is allowed. Buying more requires a fresh authorization.
    """
    if decision.authorization_state != "AUTHORIZED":
        return False, "UNAUTHORIZED_MANUAL_RISK_INCREASE"
    if requested_shares < 0:
        return False, "INVALID_SHARE_QUANTITY"
    if requested_shares == 0:
        return True, "SKIP_TRADE"
    if not _is_valid_buy_quantity(requested_shares, decision.min_buy_shares, decision.buy_increment_shares):
        return False, "INVALID_BUY_QUANTITY"
    if requested_shares > decision.max_executable_shares:
        return False, "UNAUTHORIZED_MANUAL_RISK_INCREASE"
    if requested_shares > decision.planned_entry_shares:
        return False, "REAUTHORIZATION_REQUIRED_ABOVE_PLANNED_TRANCHE"
    return True, "AUTHORIZED_MANUAL_QUANTITY"
