# ERG Source-backed Expectation / Surprise Contract v1

> Status: `ACTIVE SHADOW EVIDENCE CONTRACT`
>
> Scope: A-share short/mid ERG research only.
>
> This contract does not change Champion, Position State, risk limits, broker permissions, or long-term investment logic.

## 1. Purpose

Convert PIT-valid canonical records into auditable ERG `ExpectationEvidence` and `SurpriseEvidence` without allowing the researcher to choose a more favorable baseline after the event outcome is known.

Machine path:

```text
Frozen PIT snapshot
+ exact expectation record id
+ exact actual record id
+ frozen classification contract
        ↓
ExpectationEvidence
        ↓
SurpriseEvidence
```

The adapter is evidence infrastructure, not an alpha claim.

## 2. Supported v1 sources

Expectation sources:

```text
GUIDANCE
→ ERG baseline_type = COMPANY_GUIDANCE

CONSENSUS_EXPECTATION
→ ERG baseline_type = CONSENSUS_RECENT
```

Actual source:

```text
FINANCIAL_STATEMENT
```

v1 is deliberately limited to monetary earnings-style metrics normalized to CNY.

Unsupported units fail closed. Do not guess conversions for EPS, percentages, volumes, physical units, or mixed-unit metrics.

## 3. Preannouncement limitation

The existing canonical `GUIDANCE` entity does not yet contain a source-backed subtype proving whether a record is ordinary company guidance or an earnings preannouncement.

Therefore v1 does **not** automatically emit:

```text
EARNINGS_PREANNOUNCEMENT
```

from a generic GUIDANCE record.

Add a canonical subtype/provenance field before automating that distinction.

## 4. Frozen source-selection contract

Required fields:

```text
contract_id
schema_version
baseline_type
expectation_record_id
actual_record_id
security_id
fiscal_period
actual_period_end
metric
confidence
normalized_unit
surprise_method
metric_polarity
neutral_tolerance_abs
```

The contract is content-addressed. Any change to source selection, confidence, method, polarity, or tolerance changes `contract_id`.

This prevents silent substitution such as:

```text
consensus looks weak
→ switch to company guidance after seeing actual
```

or:

```text
midpoint comparison is inconvenient
→ switch to guidance upper bound after seeing actual
```

A new selection is a new contract/version.

## 5. PIT clock rules

For an event with `information_timestamp`:

```text
expectation.available_at < information_timestamp
```

must hold.

Equality is treated as ambiguous and fails closed in v1.

The actual result must satisfy:

```text
actual.available_at >= information_timestamp
actual.available_at <= as_of
```

If the actual was already observable before the declared event time, the event clock is inconsistent and must be repaired rather than silently accepted.

## 6. Company guidance construction

For a GUIDANCE record:

```text
low   = normalized lower
high  = normalized upper
point = normalized point_estimate
```

Expectation center is:

```text
point_estimate
```

when present; otherwise:

```text
(lower + upper) / 2
```

when both bounds exist.

A one-sided range may remain useful context, but it does not automatically support a verified two-sided range surprise.

## 7. Consensus construction

A `CONSENSUS_RECENT` v1 record must be backed by canonical `CONSENSUS_EXPECTATION` and satisfy:

```text
coverage_count >= 2
```

This is a minimum semantic guard only. It does **not** prove that two analysts constitute a statistically high-quality consensus.

The confidence field remains an explicit frozen research classification and should later be calibrated using coverage, recency, dispersion, and source quality.

## 8. Surprise methods

### 8.1 POINT_DELTA

For a point expectation:

```text
delta = actual - expectation_center
```

Direction is determined only after applying the frozen metric polarity.

### 8.2 RANGE_BREAK

For a two-sided guidance range:

```text
actual within [low - tolerance, high + tolerance]
→ NEUTRAL

actual above range
→ higher outcome

actual below range
→ lower outcome
```

Then apply metric polarity.

This avoids calling an actual result a fresh positive surprise merely because it is above the midpoint while still inside previously disclosed guidance.

## 9. Metric polarity

Required:

```text
HIGHER_IS_POSITIVE
LOWER_IS_POSITIVE
```

Do not infer polarity from the metric name.

Example:

```text
profit
→ normally HIGHER_IS_POSITIVE

cost ratio
→ may be LOWER_IS_POSITIVE
```

A different polarity creates a different content-addressed contract.

## 10. Neutral tolerance

`neutral_tolerance_abs` is a frozen governance/research parameter in normalized CNY units.

It is not an empirically optimal alpha threshold unless separately validated.

Changing the tolerance changes `contract_id` and counts as a new parameter trial where applicable.

## 11. Verified surprise gate

The adapter may calculate diagnostic deltas even when expectation quality is insufficient.

But:

```text
expectation not eligible for verified surprise
→ surprise.verified = false
→ surprise.direction = UNRESOLVED
```

Therefore:

```text
LOW confidence
NONE baseline
insufficient consensus coverage
```

cannot be presented as verified beat/miss.

## 12. Evidence lineage

Every source-backed result preserves EvidenceRefs to the exact PIT revisions:

```text
record_id@revision_id
source_tier
source_snapshot_id
contract id in note
```

So a future ERG decision can be traced from:

```text
ERG decision
→ ERG bundle
→ Expectation/Surprise result
→ PIT record revision
→ raw source snapshot
```

## 13. What v1 intentionally does not do

It does not:

- automatically select the strongest baseline among multiple sources;
- infer analyst-consensus quality from a single opaque vendor score;
- classify EPS/percent/non-monetary surprise;
- convert generic GUIDANCE into preannouncement automatically;
- decide economic materiality;
- classify prepricing or reaction thresholds;
- move Position State;
- authorize orders;
- claim alpha.

## 14. Strategy boundary

This adapter enforces:

```text
a_share_short_mid / short_mid
```

It must not feed tactical surprise states into:

```text
a_share_long_retirement / long
```

Long-term research may use the same underlying financial facts, but it requires its own Quality / FCF / Dividend / Valuation / Expected IRR logic.

## 15. Next research step

After source-backed expectation/surprise evidence is stable:

```text
Expectation / Surprise        ✅ machine evidence
Prepricing / Reaction         ✅ machine measurement
Materiality                   ← next structured family-specific contracts
        ↓
ERG Evidence Bundle
        ↓
Shadow State Machine
```

Do not promote ERG from Shadow based on implementation completion alone.
