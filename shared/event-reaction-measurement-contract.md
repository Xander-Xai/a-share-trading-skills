# Short/Mid Event Reaction Measurement Contract v1

Status: `ACTIVE SHORT/MID RESEARCH INFRASTRUCTURE CONTRACT`

This contract defines how PIT-valid event timestamps and a preselected benchmark are converted into daily-bar prepricing and reaction measurements.

It does not decide whether an event is positive/negative, material, confirmed, tradable, or worthy of a position.

## 1. Strategy boundary

This module is explicitly:

```text
strategy_id = a_share_short_mid
sleeve      = short_mid
```

The long-term retirement engine does not inherit event-reaction windows, prepricing CAR, or ERG-style tactical confirmation from this module.

## 2. Required lineage

Every measurement must preserve:

```text
event_id
event_family
information_timestamp
first_tradable_timestamp
reaction_window_contract_id
relative_performance_id
benchmark_id
benchmark_selection_contract_id
```

Therefore an event-reaction number cannot be detached from the information clock, benchmark contract or reaction-window contract that produced it.

## 3. Daily-bar measurement limitation

A daily close-to-close bar cannot cleanly isolate information that first became tradable after the regular session had already started.

Therefore v1 uses:

```text
measurement_basis
= DAILY_CLOSE_TO_CLOSE_FIRST_FULL_SESSION_V1
```

The full-session anchor is resolved deterministically:

```text
if first_tradable local time <= 09:30
and that date exists in the aligned series
→ anchor that trading date

otherwise
→ anchor the next aligned trading date
```

If the next full session is used:

```text
partial_session_reaction_omitted = true
```

This explicitly acknowledges that same-day intraday or 15:05–15:30 post-close fixed-price reaction may exist but is not isolated by the current daily-bar measurement.

A future intraday/session-price module may measure that omitted reaction separately. v1 must not fabricate it from the 15:00 daily close.

## 4. Information clock

Required:

```text
information_timestamp <= first_tradable_timestamp
```

Both timestamps must be timezone-aware.

`first_tradable_timestamp` remains governed by the session-aware execution contract. This module consumes that fact; it does not re-decide exchange/broker executability.

## 5. Prepricing windows

Prepricing windows are explicit positive integer session counts.

An N-session prepricing window:

```text
ends at the session immediately before the full-session reaction anchor
uses N close-to-close return intervals
excludes the reaction anchor session
```

Output:

```text
stock_return
benchmark_return
excess_return
cumulative_abnormal_return
```

No default prepricing window is hard-coded.

## 6. Reaction windows

An N-session reaction window:

```text
starts from the close immediately before the full-session anchor
includes the anchor session as reaction session 1
continues for N aligned trading sessions
```

Output:

```text
stock_return
benchmark_return
excess_return
cumulative_abnormal_return
```

No D1/D3/D5 value is promoted merely because it looks strongest.

## 7. Primary reaction window

The existing Benchmark & Reaction Window Contract currently leaves event-family primary windows unresolved until historical PIT research and untouched validation support a frozen choice.

Therefore v1 supports:

```text
primary_reaction_window_sessions = null
primary_window_status = UNRESOLVED_RESEARCH
```

When a future frozen contract supplies a primary window, it must already exist in the predeclared measured reaction-window set:

```text
primary_window_status = FROZEN_BY_CONTRACT
```

The measurement engine cannot promote an observed secondary window into the primary window after seeing outcomes.

## 8. Abnormal-return definition

The underlying daily measure remains:

```text
AR_t = stock_adjusted_return_t - benchmark_return_t
```

For a window:

```text
CAR = sum(AR_t)
```

and separately:

```text
excess_return
= compounded stock window return - compounded benchmark window return
```

This is not a factor-model alpha estimate or a causal attribution by itself.

## 9. Fail-closed conditions

Examples:

```text
first_tradable < information_timestamp
→ reject

no full daily session after first_tradable
→ reject

reaction anchor has no prior aligned close
→ reject

insufficient prepricing history
→ reject

insufficient reaction history
→ reject

primary window not predeclared
→ reject

long strategy context
→ reject
```

## 10. Output identity

`EventReactionMeasurement` is content-addressed:

```text
event_measurement_id
= SHA256(canonical measurement payload)
```

Changing any of these changes the identity:

```text
event timestamp
first tradable timestamp
benchmark contract
relative-performance input
window contract
window set
primary window
```

## 11. Relationship to ERG

This module supplies measurement evidence only.

```text
Prepricing Metrics
Reaction Metrics
```

must not automatically produce:

```text
ERG CONFIRMED
ERG INVALIDATED
Position READY
BUY / SELL
```

The next ERG Shadow layer must combine these measurements with Expectation, Surprise, Materiality and the existing Research-State governance.

## 12. Governance unchanged

```text
Short/Mid Champion = unchanged
ERG                = SHADOW ONLY
Long-term logic    = unchanged
AUTO_ORDER         = false
Alpha              = NOT_PROVEN
```
