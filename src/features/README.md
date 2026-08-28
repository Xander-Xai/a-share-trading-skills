# Feature / Measurement Layer

`src/features/` converts canonical PIT-valid facts into deterministic research measurements and Shadow research evidence.

It is not an order engine and is not the source of shared policy.

## Current Short/Mid path

```text
PIT Data Snapshot
↓
ShortMidMarketFeatureBuilder
↓
FeatureSnapshot

PIT Data Snapshot
↓
AdjustmentFactorBuilder
+ BenchmarkSeriesBuilder
↓
RelativePerformanceBuilder
↓
EventReactionMeasurementBuilder
↓
ERG Evidence Bundle
↓
ERG Shadow State Machine v0
```

## Modules

```text
snapshot.py
→ content-addressed feature snapshots

short_mid_market.py
→ low-subjectivity tactical market features

short_mid_verified.py
→ production-facing coverage-resolved short/mid wrapper

relative_performance.py
→ adjusted stock vs preselected benchmark
→ daily abnormal returns + explicit diagnostic windows

event_reaction.py
→ PIT event clock + explicit prepricing/reaction windows
→ first-full-session daily-bar measurement

erg_shadow.py
→ structured Eligibility / Expectation / Surprise / Materiality / Prepricing / Reaction evidence
→ content-addressed ERG evidence bundle
→ conservative Shadow research-state resolver
→ never changes position state or authorizes execution
```

## Strategy boundary

The current market/relative/event/ERG modules are tactical and must enforce:

```text
a_share_short_mid / short_mid
```

Shared upstream facts such as:

```text
DailyBar
CorporateAction
TradingSession
Benchmark data
Adjustment factors
```

may be used by both stock sleeves.

But current tactical measurements such as:

```text
MA / RVOL
5/10/20-session momentum
relative-performance windows
prepricing CAR
post-event reaction windows
ERG evidence/state transitions
```

do not automatically enter:

```text
a_share_long_retirement / long
```

The long-term engine requires separate Quality / Cash Flow / Dividend / Expected IRR / Valuation contracts.

## Measurement != decision

```text
feature available
!= Champion points

positive abnormal return
!= market confirmation

strong reaction
!= entry permission

ERG evidence
!= ERG Research State

ERG Research State
!= Position State

ERG CONFIRMED
!= order authorization
```

The current v0 ERG state machine always emits:

```text
position_state = FLAT
executable = false
```

Downstream model/state code must preserve these separations.
