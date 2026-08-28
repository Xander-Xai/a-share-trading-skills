# Disagreement Ledger & Negative-Control Protocol v1

> Status: `ACTIVE VALIDATION INFRASTRUCTURE`
>
> Purpose: measure whether the ERG/Causal Challenger contributes incremental information beyond the current Champion, rather than merely restating the same inputs in different language.

## 1. Why disagreement is first-class data

Champion and Challenger share part of the same underlying information. Agreement therefore cannot be treated as independent confirmation.

The most informative cases for model comparison are:

```text
Champion executable / Challenger not executable
Champion not executable / Challenger confirmed
material rank displacement
different invalidation logic
different event interpretation
different timing due to PIT/session rules
```

Every material disagreement must be preserved before outcomes are observed.

## 2. Required disagreement ledger

For every locked-universe stock and decision timestamp record:

```text
as_of
stock_code
stock_name
champion_score
champion_status
champion_rank
challenger_score
challenger_status
challenger_rank
research_state
position_state
strategy_type
confirmation_basis
champion_action
challenger_shadow_action
disagreement_type
disagreement_reason
entry_trigger_champion
entry_trigger_challenger
invalidation_champion
invalidation_challenger
planned_RR_champion
planned_RR_challenger
```

Allowed disagreement types:

```text
NONE
RANK_ONLY
ELIGIBILITY
EVENT_INTERPRETATION
REACTION_INTERPRETATION
EXECUTION_TIMING
ENTRY_GEOMETRY
RISK_BUDGET
STRATEGY_TYPE
DATA_CONFIDENCE
OTHER
```

## 3. Outcome fields

Outcomes are appended later; original decision fields are immutable.

For each horizon preserve, where applicable:

```text
forward_return_1d
forward_return_3d
forward_return_5d
forward_return_10d
forward_return_20d
benchmark_excess_1d
benchmark_excess_3d
benchmark_excess_5d
benchmark_excess_10d
benchmark_excess_20d
MFE_R_5d
MAE_R_5d
MFE_R_10d
MAE_R_10d
MFE_R_20d
MAE_R_20d
simulated_realized_R
rule_violation
```

Do not overwrite the original state after observing later data.

## 4. Primary disagreement metrics

For a frozen cohort compare:

```text
Disagreement Rate
= material disagreement records / all comparable records

Challenger Correction Rate
= cases where Challenger avoids a Champion false positive
  / Champion false positives in disagreement set

Challenger Miss Rate
= cases where Challenger blocks a Champion opportunity that later meets success criteria
  / blocked Champion opportunities

Net Disagreement Expectancy Delta
= expectancy_R(Challenger shadow decisions)
  - expectancy_R(Champion decisions)
  within disagreement cases

Tail-loss Delta
= tail loss metric Challenger - Champion
```

Predefine the success/failure outcome rule for each strategy family before scoring the cohort.

## 5. Confirmation-basis field

To prevent semantic mixing, every `CONFIRMED` research state must declare:

```text
EVENT_REACTION
TREND_STRUCTURE
REGIME_RELATIVE_STRENGTH
MEAN_REVERSION_SETUP
MULTI_EVIDENCE
OTHER_EXPERIMENTAL
```

A stock may be:

```text
research_state = CONFIRMED
confirmation_basis = TREND_STRUCTURE
```

without implying an earnings/event surprise has been confirmed.

## 6. Negative controls / placebo tests

ERG can appear useful merely because it re-labels generic momentum. To test event-specific increment, create placebo dates that should not contain the event information.

Minimum placebo families when historical data allows:

```text
P1: random non-event dates matched by stock and regime
P2: T-20 trading days from the actual event
P3: T+20 trading days from the actual event, excluding overlapping events
P4: same-sector matched dates with no company event
```

Apply the same reaction/relative-strength computation to placebo samples.

Primary diagnostic:

```text
Event Increment
= metric(actual-event sample) - metric(placebo-matched sample)
```

If ERG reaction variables perform similarly on placebo dates, the event-specific interpretation is not established.

## 7. Opportunity-cost accounting

A stricter gate can reduce false positives by refusing nearly every trade. Therefore track blocked-upside cost.

For every `NO_TRADE` / blocked candidate preserve:

```text
subsequent_MFE_pct_5d
subsequent_MFE_pct_10d
subsequent_MFE_pct_20d
subsequent_excess_return
```

Diagnostics:

```text
false_positive_avoided_rate
false_negative_rate
median_blocked_MFE
p90_blocked_MFE
confirmation_delay_cost
```

A lower trade count is not treated as improvement unless the cost/risk-adjusted outcome improves.

## 8. Confusion-matrix framing

For each strategy family define a frozen outcome criterion and summarize:

| Research decision | Outcome success | Outcome failure |
|---|---:|---:|
| CONFIRMED / executable | TP | FP |
| blocked / not executable | FN | TN |

Report:

```text
precision
false_positive_rate
false_negative_rate
coverage
no_trade_rate
expectancy_R
```

Classification metrics are secondary to cost-aware expectancy and drawdown; they exist to diagnose gate strictness.

## 9. Minimum sample handling

Do not claim stable subgroup effects from tiny buckets.

For every reported subgroup show:

```text
n_signals
n_trades
n_disagreements
confidence_interval_or_bootstrap_range_when_available
```

If the sample is insufficient, label the result `INSUFFICIENT_SAMPLE` rather than pooling incompatible event families solely to increase N.

## 10. Integration with existing protocols

Use together with:

- `champion-challenger-forward-test.md`;
- `erg-forward-test-extension.md`;
- `statistical-promotion-guard.md`;
- `iteration-roadmap.md`.

The Disagreement Ledger is diagnostic infrastructure. It does not change Champion production decisions until Promotion Review passes.

## 11. Promotion relevance

A Challenger component has evidence for incremental value only when the disagreement subset shows one or more measurable improvements after cost without an offsetting deterioration beyond the frozen risk tolerance, for example:

```text
positive Net Disagreement Expectancy Delta
and/or
lower tail loss / drawdown
and/or
lower rule-violation rate
```

while blocked-opportunity cost, turnover and model-selection risk are disclosed.

No fixed numeric promotion cutoff is asserted in v1; thresholds must be frozen before each formal promotion cohort.