# Feature Snapshot Contract v1

> Status: `ACTIVE FEATURE LINEAGE CONTRACT`
>
> Scope: deterministic strategy inputs derived from canonical PIT data.

## 1. Purpose

A production research system must not jump directly from mutable provider data to a strategy score.

The required lineage is:

```text
raw evidence
→ raw_snapshot_id
→ canonical PIT records
→ data_snapshot_id
→ feature_snapshot_id
→ strategy decision
```

A `FeatureSnapshot` is the immutable boundary between data/research calculations and a strategy engine.

## 2. Active implementation

```text
src/features/snapshot.py
runtime/tests/test_feature_snapshot_champion.py
```

The current reference backend stores immutable JSON feature manifests locally.

## 3. Snapshot identity

`feature_snapshot_id` is SHA-256 over canonicalized identity fields:

```text
strategy_id
sleeve
as_of
data_snapshot_id
feature_set_version
implementation_version
config_version
ordered feature values
```

`created_at` is intentionally absent from the identity.

Therefore:

```text
same data snapshot
+ same strategy context
+ same as_of
+ same feature implementation/config
+ same feature values
→ same feature_snapshot_id
```

Changing `data_snapshot_id`, a feature value, feature implementation version or config version changes the identity.

## 4. Feature value states

Each feature has one explicit state:

```text
AVAILABLE
MISSING
UNRESOLVED
```

`AVAILABLE` requires a concrete scalar value and lineage through at least one of:

```text
source_record_ids
calculation_id
```

`MISSING` and `UNRESOLVED` cannot carry a fabricated value.

Strategy engines decide which fields may tolerate `MISSING`/`UNRESOLVED`. Required Champion inputs currently fail closed unless `AVAILABLE`.

## 5. Shared facts vs strategy features

Canonical data is shared evidence.

Feature snapshots are strategy-scoped:

```text
strategy_id = a_share_short_mid
sleeve = short_mid
```

or:

```text
strategy_id = a_share_long_retirement
sleeve = long
```

A Short/Mid feature snapshot cannot be consumed by the Long engine and vice versa unless a separately versioned cross-strategy feature contract explicitly permits it.

This prevents tactical concepts such as ERG state, 5/10/20-day reaction or R-based stop semantics from leaking into the long-term engine.

## 6. Feature calculation boundary

A feature snapshot may contain:

```text
deterministic calculations
bounded research classifications
human-reviewed structured fields
```

but lineage must remain explicit.

Examples:

```text
relative strength
→ deterministic calculation_id

financial data completeness
→ source_record_ids + validation calculation_id

qualitative industry position sub-score
→ future bounded research/human-review artifact, not silently inferred here
```

## 7. No execution authority

A feature snapshot is evidence, not an order.

```text
feature_snapshot_id
!= BUY
!= position size
!= broker permission
```

Any future order requires separate portfolio/risk/execution governance.

## 8. Current limitations

The v1 contract does not yet provide:

```text
full automated feature computation from canonical market/filing data
feature dependency DAG
feature cache invalidation service
columnar feature store
cross-sectional full-market batch execution
```

The first objective is deterministic lineage and replay correctness before scaling throughput.
