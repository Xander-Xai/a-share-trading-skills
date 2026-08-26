# Scoring System

## Overview

The base model is 100 points:

- Technical: 30
- Capital participation: 30
- Fundamentals: 25
- Catalyst: 15

The score is only valid after hard eligibility checks. Apply penalties after the base score. A hard veto cannot be offset by a high score elsewhere.

The score is a ranking device, not a prediction probability. It must always be paired with data completeness, market regime, execution feasibility and portfolio constraints.

## 1. Technical — 30 points

### Trend quality — 8

- 7–8: price above key short/medium moving averages with orderly slope and no obvious late-stage blow-off
- 5–6: constructive but mixed; consolidation or early recovery
- 3–4: range-bound or unstable trend
- 0–2: broken trend, repeated failed rebounds, or persistent relative weakness

### Structure / setup — 6

Reward:

- clean breakout base
- first pullback/retest
- reclaim of a key pivot
- higher lows and controlled volatility

Penalize:

- overhead supply immediately above
- repeated failed breakout attempts
- large unfilled gaps without support

### Volume-price confirmation — 6

Reward:

- breakout with meaningful volume expansion
- pullback on declining volume
- renewed volume on reversal/reclaim

Penalize:

- low-volume breakout
- high-volume stagnation
- large-volume decline

### Relative strength — 5

Compare against:

- broad market
- relevant industry/sector
- direct peers in the locked universe

A stock does not deserve full trend points merely because the whole sector rose.

### Entry quality / reward-risk — 5

Evaluate:

- distance to logical invalidation
- distance to resistance
- deviation from MA5/MA10
- expected reward/risk
- gap/price-limit risk around the planned entry

A technically strong stock that is too extended can score poorly here.

## 2. Capital Participation — 30 points

Do not equate vendor-labeled “main force net inflow” with institutional conviction. Treat capital flow as a multi-source evidence problem.

### Turnover and volume quality — 8

Assess:

- volume trend
- turnover versus own history
- whether volume supports price progress
- liquidity sufficient for execution

### Financing / leverage participation — 5

When applicable, review:

- margin financing balance trend
- whether leverage expands with or against price confirmation

Avoid treating financing growth alone as bullish.

### Institutional / professional activity — 5

Use when available:

- Dragon-Tiger List institutional seats
- block trades
- disclosed fund/major-holder changes
- material placement or buyback activity

### Sector capital confirmation — 4

Check whether the stock is moving with genuine sector participation rather than isolated theme noise.

### Large-order / vendor flow evidence — 4

Commercial large-order or “main force” metrics may contribute here only as corroboration. Definitions vary by vendor.

### Price confirmation of capital thesis — 4

If claimed inflow does not translate into price/relative-strength confirmation, do not give full capital points.

## 3. Fundamentals — 25 points

### Earnings trend — 7

Evaluate the latest available period and the prior 2–4 reporting periods where useful:

- revenue
- attributable profit
- operating profit/margin
- YoY and sequential direction

Do not reward a large percentage increase caused only by a tiny or negative base without context.

### Earnings quality / adjusted profit — 4

Check:

- adjusted or non-recurring-profit trend
- gains from asset sales, subsidies, fair-value changes, debt restructuring, or other one-offs

### Operating cash flow — 5

For ordinary industrial/consumer/technology companies:

- compare operating cash flow with profit trend
- investigate large divergence
- review receivables and inventory when cash conversion weakens

For banks, brokers, insurers and other financial firms, do not use industrial cash-flow logic mechanically. Use sector-appropriate balance-sheet and capital metrics instead.

### Balance-sheet quality — 4

Check:

- leverage
- short-term debt pressure
- interest burden
- receivables
- inventory
- guarantees/pledges
- impairment/goodwill where material

### Industry position / moat — 3

Require evidence of real position, not a theme label.

### Valuation sanity — 2

Prefer relative valuation to the company's own history and sector.

User preference defaults:

- traditional/cyclical names: prefer valuation in the lower part of a 1–3 year range when the metric is meaningful
- growth/technology names: prefer valuation not excessively stretched versus the recent 6–12 month range
- PE/PS around or below 40 may be used as a soft preference when appropriate, never as a universal hard filter

Do not use PE mechanically for loss-making firms, deep cyclicals at peak earnings, banks, or businesses better measured by PB/FCF/EV metrics.

## 4. Catalyst — 15 points

### Certainty — 5

Highest scores require official, observable, or already-occurring catalysts:

- earnings beat / forecast
- price increase in a key commodity/product
- material order or capacity start-up
- policy already published
- buyback / dividend / restructuring step already disclosed

Rumors score low.

### Economic materiality — 5

Ask whether the catalyst can materially affect:

- revenue
- profit
- margins
- capacity utilization
- valuation regime
- industry supply/demand

### Timing / decay — 5

Catalysts should matter within the strategy horizon or provide a clear path to near-term re-rating.

Reduce score when:

- event is far away
- market has already fully priced the news
- catalyst is repeatedly recycled without new information

## Penalties

Apply after base score.

### Chase / extension penalty: 0 to -15

Examples:

- several consecutive large up days
- large deviation from MA5/MA10
- gap/limit-up continuation with poor reward-risk
- exhaustion volume near resistance

### Event-risk penalty: 0 to -15

Examples:

- earnings in the next 1–3 trading days
- ex-rights/ex-dividend mechanics that distort chart interpretation
- lock-up expiry
- major court/regulatory decision
- shareholder reduction window
- unresolved suspension/restructuring event

A binary event can instead be handled as an `event isolation` status rather than merely a numeric penalty.

### Concept-authenticity penalty: 0 to -20

Apply when a popular theme is weakly connected to actual business economics.

### Accounting-quality penalty: 0 to -20

Examples:

- profit growth dominated by non-recurring items
- cash flow deterioration unexplained by normal seasonality/capex
- rapid receivable/inventory build
- impairment or governance concerns

### Execution-risk penalty: 0 to -15

Apply when:

- realistic gap-through-stop loss is much larger than planned risk
- recent limit-up/limit-down behavior makes exits uncertain
- liquidity/slippage is poor relative to the intended position
- suspension/resumption or abnormal-volatility mechanics create unreliable technical levels
- the trade depends on an intraday exit assumption incompatible with ordinary A-share settlement

A severe execution problem is a hard veto rather than a numeric penalty.

### Factor-crowding penalty: 0 to -10

Apply to the **portfolio decision**, not necessarily the standalone company score, when the planned position adds too much exposure to an already crowded commodity/macro/style factor.

### Data-confidence penalty: 0 to -10

Use when latest official information is missing, inconsistent, stale, or not point-in-time valid.

## Hard Vetoes

Unless the user explicitly requests special-situation trading, reject new positions when any of the following is material:

- stock not in the locked user universe
- code/name identity unresolved
- ST/*ST or material delisting-risk condition
- suspension prevents normal execution
- severe regulatory/accounting/governance event not resolved
- concept thesis lacks real business evidence and is the only reason for selection
- stop/invalidation cannot be defined at acceptable risk
- realistic gap/price-limit risk would breach the account risk budget
- portfolio risk/correlation limit would be violated
- data completeness is `Insufficient`

## Sector-specific Fundamental Adjustments

### Resource / commodity

Add emphasis to:

- reserve quality
- production volume
- cost curve
- realized selling price
- commodity inventory cycle
- capex discipline

Do not interpret low PE at commodity peak as automatically cheap.

### Semiconductor / electronics / AI hardware

Add emphasis to:

- customer concentration
- inventory days
- utilization
- ASP and product mix
- capex cycle
- R&D conversion
- order visibility

### Consumer

Add emphasis to:

- channel inventory
- same-store / sell-through when available
- brand pricing power
- gross margin
- operating cash flow

### Pharma / biotech

Add emphasis to:

- approved products versus pipeline stories
- commercialization/reimbursement
- R&D expense quality
- patent/regulatory milestones
- reliance on one product

### Banks

Replace industrial cash-flow analysis with:

- NIM
- asset quality / NPL
- provision coverage
- capital adequacy
- ROE
- valuation vs PB/history

### Brokers

Focus on:

- market turnover sensitivity
- brokerage/wealth-management trend
- investment banking
- proprietary investment volatility
- ROE/capital efficiency
- balance-sheet leverage

### Utilities

Focus on:

- utilization hours
- tariff/fuel cost
- project commissioning
- capex/debt burden
- dividend/FCF sustainability

## Horizon adaptation

### Short-term mode: 5–15 trading days

Keep full weight on:

- technical structure
- current capital participation
- near-term catalyst timing
- entry quality

### Medium-term extension: roughly 15–60 trading days

Do **not** simply reuse the old short-term score. Re-underwrite and increase emphasis on:

- fundamental trend persistence
- catalyst runway
- valuation sanity
- medium-term trend / MA10–MA20 structure
- balance-sheet and cash-conversion quality

A short-term loser cannot become medium-term merely to avoid realizing a loss.

## Decision Thresholds

- 80+: high-priority candidate, only if entry is not extended and execution risk is acceptable
- 75–79: trade candidate with trigger
- 65–74: watch / wait for confirmation
- below 65: normally no new position

In a risk-off market, add roughly 5 points to the practical entry threshold or reduce size materially.

## Confidence Label

Every final score should include confidence:

- **High**: fresh official fundamentals + fresh market data + clear industry thesis + no material data conflict
- **Medium**: one important data gap or ambiguous catalyst
- **Low**: material data uncertainty; normally not executable

## Final note

A 90-point company can still be a `wait` if price is extended. A 78-point setup can still be rejected if the portfolio already has too much exposure to the same factor. Scoring ranks opportunities; it does not override risk architecture.