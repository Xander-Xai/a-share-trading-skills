# Benchmark Data Contract v1

Status: `ACTIVE RESEARCH / DATA INFRASTRUCTURE CONTRACT`

This contract defines benchmark facts and benchmark-series completeness. It does **not** decide which benchmark is correct for a stock or event.

## 1. Separation of concerns

```text
Benchmark Data
!= Benchmark Selection
```

The data layer answers:

```text
What benchmark series exists?
Is it PIT-visible?
Is the requested date range complete?
What were the observed index levels/returns?
```

A frozen research contract must separately answer:

```text
Which primary benchmark applies?
Which sector benchmark applies?
Which peer basket applies?
Why was it selected before outcomes were observed?
```

This prevents benchmark choice from becoming post-outcome parameter fitting.

## 2. Canonical benchmark entities

### BENCHMARK_MASTER

```text
benchmark_id
benchmark_type
name
currency
taxonomy
methodology_version
```

Allowed benchmark types:

```text
BROAD_INDEX
SECTOR_INDEX
PEER_BASKET
CUSTOM
```

### BENCHMARK_DAILY_BAR

```text
benchmark_id
trade_date
open
high
low
close
prev_close
level_basis = INDEX_LEVEL
```

These are benchmark/index levels, not A-share security prices.

## 3. Dataset-keyed coverage

Generic scope alone is insufficient for benchmark data because many benchmark series share the same provider and date range.

Therefore `DATASET_COVERAGE` now supports:

```text
dataset_key
```

For benchmark bars:

```text
dataset_family = BENCHMARK_DAILY_BAR
dataset_key    = <benchmark_id>
```

A request for:

```text
benchmark_id = CSI300
```

cannot be proven complete by an unkeyed assertion or an assertion for another benchmark.

## 4. Backward compatibility

Existing unkeyed coverage identities remain unchanged.

```text
dataset_key = null
```

keeps the historical v1 `DATASET_COVERAGE` record id.

This avoids rewriting old PIT evidence merely to add benchmark support.

## 5. Accepted benchmark-series coverage methods

The initial machine contract accepts:

```text
OFFICIAL_INDEX_SERIES_RECONCILED
LICENSED_VENDOR_RECONCILED
OFFICIAL_VENDOR_RECONCILED
```

A raw row count without explicit completeness reconciliation is insufficient.

## 6. BenchmarkSeries

`BenchmarkSeriesBuilder` requires:

```text
>= 2 BENCHMARK_DAILY_BAR rows
+ exact benchmark_id match
+ confirmed keyed coverage for the whole observed date span
```

Output:

```text
benchmark_series_id
benchmark_id
start_date
end_date
coverage_ref
points[]
  trade_date
  close
  return_1d
  source_bar_ref
```

`benchmark_series_id` is a deterministic SHA-256 identity of the normalized output.

## 7. No silent benchmark substitution

If the requested benchmark is missing or incomplete:

```text
FAIL CLOSED
```

The builder must not automatically substitute:

```text
CSI300
→ SSE Composite
→ sector index
→ peer basket
```

because fallback choice changes the research hypothesis.

Fallback logic, if ever allowed, belongs in a separately frozen benchmark-selection contract.

## 8. Selection remains unresolved

This version intentionally does **not** encode rules such as:

```text
all SSE stocks → SSE Composite
all large caps → CSI300
all metals → a specific metals index
```

Those rules remain research parameters to be frozen and tested under Track A / Benchmark Contract governance.

## 9. Downstream use

After benchmark data is complete, later modules may derive:

```text
relative strength
abnormal return
CAR
prepricing
reaction
```

Those modules must retain:

```text
benchmark_id
benchmark_series_id
selection_contract_id
```

so a result cannot be detached from the benchmark actually used.

## 10. Strategy boundary

Benchmark facts are shared data infrastructure.

However, current short-horizon uses such as:

```text
5/20/60-session RS
ERG prepricing
D1/D3/D5 abnormal reaction
```

remain `short_mid` research unless a separate long-term contract defines a different use.

## 11. Governance unchanged

```text
Champion unchanged
ERG SHADOW ONLY
AUTO_ORDER=false
Alpha NOT_PROVEN
```
