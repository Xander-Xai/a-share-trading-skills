---
name: a-share-short-midterm-stock-selection
description: Select, rank, size, and manage A-share stocks for short-to-medium-term holding from a user-supplied universe. Uses fresh public data, A-share execution constraints, risk-based sizing, industry-coverage auditing, adversarial review, and explicit entry/exit rules.
compatibility: Requires fresh public market data, official A-share disclosures, and web research.
metadata:
  author: yandexuanxuan
  version: "1.4.0"
  market: "China A-share"
---

# A-share Short/Mid-term Stock Selection

## 0. Governing policy

Before execution, read:

1. `../../shared/policy-precedence.md`
2. `../../shared/capital-allocation-and-entry-policy.md`
3. `../../shared/automation-execution-governance.md` when Paper / Live / broker execution / automation is involved.

The shared capital policy is the only Source of Truth for:

- Size Cap / Risk Cap / Edge Cap;
- `Final Short Cap`;
- Operating Target / Hard Ceiling;
- default strategy tranches;
- portfolio circuit breakers;
- cross-strategy rebalancing;
- large-capital liquidity constraints.

The shared automation policy governs Paper/Live mode promotion, reconciliation, idempotency, Kill Switch and compliance gates.

This Skill may be more conservative, never more aggressive.

## 1. Purpose

Build a repeatable, evidence-based A-share workflow for short-to-medium-term trading.

Default mode:

- short term: usually 5–15 trading days;
- medium-term extension: typically 15–60 trading days only after fresh re-underwriting.

A losing short-term trade must never drift into a longer hold merely to avoid realizing a loss.

The workflow separates:

1. Eligibility
2. Timing
3. Execution
4. Sizing

A good company can fail timing. A hot chart can fail eligibility. A high score can still fail execution or risk-budget constraints.

## 2. Universe lock

If the user supplies screenshots, a watchlist or fixed pool:

- extract `stock_code + stock_name`;
- deduplicate by code;
- freeze the universe before research;
- do not introduce outside names unless explicitly requested;
- keep provenance for every final name;
- if fewer than N names pass hard gates, return fewer than N rather than filling with weak names.

## 3. Point-in-time research

Every analysis must state an `as_of` timestamp and use only information public by that time.

- no later earnings to justify an earlier decision;
- no later price action as look-ahead evidence;
- unreleased reports are event risk, not facts;
- unresolved material data gaps are `Insufficient` and cannot become executable trades.

## 4. Capital allocation and risk hierarchy

The retired rule `short-term capital <= 30% of total savings` must not be used.

Current upper bound:

```text
Final Short Cap = min(Size Cap, Risk Cap, Edge Cap)
Actual Short Exposure <= Final Short Cap
```

`Final Short Cap` is a ceiling, not a requirement to stay fully invested.

If no setup qualifies:

```text
unused strategy allocation → cash
```

Do not force trades simply to reach a nominal target percentage.

### Operating Target

```text
planned loss per trade: 0.5% of strategy NAV
aggregate open initial risk: <= 2%
aggregate initial risk per industry/factor cluster: <= 1%
```

### Hard Ceiling

```text
planned loss per trade: <= 1%
aggregate open initial risk: <= 3%
```

Moving above 0.5% requires sufficiently validated Edge, favorable regime and a high-quality setup. Hard Ceiling is never exceeded.

### Portfolio structure

Default operational limits unless shared policy is stricter:

- maximum simultaneous holdings: 5;
- same industry: no more than 2 holdings;
- same dominant economic factor: no more than 2 holdings;
- no automatic averaging down;
- no default leverage.

Capital-exposure limits and risk-heat limits must both pass.

## 5. Market and sector regime

Classify environment as:

- risk-on / trend-friendly;
- neutral / rotational;
- risk-off / high-failure-rate.

Use broad-index structure, breadth, turnover, sector relative strength, leadership persistence and breakout-failure behavior.

In risk-off conditions:

- raise entry-quality requirements;
- reduce size;
- reject late breakouts and gap chasing more aggressively.

## 6. Industry, factor and role classification

For every stock tag:

1. formal industry;
2. dominant economic factor;
3. role: national/global leader, sub-sector leader, high-quality second tier, cyclical beta, event-driven, turnaround.

Do not treat formal industry labels as proof of economic diversification.

### Industry taxonomy discipline

When industry coverage matters, use one explicit taxonomy consistently. Default to the current Shenwan 2021 Level-1 classification unless the user requests another system.

- map every stock to exactly one primary Level-1 industry for coverage counting;
- keep factor tags separately;
- do not mix concept/theme boards into formal industry counts;
- use the classification valid at `as_of`;
- check current principal business after restructuring/business transformation.

Use `references/industry-coverage-audit.md`.

## 7. Industry coverage audit

Coverage is a **research-completeness diagnostic**, not a quota.

When requested:

1. compute taxonomy total;
2. compute unique industries in locked universe;
3. compute unique industries in quality-first core pool;
4. calculate coverage ratio;
5. separate:
   - `uncovered_but_available`;
   - `absent_from_universe`;
6. do not fill absent industries with outside stocks unless expansion is explicitly authorized;
7. compare only in-universe candidates for uncovered-but-available industries;
8. leave an industry uncovered if no candidate passes hard gates.

Maintain:

```text
core quality pool
+
qualified coverage supplement pool
```

Coverage supplements are not automatically equal-priority trade candidates.

## 8. Leader and concept-authenticity gate

Leader status requires at least two evidence categories such as:

- market share / production capacity;
- revenue/profit scale;
- customer/channel position;
- technology/IP/manufacturing moat;
- resource reserves/cost curve;
- brand/standard-setting role.

Theme authenticity requires material business evidence: revenue, profit, shipment, orders, capacity, customers or commercial product.

Narrative adjacency alone earns no leader/catalyst premium.

## 9. Fundamental quality gate

Use latest official report/filing. Evaluate:

- revenue;
- attributable and adjusted profit;
- OCF or sector-appropriate substitute;
- margins;
- receivables/inventory;
- leverage/financing pressure;
- impairments/goodwill;
- customer/supplier concentration;
- governance/investigation/litigation/pledges/guarantees;
- valuation sanity.

Do not apply industrial cash-flow ratios mechanically to banks, brokers or insurers.

## 10. Scoring

Base score = 100:

```text
Technical: 30
Capital participation: 30
Fundamentals: 25
Catalyst: 15
```

Use `references/scoring-system.md`.

Interpretation:

- 80+: high-priority research candidate, only if entry is not extended;
- 75–79: candidate with trigger;
- 65–74: watchlist;
- <65: normally no new position.

A score never overrides a hard veto. Industry coverage adds no score premium.

## 11. Entry-quality gate

Before `buy trigger` status, check:

- MA5/MA10/key pivot distance;
- gap-up / limit-up behavior;
- volume vs price progress;
- breakout/retest/reclaim structure;
- nearby resistance;
- stop distance;
- realistic Reward/Risk;
- next 3–5 sessions of event risk;
- sector-cycle phase.

Preferred:

- confirmed breakout;
- first healthy pullback/retest;
- reclaim of key support/pivot;
- sector leader strengthening after consolidation.

Avoid emotional gap chasing, low-volume breakout, high-volume stagnation and blind entry before binary events.

## 12. A-share execution-risk gate

Account for:

- ordinary newly bought A-shares not being freely reversible intraday;
- gap-through-stop risk;
- daily price limits;
- suspension/resumption;
- corporate-action chart distortion;
- liquidity/slippage.

Never model a stop as a guaranteed fill price.

If realistic gap/limit scenarios breach risk budget, reduce size or reject the trade.

## 13. Position sizing

Define:

```text
E = planned entry
S = invalidation / stop
R_account = maximum allowed currency loss
```

Then:

```text
shares ≈ R_account / abs(E - S)
```

Round down to executable board lot and apply capital/factor limits.

A wider stop means smaller size. If resulting size is too small to matter, skip the trade rather than widening the stop.

## 14. Entry tranches

The old account-size-based `3/4/4` strategy-tranche rule is retired.

### Default

```text
50% Setup Entry
50% Confirmation Entry
```

Second tranche only when the first thesis is positively confirmed, e.g. breakout holds, retest succeeds, relative strength improves, sector/volume/catalyst confirms.

### Three-stage exception

```text
50% / 30% / 20%
```

Only when the strategy has three genuine confirmation levels.

### Prohibition

```text
first tranche loses
→ buy more only to lower average cost
```

is forbidden.

### Strategy tranche vs execution slicing

A large order may be split into child orders for liquidity. That does not create additional strategy tranches.

## 15. Holding states

Every open position is one of:

- `strengthening`;
- `intact`;
- `weakening`;
- `invalidated`.

Use `references/holding-risk-management.md`.

Core rules:

- no mechanical averaging down;
- add only after positive confirmation;
- if price fails to behave as expected within ~3–5 sessions and relative strength deteriorates, consider time stop/reduction;
- extend beyond 15 sessions only after fresh thesis, score, stop and risk calculation.

## 16. Stop rules

Use:

```text
price / invalidation stop
+ thesis stop
+ time stop
```

Execution order:

```text
define invalidation
→ stop distance
→ risk budget
→ shares
```

Never enter first and invent the stop later. Never widen stop in the losing direction merely to avoid a loss.

## 17. Profit management

Primary hierarchy:

```text
R multiple
+ technical structure
+ original setup target
```

Prefer realistic `Reward/Risk >= 2`.

Around +1.5R to +2R, partial profit-taking of roughly 1/3–1/2 may be considered; remaining size may use trend/trailing logic.

Historical percentage zones are secondary observation aids only:

- traditional/cyclical: roughly +3% to +5% when momentum stalls;
- growth/technology: roughly +6% to +10% when momentum stalls.

If they conflict, **R/structure wins**.

## 18. Portfolio construction

A large shortlist is a research whitelist, not a simultaneous portfolio.

```text
whitelist
→ daily rescore
→ 8–10 watch names
→ 3–5 executable candidates
→ 0–3 actual new entries
```

Portfolio heat is planned loss at invalidation, not merely capital invested.

Industry coverage belongs at whitelist/research layer and never overrides same-industry, same-factor, timing or heat limits.

Actual short exposure must remain within `Final Short Cap`; being below it is allowed.

## 19. Circuit breakers

From strategy-account high-water mark:

```text
-4% → reduce exposure and use lower-end risk sizing
-6% → no new positions; review regime/process
-8% → pause strategy; formal review before resuming
```

Do not reset high-water mark to remove the signal.

## 20. Short-to-medium transition

Beyond 15 trading days requires fresh:

- thesis;
- official fundamental/event check;
- score;
- market/sector regime;
- invalidation;
- position-risk calculation;
- confirmation that extension is not motivated by loss aversion.

If re-underwriting fails, reduce or exit.

## 21. Adversarial review

Before finalizing, run:

- universe auditor;
- identity auditor;
- point-in-time auditor;
- industry-taxonomy auditor;
- industry-coverage auditor;
- concept auditor;
- accounting auditor;
- event auditor;
- technical auditor;
- execution auditor;
- portfolio/factor auditor;
- source auditor;
- alternative auditor;
- no-trade auditor;
- policy-precedence auditor.

Industry-coverage audit must verify consistent taxonomy, no duplicate Level-1 counting, no stale classifications, no outside-universe filler, and no quality downgrade solely for coverage.

## 22. Source policy

Use `references/data-source-policy.md`.

- official filings for material facts;
- current market data for current decisions;
- explicit `as_of`;
- unknown remains unknown;
- vendor “main force inflow” is supporting evidence only;
- industry classification comes from declared formal taxonomy, not concept boards.

## 23. Required output

When screening a universe, report:

1. data coverage and `as_of`;
2. market regime;
3. ranked research pool with score, factor, role, confidence and status;
4. executable candidates with trigger, invalidation, gap risk, tranche logic and risk budget;
5. near misses;
6. adversarial audit;
7. current `Final Short Cap`, Operating Target and Hard Ceiling tier;
8. current deployed exposure and remaining cash/unused capacity.

When industry coverage is requested, additionally report taxonomy/version, universe/core coverage, uncovered/absent industries, qualified in-universe supplements and intentionally uncovered categories.

## 24. Learning loop

Every closed trade records:

- setup;
- entry score;
- market/sector regime;
- entry/exit/invalidation;
- MFE/MAE;
- realized R;
- slippage/fees;
- rule violations;
- thesis vs execution quality.

Review by setup and regime. Do not change rules after a handful of trades.

## 25. Paper / Live / Automation

When moving beyond research-only mode, read:

- `../../shared/automation-execution-governance.md`;
- `references/validation-metrics-and-trade-ledger.md`;
- `references/paper-live-automation-roadmap.md`.

Default:

```text
AUTO_MONITOR = true
AUTO_ORDER   = false
```

Paper/Live execution must be auditable, reconciled and fail closed on unknown broker/data/policy state.

## 26. Reference and example files

Core references:

- `references/scoring-system.md`
- `references/holding-risk-management.md`
- `references/data-source-policy.md`
- `references/industry-coverage-audit.md`
- `references/adversarial-review.md`
- `references/evaluation-cases.md`
- `references/research-basis.md`
- `references/validation-metrics-and-trade-ledger.md`
- `references/paper-live-automation-roadmap.md`

Historical evidence:

- `references/core-pool-snapshot-2026-08-26.md` — intermediate 36-stock snapshot;
- `examples/2026-08-26-final-watchlist-case-study.md` — later/final same-day 43-stock research state;
- `examples/2026-08-26-final-watchlist.json` — machine-readable 43-stock baseline;
- `examples/README.md` — example immutability and follow-up rules.

The 36→43 change is same-day research evolution, not two competing current whitelists. All are Level-4 history and never override a fresh run.
