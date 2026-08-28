# Short/Mid-term Research Iteration Roadmap v1

> Status: `ACTIVE GOVERNANCE ROADMAP`
>
> Scope: `a-share-short-midterm-stock-selection` research/validation evolution.
>
> This roadmap defines **how the repository should iterate**, not a shortcut for changing production rules. Any model or parameter change must still follow `shared/research-model-governance.md`, the Champion/Challenger protocol, point-in-time rules, and the shared capital/risk policy.

## 1. North Star

The objective is not to maximize a single historical return number. The objective is to build a research system that is:

```text
point-in-time valid
+ economically interpretable
+ executable in A-shares
+ robust after costs
+ stable across regimes
+ resistant to data snooping
+ auditable when wrong
```

The long-run target architecture is:

```text
Universe / Point-in-Time Gate
→ Fundamental Eligibility
→ Expectation–Reaction Gate (ERG)
→ Market / Sector Regime
→ Participation / Relative Strength
→ Research State
→ Execution Gate
→ Risk Budget
→ Position State
→ Portfolio / Factor Risk
→ MFE / MAE Learning
→ Forward / Ablation Validation
→ Statistical Promotion Guard
```

## 2. Non-negotiable iteration rules

Every future iteration must obey these rules:

1. **Champion remains unchanged until Promotion Review passes.**
2. New ideas enter `Challenger / Shadow` first.
3. Never tune on future information or later price action.
4. Freeze each cohort's feature definitions, thresholds, benchmarks, costs and execution assumptions before observing outcomes.
5. Record `NO_TRADE`, failed candidates and negative results, not only winners.
6. Do not silently merge multiple incompatible strategy types.
7. Prefer removing non-value modules over accumulating features.
8. Complexity must earn its keep through forward/ablation evidence.
9. A parameter that looks intuitive but has no sample-out robustness remains a governance parameter, not an alpha claim.
10. Model promotion and automation promotion are separate decisions.

## 3. Iteration ladder

### Phase 0 — Data and audit integrity

**Goal:** ensure later research results are trustworthy before adding more alpha logic.

Required work:

- freeze `as_of`, `information_timestamp`, `first_tradable_timestamp`;
- preserve source provenance and `source_tier`;
- verify corporate-action-adjusted price history;
- retain delisted/ST names where applicable for historical tests;
- respect T+1, price limits, suspensions and gap-through-stop behavior;
- define benchmark history point-in-time;
- preserve event publication timestamps, including after-close disclosures;
- separate unavailable data from zero/neutral data.

Exit criteria:

```text
PIT audit = PASS
survivorship audit = PASS
execution calendar audit = PASS
source provenance coverage = acceptable
```

If Phase 0 fails, do not interpret any backtest as promotion evidence.

---

### Phase 1 — ERG Shadow baseline

**Goal:** accumulate untouched real-time/forward records for the newly integrated Expectation–Reaction Gate.

Freeze:

```text
erg_version
expectation source policy
expectation confidence rules
materiality definitions
prepricing windows
reaction windows
benchmark selection
research-state rules
strategy-type rules
```

For every event-driven candidate record at minimum:

```text
Expectation Baseline
Surprise
Materiality
Prepricing
Post-event Reaction
Research State
Position State
Strategy Type
Entry Trigger
Invalidation
Planned RR
```

Primary question:

> Does ERG reduce false-positive catalyst trades and chasing without destroying too much useful opportunity?

Diagnostics:

- candidate → confirmed rate;
- confirmed → entry rate;
- positive-surprise / negative-reaction frequency;
- priced-in false-positive rate;
- invalidated-after-entry rate;
- no-trade rate;
- expectancy by expectation-confidence bucket.

No production promotion in this phase.

---

### Phase 2 — Module ablation

**Goal:** determine which parts of ERG add incremental value.

Run the frozen ladder:

```text
A: Eligibility only
B: A + Expectation / Surprise
C: B + Economic Materiality
D: C + Prepricing
E: D + Post-event Reaction
F: E + Regime / Participation / Execution / Risk
```

For each increment compare:

- net expectancy in R;
- excess return;
- Profit Factor;
- Max Drawdown;
- Calmar;
- tail loss;
- turnover and cost drag;
- MFE / MAE distributions;
- no-trade rate;
- rule-violation rate.

Decision logic:

```text
adds robust value → retain
no material value → simplify/remove
helps only one regime → condition explicitly
hurts execution/cost → reject or redesign
```

Do not keep a component merely because it sounds economically reasonable.

---

### Phase 3 — Event-family specialization

**Goal:** stop assuming all catalysts behave the same.

Maintain separate cohorts for:

```text
EARNINGS
EARNINGS_PREANNOUNCEMENT
ORDER_CONTRACT
COMMODITY_PRODUCT_PRICE
POLICY
CAPITAL_STRUCTURE
OTHER
```

Each family gets its own materiality logic.

Examples:

**Earnings**

```text
actual vs expectation
+ quarter acceleration
+ margin/cash conversion
+ guidance
```

**Orders**

```text
order / annual revenue
order / segment revenue
expected margin
recognition window
execution/cancellation risk
```

**Commodity / product price**

```text
price
→ realized ASP
→ input cost
→ unit margin
→ volume
→ profit sensitivity
```

**Policy**

```text
policy
→ demand / supply / cost / price / capacity / competition
→ company exposure
→ earnings path
```

Promotion evidence must not be created by pooling unrelated event types solely to inflate sample size.

---

### Phase 4 — Regime conditioning

**Goal:** determine whether the same setup should be treated differently in different market environments.

Current regime families:

```text
TREND_FRIENDLY
ROTATIONAL_NEUTRAL
MEAN_REVERTING
RISK_OFF
```

Research questions:

- Does breakout confirmation work only in trend-friendly regimes?
- Does strong ERG surprise still require different execution in risk-off regimes?
- Does prepricing have different thresholds in high-beta sectors?
- Does relative strength matter more during rotation?
- Does the system need a separate mean-reversion Challenger rather than forcing trend rules to handle it?

Do not retrofit a losing trend trade into mean reversion. A dedicated mean-reversion model must be a separate research family.

---

### Phase 5 — Execution and invalidation calibration

**Goal:** improve trade implementation without pretending entry/stop parameters are universal truths.

Candidate parameters to study:

- breakout/retest/reclaim definitions;
- acceptable distance from pivot/structure;
- gap filters;
- event-gap risk handling;
- stop/invalidation buffer;
- time-review windows;
- partial-profit rules;
- minimum realistic Reward/Risk;
- tranche logic.

Rules:

- invalidation is thesis/structure based first;
- ATR may be a volatility buffer, not a magical stop formula;
- never widen invalidation after entry merely to avoid a loss;
- nearby parameter values must show a broad performance plateau rather than one narrow optimum.

Use MFE/MAE to ask:

```text
Are stops too tight?
Are targets too conservative?
Do winners require more time?
Are weak trades failing quickly enough to justify a time stop?
```

---

### Phase 6 — Portfolio and factor-risk iteration

**Goal:** improve portfolio-level survival rather than evaluating trades independently.

Study:

- same-industry concentration;
- same-economic-factor concentration;
- commodity beta clusters;
- growth/liquidity beta clusters;
- event-calendar clustering;
- hidden correlation during risk-off periods;
- account-level overlap with long-term sleeves.

Current shared limits remain governance constraints until separately validated.

Potential future Challenger fields:

```text
marginal_portfolio_risk
cluster_heat_before
cluster_heat_after
correlation_stress_state
factor_contribution_to_risk
```

A high-quality single-stock setup may still be rejected if it worsens portfolio concentration.

---

### Phase 7 — Statistical robustness and model-selection control

**Goal:** prevent research iteration itself from manufacturing false alpha.

Maintain the trial ledger in `statistical-promotion-guard.md`.

For every material research family preserve:

```text
number_of_trials
parameter_grid
selection_rule
losing/neutral variants
parameter_stability_summary
untouched_test_status
```

When sample/tooling permit, add:

```text
Deflated Sharpe Ratio
Probability of Backtest Overfitting
White/SPA-style reality-check status
```

Warning signs:

- edge exists at only one narrow threshold;
- benchmark or test window changed after seeing results;
- features are repeatedly added against the same validation period;
- a small number of outliers create most of the excess return;
- performance disappears after realistic costs;
- a model looks good only after many undisclosed trials.

---

### Phase 8 — Partial promotion before full-model replacement

**Goal:** promote only components that demonstrably add value.

Allowed decisions:

```text
PROMOTE_SELECTED_COMPONENTS
KEEP_SHADOW
REMOVE_COMPONENT
REVISE_AND_RESTART
REJECT
```

Examples:

- Prepricing may be promoted while a noisy consensus source remains Shadow.
- Research-state/position-state separation may be promoted for governance even if it adds no return, if it materially reduces rule violations.
- A new execution filter may be retained only for one regime.

Do not require an all-or-nothing replacement of the existing Champion.

---

### Phase 9 — Champion redesign, only if evidence supports it

Only after enough forward/ablation evidence should the repository consider replacing the current compensatory Champion score.

Potential future direction:

```text
Hard Gates
→ Research State
→ intra-state Ranker
→ Execution Gate
→ Risk / Position
```

In that design, a numerical score becomes a **ranker**, not an engine that can compensate for a failed causal gate.

A proposed Champion redesign must answer:

- What exact failure of the current Champion does it fix?
- Which forward evidence shows improvement?
- Which components were removed as non-value?
- Does complexity increase?
- Does drawdown/tail risk worsen?
- Is the advantage robust across regimes and event families?

---

### Phase 10 — Automation promotion

Automation is last, not first.

```text
Research Model Promotion != Automation Promotion
```

Before increasing automation autonomy, separately validate:

- data freshness and fallback;
- broker reconciliation;
- idempotency;
- order-state recovery;
- price-limit/suspension handling;
- kill switch;
- manual override;
- audit logs;
- fail-closed behavior.

No research edge justifies unsafe execution infrastructure.

## 4. Recommended next experiment queue

Priority order:

### P0 — Start now

1. Freeze ERG v1 Forward cohort.
2. Record the current 8-stock case as an initial ERG/Champion comparison sample.
3. Build event-timestamp + first-tradable-timestamp coverage.
4. Record expectation baseline confidence instead of forcing consensus.
5. Capture MFE/MAE and realized R for every executable Shadow/Champion signal.

### P1 — After enough forward observations

6. Run ERG ablation A→F.
7. Compare Prepricing + Reaction versus generic Catalyst scoring.
8. Compare `State First, Rank Second` against pure total-score ranking.
9. Analyze no-trade decisions as first-class outcomes.
10. Split earnings, order, commodity and policy events.

### P2 — After multi-regime data

11. Test regime-conditioned execution rules.
12. Calibrate time stops and partial-profit behavior using MFE/MAE.
13. Study portfolio cluster heat and hidden correlation.
14. Run parameter-stability surfaces and model-selection diagnostics.

### P3 — Promotion review

15. Promote only components that improve robustness/expectancy or materially reduce rule violations.
16. Keep the current Champion if the Challenger cannot demonstrate a cost-aware sample-out advantage.

## 5. Required experiment memo

Every meaningful iteration should create a short memo with:

```text
research_family_id
hypothesis
problem_being_fixed
baseline_model
challenger_change
frozen_as_of / cohort period
universe
features changed
parameters changed
number_of_trials
expected mechanism
primary metric
risk metrics
cost assumptions
ablation plan
promotion criteria
result
failure modes
next action
```

This prevents repository evolution from becoming undocumented intuition.

## 6. Stop conditions for iteration

Pause feature expansion and return to data/governance review if any occurs:

- point-in-time violations;
- missing event timestamps at material scale;
- repeated parameter changes mid-cohort;
- unexplained discrepancies between research and simulated execution;
- increasing rule-violation rate;
- apparent edge driven by a few names/events;
- costs/slippage erase the gross edge;
- too many unresolved data fields to reproduce results.

## 7. Definition of a successful iteration

A successful iteration does **not** have to increase gross return.

It can succeed by:

- improving net expectancy;
- reducing drawdown/tail loss;
- reducing false positives;
- reducing rule violations;
- reducing turnover/cost drag;
- improving interpretability;
- improving point-in-time reproducibility;
- removing a useless feature;
- identifying that a strategy only works in a specific regime.

The guiding principle is:

```text
More evidence, fewer stories.
More robustness, fewer parameters.
More auditability, less hindsight.
```

## 8. Current status

As of `2026-08-28`:

```text
Champion = ACTIVE
Causal Challenger v1.1 = SHADOW ONLY
ERG v1 = SHADOW ONLY
Statistical Promotion Guard = ACTIVE GOVERNANCE SUPPORT
Next valid step = frozen Forward cohort + ERG ablation data collection
```

No repository-specific alpha claim is considered proven until the forward/promotion process says so.
