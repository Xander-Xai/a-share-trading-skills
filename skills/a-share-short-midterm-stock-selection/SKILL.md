---
name: a-share-short-midterm-stock-selection
description: Select, rank, and manage A-share stocks for short-to-medium-term holding from a user-supplied universe. Use when the user asks to screen stocks, build a high-quality leader watchlist, avoid concept-only names, score candidates with technicals, capital participation, fundamentals and catalysts, define entry/exit rules, or re-audit a shortlist. The skill locks to the supplied universe, validates every selected stock with fresh public information, applies A-share execution constraints and portfolio risk limits, and performs adversarial review before finalizing.
compatibility: Requires access to fresh public market data, official A-share disclosures, and web research. Designed for ChatGPT/Codex and other Agent Skills-compatible clients.
metadata:
  author: yandexuanxuan
  version: "1.1.0"
  market: "China A-share"
---

# A-share Short/Mid-term Stock Selection

## Purpose

Build a reusable, evidence-based A-share selection and holding workflow for short-to-medium-term trading.

Default mode:
- **Short-term:** usually 5–15 trading days.
- **Medium-term extension:** only when the user explicitly asks for it or when a short-term winner is re-underwritten as a new decision; typically 15–60 trading days, never by inertia.

The holding period is a consequence of thesis validity, trend structure and event risk, not a forced calendar target.

The core objective is not to predict which stock will rise tomorrow. The objective is to create a high-quality eligible pool, then only trade names whose business quality, industry position, price structure, capital participation, catalyst, execution feasibility and risk/reward align at the same time.

This skill separates four decisions that must never be mixed:

1. **Eligibility** — Is this a real, investable company worth tracking?
2. **Timing** — Is the current price/volume structure attractive enough to trade now?
3. **Execution** — Can the trade actually be entered and exited safely under A-share rules and liquidity constraints?
4. **Sizing** — How much capital can be risked without violating portfolio rules?

A good company can fail the timing gate. A hot chart can fail the eligibility gate. A high-scoring stock can still be rejected because of T+1/gap/price-limit risk or portfolio concentration.

## Non-negotiable Rules

### Universe lock

If the user supplies screenshots, a stock list, a watchlist, or a fixed candidate pool:

- Extract `stock_code + stock_name` first.
- Deduplicate by stock code before research.
- Freeze the universe before web research.
- Never introduce stocks that were not in the supplied universe unless the user explicitly asks for outside alternatives.
- Keep a provenance note for each final name showing where it came from.
- If an exact number N is requested but fewer than N names pass hard gates, return fewer names and explain the shortage. Never fill the list with weak names merely to hit a quota.

### Point-in-time research

Every analysis must state an `as of` date/time and use only information available by that timestamp.

- Do not use later earnings, later revisions or later price action to justify an earlier decision.
- If a report is scheduled but unreleased, classify it as event risk.
- If a current-data gap cannot be resolved, mark the conclusion `Partial` or `Insufficient` instead of guessing.

### User strategy defaults

Unless the user overrides them, use these portfolio constraints:

- Default holding horizon: **5–15 trading days**.
- Total trading capital: **no more than 30% of total savings**.
- Maximum simultaneous holdings: **5 stocks**.
- Same industry: **no more than 2 holdings**.
- Same macro/commodity/factor exposure: **no more than 2 holdings**, even when exchange industry classifications differ.
- Maximum planned loss per trade: **0.5% of strategy capital**.
- Maximum aggregate open risk: **2% of strategy capital**.
- Maximum aggregate risk in one industry/factor cluster: **1% of strategy capital**.
- Never average down automatically because price fell.
- Portfolio drawdown circuit breakers, measured from the strategy account's recent high-water mark:
  - **4% drawdown** → reduce exposure and tighten new-entry standards.
  - **6% drawdown** → stop opening new positions.
  - **8% drawdown** → pause the strategy and perform a full review before resuming.

For tranche defaults:

- Strategy capital below RMB 10,000: up to 2 active names, usually 3 entry tranches.
- RMB 10,000–100,000: up to 3 active names, usually 4 entry tranches.
- Above RMB 100,000: up to 5 active names, usually 4 entry tranches.

These are operational defaults, not reasons to force a trade.

## First-principles Model

Use the following mental model:

`Trade quality = business quality × industry position × current information quality × market participation × catalyst × favorable entry × executable structure`

Then discount it by:

`crowding + event risk + accounting risk + valuation risk + factor concentration + gap/price-limit risk + liquidity/slippage risk`.

Do not let one attractive dimension compensate for a failed hard gate.

## Workflow

### Step 1 — Normalize and audit the universe

Create a clean table with:

- code
- name
- source batch/file/screenshot
- exchange/board
- current status

Then check:

- duplicate codes
- name/code mismatches
- suspension status
- ST/*ST/risk-warning status
- delisting or major regulatory risk
- newly listed names with insufficient history, when moving-average history is required

The output is the **eligible raw universe**.

### Step 2 — Classify industry, economic factor and role

For every stock, tag:

1. **Industry** — e.g. copper, semiconductor packaging, home appliances, brokerage.
2. **Economic driver/factor** — e.g. copper price, AI capex, consumer recovery, grid capex, market-turnover sensitivity.
3. **Role** — national/global leader, sub-sector leader, high-quality second tier, cyclical beta, event-driven, turnaround.

This prevents fake diversification and stops a turnaround stock being scored as if it were a quality compounder.

### Step 3 — Verify leader status and reject concept-only names

A stock should receive a leader/quality premium only when at least two kinds of evidence support it, such as:

- market share or production capacity
- revenue/profit scale
- customer or channel position
- technology/IP/manufacturing moat
- resource reserves or cost curve
- brand strength
- industry-standard-setting role
- globally or domestically meaningful ranking

Do not accept “leader” merely because a media article or theme page uses the label.

Apply the **concept authenticity test**:

- Is the theme part of the company's main business?
- Is there material revenue, profit, shipment, order, capacity, customer, or product evidence?
- Has the company itself confirmed the exposure in official disclosure?
- Is the catalyst economically meaningful now, or only a future possibility?

If the answer is mostly narrative, treat it as concept-only. Such a name cannot receive a leader premium, and its catalyst score remains low.

Do not force every industry to be represented. A missing industry is preferable to inserting a weak representative.

### Step 4 — Fundamental quality gate

Use the latest available official report, earnings forecast, or company filing. Do not rely on stale annual data when a newer quarterly/interim report exists.

Evaluate:

- revenue trend
- attributable net profit trend
- adjusted/non-recurring-profit quality
- operating cash flow
- gross margin / operating margin trend
- accounts receivable and inventory
- leverage and financing pressure
- major asset impairment or goodwill risk
- customer/supplier concentration where relevant
- governance, investigation, litigation, pledges, guarantees, or audit issues
- valuation versus own history and sector, when valuation metrics are meaningful

Do not mechanically apply the same accounting ratios to every industry. See `references/scoring-system.md`.

### Step 5 — Market and sector regime gate

Before ranking individual stocks, determine whether the market and the stock's sector are:

- risk-on / trend-friendly
- neutral / rotational
- risk-off / high failure-rate

Use broad-index structure, market breadth, turnover, sector relative strength, leadership persistence, and recent breakout-failure/limit-up behavior as context.

If risk-off:

- raise the effective entry threshold by about 5 points,
- reduce initial size,
- reject late-stage breakouts and gap-chasing more aggressively.

Also compare each stock with:

- broad market
- sector index / peer basket
- direct peers inside the locked universe

The goal is to detect true relative leadership rather than a stock merely rising with its whole sector.

### Step 6 — Score each stock

Base score is 100 points:

- **Technical: 30**
- **Capital participation: 30**
- **Fundamentals: 25**
- **Catalyst: 15**

Then apply penalties and hard vetoes.

Use `references/scoring-system.md` for the full rubric.

Default interpretation:

- **80+**: high-priority candidate, only if entry is not extended.
- **75–79**: trade candidate with trigger.
- **65–74**: watchlist; wait for confirmation.
- **Below 65**: do not open a new position under normal conditions.

A score never overrides a hard veto.

### Step 7 — Apply entry-quality and chase-risk checks

Before naming a stock “buyable”, verify:

- distance from MA5 / MA10 / key breakout level
- recent gap-up and limit-up behavior
- volume expansion versus price progress
- whether the stock is breaking out, retesting, or already extended
- nearby overhead supply/resistance
- stop distance and expected reward/risk
- next 3–5 trading days of scheduled event risk
- whether the stock/sector is in the first or late phase of a momentum move

Preferred entry structures:

- breakout with sufficient volume and close confirmation
- first healthy pullback/retest after breakout
- reclaim of MA5/MA10 or key pivot after a controlled correction
- sector leader turning stronger than peers after consolidation

Avoid:

- emotional gap chasing
- buying after several large up days solely because the stock is “strong”
- low-volume breakout
- high-volume stagnation near resistance
- entering immediately before binary events without an explicit event-risk plan

### Step 8 — A-share execution-risk gate

Execution risk is a separate gate.

Ordinary A-share positions should be managed with awareness that:

- shares bought are generally not freely sellable before settlement unless the security is specifically eligible for same-day round-trip trading,
- daily price limits and gaps can make a planned stop price untradeable,
- suspensions, abnormal-volatility measures and corporate actions can distort technical levels.

Therefore:

- never model a stop as a guaranteed fill price,
- if a gap opens beyond the stop, use first-executable-price logic,
- reduce size before binary events when gap risk is unacceptable,
- reject trades whose expected downside under realistic gap/limit scenarios would breach the risk budget.

### Step 9 — Position sizing by risk, not conviction language

Define first:

- planned entry
- invalidation/stop price
- loss per share
- maximum allowed account loss

Then calculate:

`position shares ≈ max allowed trade loss / abs(entry price - invalidation price)`

Round down to an executable board lot and then apply capital-concentration limits.

A wider stop requires a smaller position. If the resulting position is too small to matter, skip the trade instead of widening the stop arbitrarily.

### Step 10 — Holding management

Every open position must have four states:

- thesis strengthening
- thesis intact
- thesis weakening
- thesis invalidated

Do not manage positions using profit/loss percentage alone.

Use `references/holding-risk-management.md` for detailed rules.

Core rules:

- No mechanical averaging down.
- Add only after confirmation, not because a stock became cheaper.
- If price does not behave as expected within roughly 3–5 trading days and relative strength deteriorates, consider a time stop or reduction.
- Traditional/cyclical names may begin partial profit-taking around **+3% to +5%** when momentum stalls.
- Growth/technology names may begin partial profit-taking around **+6% to +10%** when momentum stalls.
- These are management zones, not mandatory ceilings.
- Extend beyond 15 trading days only after a fresh re-underwriting decision with a new thesis, score, stop and risk budget.

### Step 11 — Portfolio construction

A 36-stock or similar shortlist is a **research whitelist**, not a simultaneous portfolio.

Convert it through:

`whitelist -> daily rescore -> 8–10 watch names -> 3–5 executable candidates -> 0–3 actual new entries`

Actual holdings remain constrained by:

- max 5 stocks,
- max 2 same industry,
- max 2 same economic factor,
- max 1% aggregate risk per factor cluster,
- max 2% aggregate open risk.

### Step 12 — Adversarial review before final answer

Run the following independent checks:

1. **Universe auditor** — Did any final name come from outside the user-supplied pool?
2. **Identity auditor** — Are code and company name correct?
3. **Concept auditor** — Is the claimed theme economically real or merely narrative?
4. **Accounting auditor** — Does profit growth reconcile with revenue, adjusted profit, cash flow and balance-sheet changes?
5. **Event auditor** — Is there earnings, suspension, ex-rights, lock-up expiry, reduction, restructuring, inquiry or other binary risk nearby?
6. **Technical auditor** — Is the stock already too extended, showing distribution, or late in the sector move?
7. **Execution auditor** — Is the assumed stop realistically executable under T+1, gap and price-limit constraints?
8. **Portfolio auditor** — Are selected stocks secretly concentrated in the same commodity, macro factor, or style?
9. **Source auditor** — Are key claims based on current, authoritative sources and point-in-time valid?
10. **Alternative auditor** — Within the locked universe, is there a clearly superior eligible alternative that was missed?
11. **No-trade auditor** — Is the system forcing a trade merely because the user asked for a list?

If a selected stock fails a hard gate, remove it, replace it only with the next-ranked eligible stock from the locked universe, and rerun the checks.

## Source Policy

Use `references/data-source-policy.md`.

Minimum standards:

- Fundamental facts should be grounded in official exchange/CNINFO/company filings whenever available.
- Current price/technical analysis must use the latest completed trading session, or current intraday data when the user explicitly asks for intraday analysis.
- Every time-sensitive output must state an `as of` date/time.
- If data is incomplete or a report has not yet been released, label it unknown instead of estimating it as fact.
- Commercial “main force net inflow” metrics are vendor-defined and must be treated as supporting evidence, never a standalone buy signal.
- Maintain a research trail for every selected stock.

## Required Output Format

When screening a universe, return:

### 1. Data coverage

State:

- as-of date/time
- number of raw records
- number after deduplication
- whether the universe is locked
- whether any data gaps remain

### 2. Market regime

Give a short regime label and the implications for entry aggressiveness.

### 3. Final ranked pool

For each selected stock include:

- code / name
- source provenance
- industry
- economic factor
- role / leader evidence
- technical score / 30
- capital score / 30
- fundamental score / 25
- catalyst score / 15
- penalties
- final score
- confidence level
- data completeness
- current status: `buy trigger / wait for pullback / wait for breakout / event isolation / avoid`
- one-line main risk

### 4. Top executable candidates

Normally narrow the pool to 3–5 names only when they actually meet entry standards.

For each executable candidate provide:

- preferred trigger
- alternative pullback entry
- invalidation/stop
- realistic gap-risk note
- first profit-management zone
- secondary/trailing plan
- suggested tranche logic
- maximum risk budget

### 5. Near misses

Show a small number of high-quality excluded names and the exact reason they failed today. This prevents opaque ranking changes.

### 6. Adversarial audit

Explicitly report:

- outside-universe names: 0 or list them as an error
- duplicates: 0 or list them as an error
- concept-only failures removed
- accounting-quality failures removed
- event-risk names isolated
- execution-risk failures removed
- factor concentration check result
- whether `no trade today` was considered

## Learning and Review

Every closed trade should be logged with:

- setup type
- entry score
- market/sector regime
- entry/exit/invalidation
- MFE and MAE
- realized R multiple
- rule violations
- thesis correctness vs execution quality

Review statistics by setup and regime, not only overall win rate.

Do not change rules after a handful of trades. Prefer a meaningful sample before recalibrating thresholds to avoid overfitting recent outcomes.

## Current Snapshot

The 36-stock pool produced in the 2026-08-26 screening session is stored in:

`references/core-pool-snapshot-2026-08-26.md`

Treat it as a historical snapshot, not a permanent buy list. Revalidate after new earnings, material announcements, large price moves, or market-regime changes.

## Reference Files

- `references/scoring-system.md` — detailed score rubric and sector-specific adjustments.
- `references/holding-risk-management.md` — entry, sizing, add/reduce/exit, time-stop, and portfolio rules.
- `references/data-source-policy.md` — source hierarchy, freshness rules, point-in-time evidence standards.
- `references/adversarial-review.md` — red-team checklist.
- `references/evaluation-cases.md` — reusable evaluation cases.
- `references/research-basis.md` — external research and regulatory basis for the design.
- `references/core-pool-snapshot-2026-08-26.md` — current 36-stock historical snapshot.

## Final Principle

The skill must be willing to conclude **“no trade today.”**

Stock selection is a qualification process. Timing is a separate decision. Execution feasibility and risk control override both.