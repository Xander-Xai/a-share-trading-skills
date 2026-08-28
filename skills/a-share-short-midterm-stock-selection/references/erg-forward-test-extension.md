# ERG Forward-Test Extension v1

> Applies to the existing Champion vs Challenger protocol.
>
> ERG remains part of the Challenger shadow path. This file adds ERG-specific fields and ablations without changing shared capital/risk rules.

## 1. Frozen ERG fields

Before each cohort, freeze:

```text
erg_version
expectation_source_policy
expectation_confidence_rules
surprise_definition
materiality_definition
prepricing_windows
reaction_windows
benchmark_selection_policy
research_state_rules
strategy_type_rules
```

Any material change starts a new cohort/version.

## 2. Signal ledger additions

For event-driven candidates preserve:

```text
information_timestamp
first_tradable_timestamp
source_tier
expectation_baseline_type
expectation_confidence
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
post_event_RVOL
research_state
position_state
strategy_type
```

`null/UNRESOLVED` is valid. Fabricated values are not.

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

For each level report the same cost/risk assumptions.

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
```

The goal is not to maximize confirmation count. A higher `no_trade_rate` can be desirable if expectancy and tail risk improve after cost.

## 6. Main performance metrics

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
```

## 7. Statistical promotion guard

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

## 8. Promotion interpretation

ERG can only be considered for Champion promotion if its incremental modules demonstrate useful out-of-sample discrimination or risk improvement after costs.

Possible conclusions:

```text
PROMOTE_ERG_COMPONENTS
KEEP_SHADOW
REMOVE_NONVALUE_COMPONENTS
REVISE_AND_RESTART
```

Promotion may be partial. For example, `Prepricing` can be retained while a noisy expectation source is removed.
