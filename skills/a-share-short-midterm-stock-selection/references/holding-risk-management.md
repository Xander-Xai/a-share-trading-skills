# Holding and Risk Management v2

## 0. Governing policy

This reference is subordinate to:

```text
../../../shared/policy-precedence.md
../../../shared/capital-allocation-and-entry-policy.md
../SKILL.md
```

If any number here conflicts with shared policy, shared policy wins.

## 1. Goal

Convert a stock-selection result into a repeatable short/mid-term execution plan.

Default mode is 5–15 trading days. A position may extend to roughly 15–60 trading days only after explicit re-underwriting; it must never drift longer simply because the trader refuses to realize a loss.

Priority:

1. survive,
2. preserve optionality,
3. exploit asymmetric setups,
4. add only when thesis is working,
5. learn from process quality.

## 2. Define the trade before entry

Every trade must specify:

- thesis,
- setup type,
- entry trigger,
- invalidation condition,
- stop/invalidation price,
- realistic gap-risk scenario,
- expected first target/management zone,
- maximum account loss,
- strategy tranche structure,
- event dates,
- sector/factor exposure.

Do not enter first and invent the plan later.

## 3. Risk-based sizing

Let:

```text
E = planned entry
S = invalidation / stop
R_account = allowed currency loss
```

Then:

```text
shares ≈ R_account / abs(E - S)
```

Round down to an executable board lot and apply capital-concentration limits.

### Operating Target

```text
per trade planned risk: 0.5% of strategy NAV
aggregate open initial risk: <= 2%
aggregate initial risk per industry/factor cluster: <= 1%
```

### Hard Ceiling

```text
per trade planned risk: <= 1%
aggregate open initial risk: <= 3%
```

A wider stop requires a smaller position. Never widen the stop just to keep a preferred position size.

Moving above the 0.5% operating target requires validated Edge, favorable regime and a high-quality setup. The 1%/3% hard ceilings are never exceeded.

## 4. Gap-adjusted risk

For event-sensitive or high-volatility names, estimate plausible loss if price gaps through the planned stop.

If realistic execution loss would materially exceed the allowed risk budget:

- reduce size,
- avoid holding through the event,
- or skip the trade.

A stop price is an invalidation level, not a guaranteed fill price.

## 5. A-share execution constraints

### Entry-day reversibility

Ordinary newly bought A-shares generally cannot be freely reversed intraday. Therefore the first tranche must be survivable if the market moves against the position the same day.

### Price-limit and gap risk

If price gaps beyond invalidation or becomes non-executable:

- do not pretend the stop filled at the modeled price;
- mark `stop breached / awaiting executable exit`;
- exit at the first executable opportunity unless a fresh independent thesis justifies otherwise;
- record realized slippage.

### Corporate actions

Before interpreting moving averages/support, check ex-rights/ex-dividend adjustments, suspension/resumption, bonus issues, restructurings and abnormal-volatility measures.

## 6. Strategy tranches — old 3/4/4 rule retired

The historical rule that tranche count should rise mechanically with account size is retired.

### Default

```text
Tranche 1: 50% Setup Entry
Tranche 2: 50% Confirmation Entry
```

### Three-stage exception

```text
50% / 30% / 20%
```

only when the strategy has three distinct confirmation levels.

### Positive-confirmation rule

Later tranches require evidence such as:

- breakout holds,
- retest succeeds,
- relative strength improves,
- sector participation remains healthy,
- volume-price behavior improves,
- new catalyst/fundamental information strengthens the thesis.

### Prohibition

Price decline by itself is never an add signal. Do not add merely to lower cost.

### Strategy tranche vs execution split

A large strategy tranche may be split into several child orders for liquidity and slippage control. That does not create additional strategy tranches.

## 7. No mechanical averaging down

Historical `-5% traditional / -10% technology` levels are reassessment zones only, not automatic add levels.

An add after drawdown requires:

- original thesis intact,
- no adverse official disclosure,
- price structure stabilizing/reclaiming,
- improving volume-price behavior,
- intact/improving sector relative strength,
- score still at trade-candidate level,
- Reward/Risk still acceptable,
- portfolio risk still within limits.

If these conditions are absent, do not add.

## 8. Profit-management hierarchy

Primary rule:

```text
R multiple
+ technical structure
+ original setup target
```

Prefer realistic Reward/Risk >= 2 when possible.

Around +1.5R to +2R:

- consider realizing roughly 1/3 to 1/2;
- manage remaining size with trend structure or a trailing method.

### Secondary percentage observation zones

These are not hard ceilings:

- traditional/cyclical/lower-beta: roughly +3% to +5% when momentum stalls;
- growth/technology/higher-beta: roughly +6% to +10% when momentum stalls.

If percentage zones conflict with R-based or structural logic, **R/structure takes priority**.

## 9. Trailing management

Possible methods:

- close below MA5 after an extended move,
- close below MA10 for a slower trend,
- break of prior 2–3 day swing low,
- failure of breakout level,
- relative-strength breakdown vs sector.

Choose a method that matches volatility. Never loosen a stop merely to avoid realizing a loss.

## 10. Time stop

If after roughly 3–5 trading days:

- price has not progressed,
- relative strength deteriorates,
- volume participation fades,
- catalyst timing slips,
- or opportunity cost rises materially,

consider reducing or closing even if the hard stop has not triggered.

## 11. Thesis states

### Strengthening

Hold; consider adding only if risk budget permits and positive confirmation exists.

### Intact

Hold planned size; avoid unnecessary trading.

### Weakening

Reduce/tighten; do not add.

### Invalidated

Exit according to execution constraints; do not wait for breakeven.

## 12. Event isolation

Potential binary events include:

- earnings/interim report,
- performance forecast,
- major contract,
- shareholder reduction/lock-up expiry,
- restructuring,
- litigation/regulatory decision,
- suspension/resumption,
- material commodity/policy decision.

Before holding through one, explicitly evaluate upside, downside, gap risk and whether the position can absorb a non-executable stop.

## 13. Short-to-medium transition

Beyond 15 trading days requires fresh:

- thesis,
- official event/fundamental check,
- 100-point score,
- market/sector regime,
- invalidation,
- position-risk calculation.

If re-underwriting fails, reduce or exit.

## 14. Portfolio construction

Default operational caps unless shared policy is stricter:

- max simultaneous holdings: 5;
- max 2 same industry;
- max 2 same dominant economic factor.

Track portfolio heat as the sum of planned loss at invalidation.

```text
Operating Target heat: <= 2%
Hard Ceiling heat: <= 3%
```

## 15. Circuit breakers

Measured from strategy-equity high-water mark:

```text
-4%: reduce exposure and use lower-end risk sizing
-6%: no new positions; review regime/process
-8%: pause strategy; formal review before resuming
```

Do not reset the high-water mark to hide drawdown.

## 16. Post-trade review

Record:

- stock / setup,
- entry reason and score,
- market/sector regime,
- planned and actual fills,
- exit reason,
- MFE / MAE,
- realized R,
- fees/slippage,
- stop compliance,
- rule violations,
- thesis correctness vs execution quality.

Classify outcomes:

- good process / good result,
- good process / bad result,
- bad process / good result,
- bad process / bad result.

Track win rate, average winner/loser, expectancy in R, maximum drawdown, time-to-work and rule-violation rate by setup and regime.
