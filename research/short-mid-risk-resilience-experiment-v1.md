# Short/Mid Risk-Resilience Experiment Protocol v1

> Status: `ACTIVE RESEARCH PROTOCOL / SHADOW ONLY`
>
> Purpose: validate the hypotheses abstracted from the 600699 retrospective review, blind replay and theoretical adversarial audit without changing production Champion or risk caps.
>
> Active governance layer: `skills/a-share-short-midterm-stock-selection/references/risk-resilience-layer.md`.

## 1. Why this experiment exists

The repository already controls planned risk, portfolio heat, execution constraints and holding state, but the 600699 review exposed a missing empirical question:

```text
How should the system behave when an initially reasonable setup fails to produce expected right-side confirmation?
```

This protocol tests whether additional resilience diagnostics improve tail risk or decision quality after costs.

It does not assume that the 600699 outcome proves any rule.

## 2. Frozen research family

```text
research_family_id = SHORT_MID_RISK_RESILIENCE_V1
status = SHADOW
production_effect = NONE
```

Material changes to feature definitions, windows, thresholds, benchmark, costs or outcome definitions create a new experiment version and increment the trial ledger.

## 3. Baseline

Use the current production architecture as baseline:

```text
Champion
+ current Entry Quality Gate
+ current shared capital/risk policy
+ current holding state machine
+ current A-share execution assumptions
```

The resilience Challenger may block/reduce hypothetical risk in research simulations, but it cannot create a production entry that Champion does not already permit.

## 4. Track R1 — Early Follow-through

### Hypothesis

Weak early price progress plus deteriorating relative strength after entry may identify a subset of false-positive setups before full structural invalidation.

### Candidate features

```text
MFE_3d
MFE_5d
MAE_3d
MAE_5d
RS_3d
RS_5d
RVOL_3d
RVOL_5d
price_progress_per_RVOL
breakout_hold
retest_success
```

### Important boundary

`3d` and `5d` are candidate research windows, not assumed optimal values.

### Outcomes

```text
future_MFE_R
future_MAE_R
realized_R_under_baseline
realized_R_under_candidate_review
stop_out_rate
large_MAE_rate
blocked_MFE
confirmation_delay_cost
```

### Primary question

Does a frozen early-review rule reduce tail loss or false positives without blocking too much upside?

## 5. Track R2 — Volume / Price Efficiency

### Hypothesis

Volume is more useful when interpreted jointly with price progress than as a monotonic bullish variable.

Candidate family:

```text
signed_price_progress / RVOL
absolute_price_progress / RVOL
close_location_value x RVOL
relative_return x turnover_percentile
```

Do not choose the best formula after seeing the final test set.

### Adversarial control

Compare against:

```text
RVOL alone
turnover alone
price return alone
random/placebo thresholds
```

### Metrics

```text
Delta_Expectancy_R
Delta_CVaR95
Delta_MaxDD
false_positive_delta
false_negative_delta
turnover_delta
cost_drag_delta
```

## 6. Track R3 — Stress-aware Sizing

### Hypothesis

Sizing from planned stop distance alone may understate A-share execution tail risk when gaps, limits or delayed exits are material.

For every eligible historical/Paper signal, construct:

```text
S0 = planned invalidation fill
S1 = adverse gap beyond invalidation
S2 = historical adverse-gap tail estimate when PIT-valid
S3 = limit-constrained / delayed-exit scenario where applicable
```

Candidate research outputs:

```text
planned_loss_R
stress_loss_R_S1
stress_loss_R_S2
stress_loss_R_S3
size_reduction_required_to_fit_policy
trade_rejection_state
```

### Promotion logic

This is primarily a risk-reduction hypothesis. It must improve tail metrics such as CVaR / p95 single-trade loss without destroying baseline expectancy or coverage beyond frozen tolerances.

Exact stress multipliers are not production parameters until validated.

## 7. Track R4 — Holding Inertia / Cost Anchoring

### Hypothesis

Positions held beyond the original thesis window may exhibit worse risk-adjusted outcomes when HOLD decisions are driven by being below cost rather than fresh evidence.

Required data:

```text
original_strategy_type
original_horizon
entry_cost
current_price
fresh_score_at_review
fresh_thesis_state
position_state
reunderwriting_completed
manual_override_reason
holding_days
```

Diagnostic labels:

```text
EVIDENCE_BASED_HOLD
COST_ANCHORED_HOLD_CANDIDATE
HORIZON_DRIFT
STRATEGY_TYPE_DRIFT
REUNDERWRITTEN_EXTENSION
```

Do not infer trader psychology from price alone. A cost-anchoring label requires an explicit decision record or user-confirmed reason.

Metrics:

```text
post_review_Expectancy_R
post_review_MAE_R
recovery_probability_when_calibrated
opportunity_cost
holding_horizon_breach_rate
```

## 8. Track R5 — Conditional Path Calibration

### Objective

Eventually replace qualitative path language with empirical probabilities **only if** adequate frozen data exists.

Candidate states:

```text
CONTINUATION_CONFIRMED
NEUTRAL_NO_FOLLOW_THROUGH
FAILURE / INVALIDATION
```

Probability output is prohibited until the calibration contract declares:

```text
universe
signal definition
state definition
forecast horizon
benchmark
cost model
sample size
regime segmentation
confidence interval method
validation split
untouched forward status
```

Until then the production/user-facing representation remains conditional paths without numeric probabilities.

## 9. Common experiment contract

All R1–R5 comparisons must preserve:

```text
same PIT universe
same information timestamps
same corporate-action treatment
same T+1 / limit / suspension assumptions
same transaction costs
same slippage assumptions
same baseline risk policy
same benchmark definition
same outcome horizon within a cohort
```

If any of these changes, close the old cohort and create a new experiment version.

## 10. Required segmentation

At minimum report by:

```text
Champion score bucket
setup_type
market_regime
sector_regime
confirmation_basis
entry_extension_bucket
liquidity bucket
position-size bucket
winner/loser
holding_days
```

Do not pool semantically different setups solely to increase N.

## 11. Core metrics

```text
Expectancy_R
Profit_Factor
Median_R
MaxDD
CVaR95
p95_single_trade_loss_R
MFE_R
MAE_R
MFE_capture
false_positive_rate
false_negative_rate
blocked_MFE
confirmation_delay_cost
turnover
cost_drag
coverage
PIT_error_rate
rule_violation_rate
```

For risk filters, report both protected downside and blocked upside.

## 12. Anti-overfitting requirements

Use `statistical-promotion-guard.md`.

For each feature/window family preserve:

```text
number_of_trials
parameter_grid
selection_rule
primary_metric
secondary_metrics
parameter_stability
untouched_test_status
DSR / PBO when feasible
```

Desired evidence:

```text
broad plateau
not
single narrow parameter spike
```

## 13. Negative controls

At minimum include:

```text
randomized review-day placebo
random pivot offsets
RVOL-only control
return-only control
no-follow-through label with shuffled outcomes
```

Purpose: detect whether apparent improvement comes from researcher freedom or generic market-state effects.

## 14. Promotion / rejection

Possible outcomes by track:

```text
KEEP_SHADOW
REVISE_AND_RESTART
PROMOTION_REVIEW_CANDIDATE
REJECT_COMPONENT
```

No component may promote itself.

Promotion requires:

```text
PIT-valid evidence
cost-aware improvement
robustness across nearby parameters
acceptable coverage
no hidden increase in execution risk
untouched forward evidence
statistical review
human Promotion Review
```

## 15. Relationship to 600699

The 600699 records are seed cases, not proof:

- `skills/a-share-short-midterm-stock-selection/examples/2026-08-05-600699-retrospective-live-sample.json`
- `skills/a-share-short-midterm-stock-selection/examples/2026-08-05-600699-blind-replay-frozen.md`
- `skills/a-share-short-midterm-stock-selection/examples/2026-08-05-600699-blind-replay-frozen.json`
- `skills/a-share-short-midterm-stock-selection/examples/2026-08-29-600699-position-review.md`

The blind replay may validate process/PIT discipline but is not untouched forward alpha evidence.

## 16. Final research rule

```text
A risk-resilience idea earns production status only if it improves survival / tail risk / process quality
without hiding unacceptable opportunity cost or relying on hindsight-selected parameters.
```
