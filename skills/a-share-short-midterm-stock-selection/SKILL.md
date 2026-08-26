---
name: a-share-short-midterm-stock-selection
description: Select, rank, size, and manage A-share stocks for short-to-medium-term holding from a user-supplied universe. Uses fresh public data, A-share execution constraints, risk-based sizing, adversarial review, and explicit entry/exit rules.
compatibility: Requires fresh public market data, official A-share disclosures, and web research.
metadata:
  author: yandexuanxuan
  version: "1.2.0"
  market: "China A-share"
---

# A-share Short/Mid-term Stock Selection

## 0. Governing policy

Before execution, read:

1. `../../shared/policy-precedence.md`
2. `../../shared/capital-allocation-and-entry-policy.md`

The shared policy is the only Source of Truth for:

- total short/mid-term capital allocation,
- Size Cap / Risk Cap / Edge Cap,
- Operating Target and Hard Ceiling,
- default strategy tranches,
- portfolio circuit breakers,
- cross-strategy rebalancing and profit transfer,
- large-capital liquidity constraints.

This Skill may be more conservative, but never more aggressive than shared policy.

## 1. Purpose

Build a repeatable, evidence-based A-share workflow for short-to-medium-term trading.

Default mode:

- short term: usually 5–15 trading days;
- medium-term extension: typically 15–60 trading days only after fresh re-underwriting.

A short-term trade must never drift into a longer hold merely because the position is losing.

The workflow separates four decisions:

1. Eligibility
2. Timing
3. Execution
4. Sizing

A good company can fail timing. A hot chart can fail eligibility. A high score can still fail execution or risk-budget constraints.

## 2. Universe lock

If the user supplies screenshots, a watchlist or a fixed pool:

- extract `stock_code + stock_name`;
- deduplicate by code;
- freeze the universe before research;
- do not introduce outside names unless explicitly requested;
- keep provenance for every final name;
- if fewer than N names pass hard gates, return fewer than N rather than filling with weak names.

## 3. Point-in-time research

Every analysis must state an `as_of` timestamp and only use information public by that time.

- no later earnings to justify an earlier decision;
- no later price action as look-ahead evidence;
- unreleased reports are event risk, not facts;
- unresolved data gaps must be labeled `Partial` or `Insufficient`.

## 4. Capital allocation and risk hierarchy

The old rule `short-term capital <= 30% of total savings` is retired.

Short/mid-term strategy capital is determined only by shared policy:

```text
Short Allocation = min(Size Cap, Risk Cap, Edge Cap)
```

Current Size Cap examples are maintained in shared policy and vary with stock-dedicated capital size. Do not copy a permanent 30% cap into this Skill.

### Operating Target

Default daily operating risk:

```text
planned loss per trade: 0.5% of strategy NAV
aggregate open initial risk: <= 2%
aggregate initial risk per industry/factor cluster: <= 1%
```

### Hard Ceiling

Absolute upper boundary:

```text
planned loss per trade: <= 1%
aggregate open initial risk: <= 3%
```

Moving from 0.5% toward 1% requires sufficiently validated Edge, favorable regime and a high-quality setup. The hard ceiling is never exceeded.

### Portfolio structure

Default operational limits unless shared policy is stricter:

- maximum simultaneous holdings: 5;
- same industry: no more than 2 holdings;
- same dominant economic factor: no more than 2 holdings;
- no automatic averaging down;
- no default leverage.

## 5. Market and sector regime

Before ranking stocks, classify the environment as:

- risk-on / trend-friendly,
- neutral / rotational,
- risk-off / high-failure-rate.

Use broad-index structure, breadth, turnover, sector relative strength, leadership persistence and breakout-failure behavior.

In risk-off conditions:

- raise effective entry quality requirements;
- reduce initial size;
- reject late breakouts and gap chasing more aggressively.

## 6. Industry, factor and role classification

For every stock tag:

1. industry,
2. economic driver/factor,
3. role: national/global leader, sub-sector leader, high-quality second tier, cyclical beta, event-driven, turnaround.

Do not treat exchange industry labels as proof of diversification.

## 7. Leader and concept-authenticity gate

Leader status requires at least two evidence categories such as:

- market share / production capacity,
- revenue/profit scale,
- customer/channel position,
- technology/IP/manufacturing moat,
- resource reserves/cost curve,
- brand or standard-setting role.

A theme is economically authentic only when official or reliable evidence supports material revenue, profit, shipment, order, capacity, customer or product exposure.

Narrative adjacency alone does not earn leader or catalyst premium.

## 8. Fundamental quality gate

Use the latest official report or filing. Evaluate:

- revenue trend,
- attributable and adjusted profit,
- operating cash flow or sector-appropriate substitute,
- margins,
- receivables/inventory,
- leverage and financing pressure,
- impairments/goodwill,
- customer/supplier concentration,
- governance, investigations, litigation, pledges and guarantees,
- valuation sanity where meaningful.

Do not apply industrial cash-flow ratios mechanically to banks, brokers or insurers.

## 9. Scoring

Base score = 100:

```text
Technical: 30
Capital participation: 30
Fundamentals: 25
Catalyst: 15
```

Use `references/scoring-system.md` for the full rubric.

Interpretation:

- 80+: high-priority candidate, only if entry is not extended;
- 75–79: executable candidate with trigger;
- 65–74: watchlist;
- <65: normally no new position.

A score never overrides a hard veto.

## 10. Entry-quality gate

Before calling a stock buyable, check:

- distance from MA5/MA10/key pivot,
- gap-up and limit-up behavior,
- volume expansion vs price progress,
- breakout/retest/reclaim structure,
- nearby resistance,
- stop distance,
- realistic Reward/Risk,
- next 3–5 sessions of event risk,
- sector-cycle phase.

Preferred structures:

- confirmed breakout,
- first healthy pullback/retest,
- reclaim of key support/pivot,
- sector leader strengthening after consolidation.

Avoid emotional gap chasing, low-volume breakout, high-volume stagnation, and blind entry before binary events.

## 11. A-share execution-risk gate

Ordinary A-share execution must account for:

- inability to freely reverse ordinary newly bought shares intraday,
- gap-through-stop risk,
- daily price limits,
- suspension/resumption,
- corporate-action chart distortion,
- liquidity/slippage.

Never model a stop as a guaranteed fill price.

If realistic gap/limit scenarios breach the risk budget, reduce size or reject the trade.

## 12. Position sizing

Define first:

- planned entry `E`,
- invalidation/stop `S`,
- maximum allowed account loss `R_account`.

Then:

```text
shares ≈ R_account / abs(E - S)
```

Round down to an executable board lot and apply concentration limits.

A wider stop means smaller size. If the resulting position is too small to matter, skip the trade rather than widening the stop.

## 13. Entry tranches — current policy

The old capital-size rule of `3 / 4 / 4 strategy tranches` is retired.

### Default

```text
50% Setup Entry
50% Confirmation Entry
```

The second tranche is allowed only when the first thesis is being positively confirmed, for example:

- breakout holds,
- retest succeeds,
- relative strength improves,
- volume/sector/catalyst confirms,
- new information strengthens the original thesis.

### Three-stage exception

Only if the strategy itself has three clear confirmation levels:

```text
50% / 30% / 20%
```

The second and third tranches still require positive confirmation.

### Explicit prohibition

```text
first tranche loses money
→ buy more only to lower cost
```

is forbidden.

### Strategy tranche vs execution split

A large order may be split into many child orders for liquidity. That does not create more strategy tranches.

## 14. Holding states

Every open position is one of:

- thesis strengthening,
- thesis intact,
- thesis weakening,
- thesis invalidated.

Use `references/holding-risk-management.md` for detailed actions.

Core rules:

- no mechanical averaging down;
- add only after confirmation;
- if price fails to behave as expected within roughly 3–5 sessions and relative strength deteriorates, consider a time stop or reduction;
- extend beyond 15 sessions only after fresh thesis, score, stop and risk calculation.

## 15. Stop rules

Use three dimensions:

```text
price / invalidation stop
+ thesis stop
+ time stop
```

Execution order:

```text
define invalidation
→ calculate stop distance
→ calculate risk budget
→ calculate shares
```

Never enter first and invent a stop later. Never widen the stop in the losing direction merely to avoid realizing a loss.

## 16. Profit management

The primary hierarchy is:

```text
R multiple
+ technical structure
+ original setup target
```

Prefer setups with expected Reward/Risk >= 2 when realistic.

Around +1.5R to +2R, partial profit-taking of roughly 1/3 to 1/2 may be considered; remaining size can use trend structure or trailing logic.

Historical percentage zones remain only secondary observation aids:

- traditional/cyclical: roughly +3% to +5% when momentum stalls;
- growth/technology: roughly +6% to +10% when momentum stalls.

These percentages are not mandatory ceilings. If they conflict with R-based or structural logic, **R/structure takes priority**.

## 17. Portfolio construction

A large shortlist is a research whitelist, not a simultaneous portfolio.

Typical funnel:

```text
whitelist
→ daily rescore
→ 8–10 watch names
→ 3–5 executable candidates
→ 0–3 actual new entries
```

Portfolio heat must be tracked as planned loss at invalidation, not only money invested.

## 18. Circuit breakers

Measured from strategy-account high-water mark:

```text
-4% drawdown
→ reduce exposure and cap new-trade risk at the lower end

-6%
→ no new positions; review regime and process

-8%
→ pause the strategy and complete formal review before resuming
```

Do not reset the high-water mark to remove the signal.

## 19. Short-to-medium transition

Beyond 15 trading days requires fresh re-underwriting:

- rewrite thesis,
- refresh official fundamentals/events,
- rescore,
- reassess market/sector regime,
- define new invalidation,
- recalculate risk,
- confirm the extension is not motivated by loss aversion.

If it fails, reduce or exit according to the original plan.

## 20. Adversarial review

Before finalizing, run:

- universe auditor,
- identity auditor,
- concept auditor,
- accounting auditor,
- event auditor,
- technical auditor,
- execution auditor,
- portfolio/factor auditor,
- source auditor,
- alternative auditor,
- no-trade auditor,
- policy-precedence auditor.

If a hard gate fails, remove the name and rerun checks.

## 21. Source policy

Use `references/data-source-policy.md`.

- official filings for material facts;
- current price/technical data for current decisions;
- explicit `as_of`;
- unknown remains unknown;
- vendor “main force inflow” is supporting evidence only.

## 22. Required output

When screening a universe, report:

1. data coverage and `as_of`;
2. market regime;
3. ranked pool with score, factor, role, confidence and status;
4. top executable candidates with trigger, invalidation, realistic gap risk, tranche logic and risk budget;
5. near misses;
6. adversarial audit;
7. current shared-policy allocation/risk tier.

## 23. Learning loop

Every closed trade should record:

- setup,
- entry score,
- market/sector regime,
- entry/exit/invalidation,
- MFE/MAE,
- realized R,
- slippage/fees,
- rule violations,
- thesis quality vs execution quality.

Review by setup and regime. Do not change rules after a handful of trades.

## 24. Historical snapshot

`references/core-pool-snapshot-2026-08-26.md` is a historical research snapshot only. It does not override current policy or current data.
