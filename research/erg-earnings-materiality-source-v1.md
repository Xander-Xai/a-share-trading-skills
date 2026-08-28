# ERG Earnings Materiality Source Producer v1

## Status

```text
IMPLEMENTED FOR SHADOW RESEARCH
ALPHA NOT PROVEN
NO ORDER AUTHORITY
```

## Why this layer exists

After source-backed Expectation / Surprise, the largest remaining manual ERG component for earnings events was Materiality.

A reported result can differ from expectation without materially changing normalized earnings power. Conversely, a large negative earnings deterioration can be economically material even though it is not a positive trade signal.

Therefore v1 keeps:

```text
Surprise direction
!= Materiality magnitude
```

## Data path

```text
Frozen PIT FINANCIAL_STATEMENT (current event)
+
Frozen PIT FINANCIAL_STATEMENT (pre-event comparable period)
+
Frozen EarningsMaterialityContract
        ↓
PITEarningsMaterialityProducer
        ↓
Diagnostics
        ↓
MaterialityEvidence
```

## Conservative decisions

### 1. No hidden default threshold

The default mode is:

```text
EVIDENCE_ONLY
→ state = UNRESOLVED
```

The system computes diagnostics without claiming that a particular percentage change is material.

### 2. Optional deterministic rule is explicit

`THRESHOLD_RULE_V1` is available only when the contract freezes thresholds before the result is interpreted.

Those values are governance/research parameters, not empirically optimal constants.

### 3. Low-base growth fails closed

If the comparable-period denominator is zero or below the frozen low-base floor, percentage-growth materiality remains `UNRESOLVED`.

### 4. Direction is not mixed into Materiality

Both +30% and -30% comparable-period earnings changes can be `MATERIAL` under the same magnitude rule.

Bullish/bearish interpretation remains in Surprise and later ERG state logic.

### 5. Cash flow is diagnostic in v1

Operating cash flow and cash-conversion ratios can be preserved, but v1 does not make them universal hard gates.

This avoids forcing manufacturing-company cash-flow semantics onto banks, brokers, insurers or other financial institutions.

## Supported diagnostics

The producer can compare the frozen current and comparator statements for:

```text
primary earnings metric
adjusted earnings metric
revenue
operating cash flow
```

and derives:

```text
comparable-period growth
low-base flags
cash conversion
headline-vs-adjusted gap
```

Optional metrics become required if the frozen contract names them; missing source data then fails closed.

## Current limitations

v1 does not yet model:

- quarter-on-quarter acceleration separately from cumulative YTD statements;
- one-off item taxonomy from notes to financial statements;
- bank/broker/insurer-specific earnings quality;
- commodity-cycle normalized earnings;
- segment-level margin transmission;
- balance-sheet stress as a separate materiality veto;
- threshold calibration from historical/forward evidence.

These should be added as event/industry-specific extensions rather than silently embedded into one universal materiality score.

## Next integration step

Connect one earnings-event pipeline end to end:

```text
PIT Expectation / Surprise
+
PIT Earnings Materiality
+
Measured Prepricing / Reaction
        ↓
ERGEvidenceBundle
        ↓
ERGShadowStateMachine
```

Then persist the full bundle/decision for replay and forward evaluation.
