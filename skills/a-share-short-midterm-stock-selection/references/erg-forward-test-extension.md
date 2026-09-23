# ERG Forward-Test Extension v1.2

> Applies to the existing Champion vs Challenger protocol.
>
> ERG remains part of the Challenger shadow path. This file adds ERG-specific fields and ablations without changing shared capital/risk rules.

## 1. Frozen ERG fields

Before each new cohort, freeze:

```text
erg_version
expectation_source_policy
expectation_confidence_rules
surprise_definition
materiality_definition
prepricing_windows
benchmark_contract_version
reaction_window_contract_version
primary_reaction_window
secondary_reaction_windows
research_state_rules
confirmation_basis_rules
strategy_type_rules
session_rule_version
```

Any material change starts a new cohort/version.

Benchmark/window fields follow `benchmark-and-reaction-window-contract.md`.

A legacy cohort that predates the benchmark/window contract remains immutable and must not be retrofitted and relabeled as original forward evidence.

## 2. Signal ledger additions

For event-driven candidates preserve:

```text
information_timestamp
source_tier
exchange
board
session_rule_version
session_type
post_close_eligible
suspension_state_at_1500
broker_post_close_support
first_exchange_tradable_timestamp
first_broker_executable_timestamp
first_tradable_timestamp
first_tradable_resolution_status
benchmark_contract_version
primary_benchmark
sector_benchmark
peer_basket_rule
reaction_window_contract_version
primary_reaction_window
secondary_reaction_windows
expectation_baseline_type
expectation_confidence
expectation_coverage_flag
expectation_center
expectation_dispersion
surprise_direction
materiality_state
prepricing_state
pre_event_AR_5
pre_event_AR_20
reaction_state
overnight_AR
post_event_AR_1
post_event_AR_3
post_event_AR_5
abnormal_return_primary
abnormal_return_sector
abnormal_return_peer
benchmark_sensitivity
window_sensitivity
post_event_RVOL
research_state
confirmation_basis
position_state
strategy_type
planned_RR
```

`null/UNRESOLVED` is valid. Fabricated values are not.

Session fields follow `session-aware-execution-calendar.md`.

## 3. Required event-type breakdown

At minimum, separate when sample size allows:

```text
EARNINGS
EARNINGS_PREANNOUNCEMENT
ORDER_CONTRACT
COMMODITY_PRODUCT_PRICE
POLICY
CAPITAL_STRUCTURE
OTHER
```

Do not pool fundamentally different event families merely to increase sample size.

## 4. Ablation ladder

Run incrementally when data allows:

```text
A: Eligibility only
B: A + Expectation / Surprise
C: B + Economic Materiality
D: C + Prepricing
E: D + Post-event Reaction
F: E + Regime / Participation / Execution / Risk
```

For each level report the same cost/risk assumptions and the same frozen benchmark/window contract.

## 5. ERG-specific diagnostics

Compare:

```text
candidate_to_confirmed_rate
confirmed_to_entry_rate
positive_surprise_negative_reaction_rate
negative_surprise_positive_reaction_rate
priced_in_false_positive_rate
invalidated_after_entry_rate
no_trade_rate
expectation_coverage_rate
session_resolution_rate
benchmark_sensitive_rate
window_sensitive_rate
```

A lower trade count is not treated as improvement by itself. Compare blocked-opportunity cost and subsequent MFE of rejected/no-trade candidates.

## 6. Decision robustness diagnostics

Use `methodology-consolidation-and-validation-contract.md`.

Where repeated observations exist, preserve:

```text
rank_today
rank_5d_median
rank_dispersion_5d
research_state_changes_5d
position_state_changes_5d
champion_rank
challenger_rank
champion_challenger_rank_gap
champion_challenger_state_disagreement
```

These measure reproducibility/sensitivity only. They do not establish alpha.

## 7. Disagreement diagnostics

Use `disagreement-ledger-and-negative-control.md` and preserve:

```text
champion_action
challenger_shadow_action
disagreement_type
disagreement_reason
confirmation_basis
```

Primary diagnostics:

```text
disagreement_rate
challenger_correction_rate
challenger_miss_rate
net_disagreement_expectancy_delta
confirmation_delay_cost
median_blocked_MFE
p90_blocked_MFE
```

Agreement is not treated as independent model confirmation because Champion and Challenger share inputs.

## 8. Negative controls / placebo

When historical point-in-time data allows, compare actual event dates with matched placebo dates:

```text
random matched non-event dates
T-20 matched dates
T+20 non-overlap dates
same-sector non-event dates
```

Actual and placebo samples must use the same benchmark/window/session/cost contracts.

Report:

```text
event_increment_vs_placebo
```

If event-specific ERG variables show similar behavior on placebo dates, do not attribute the effect to event information without further evidence.

## 9. Main performance metrics

Reuse the repository standard metrics:

```text
Net Return
Excess Return
Expectancy_R
Profit Factor
Max Drawdown
Calmar
Win Rate
Avg Win_R
Avg Loss_R
Turnover
Cost Drag
MFE / MAE
Rule Violation Rate
```

Additionally compare:

```text
expectancy_by_event_type
expectancy_by_expectation_confidence
expectancy_by_prepricing_state
expectancy_by_reaction_state
expectancy_by_confirmation_basis
false_positive_rate
false_negative_rate
no_trade_opportunity_cost
benchmark_sensitivity_rate
window_sensitivity_rate
```

`planned_RR` remains entry geometry, not an alpha metric.

When sample size permits, estimate:

```text
E[R | event_type, research_state, confirmation_basis, regime, execution_state]
```

instead of treating a fixed minimum R/R as proof of edge.

## 10. Validation maturity

Use the three evidence levels in `methodology-consolidation-and-validation-contract.md`:

```text
Level A = Integration / Case Validation
Level B = Historical Point-in-Time Research Validation
Level C = Untouched Forward Validation
```

A component may pass Level A while remaining `PROMOTION_NOT_PROVEN`.

## 11. Statistical promotion guard

For each research family, preserve:

```text
number_of_trials
parameter_stability_summary
selection_bias_risk
DSR
PBO
reality_check_status
untouched_test_status
```

See `statistical-promotion-guard.md`.

No fixed DSR/PBO cutoff is hard-coded in this version. Missing diagnostics must be disclosed and generally keep a heavily tuned model in Shadow state.

## 12. First frozen Forward cohort

The public example is a synthetic immutable cohort fixture:

- `../examples/synthetic-forward-cohort.md`
- `../examples/synthetic-forward-cohort.json`

The baseline decision fields must not be rewritten after later prices are observed. Outcomes are appended at predefined horizons.

Because that cohort predates `benchmark-and-reaction-window-contract.md`, any newly computed benchmark/window diagnostics for it are supplemental post-hoc analysis unless explicitly versioned as a separate research artifact.

## 13. Promotion interpretation

ERG can only be considered for Champion promotion if its incremental modules demonstrate measurable out-of-sample discrimination or risk improvement after costs.

Possible conclusions:

```text
PROMOTE_ERG_COMPONENTS
KEEP_SHADOW
CONDITION_COMPONENT
REMOVE_NONVALUE_COMPONENTS
REVISE_AND_RESTART
```

Promotion may be partial. For example, `Prepricing` can be retained while a noisy expectation source is removed.
