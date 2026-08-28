# Statistical Promotion Guard v1

> Status: research/model-governance support module.
>
> Purpose: reduce the chance that a Challenger appears superior only because many variants, thresholds, windows or parameter combinations were tried and the best-looking result was selected after the fact.

## 1. Why this exists

Walk-forward testing is necessary but not sufficient if researchers repeatedly test many model families or parameters and only preserve the winners.

Therefore every material model experiment should preserve the selection path, not only the final backtest.

## 2. Trial Ledger

For each research family record:

```text
research_family_id
hypothesis
start_timestamp
end_timestamp
universe_definition
feature_family
parameter_grid
number_of_trials
selection_rule
primary_metric
secondary_metrics
researcher_notes
```

A material change to features, thresholds, holding period, stop/exit logic, benchmark or regime logic counts as a new trial/version.

Do not reset `number_of_trials` merely because the latest variant looks better.

## 3. Minimum anti-snooping checks

Before Promotion Review, ask:

- How many model/parameter variants were considered?
- Were losing/neutral variants preserved?
- Was the test window changed after results were seen?
- Were features added after inspecting the same validation set?
- Were thresholds tuned to a small number of memorable trades?
- Is the apparent edge robust to nearby parameter values?
- Does the edge persist by regime, factor and event type?

Any unresolved answer lowers confidence or forces `REVISE_AND_RESTART`.

## 4. Statistical diagnostics

When sample structure and tooling permit, calculate or estimate:

```text
Deflated Sharpe Ratio (DSR)
Probability of Backtest Overfitting (PBO)
```

A White/SPA-style reality-check family may also be used when many strategies are compared against the same benchmark.

These diagnostics are not magic pass/fail numbers. They are evidence about selection bias and multiple testing.

If implementation is unavailable, the model may remain in Shadow/Research state, but the missing diagnostic must be disclosed rather than silently treated as passed.

## 5. Parameter Stability

Promotion evidence should include local sensitivity around important parameters.

Examples:

```text
RS window: 10 / 20 / 30 days
RVOL lookback: 10 / 20 / 40 days
minimum RR: nearby values around the proposed threshold
holding review: nearby windows
```

Desired pattern:

```text
broad plateau of acceptable results
```

Undesired pattern:

```text
one narrow parameter spike surrounded by poor results
```

A narrow spike is an overfitting warning even if the headline Sharpe is high.

## 6. Nested selection discipline

When enough data exists, separate:

```text
train / research
→ validation / model selection
→ untouched test or forward period
```

Do not repeatedly inspect the final test period and continue tuning against it.

If the final test period has been used for iterative model selection, it is no longer untouched and must be relabeled.

## 7. Promotion report fields

Add to Challenger promotion reports:

```text
number_of_trials
parameter_stability_summary
selection_bias_risk
DSR
PBO
reality_check_status
untouched_test_status
```

Allowed values when unavailable:

```text
NOT_COMPUTED
INSUFFICIENT_SAMPLE
NOT_APPLICABLE
```

Never replace missing diagnostics with optimistic assumptions.

## 8. Decision guidance

Possible outcomes:

```text
PASS_STATISTICAL_REVIEW
KEEP_SHADOW
REVISE_AND_RESTART
REJECT
```

Statistical review never overrides execution, risk, point-in-time or cost failures.

Likewise, a low estimated overfitting risk does not prove economic causality or future profitability.

## 9. Complexity budget

A new feature/module should earn its complexity.

Before promotion ask:

```text
Does this feature improve out-of-sample discrimination or risk-adjusted expectancy?
Does it improve robustness across regimes?
Does it reduce tail risk or rule violations?
Is the gain large enough to justify new data dependencies and failure modes?
```

If not, prefer the simpler model.
