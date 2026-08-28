# Short/Mid Relative Performance Contract v1

Status: `ACTIVE SHORT/MID RESEARCH INFRASTRUCTURE CONTRACT`

This contract defines deterministic relative-performance calculations between one adjusted A-share price series and one benchmark series that has already been selected under a frozen benchmark-selection contract.

It does not select the benchmark and does not promote any signal to Champion or ERG.

## 1. Strategy boundary

This implementation is explicitly tactical:

```text
strategy_id = a_share_short_mid
sleeve      = short_mid
```

Invocation with the long-term sleeve must fail closed.

The long-term retirement engine may use shared benchmark facts, but this Short/Mid relative-performance artifact and its tactical windows do not automatically become long-term inputs.

## 2. Required inputs

```text
AdjustmentSeries
BenchmarkSeries
benchmark_selection_contract_id
benchmark_role
explicit diagnostic windows, optional
```

The stock side must be based on the deterministic corporate-action-adjusted research series. The benchmark side must have its own keyed dataset-coverage proof.

## 3. Benchmark selection is external

```text
RelativePerformanceBuilder
!= BenchmarkSelector
```

The builder must never silently change:

```text
primary benchmark
sector benchmark
peer benchmark
```

If a requested benchmark is unavailable, the operation fails rather than substituting another series.

The output always carries:

```text
benchmark_id
benchmark_role
benchmark_selection_contract_id
benchmark_series_id
```

## 4. Exact date alignment

v1 requires:

```text
stock adjusted dates == benchmark dates
```

exactly.

No intersection-only calculation is allowed because silently dropping missing dates can alter cumulative performance and event-window interpretation.

If either side is missing a date:

```text
FAIL CLOSED
```

## 5. Daily abnormal return

For aligned session `t`:

```text
stock_return_1d(t)
= stock_adjusted_close(t) / stock_adjusted_close(t-1) - 1

benchmark_return_1d(t)
= benchmark_close(t) / benchmark_close(t-1) - 1

abnormal_return_1d(t)
= stock_return_1d(t) - benchmark_return_1d(t)
```

This is a simple market-model-free abnormal-return definition. It is not a beta-adjusted CAPM residual or factor-model alpha.

## 6. Explicit diagnostic windows

Windows are never selected after observing the result.

The caller may supply explicit session counts such as:

```text
1
5
20
```

but these values become part of the content-addressed result. The builder has no hidden default tactical window.

For an N-session window ending on the latest aligned date:

```text
stock_return
benchmark_return
excess_return = stock_return - benchmark_return
cumulative_abnormal_return = sum(daily abnormal returns)
```

If requested history is insufficient:

```text
FAIL CLOSED
```

Formal event-family Primary Reaction Windows remain governed separately by the existing benchmark/reaction-window contract. Diagnostic windows do not become the Primary Reaction Window merely because they are available.

## 7. Cumulative abnormal return vs excess compounded return

The output keeps both concepts separate:

```text
excess_return
= compounded stock window return - compounded benchmark window return

cumulative_abnormal_return
= sum(stock daily return - benchmark daily return)
```

They are related but not numerically identical in general.

## 8. Lineage

Every output carries:

```text
adjustment_series_id
benchmark_series_id
benchmark_id
benchmark_selection_contract_id
```

and the final artifact is content-addressed:

```text
relative_performance_id
= SHA256(canonical output payload)
```

Changing the benchmark-selection contract, benchmark, window set or input series changes the identity.

## 9. No interpretation/promotion

This module calculates evidence only.

It does not decide:

```text
Market confirms
Prepricing is high
Reaction is positive
Research State = CONFIRMED
Champion technical score
Position State
Order size
```

Those are downstream research/model decisions.

## 10. Next use

The intended next layer is event-aware research:

```text
RelativePerformanceSeries
+ frozen event timestamp / first tradable timestamp
+ frozen reaction-window contract
↓
Prepricing / Reaction Metrics
↓
ERG Shadow Engine
```

## 11. Governance unchanged

```text
Short/Mid Champion = unchanged
ERG                = SHADOW ONLY
Long-term logic    = unchanged
AUTO_ORDER         = false
Alpha              = NOT_PROVEN
```
