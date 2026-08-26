# Holding and Risk Management

## Goal

Convert a stock-selection result into a repeatable execution plan.

Default mode is short-term A-share holding, normally 5–15 trading days. A position may become medium-term only after an explicit re-underwriting decision; it must never drift from “short-term trade” into “longer hold” merely because the trader does not want to realize a loss.

Priority order:

1. survive
2. preserve optionality
3. exploit asymmetric setups
4. compound only when the thesis is working
5. learn from process quality, not lucky outcomes

## 1. Define the trade before entry

Every planned trade must specify:

- thesis
- setup type
- entry trigger
- invalidation condition
- initial stop/invalidation price
- realistic gap-risk scenario
- expected first target/management zone
- maximum account loss
- planned tranche structure
- known event dates
- sector/factor exposure

Do not enter first and invent the plan later.

## 2. Risk-based sizing

Let:

- `E` = planned entry price
- `S` = invalidation/stop price
- `R_account` = maximum allowed loss in currency

Then:

`shares ≈ R_account / abs(E - S)`

Round down to an executable board lot.

Default risk limits:

- each trade: planned loss <= 0.5% of strategy capital
- all open trades combined: <= 2%
- one industry or economic-factor cluster: <= 1%

A wider stop requires a smaller position. Never widen the stop simply to keep a preferred share count.

### Gap-adjusted risk

For event-sensitive or high-volatility names, also estimate a plausible gap-through-stop loss.

If a realistic gap/price-limit scenario would cause account loss far above the allowed risk budget, either:

- reduce size materially,
- avoid holding through the event,
- or skip the trade.

The stop price is an invalidation level, not a guaranteed execution price.

## 3. A-share execution constraints

Ordinary A-share execution has market-specific constraints.

### Entry-day reversibility

Shares bought are generally not freely sellable before settlement unless the security is specifically eligible for same-day round-trip trading. Therefore:

- do not take an oversized “test entry” assuming it can always be reversed intraday,
- give extra weight to opening-gap and first-entry quality,
- size the first tranche so an adverse same-day move is survivable.

### Price-limit / gap risk

If price gaps beyond the invalidation level or is not executable because of a price limit:

- do not pretend the stop filled at the planned number,
- mark the trade as `stop breached / awaiting executable exit`,
- exit at the first executable opportunity unless a fresh independent thesis explicitly justifies otherwise,
- record realized slippage separately in post-trade review.

### Corporate-action distortion

Before using moving averages or support levels, check for:

- ex-dividend/ex-rights adjustment
- suspension/resumption
- split/bonus issue
- material restructuring or abnormal-volatility measures

Do not treat a mechanically adjusted chart as an ordinary technical breakdown without adjustment.

## 4. Entry tranches

Tranches reduce timing error; they are not a license to average down.

### Breakout setup

- tranche 1: small position on confirmed breakout
- tranche 2: add only if breakout holds or retest succeeds
- tranche 3+: add only if trend and sector participation remain strong

### Pullback setup

- tranche 1: near validated support/reclaim
- tranche 2: after price confirms support and relative strength improves
- later tranches: only after the position becomes technically safer, not merely cheaper

Capital-size defaults:

- below RMB 10,000: up to 2 names, roughly 3 tranches
- RMB 10,000–100,000: up to 3 names, roughly 4 tranches
- above RMB 100,000: up to 5 names, roughly 4 tranches

Do not force all tranches to be used.

## 5. No mechanical averaging down

Price decline alone is never an add signal.

Historical “-5% traditional / -10% technology” levels are **reassessment zones**, not automatic add levels.

An add after drawdown requires all of the following:

- original business thesis remains intact
- no new adverse official disclosure
- price has stopped making lower lows or reclaimed a key structure such as MA5/MA10/pivot
- volume-price behavior improves
- sector relative strength improves or remains intact
- updated total score remains at trade-candidate level
- expected reward/risk remains acceptable
- portfolio risk remains within limits

If these conditions are absent, do not add.

## 6. Profit management

Fixed percentages are management zones, not hard upside ceilings.

### Traditional / cyclical / lower-beta names

At roughly +3% to +5%, check:

- is momentum weakening?
- has price reached resistance?
- has sector strength rolled over?
- is volume becoming distributive?
- has the original catalyst already been priced in?

If yes, consider partial profit-taking.

### Growth / technology / higher-beta names

At roughly +6% to +10%, apply the same checks.

If trend remains strong, do not exit solely because the percentage target was reached. Use a trailing structure.

## 7. Trailing management

Possible trailing methods:

- close below MA5 after an extended move
- close below MA10 for a slower trend
- break of prior 2–3 day swing low
- failure of breakout level after a strong run
- relative-strength breakdown versus the sector

Choose the method that matches volatility. Do not change from a tight method to a loose method simply to avoid taking a loss.

## 8. Time stop

A short-term trade should work within a reasonable time.

If 3–5 trading days after entry:

- price has not progressed as expected,
- relative strength is deteriorating,
- volume participation is fading,
- catalyst timing has slipped,
- or a materially better opportunity appears while the thesis has not strengthened,

consider reducing or closing even if the hard stop has not triggered.

Time stop prevents capital from being trapped in “not wrong yet” positions.

## 9. Thesis-state management

Maintain one of four states.

### Thesis strengthening

Examples:

- earnings/catalyst better than expected
- sector leadership improves
- breakout confirmed with volume
- operating data or product price supports the original thesis

Action:

- hold
- consider add only if risk budget permits
- trail stop rationally

### Thesis intact

Action:

- hold planned size
- no unnecessary trading

### Thesis weakening

Examples:

- sector loses leadership
- failed breakout
- cash-flow/earnings quality concern emerges
- catalyst is delayed or priced in
- relative strength deteriorates materially

Action:

- reduce
- tighten invalidation
- do not add

### Thesis invalidated

Examples:

- hard technical breakdown
- adverse official disclosure changes the business thesis
- fraud/regulatory/governance event
- risk budget breached
- event outcome directly contradicts the thesis

Action:

- exit according to execution constraints
- do not rationalize or “wait for breakeven”

## 10. Event isolation

Treat the following as potential binary events:

- earnings/interim report
- performance forecast
- major contract outcome
- ex-rights/ex-dividend event that distorts chart levels
- shareholder reduction/lock-up expiry
- restructuring decision
- litigation/regulatory decision
- suspension/resumption
- major commodity/policy decision directly tied to the thesis

Before holding through a binary event, explicitly decide:

- event upside
- event downside
- gap risk
- whether position size can absorb a non-executable stop
- whether the event is already priced in

If the event risk cannot be quantified or accepted, reduce or avoid exposure before the event.

## 11. Short-term to medium-term transition

A trade can remain beyond 15 trading days only after a **fresh decision**.

Required re-underwriting:

- current thesis written again in one sentence
- fresh official fundamental/event check
- refreshed 100-point score
- new market/sector regime assessment
- new invalidation level
- new position-risk calculation
- confirmation that holding is not motivated by avoiding a loss

If re-underwriting passes, the trade may transition to medium-term management, typically up to roughly 15–60 trading days depending on catalyst and trend.

If it fails, exit or reduce according to the original plan.

## 12. Portfolio construction

Maximum simultaneous holdings: 5.

### Industry limit

No more than 2 holdings from the same industry.

### Factor limit

No more than 2 holdings driven primarily by the same macro factor.

Examples:

- copper miners + copper smelters may belong to the same copper factor
- multiple AI-server/electronics names may share AI-capex risk
- brokerages may share market-turnover risk

Industry labels do not override factor correlation.

### Portfolio heat

Track planned open risk, not only capital invested.

`portfolio heat = sum of planned loss at each position's invalidation level`

Default maximum portfolio heat: 2% of strategy capital.

## 13. Portfolio circuit breakers

Measure drawdown from the strategy account's recent equity high-water mark.

### -4%

- reduce gross exposure
- stop marginal setups
- require stronger confirmation

### -6%

- no new positions
- review whether losses share a common factor, regime mismatch, or process error

### -8%

- pause strategy
- close or reduce positions whose thesis is not clearly intact
- perform a full review before resuming

Do not reset the high-water mark merely to remove the drawdown signal.

## 14. Post-trade review

For every closed trade record:

- stock / setup type
- entry reason
- score at entry
- market and sector regime
- planned entry/stop and actual fills
- actual exit reason
- maximum favorable excursion (MFE)
- maximum adverse excursion (MAE)
- realized R multiple
- slippage caused by gap/price-limit/execution constraints
- whether the stop was respected
- whether the trade violated universe/industry/factor rules
- whether the thesis was correct even if execution was poor

Classify the outcome into:

- good process / good result
- good process / bad result
- bad process / good result
- bad process / bad result

Track statistics by setup and regime:

- win rate
- average winner / average loser
- expectancy in R
- maximum drawdown
- time-to-work
- rule-violation rate

Do not change a rule after a handful of trades. Prefer a meaningful sample to avoid fitting the strategy to recent noise.

The strategy should optimize process quality, not celebrate lucky rule violations.