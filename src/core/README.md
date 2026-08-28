# Production Core Contracts

`src/core/` contains machine-enforced contracts shared by the long and short/mid strategy implementations.

It is implementation, not a new policy source of truth. Upstream rules remain in `shared/` and the strategy Skills.

## Current modules

```text
strategy_boundary.py
→ canonical strategy_id / sleeve identities
→ fail closed on cross-sleeve context mismatch

pit.py
→ canonical PIT metadata validation
→ timestamp awareness
→ strategy visibility
→ permitted-use vocabulary

pit_store.py
→ append-only reference PIT store
→ immutable record/revision identity
→ payload hashing
→ replay visibility
→ latest observable revision selection
→ deterministic data snapshot manifests
→ intended-use licensing gate
→ snapshot materialization integrity check
```

## Store backend status

The first store backend deliberately uses:

```text
records.jsonl
snapshots/<snapshot_id>.json
```

This is a **reference/research MVP backend**, not the final scale architecture.

Reasons:

1. replay semantics and revision behavior remain directly inspectable;
2. no new database dependency is required before contracts stabilize;
3. deterministic snapshot identity can be tested before introducing storage complexity;
4. the interface can later be backed by Parquet/DuckDB or another store without changing strategy semantics.

Do not interpret JSONL as the long-run storage recommendation for a full historical A-share dataset.

## Snapshot identity

A snapshot is keyed by a SHA-256 hash over:

```text
snapshot schema version
strategy_id
sleeve
as_of
intended_use
ordered selected record references
```

Each selected record reference includes:

```text
record_id
revision_id
entity_type
security_id
available_at
source_snapshot_id
payload_hash
```

`created_at` is deliberately excluded from snapshot identity.

Therefore the same:

```text
store contents
+ strategy context
+ as_of
+ filters
+ intended_use
```

must resolve to the same `snapshot_id`.

## Replay revision rule

For each stable `record_id`, replay selects the latest revision whose:

```text
available_at <= replay_as_of
```

Later revisions are invisible to earlier replays.

## Data-use gate

`RESEARCH` snapshots may include records labelled for research or with unresolved production licensing, subject to upstream governance and law.

`INTERNAL_PRODUCTION` snapshots fail closed if a selected required record is not explicitly:

```text
INTERNAL_PRODUCTION_ALLOWED
or
REDISTRIBUTION_ALLOWED
```

`REDISTRIBUTION` requires:

```text
REDISTRIBUTION_ALLOWED
```

This is a machine guard, not legal advice and not a substitute for checking vendor/exchange contracts.

## CLI

Build a snapshot from an existing local store:

```bash
python runtime/pit_snapshot.py \
  --store-root /path/to/pit-store \
  --strategy-id a_share_short_mid \
  --sleeve short_mid \
  --as-of 2026-08-28T18:00:00+08:00
```

## Tests

```bash
python -m unittest discover -s runtime/tests -v
```

The current tests cover immutable identity, revision lineage, historical visibility, deterministic snapshot identity, sleeve visibility, permitted-use gating and missing-record detection during snapshot materialization.
