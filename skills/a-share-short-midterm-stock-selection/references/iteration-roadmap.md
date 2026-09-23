# Short/Mid-term Research Iteration Roadmap v1.1

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
11. Independent experiment tracks remain attributable until their separate contribution has been measured.
12. Do not combine multiple new research tracks into one model before one-at-a-time or staged attribution is available.

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
- separate unavailable data from zero/neutral data;
- resolve event execution through the session-aware exchange/broker contract.

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

**Goal:** accumulate untouched real-time/forward records for the integrated Expectation–Reaction Gate.

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
confirmation-basis rules
strategy-type rules
session-rule version
```

For every event-driven candidate record at minimum:

```text
Expectation Baseline
Surprise
Materiality
Prepricing
Post-event Reaction
Research State
Confirmation Basis
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
- expectancy by expectation-confidence bucket;
- blocked-opportunity MFE;
- session-resolution rate.

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
- CVaR / tail loss;
- turnover and cost drag;
- MFE / MAE distributions;
- no-trade rate;
- blocked-opportunity cost;
- rule-violation rate.

Decision logic:

```text
measurable sample-out increment → retain for further review
no measurable increment → simplify/remove
increment only in one regime → condition explicitly
execution/cost deterioration dominates increment → reject or redesign
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
- Does ERG surprise require different execution in risk-off regimes?
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
- tranche logic;
- limit-hit density;
- price-progress-per-RVOL;
- stress loss under gap/price-limit scenarios.

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

A single-stock setup may still be rejected if it worsens portfolio concentration beyond current policy.

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
- a model appears only after many undisclosed trials.

---

### Phase 8 — Partial promotion before full-model replacement

**Goal:** promote only components that demonstrate incremental contribution under the frozen contract.

Allowed decisions:

```text
PROMOTE_SELECTED_COMPONENTS
KEEP_SHADOW_WITHOUT_EXPANSION
CONDITION
REMOVE_COMPONENT
REVISE_AND_RESTART
REJECT
```

Examples:

- Prepricing may be promoted while a noisy consensus source remains Shadow.
- Research-state/position-state separation may be promoted for governance if it materially reduces rule violations even without return increment.
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
- Which forward evidence shows measurable change?
- Which components were removed as non-incremental?
- How many fields/sources/parameters were added or removed?
- Does drawdown/tail risk worsen?
- Is the effect stable across regimes and event families?

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

## 4. Parallel VNext experiment tracks

The detailed experiment catalog and machine-readable registry are:

- `vnext-experiment-directions.md`
- `vnext-experiment-directions.json`

Five tracks remain independent until attribution is available:

```text
A — ERG Precision
B — Conditional Participation
C — Execution / Overreaction Shield
D — Disagreement Arbitration
E — Champion Simplification
```

Research lanes:

```text
Alpha / discrimination: A, B, D
Tail-risk / execution: C
Complexity / maintenance: E
```

Current implementation order is based on repository readiness rather than expected return:

```text
D0 → C → A → E → B
```

Do not merge A+B+C+D+E into one VNext model before independent or staged attribution is available.

## 5. Common VNext measurement contract

Every track reports the same shared metrics when compared under the same baseline:

```text
Delta_Expectancy_R
Delta_Excess_Return
Delta_Profit_Factor
Delta_Max_Drawdown
Delta_CVaR95
Delta_Cost_Drag
False_Positive_Delta
False_Negative_Delta
Coverage
Data_Missing_Rate
Turnover_Delta
Rule_Violation_Delta
Added_Fields
Added_External_Data_Sources
Added_Tunable_Parameters
Number_of_Trials
```

Engineering complexity diagnostic:

```text
AddedComplexity
= Added_Fields
+ 2 * Added_External_Data_Sources
+ Added_Tunable_Parameters

IncrementalEdgePerComplexity
= Delta_Expectancy_R / max(1, AddedComplexity)
```

Final comparison uses hard data/risk gates first and Pareto comparison second. Do not convert all dimensions into another arbitrary 100-point enhancement score.

## 6. Stage-1 screening parameters

The detailed values live in `vnext-experiment-directions.md/json`.

Current first-cycle governance candidates include:

```text
return-oriented:
Delta_Expectancy_R > 0
Coverage >= 70%
Delta_Cost_Drag <= +0.05R/trade
MaxDD_new <= 1.10 * MaxDD_baseline
CVaR95_new <= 1.05 * CVaR95_baseline

risk-oriented Track C:
CVaR95_new < baseline
MaxDD_new <= baseline

filtering claim diagnostics:
relative false-positive reduction >= 15%
false-negative change <= +10 percentage points
```

These are project governance parameters for experiment screening, not claims of market-optimal thresholds. Freeze before formal evaluation and version any change.

## 7. Recommended next experiment queue

### P0 — Already started / active infrastructure

1. First ERG/Champion Forward cohort is frozen at `2026-08-28T18:10:00+08:00`.
2. Session-aware `first_tradable_timestamp` contract is active.
3. Disagreement Ledger is active.
4. Negative-control/placebo protocol is active.
5. D0 disagreement measurement has started.

### P1 — Next implementation candidates

6. Build Track C price/execution stress fields and frozen C0→C4 tests.
7. Build Track A benchmark contract, event-family reaction-window contract and expectation-coverage calibration.
8. Start one-at-a-time Track E Champion ablations once baseline replay is reproducible.
9. Continue ERG A→F ablation and no-trade opportunity-cost collection.

### P2 — Data-dependent track

10. Audit PIT positioning/ownership data coverage before implementing Track B.
11. Start B only if the intended universe has explicit coverage/staleness reporting.
12. Continue event-family specialization and regime conditioning.
13. Calibrate time stops and partial-profit behavior using MFE/MAE.
14. Study portfolio cluster heat and hidden correlation.

### P3 — Promotion review

15. Compare A/B/C/D/E within their lane and on common metrics.
16. Remove Pareto-dominated variants.
17. Run statistical selection-bias controls before component promotion.
18. Promote only components that pass the existing Champion/Challenger governance.

## 8. Required experiment memo

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

VNext track experiments additionally record:

```text
track_id
lane
Added_Fields
Added_External_Data_Sources
Added_Tunable_Parameters
AddedComplexity
IncrementalEdgePerComplexity
Coverage
Data_Missing_Rate
```

This prevents repository evolution from becoming undocumented intuition.

## 9. Experiment artifact layout

For A/B/C/D/E versions use:

```text
references/experiments/<track>/<version>/hypothesis.md
references/experiments/<track>/<version>/data-contract.md
references/experiments/<track>/<version>/frozen-config.json
references/experiments/<track>/<version>/result.md
```

A completed frozen config is immutable. A material parameter/feature change starts a new version.

## 10. Stop conditions for iteration

Pause feature expansion and return to data/governance review if any occurs:

- point-in-time violations;
- missing event timestamps at material scale;
- repeated parameter changes mid-cohort;
- unexplained discrepancies between research and simulated execution;
- increasing rule-violation rate;
- apparent edge driven by a few names/events;
- costs/slippage erase the gross edge;
- too many unresolved data fields to reproduce results;
- independent tracks are combined before attribution is established.

## 11. Definition of an accepted iteration outcome

An iteration does not have to increase gross return.

Evidence may support retention when it measurably:

- increases net expectancy;
- reduces drawdown/tail loss;
- reduces false positives while disclosing false negatives;
- reduces rule violations;
- reduces turnover/cost drag;
- improves point-in-time reproducibility;
- removes a non-incremental feature;
- identifies a regime-limited effect and conditions it explicitly.

The guiding principle is:

```text
More evidence, fewer stories.
More robustness, fewer parameters.
More auditability, less hindsight.
```

## 12. Current status

As of `2026-08-28`:

```text
Skill = v1.7.0
Champion = ACTIVE
Causal Challenger v1.1 = SHADOW ONLY
ERG v1 = SHADOW ONLY
Session-aware execution contract = ACTIVE
Statistical Promotion Guard = ACTIVE GOVERNANCE SUPPORT
public synthetic Forward-cohort fixture = SCHEMA TEST ONLY
Disagreement Ledger / Negative Control = ACTIVE
Track D0 = STARTED
Tracks A/B/C/E = PROPOSED
```

No repository-specific alpha claim is considered proven until the forward/promotion process says so.
