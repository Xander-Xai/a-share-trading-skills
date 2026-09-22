# Pre-Trade Order Authorization Contract v1.1

> Status: **ACTIVE HARD-VETO GOVERNANCE**.
>
> Scope: every **real-money** action that increases A-share risk (`ENTRY` / `ADD`) across all strategies.
>
> This contract is an **order-permission gate**. Research can still run when inputs are missing, but no module may emit an executable real-money buy quantity until this contract passes.
>
> **Paper mode is separate:** Paper research may reuse the same sizing geometry with `paper_capital_rmb`, paper positions and synthetic risk budgets, but it must not ask for or fabricate the user's personal emergency reserve / cash-need answers. Paper artifacts must be explicitly labeled `PAPER` and remain non-executable.

## 1. Why this contract exists

A repository can contain excellent selection, timing and exit rules while the human still buys arbitrary quantities or converts vague research language into orders.

This contract makes the sequence mandatory:

```text
personal cash safety
→ eligible idle capital
→ account / strategy risk budget
→ security setup
→ invalidation
→ position sizing
→ explicit ENTRY / ADD state
→ executable share quantity
```

The order must not be reversed.

## 2. Hard distinction: research vs executable advice

Allowed without personal capital inputs:

```text
RESEARCH
WATCH
READY
NO_TRADE
```

Not allowed without a complete pre-trade card:

```text
ENTRY with shares
ADD with shares
buy 100/200/300 shares
allocate RMB X now
```

If any mandatory field is missing:

```text
authorization_state = NEED_USER_INPUT
max_executable_shares = 0
```

The system must ask for the missing fields instead of guessing.

## 3. Mandatory questionnaire before ENTRY / ADD

### 3.1 Capital safety

The program must collect or refresh:

```yaml
available_idle_cash_rmb:
stock_account_equity_rmb:
capital_eligibility: PASS|FAIL|UNKNOWN
cash_need_gate: PASS|FAIL|UNKNOWN
emergency_reserve_gate: PASS|FAIL|UNKNOWN
debt_leverage_gate: PASS|FAIL|UNKNOWN
risk_capacity: LOW|MEDIUM|HIGH|UNKNOWN
risk_willingness: LOW|MEDIUM|HIGH|UNKNOWN
```

Definitions:

- `available_idle_cash_rmb`: cash already judged eligible for stock risk; it excludes living costs, emergency reserve, near-term liabilities and borrowed money.
- `stock_account_equity_rmb`: shared Level-1A denominator.
- `cash_need_gate`: checks whether this money may be forced out during the planned holding window.

Any of the following blocks risk increase:

```text
capital_eligibility != PASS
cash_need_gate != PASS
emergency_reserve_gate != PASS
debt_leverage_gate != PASS
available_idle_cash_rmb <= 0
```

### 3.2 Account and current exposure

For short/mid the program must collect or retrieve:

```yaml
strategy_nav_rmb:
current_account_symbol_exposure_rmb:
current_account_cluster_exposure_rmb:
current_total_short_exposure_rmb:
current_short_symbol_exposure_rmb:
current_short_cluster_exposure_rmb:
current_open_initial_risk_rmb:
current_factor_initial_risk_rmb:
current_trade_planned_risk_rmb:   # existing shares' risk to the CURRENT invalidation
final_short_cap_rmb:
```

Unknown required exposure/cap data blocks executable sizing.

### 3.3 Trade geometry

For short/mid:

```yaml
position_state: ENTRY|ADD
entry_price:
invalidation_price:
trigger_confirmed: true|false
positive_add_confirmation: true|false
user_max_loss_this_trade_rmb:
```

For long:

```yaml
position_state: ENTRY|ADD
entry_price:
long_target_total_position_rmb:
current_long_symbol_exposure_rmb:
planned_tranche_fraction:
valuation_gate: PASS|FAIL|UNKNOWN
portfolio_gate: PASS|FAIL|UNKNOWN
thesis_gate: PASS|FAIL|UNKNOWN
balance_gate: PASS|FAIL|UNKNOWN
```

No executable order may be generated before the relevant trigger/gates pass.

## 4. Sizing hierarchy — every cap applies, use the minimum

### 4.1 Short/mid allowed new loss

Normal production sizing uses the Operating Target, not the Hard Ceiling:

```text
per_trade_operating_risk = 0.5% × short_mid_strategy_nav

remaining_user_trade_risk
= max(0, user_max_loss_this_trade_rmb - current_trade_planned_risk)

remaining_trade_risk
= max(0, per_trade_operating_risk - current_trade_planned_risk)

remaining_portfolio_heat
= max(0, 2% × strategy_nav - current_open_initial_risk)

remaining_factor_heat
= max(0, 1% × strategy_nav - current_factor_initial_risk)

allowed_new_loss
= min(
    remaining_user_trade_risk,
    remaining_trade_risk,
    remaining_portfolio_heat,
    remaining_factor_heat
  )
```

`user_max_loss_this_trade_rmb` is the user's maximum planned loss for the **whole trade across all tranches**, not a fresh allowance for each ADD. The 1% per-trade / 3% aggregate Hard Ceiling is not a sizing target and cannot be used merely because the user wants a larger position.

### 4.2 Short/mid share caps

Compute each independently:

```text
shares_by_risk
shares_by_idle_cash
shares_by_short_symbol_cap
shares_by_short_cluster_cap
shares_by_account_symbol_cap
shares_by_account_cluster_cap
shares_by_final_short_cap
```

Then:

```text
max_total_new_shares
= valid_buy_quantity_floor(min(all share caps), security_quantity_rule)
```

Default first strategic tranche:

```text
ENTRY planned_shares
= valid_buy_quantity_floor(50% × max_total_new_shares, security_quantity_rule)
```

An ADD is allowed only after explicit positive confirmation. It may use remaining authorized capacity, but never exceed any current cap.

If rounding makes the result less than the security's minimum valid buy quantity:

```text
NO_TRADE_POSITION_TOO_SMALL_FOR_RISK_BUDGET
```

Do not widen the stop or increase risk to make the trade worth doing.

### 4.3 Long-term share caps

Long-term sizing does not invent a short-term stop. It requires an approved long-term target position from the long engine.

```text
new_order_value
<= min(
  available_idle_cash,
  remaining_long_target_position,
  remaining_account_symbol_cap,
  remaining_account_cluster_cap
)
```

Then apply the approved strategic tranche (`40/30/30`, approved exception, or more conservative plan) and the security-specific minimum/increment rule.

If no approved target position / valuation / thesis / balance / portfolio gates exist:

```text
READY / WATCH
max_executable_shares = 0
```

## 4.4 Security-specific buy quantity rules

Do not assume every A-share venue uses a universal 100-share board lot.

Current execution baseline (must be refreshed before Live if exchange rules change):

```text
SSE main board:  minimum 100, increment 100
SZSE main board / ChiNext: minimum 100, increment 100
SSE STAR Market: minimum 200, increment 1 above the minimum
BSE: minimum 100, increment 1 above the minimum
```

Runtime must store or derive:

```yaml
min_buy_shares:
buy_increment_shares:
security_board:
quantity_rule_as_of:
```

If the board / quantity rule is unknown:

```text
authorization_state = NEED_USER_INPUT
max_executable_shares = 0
```

Official rule baselines:

- SSE Trading Rules (2026 revision): https://www.sse.com.cn/lawandrules/sselawsrules2025/stocks/exchange/c/c_20260424_10816482.shtml
- SZSE Trading Rules (2026 revision): https://docs.static.szse.cn/www/lawrules/rule/trade/current/W020260424690713155663.pdf
- BSE Trading Rules (2026): https://www.bse.cn/jygl_list/200028217.html

## 5. Account-level concentration cap helper

Until Level 1A supplies a more specific cap, runtime may use the conservative end of current Level-1A reference ranges:

```text
Stock Account Equity <= 50k:
  account symbol cap 30%
  account cluster cap 40%

50k–300k:
  symbol 20%
  cluster 30%

300k–2m:
  symbol 15%
  cluster 25%

>=2m:
  symbol 10%
  cluster 20%
```

These are ceilings, not target allocations.

## 6. Required output before a manual order

Every real-money buy recommendation must print a pre-trade card:

```yaml
authorization_state:
position_state:
risk_warning: 股票可能盈利也可能亏损；本次股数是风险上限约束后的建议，不是收益保证
available_idle_cash_rmb:
stock_account_equity_rmb:
entry_price:
invalidation_price:
allowed_new_loss_rmb:
max_executable_shares:
planned_entry_shares:
planned_notional_rmb:
worst_case_planned_loss_rmb:
current_trade_planned_risk_rmb:
min_buy_shares:
buy_increment_shares:
binding_constraints:
cash_need_gate:
emergency_reserve_gate:
debt_leverage_gate:
account_symbol_cap_state:
account_cluster_cap_state:
final_short_cap_state:
time_stop:
decision_id:
```

The system must explain which constraint was binding.

## 7. Increase-risk overrides are forbidden

Human/manual override may make the system more conservative, for example buying fewer shares or skipping a trade.

It may not override a failed capital gate to buy more.

Forbidden:

```text
FAIL cash_need_gate -> manual buy anyway
FAIL emergency reserve -> manual buy anyway
borrowed money -> manual buy anyway
unknown Final Short Cap -> guess a size
risk budget gives 0 shares -> widen stop / raise risk until the venue minimum fits
ADD without positive confirmation
```

Risk-reducing actions (`TRIM` / `EXIT`) remain allowed when data are incomplete if needed to protect capital.

## 8. Manual order discipline

Before the user manually places an order:

1. freeze the pre-trade card and `decision_id`;
2. show the maximum executable shares and the planned tranche;
3. remind that buying fewer shares is allowed, buying more requires a fresh authorization;
4. after execution, record actual shares/price/fees;
5. no silent change of invalidation;
6. ADD requires a new authorization cycle.

The repository cannot physically stop a broker order placed outside the system, but any such increase-risk trade must be logged as:

```text
UNAUTHORIZED_MANUAL_RISK_INCREASE
rule_violation = true
```

and cannot be treated as strategy-compliant performance.

## 9. Re-entry

After EXIT:

```text
EXIT
→ COOLDOWN
→ fresh capital questionnaire if stale
→ fresh underwriting
→ READY
→ new ENTRY authorization
```

A prior loss, prior cost basis, or desire to earn the money back is not an input to new sizing.

## 10. Final rule

```text
No personal capital context
→ no executable buy size.

No invalidation / approved long target
→ no executable buy size.

No clear ENTRY / ADD trigger
→ no executable buy size.

All gates pass
→ size is calculated by the most restrictive constraint,
   rounded down, and presented as a maximum / planned tranche.
```
