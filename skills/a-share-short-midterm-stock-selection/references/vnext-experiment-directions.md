# VNext Parallel Experiment Directions v1

> Status: `ACTIVE RESEARCH DIRECTION CATALOG`
>
> Scope: future short/mid-term model iterations after Skill v1.7.0.
>
> This document defines independent Challenger research tracks. It does **not** change the current Champion, ERG Shadow status, shared capital rules, or order permissions.

## 1. Objective

Future repository changes must answer a measurable question:

```text
What specific failure mode is being targeted?
What data is required point-in-time?
What is the frozen baseline?
What metric must change?
What cost / risk / coverage deterioration is accepted?
What evidence rejects the hypothesis?
```

Do not create another full-methodology version merely because a new idea exists. New ideas enter as modules or experiment tracks, remain independently attributable, and are combined only after their incremental contribution is measured.

Current baseline:

```text
Champion = Technical 30 / Capital 30 / Fundamentals 25 / Catalyst 15
Causal Challenger v1.1 + ERG v1 = SHADOW ONLY
Skill = v1.7.0
Forward baseline = synthetic fixture for schema/process checks only; real cohorts are private
```

## 2. Common experiment contract

All A/B/C/D/E tracks must use the same comparison contract when they are compared against the same baseline cohort:

```text
same universe
same as_of / point-in-time information
same session-aware first_tradable_timestamp logic
same corporate-action treatment
same T+1 / price-limit / suspension rules
same transaction-cost assumptions
same slippage / impact assumptions
same position-sizing policy
same risk budget
same benchmark contract for the cohort
same evaluation horizons
same frozen outcome definition
```

No track may change the universe, benchmark, execution cost or evaluation window after observing results unless the old cohort is closed and a new version starts.

## 3. Common metric set

Every track reports at minimum:

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

Define:

```text
AddedComplexity
= Added_Fields
+ 2 * Added_External_Data_Sources
+ Added_Tunable_Parameters

IncrementalEdgePerComplexity
= Delta_Expectancy_R / max(1, AddedComplexity)
```

`IncrementalEdgePerComplexity` is an engineering comparison metric, not a return forecast.

## 4. Stage-1 screening thresholds

These are provisional governance parameters for the first comparison cycle. They are not claimed to be academically optimal. Freeze them before a formal cohort and do not move them after outcomes are observed.

For a return-oriented Challenger:

```text
Delta_Expectancy_R > 0
Coverage >= 70%
Delta_Cost_Drag <= +0.05R / trade
MaxDD_new <= 1.10 * MaxDD_baseline
CVaR95_new <= 1.05 * CVaR95_baseline
```

For a risk-reduction Challenger such as Track C:

```text
CVaR95_new < CVaR95_baseline
MaxDD_new <= MaxDD_baseline
```

If a track claims that stricter filtering reduces false positives, additionally report:

```text
relative_false_positive_reduction
false_negative_change_pp
median_blocked_MFE
p90_blocked_MFE
confirmation_delay_cost
```

Stage-1 diagnostic targets:

```text
relative_false_positive_reduction >= 15%
false_negative_change_pp <= +10pp
```

Failure to meet a Stage-1 target does not automatically delete the research family; it determines whether the next action is `REVISE`, `CONDITION`, `KEEP_SHADOW_WITHOUT_EXPANSION`, or `REMOVE_COMPONENT`.

## 5. Track A — ERG Precision

### A.1 Targeted failure modes

Current ERG can still contain researcher degrees of freedom in:

```text
benchmark selection
reaction-window selection
expectation-source selection
surprise scaling
prepricing interpretation
```

These choices can create hindsight bias even when the ERG causal order itself is fixed.

### A.2 Hypothesis

Freezing benchmark selection, event-family reaction windows and expectation confidence before outcomes are known will improve event-signal discrimination relative to current ERG without relying on post-event researcher choice.

### A.3 Proposed additions

Minimum fields:

```text
primary_benchmark
sector_benchmark
peer_benchmark
benchmark_selection_rule
primary_reaction_window
secondary_reaction_windows
expectation_coverage_flag
expectation_confidence
expectation_dispersion
surprise_normalization_method
prepricing_bucket
```

### A.4 Benchmark contract

For every cohort define before observing outcomes:

```text
primary_benchmark
sector_benchmark
peer_basket_rule
benchmark_fallback_rule
```

A later benchmark that produces a different abnormal return requires a new experiment version; it cannot overwrite the original cohort.

### A.5 Reaction-window contract

Each event family must eventually have one frozen primary reaction window and secondary diagnostic windows.

Example research layout only:

```text
EARNINGS: primary = to be estimated and frozen
ORDER_CONTRACT: primary = to be estimated and frozen
COMMODITY_PRODUCT_PRICE: primary = to be estimated and frozen
POLICY: primary = to be estimated and frozen
```

Do not inspect D1/D3/D5 results and then promote whichever window is largest.

### A.6 Expectation-coverage calibration

Measure:

```text
Expectation_Coverage
= events with reconstructable expectation baseline
/ all eligible events
```

Report expectancy separately for:

```text
HIGH
MEDIUM
LOW
NONE
```

`NONE` cannot be relabeled as a verified beat/miss.

### A.7 Primary experiment

Compare:

```text
A0 = current ERG v1
A1 = A0 + frozen benchmark contract
A2 = A1 + event-family primary reaction window
A3 = A2 + expectation coverage/confidence calibration
A4 = A3 + normalized prepricing buckets
```

### A.8 Primary metrics

```text
Delta_Expectancy_R
Event_Increment_vs_Placebo
False_Positive_Delta
False_Negative_Delta
Expectation_Coverage
Median_Blocked_MFE
P90_Blocked_MFE
```

### A.9 Rejection / redesign evidence

Examples:

```text
Event_Increment_vs_Placebo <= 0 across untouched cohorts
Coverage < 70% without a clearly defined coverage-limited universe
Delta_Expectancy_R <= 0 after costs
result depends on a single benchmark or narrow reaction window
blocked-opportunity cost offsets false-positive reduction
```

### A.10 Estimated engineering load

Repository planning estimate, not outcome evidence:

```text
new fields: ~8–12
new external data sources: 1–3 depending on expectation provider
PIT burden: medium-high
parameter-selection risk: medium-high
```

---

## 6. Track B — Conditional Participation

### B.1 Targeted failure mode

The current Champion allocates 60/100 points to Technical + Capital Participation. Generic trend/volume evidence may behave differently across ownership, participation and market regimes.

### B.2 Hypothesis

Relative strength and participation signals may have different expectancy conditional on positioning evidence and regime. Conditioning these signals may provide incremental discrimination relative to generic momentum/volume scoring.

### B.3 Evidence layers

Separate:

```text
Participation
= turnover / traded value / RVOL / liquidity / price progress

Positioning
= fund/shareholder disclosure / financing / disclosed seats / block trades / buyback

Vendor flow
= corroborative only, never equivalent to institutional positioning
```

### B.4 Candidate fields

```text
institutional_positioning_tier
institutional_ownership_bucket
financing_change_bucket
turnover_percentile
RVOL
price_progress_per_RVOL
relative_strength_20d
relative_strength_60d
regime
sector_relative_strength
positioning_data_timestamp
positioning_data_staleness_days
```

### B.5 Point-in-time restriction

Low-frequency ownership disclosures must use the publication timestamp that was actually available at the decision time. Later fund holdings cannot be backfilled into earlier decisions.

### B.6 Primary experiment

Start with buckets, not a fitted black-box model:

```text
B0 = current generic RS / participation logic
B1 = B0 stratified by positioning tier
B2 = B1 stratified by regime
B3 = B2 + interaction of RS x positioning x regime
```

Only after stable sample-out bucket effects exist may a calibrated model be tested.

### B.7 Primary metric

```text
Conditional_Momentum_Increment
= Expectancy_R(conditional signal)
- Expectancy_R(generic signal)
```

Also report:

```text
Expectancy_by_Regime
Expectancy_by_Positioning_Tier
Profit_Factor
MaxDD
CVaR95
Turnover
Cost_Drag
Coverage
Positioning_Data_Missing_Rate
```

### B.8 Rejection / redesign evidence

```text
conditional buckets show no sample-out separation
PIT ownership data coverage is insufficient for the intended universe
benefit disappears after stale-data controls
benefit is concentrated in one narrow regime without an explicit regime rule
added turnover/cost consumes the conditional increment
```

### B.9 Estimated engineering load

```text
new fields: ~10–15
new external data sources: 2–4
PIT burden: high
parameter-selection risk: high
```

---

## 7. Track C — Execution / Overreaction Shield

### C.1 Targeted failure modes

```text
late-stage chase
gap-through-stop
limit-hit overreaction
high-volume low-price-progress
post-event extension
suspension/resumption execution stress
```

This track is evaluated primarily as a tail-risk and execution-efficiency module.

### C.2 Hypothesis

Explicit extension, limit-hit, price-efficiency and gap-stress diagnostics can reduce tail loss and drawdown without creating excessive blocked-upside cost.

### C.3 Candidate fields

```text
upper_limit_hits_20d
upper_limit_hits_60d
limit_hit_density
days_since_last_limit_hit
gap_pct
gap_percentile_1y
distance_to_MA10_in_ATR
distance_to_recent_high
pre_event_AR20
RVOL
price_progress_per_RVOL
historical_gap_p95
stress_fill_price
stress_loss_R
```

### C.4 Price-efficiency diagnostic

Candidate research measure:

```text
PriceProgressPerRVOL
= absolute or signed price progress / max(RVOL, epsilon)
```

The exact numerator/window remains a research parameter and must be frozen per experiment version.

### C.5 Gap stress

For every planned trade simulate at least:

```text
S0 = planned invalidation fill
S1 = 1 ATR adverse gap beyond invalidation
S2 = historical p95 adverse overnight gap
S3 = price-limit constrained exit scenario where applicable
```

Record:

```text
stress_loss_R_S0
stress_loss_R_S1
stress_loss_R_S2
stress_loss_R_S3
```

### C.6 Primary experiment

```text
C0 = current execution gate
C1 = C0 + extension/gap filter
C2 = C1 + limit-hit density
C3 = C2 + price-progress-per-RVOL
C4 = C3 + gap-through-stop stress sizing/rejection
```

### C.7 Primary metrics

```text
Delta_CVaR95
Delta_Max_Drawdown
p95_single_trade_loss_R
gap_through_stop_rate
Delta_Expectancy_R
Median_Blocked_MFE
P90_Blocked_MFE
No_Trade_Rate
```

### C.8 Rejection / redesign evidence

```text
CVaR95 does not decline on untouched cohorts
MaxDD does not decline while trade count materially collapses
blocked MFE shows persistent large opportunity cost
filter adds no information beyond current extension penalty
stress model depends on one narrow ATR/gap parameter
```

### C.9 Estimated engineering load

```text
new fields: ~8–12
new external data sources: 0–1
PIT burden: medium
parameter-selection risk: medium
```

---

## 8. Track D — Disagreement Arbitration

### D.1 Targeted failure mode

Champion and ERG share inputs, so agreement is not independent evidence. The incremental information is more visible in cases where they disagree.

### D.2 Hypothesis

Certain disagreement types may systematically identify false positives, missed opportunities, timing errors or strategy-family mismatches. Measuring these cases can determine whether ERG contributes incremental decision value and where.

### D.3 Existing infrastructure

Use:

- `disagreement-ledger-and-negative-control.md`
- `champion-challenger-forward-test.md`
- `examples/synthetic-forward-cohort.*`

No new raw market feature is required for D0.

### D.4 Stages

```text
D0 = record disagreement only; no arbitration
D1 = frozen rule-based arbitration by disagreement type
D2 = calibrated meta-model only after enough untouched disagreement samples
```

D2 cannot start merely because a small in-sample classifier fits the existing ledger.

### D.5 Disagreement types

```text
RANK_ONLY
ELIGIBILITY
EVENT_INTERPRETATION
REACTION_INTERPRETATION
EXECUTION_TIMING
ENTRY_GEOMETRY
RISK_BUDGET
STRATEGY_TYPE
DATA_CONFIDENCE
```

### D.6 Primary metrics

```text
Disagreement_Rate
Challenger_Correction_Rate
Challenger_Miss_Rate
Net_Disagreement_Expectancy_Delta
Tail_Loss_Delta
Confirmation_Delay_Cost
Median_Blocked_MFE
P90_Blocked_MFE
```

Primary metric:

```text
Net_Disagreement_Expectancy_Delta
= Expectancy_R(Challenger shadow decisions)
- Expectancy_R(Champion decisions)
within disagreement cases
```

### D.7 Minimum sample discipline

Every disagreement subtype must report:

```text
n_records
n_executable_signals
n_outcomes
bootstrap_interval_when_available
```

Label `INSUFFICIENT_SAMPLE` rather than pooling semantically unrelated disagreement types solely to increase N.

### D.8 Rejection / redesign evidence

```text
Net_Disagreement_Expectancy_Delta <= 0 on untouched cohorts
a claimed correction rate is offset by larger Challenger miss rate
differences disappear after matching risk/execution assumptions
subtype effect exists only in a handful of names/events
```

### D.9 Estimated engineering load

```text
new raw market fields: ~0
new external data sources: 0
PIT burden: low beyond existing ledger discipline
sample-acquisition burden: high because disagreement must occur naturally
parameter-selection risk: low-to-medium for D0/D1, higher for D2
```

---

## 9. Track E — Champion Simplification

### E.1 Targeted failure mode

The current Champion may contain overlapping or weakly incremental scoring components. Repeated feature addition can increase model-selection risk, data requirements and maintenance cost.

### E.2 Hypothesis

Removing or consolidating non-incremental components may preserve or improve sample-out expectancy/risk while reducing data dependence, tunable parameters and interpretive ambiguity.

### E.3 Candidate ablations

Test independently:

```text
E1 = remove vendor-flow contribution
E2 = remove/reduce redundant MA/technical subfeatures
E3 = consolidate Technical + Capital into RS + Participation + Execution
E4 = use Fundamentals only as eligibility gate, not compensatory score
E5 = replace generic Catalyst score with ERG event state in Shadow comparison
```

Do not apply E1–E5 simultaneously in the first attribution round.

### E.4 Marginal-value definition

For each component i:

```text
MarginalValue_i
= Metric_full - Metric_without_i
```

Report at minimum:

```text
Delta_Expectancy_R
Delta_MaxDD
Delta_CVaR95
Delta_Turnover
Delta_Cost_Drag
Coverage
Data_Missing_Rate
Feature_Count_Delta
Added_or_Removed_Tunable_Parameters
```

### E.5 Complexity efficiency

```text
EdgePerFeature
= Expectancy_R / max(1, active_feature_count)

IncrementalEdgePerFeature
= Delta_Expectancy_R / max(1, absolute_feature_count_change)
```

These are engineering diagnostics, not standalone promotion rules.

### E.6 Primary experiment

```text
E0 = current Champion
E1/E2/E3/E4/E5 = one-at-a-time ablations
E6 = combine only ablations that independently survive untouched tests
```

### E.7 Rejection / redesign evidence

```text
removed component produces material sample-out expectancy loss
simplification increases tail loss beyond frozen tolerance
coverage gain is achieved at the cost of materially weaker discrimination
combined E6 loses the independent attribution observed in one-at-a-time tests
```

### E.8 Estimated engineering load

```text
new fields: 0–3
external data sources: typically unchanged or reduced
PIT burden: low-to-medium
parameter-selection risk: low relative to feature-expansion tracks, but multiple-ablation testing still requires trial accounting
```

---

## 10. Three research lanes

Do not force all tracks into one scalar ranking before their purpose is clear.

### Alpha / discrimination lane

```text
Track A — ERG Precision
Track B — Conditional Participation
Track D — Disagreement Arbitration
```

Primary emphasis:

```text
Delta_Expectancy_R
Event/Conditional Increment
False Positive / False Negative trade-off
```

### Tail-risk / execution lane

```text
Track C — Execution / Overreaction Shield
```

Primary emphasis:

```text
Delta_CVaR95
Delta_MaxDD
gap-through-stop loss
blocked-opportunity cost
```

### Complexity / maintenance lane

```text
Track E — Champion Simplification
```

Primary emphasis:

```text
IncrementalEdgePerComplexity
Coverage
Data_Missing_Rate
Feature_Count
```

Final selection uses hard risk/data gates first and Pareto comparison second.

## 11. Pareto comparison protocol

After each track has an untouched result set, classify outcomes on the following axes:

```text
Expectancy_R
MaxDD
CVaR95
Cost_Drag
Coverage
False_Positive_Rate
False_Negative_Rate
AddedComplexity
Rule_Violation_Rate
```

A track is Pareto-dominated when another track is at least as strong on all frozen comparison axes and strictly stronger on at least one, under the same experiment contract.

Do not compress all axes into one arbitrary 100-point enhancement score for promotion.

## 12. Implementation order

The order below is based on current repository readiness, not expected market return:

```text
1. D0 Disagreement measurement — infrastructure already active
2. C Execution/Overreaction data fields and stress tests
3. A ERG Precision benchmark/window contracts
4. E Champion one-at-a-time ablations
5. B Conditional Participation after PIT positioning data coverage is established
```

Rationale:

- D0 requires almost no new raw market data;
- C mainly depends on reproducible price/execution history;
- A requires expectation data and benchmark/window contracts;
- E requires a complete baseline replay environment;
- B has the largest PIT positioning-data burden.

## 13. Required experiment artifacts

Each track version must create:

```text
references/experiments/<track>/<version>/hypothesis.md
references/experiments/<track>/<version>/data-contract.md
references/experiments/<track>/<version>/frozen-config.json
references/experiments/<track>/<version>/result.md
```

Optional machine outputs:

```text
signal-ledger.csv/json
trade-ledger.csv/json
ablation-table.csv/json
parameter-stability.csv/json
placebo-results.csv/json
```

Do not overwrite a completed frozen-config. Parameter changes create a new version.

## 14. Experiment status vocabulary

Use only:

```text
PROPOSED
DATA_AUDIT
FROZEN
RUNNING
INSUFFICIENT_SAMPLE
KEEP_SHADOW_WITHOUT_EXPANSION
CONDITION
REVISE
REMOVE_COMPONENT
PROMOTION_REVIEW
PROMOTED_COMPONENT
```

Avoid free-form labels that cannot be mapped to a defined next action.

## 15. Promotion boundary

None of A/B/C/D/E is authorized to change production decisions by being listed here.

Required path remains:

```text
Hypothesis
→ Point-in-Time data audit
→ Frozen experiment
→ Historical / placebo / ablation where applicable
→ Untouched Forward
→ Statistical promotion guard
→ Human review
→ Partial component promotion when evidence supports it
```

A track may be retained for governance/reproducibility even when it does not increase return, but that reason must be stated separately from any alpha claim.

## 16. Current next actions

As of `2026-08-28`:

```text
D0 = STARTED through the active disagreement ledger
A = PROPOSED
B = PROPOSED
C = PROPOSED
E = PROPOSED
```

The public synthetic Forward-cohort fixture is not an empirical integration sample and cannot support track promotion. Private cohorts must preserve the same immutable-decision discipline.
