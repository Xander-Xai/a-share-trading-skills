# Canonical PIT Store + Snapshot Engine — Implementation v1

> Status: `P1 IMPLEMENTATION STARTED`
>
> Scope: first executable implementation of the Production Architecture P1 reproducible-data core.
>
> This document records implementation status only. It does not change strategy Alpha, Champion/Challenger status or execution permission.

## 1. What is now implemented

The repository now has a machine path:

```text
PITMetadata
→ append-only PITStore
→ replay visibility
→ latest observable revision
→ deterministic Snapshot Manifest
→ materialization integrity check
```

Files:

```text
src/core/pit.py
src/core/pit_store.py
src/core/strategy_boundary.py
runtime/pit_snapshot.py
runtime/tests/test_pit_store.py
```

## 2. Record identity

A logical fact keeps a stable:

```text
record_id
```

Each source revision gets a distinct:

```text
revision_id
```

Known lineage uses:

```text
supersedes_revision_id
```

The store rejects:

```text
same record_id + revision_id
+ different payload
```

as an immutable identity conflict.

## 3. Payload integrity

Each payload is canonicalized and SHA-256 hashed.

```text
payload
→ canonical JSON
→ payload_hash
```

The metadata hash and actual payload must match before a record can be read as valid evidence.

## 4. Historical visibility

For replay at time `T`:

```text
available_at <= T
```

is required.

For the same stable `record_id`, the snapshot selects the latest revision that was visible at `T`.

A later correction cannot leak into an earlier replay.

## 5. Strategy visibility

The shared data layer still honors the cross-sleeve contract.

A record can be visible to:

```text
[long]
[short_mid]
[long, short_mid]
```

Visibility to both strategies means both can read the fact. It does not allow one strategy to consume the other's decision state.

## 6. Deterministic snapshot ID

The snapshot identity is derived from:

```text
strategy_id
sleeve
as_of
intended_use
selected record references
```

and therefore does not depend on wall-clock `created_at`.

The same inputs/data selection must resolve to the same `snapshot_id`.

This becomes the future anchor for:

```text
Decision
Experiment
Forward cohort
Replay
Paper order
```

through a common:

```text
data_snapshot_id
```

## 7. Intended-use gate

The store distinguishes snapshot intent:

```text
RESEARCH
INTERNAL_PRODUCTION
REDISTRIBUTION
```

Internal production fails closed when a selected record is only `RESEARCH_ONLY` or has unresolved production permission.

This is a software control, not legal advice.

## 8. Current storage backend

v1 intentionally uses:

```text
records.jsonl
snapshots/<snapshot_id>.json
```

This keeps revision/replay behavior transparent while the semantics are still stabilizing.

It is **not** a claim that JSONL is sufficient for 5–10 years of full-market A-share history.

The likely next storage step, once the contracts are stable, is:

```text
raw evidence
→ Parquet normalized tables
→ DuckDB analytical queries
```

The backend must remain replaceable without changing PIT semantics.

## 9. Acceptance tests in v1

Current tests cover:

```text
idempotent append
immutable identity conflict
supersedes lineage existence
future revision exclusion
latest visible revision selection
deterministic snapshot ID
strategy visibility
research-only data blocked from internal-production snapshot
explicit production permission accepted
missing/mutated snapshot record detection
```

## 10. What is still missing

This is not yet a complete Canonical Data Platform.

Still pending:

```text
official disclosure adapter
security master store
trading calendar store
market-bar ingestion
financial statement normalizer
corporate-action ingestion
index/industry PIT membership
consensus expectation adapter
full source raw evidence archive
columnar historical backend
snapshot-to-feature lineage
snapshot-to-decision lineage
```

## 11. Next implementation step

Do not jump to Broker or ERG yet.

Next P1 work should be:

```text
Canonical entity schemas
+ official/source adapters
+ local normalized historical backend
+ snapshot query coverage
```

Then P2 can code the current Short/Mid Champion against stable feature/data snapshots.

## 12. Governance unchanged

```text
Short/Mid Champion = unchanged
ERG / Causal Challenger = SHADOW ONLY
Long-term engine = independent
AUTO_ORDER = false
Alpha = NOT_PROVEN
```
