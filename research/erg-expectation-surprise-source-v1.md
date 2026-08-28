# ERG Expectation / Surprise Source-backed Adapter v1

> Status: `IMPLEMENTED RESEARCH INFRASTRUCTURE`
>
> Strategy: `a_share_short_mid / short_mid`
>
> Alpha status: `NOT_PROVEN`

## Why this exists

ERG v0 already had machine objects for expectation and surprise, but the caller could still populate those objects manually. That left a large gap between:

```text
PIT canonical facts
```

and:

```text
ExpectationEvidence / SurpriseEvidence
```

This v1 closes the first part of that gap for monetary earnings-style events.

## Implemented path

```text
Frozen PIT snapshot
        ↓
Exact GUIDANCE or CONSENSUS_EXPECTATION revision
        +
Exact FINANCIAL_STATEMENT revision
        ↓
Frozen ExpectationSurpriseContract
        ↓
PITExpectationSurpriseAdapter
        ↓
ExpectationEvidence
        ↓
SurpriseEvidence
```

## Important methodological choice

The adapter does **not** search all available expectation sources and choose the one that produces the largest surprise.

The frozen contract names the exact records before evaluation.

This removes one source of hidden researcher degrees of freedom.

## Guidance range semantics

For a disclosed guidance range, v1 can use `RANGE_BREAK`:

```text
actual inside disclosed range
→ NEUTRAL

actual above range
→ positive for HIGHER_IS_POSITIVE metrics

actual below range
→ negative for HIGHER_IS_POSITIVE metrics
```

This is intentionally different from a naive midpoint rule.

Example:

```text
guidance = 95–105
actual = 103
```

A midpoint-only method would call this positive relative to 100.

`RANGE_BREAK` instead records it as inside the already disclosed range, therefore `NEUTRAL` unless a separately frozen method says otherwise.

## Consensus semantics

v1 requires at least two observations before the canonical record can be used as `CONSENSUS_RECENT`.

This is only a semantic floor. Future Track A work still needs to calibrate:

```text
coverage
recency
dispersion
source breadth
confidence
```

before any HIGH/MEDIUM confidence rule is claimed to be empirically effective.

## PIT protections

The adapter rejects:

```text
expectation.available_at >= information_timestamp
```

and rejects an event clock where:

```text
actual.available_at < information_timestamp
```

This makes it harder to accidentally use a forecast snapshot refreshed after the result was published.

## Scope limitation

v1 supports monetary totals normalized to CNY.

It intentionally fails on unsupported units rather than silently guessing conversions.

Examples requiring later adapters:

```text
EPS
margin percentage
production volume
commodity price
subscriber count
order quantity
```

## Preannouncement limitation

Canonical `GUIDANCE` currently does not carry enough source-backed subtype information to prove that an item is specifically an earnings preannouncement.

Therefore v1 does not automatically map generic GUIDANCE to:

```text
EARNINGS_PREANNOUNCEMENT
```

That distinction should be added at the canonical-data layer first.

## What remains manual / contract-driven

The following are deliberately not inferred from outcomes:

```text
expectation source selection
expectation confidence
surprise method
metric polarity
neutral tolerance
```

They are frozen in a content-addressed contract.

## Tests

The test suite covers:

- guidance range inside / above / below;
- frozen neutral tolerance;
- low-confidence baseline;
- point guidance;
- one-sided range unresolved;
- consensus with source coverage;
- single-analyst rejection;
- consensus method mismatch;
- expectation timestamp leakage;
- inconsistent actual event clock;
- missing actual metric;
- polarity inversion;
- exact source-record selection;
- deterministic output identity;
- contract identity sensitivity;
- long-sleeve rejection;
- unsupported-unit fail-closed.

## Next step

Build event-family-specific `MaterialityEvidence` producers.

Recommended first family:

```text
EARNINGS
```

because the current canonical data already contains FinancialStatement metrics and this creates the shortest path to a fully source-backed ERG earnings bundle.

Possible v1 earnings materiality contract should separate:

```text
reported change
normalized earnings significance
cash-flow confirmation
balance-sheet contradiction
low-base / one-off flags
```

without inventing an opaque one-number alpha score.
