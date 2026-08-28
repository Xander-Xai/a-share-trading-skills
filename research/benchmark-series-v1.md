# Benchmark Series v1 Research Note

Status: `IMPLEMENTED / DATA INFRASTRUCTURE`

## Purpose

Create a canonical benchmark time-series layer before implementing Relative Strength or ERG abnormal-return logic.

## Why this is separate from benchmark selection

The repository already recognized benchmark selection as a source of researcher freedom.

This implementation therefore separates:

```text
benchmark data correctness
```

from:

```text
benchmark selection policy
```

`BenchmarkSeriesBuilder` only builds the benchmark explicitly requested by `benchmark_id`. It never chooses or substitutes a benchmark.

## Implemented

### Canonical entities

```text
BENCHMARK_MASTER
BENCHMARK_DAILY_BAR
```

### Keyed dataset coverage

`DATASET_COVERAGE` gains an optional:

```text
dataset_key
```

For benchmark bars:

```text
dataset_family = BENCHMARK_DAILY_BAR
dataset_key    = benchmark_id
```

This prevents one complete benchmark series from accidentally proving completeness for another.

Existing unkeyed coverage record ids remain backward compatible.

### Deterministic benchmark series

`src/data/benchmarks.py` produces:

```text
benchmark_series_id
coverage_ref
close series
1-day returns
source-record lineage
```

### Runtime

```text
runtime/build_benchmark_series.py
```

builds a requested benchmark from a PIT snapshot.

## Explicit non-goals

This version does not decide:

```text
primary broad benchmark
sector benchmark
peer basket
benchmark fallback
```

It also does not yet calculate:

```text
Relative Strength
Abnormal Return
CAR
ERG Reaction
```

## Next implementation step

```text
Adjusted Stock Series
+ Frozen Benchmark Series
↓
Relative Performance / Abnormal Return Engine
```

That later engine must carry the exact benchmark id and benchmark-series identity into its output.

## Governance unchanged

```text
Short/Mid Champion = unchanged
ERG                = SHADOW ONLY
Long-term logic    = unchanged
AUTO_ORDER         = false
Alpha              = NOT_PROVEN
```
