from __future__ import annotations

import json
import sys
import uuid
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.core.pretrade_risk_gate import (
    CapitalSafetyInput,
    LongPreTradeInput,
    ShortMidPreTradeInput,
    evaluate_long_pretrade,
    evaluate_short_mid_pretrade,
)


def ask_float(prompt: str):
    raw = input(prompt).strip()
    if raw == "":
        return None
    try:
        return float(raw)
    except ValueError:
        return None


def ask_yes_no(prompt: str):
    raw = input(prompt + " [y/n]: ").strip().lower()
    if raw in {"y", "yes", "是", "1"}:
        return True
    if raw in {"n", "no", "否", "0"}:
        return False
    return None


def gate_from_yes(value):
    if value is True:
        return "PASS"
    if value is False:
        return "FAIL"
    return "UNKNOWN"


def gate_from_no(value):
    if value is False:
        return "PASS"
    if value is True:
        return "FAIL"
    return "UNKNOWN"


def ask_risk_level(prompt: str):
    raw = input(prompt + " [LOW/MEDIUM/HIGH]: ").strip().upper()
    if raw in {"LOW", "MEDIUM", "HIGH"}:
        return raw
    return "UNKNOWN"


def collect_capital_safety():
    print("\n=== 资金资格：先判断这笔钱是否真的能承担股票风险 ===")
    idle_cash = ask_float("本次可用于股票、即使亏损也不影响生活的闲钱（元）：")
    equity = ask_float("当前 Stock Account Equity / 股票账户权益（元）：")
    emergency = ask_yes_no("应急金是否已与股票资金分开并足以避免突发支出时被迫卖股？")
    cash_need = ask_yes_no("计划持有期内，这笔钱是否可能因生活/医疗/住房/教育/债务/税费等被迫取出？")
    borrowed = ask_yes_no("本次资金是否包含借款、融资或抵押核心生活资产所得资金？")
    risk_capacity = ask_risk_level("客观财务风险承受能力")
    risk_willingness = ask_risk_level("主观风险意愿")

    emergency_gate = gate_from_yes(emergency)
    cash_need_gate = gate_from_no(cash_need)
    debt_gate = gate_from_no(borrowed)
    capital_gate = (
        "PASS"
        if emergency_gate == cash_need_gate == debt_gate == "PASS" and idle_cash is not None and idle_cash > 0
        else "FAIL" if "FAIL" in {emergency_gate, cash_need_gate, debt_gate} else "UNKNOWN"
    )

    return CapitalSafetyInput(
        available_idle_cash_rmb=idle_cash,
        stock_account_equity_rmb=equity,
        capital_eligibility=capital_gate,
        cash_need_gate=cash_need_gate,
        emergency_reserve_gate=emergency_gate,
        debt_leverage_gate=debt_gate,
        risk_capacity=risk_capacity,
        risk_willingness=risk_willingness,
    )


def run_short_mid(capital, action):
    print("\n=== 短中期：风险预算 + 结构失效点反推股数 ===")
    inp = ShortMidPreTradeInput(
        capital=capital,
        position_state=action,
        entry_price=ask_float("计划买入价/触发价（元）："),
        invalidation_price=ask_float("交易逻辑失效价（元）："),
        strategy_nav_rmb=ask_float("当前短中期策略 NAV（元）："),
        user_max_loss_this_trade_rmb=ask_float("你对本次交易最多可承受的计划亏损（元）："),
        trigger_confirmed=ask_yes_no("ENTRY/ADD 的预定义价格或结构触发是否已经确认？"),
        positive_add_confirmation=(
            ask_yes_no("本次 ADD 是否来自正向确认，而不是因为下跌/摊低成本？") if action == "ADD" else None
        ),
        current_account_symbol_exposure_rmb=ask_float("当前账户该股票总暴露（长期+短中期，元）："),
        current_account_cluster_exposure_rmb=ask_float("当前账户同风险簇总暴露（元）："),
        current_total_short_exposure_rmb=ask_float("当前短中期全部股票暴露（元）："),
        current_short_symbol_exposure_rmb=ask_float("当前短中期该股票暴露（元）："),
        current_short_cluster_exposure_rmb=ask_float("当前短中期同风险簇暴露（元）："),
        current_open_initial_risk_rmb=ask_float("当前短中期全部未平仓初始风险合计（元）："),
        current_factor_initial_risk_rmb=ask_float("当前同一行业/因子的未平仓初始风险合计（元）："),
        final_short_cap_rmb=ask_float("当前 Final Short Cap（元；不知道就留空，程序将拒绝给买入股数）："),
    )
    return evaluate_short_mid_pretrade(inp)


def run_long(capital, action):
    print("\n=== 长期：目标仓位 + 估值/组合 Gate 反推本批股数 ===")
    inp = LongPreTradeInput(
        capital=capital,
        position_state=action,
        entry_price=ask_float("计划买入价（元）："),
        long_target_total_position_rmb=ask_float("长期模型已批准的该股目标总仓位金额（元）："),
        current_account_symbol_exposure_rmb=ask_float("当前账户该股票总暴露（元）："),
        current_account_cluster_exposure_rmb=ask_float("当前账户同风险簇总暴露（元）："),
        valuation_gate=gate_from_yes(ask_yes_no("Valuation Gate 是否通过？")),
        portfolio_gate=gate_from_yes(ask_yes_no("Portfolio Gate 是否通过？")),
        thesis_gate=gate_from_yes(ask_yes_no("Thesis Gate 是否通过？")),
        balance_gate=gate_from_yes(ask_yes_no("Balance Gate 是否通过？")),
        planned_tranche_fraction=ask_float("本批占目标仓位比例（如40%输入0.40）："),
    )
    return evaluate_long_pretrade(inp)


def main():
    print("A-share Pre-Trade Authorization Gate")
    print("原则：股票可能盈利也可能亏损；先保护生活现金流，再决定能否承担风险。")
    sleeve = input("策略 [short_mid/long]: ").strip().lower()
    action = input("动作 [ENTRY/ADD]: ").strip().upper()
    capital = collect_capital_safety()

    if sleeve == "short_mid":
        decision = run_short_mid(capital, action)
    elif sleeve == "long":
        decision = run_long(capital, action)
    else:
        print(json.dumps({"authorization_state": "BLOCKED", "reason": "unknown strategy"}, ensure_ascii=False, indent=2))
        return 2

    out = dict(decision.__dict__)
    out["decision_id"] = str(uuid.uuid4())
    out["manual_order_rule"] = "可以买得更少；买得更多必须重新授权。任何未授权增仓都应记录为规则违规。"
    print("\n=== Pre-Trade Card ===")
    print(json.dumps(out, ensure_ascii=False, indent=2))
    return 0 if decision.authorization_state == "AUTHORIZED" else 1


if __name__ == "__main__":
    raise SystemExit(main())
