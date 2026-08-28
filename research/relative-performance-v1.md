# Relative Performance / Abnormal Return v1

Status: `IMPLEMENTED / SHORT_MID RESEARCH INFRASTRUCTURE`

## Purpose

Build the first deterministic bridge from corrected stock prices and frozen benchmark data into ERG-relevant market evidence.

```text
Adjusted Stock Series
+ Benchmark Series
+ Benchmark Selection Contract
↓
Daily Relative Performance
↓
Explicit Window Diagnostics
```

## Implemented

`src/features/relative_performance.py` adds:

```text
RelativePerformanceBuilder
RelativePerformancePoint
WindowPerformance
RelativePerformanceSeries
```

### Daily metrics

```text
stock_return_1d
benchmark_return_1d
abnormal_return_1d
```

### Explicit windows

Optional windows are caller supplied, validated, sorted and stored in the result identity.

For each requested N-session diagnostic:

```text
stock_return
benchmark_return
excess_return
cumulative_abnormal_return
```

There is intentionally no hidden default window.

## Anti-snooping controls

The implementation does not choose a benchmark or reaction window.

It requires:

```text
benchmark_selection_contract_id
```

and exact stock/benchmark date alignment.

Therefore:

```text
missing benchmark date
→ fail closed

insufficient requested window history
→ fail closed

long strategy context
→ fail closed
```

## Interpretation boundary

The daily abnormal return is:

```text
stock_return - benchmark_return
```

It is not claimed to be:

```text
factor-model alpha
CAPM residual
causal event effect
trading alpha
```

Those require additional hypotheses and validation.

## Why this is Short/Mid-only

Current use is tactical:

```text
relative strength
prepricing
post-event reaction
ERG
```

The underlying adjusted prices and benchmark facts are shared infrastructure, but this artifact is tagged:

```text
a_share_short_mid / short_mid
```

so tactical 1/5/20-session reasoning cannot silently enter the long-term retirement engine.

## Runtime

`runtime/build_relative_performance.py` builds stock adjustment, benchmark series and relative performance from one PIT snapshot and an explicit benchmark contract id.

## Tests

The initial test suite covers:

```text
daily abnormal return
explicit window metrics
deterministic identity
selection-contract identity sensitivity
long-sleeve rejection
insufficient-history rejection
exact date alignment
required selection contract
duplicate window rejection
```

## Next step

Do not jump directly to ERG state changes.

The next machine layer should use the existing event/PIT contracts to separate:

```text
Prepricing Window
Event Reaction Window
```

with windows frozen before outcomes.

That layer can then feed ERG Shadow without changing Champion.

## Governance unchanged

```text
Short/Mid Champion = unchanged
ERG                = SHADOW ONLY
Long-term logic    = unchanged
AUTO_ORDER         = false
Alpha              = NOT_PROVEN
```
