# Event Prepricing / Reaction Measurement v1

Status: `IMPLEMENTED / SHORT_MID RESEARCH INFRASTRUCTURE`

## Purpose

Take the next step from relative-performance evidence toward ERG without prematurely encoding an ERG state transition.

```text
PIT Event Clock
+ RelativePerformanceSeries
+ Frozen Reaction Window Contract
↓
Prepricing Metrics
+ Reaction Metrics
```

## Key design decision: daily bars cannot measure every first reaction

The repository now supports 2026 session-aware `first_tradable_timestamp`, including the possibility of same-day post-close fixed-price trading.

A normal daily bar is still anchored around the regular-session close. If information becomes tradable after the regular session begins, that daily bar contains pre-event price movement or may omit same-day post-close reaction.

Therefore v1 does not pretend otherwise.

It measures:

```text
first full regular daily-bar session on/after first tradable time
```

and records:

```text
partial_session_reaction_omitted = true
```

when an earlier partial/intraday/post-close reaction is not isolated.

This is deliberately more conservative than labeling the same day's close as post-event reaction when the information arrived later.

## Implemented

`src/features/event_reaction.py` adds:

```text
EventReactionMeasurementBuilder
EventReactionMeasurement
EventWindowMetric
```

Inputs include:

```text
event_id
event_family
information_timestamp
first_tradable_timestamp
reaction_window_contract_id
prepricing_windows
reaction_windows
optional frozen primary reaction window
```

The output keeps benchmark and relative-performance lineage.

## Prepricing semantics

An N-session prepricing metric ends immediately before the reaction anchor and therefore excludes the reaction session.

This is designed for later testing of the repository hypothesis:

```text
positive surprise
+ heavy pre-event run-up
may behave differently from
positive surprise
+ little pre-event pricing
```

No prepricing threshold or bucket is promoted in v1.

## Reaction semantics

An N-session reaction metric begins with the anchor session as reaction session 1.

For each window the engine records:

```text
stock_return
benchmark_return
excess_return
CAR
```

Primary windows remain unresolved unless supplied by an already-frozen contract.

## What v1 intentionally does not do

It does not:

```text
classify surprise
estimate materiality
set a Prepricing bucket
interpret reaction sign
set benchmark sensitivity
set window sensitivity
change Research State
change Position State
change Champion score
```

Those remain later layers.

## Runtime

`runtime/build_event_reaction.py` provides an end-to-end research path from one PIT snapshot:

```text
AdjustmentSeries
→ BenchmarkSeries
→ RelativePerformanceSeries
→ EventReactionMeasurement
```

with explicit benchmark and reaction-window contract IDs.

## Tests

Coverage includes:

```text
after-close → next full session anchor
before-open → same-day full session anchor
intraday → next full session anchor
prepricing excludes reaction anchor
primary window must be predeclared
resolved primary window status
information/tradable timestamp ordering
insufficient pre/post history fail-closed
long-sleeve rejection
deterministic identity
contract-id sensitivity
```

## Next step

After this measurement layer passes CI/merge, the next implementation should be an ERG evidence-state bridge rather than a production promotion:

```text
Expectation / Surprise evidence
Materiality evidence
Prepricing measurement
Reaction measurement
↓
ERG Shadow Evidence Bundle
```

The bundle should still allow:

```text
UNRESOLVED
```

for missing expectation or primary reaction windows.

## Governance unchanged

```text
Short/Mid Champion = unchanged
ERG                = SHADOW ONLY
Long-term logic    = unchanged
AUTO_ORDER         = false
Alpha              = NOT_PROVEN
```
