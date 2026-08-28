# Canonical Point-in-Time Data Contract v1.2

> Status: `ACTIVE DATA / REPLAY CONTRACT`
>
> Scope: data adapters, historical replay, Forward cohorts, Champion/Challenger research, long-term valuation research and future Paper/Live decision records.
>
> Normalized payload shapes are governed by `canonical-entity-schema-contract.md`; this file governs time, revision, provenance, visibility and snapshot semantics.

## 1. First principle

A production research system must be able to answer:

> At this exact historical time, what information was legally/publicly available to the strategy, from which source/version, and when did our system actually ingest it?

A row with only `date=YYYY-MM-DD` is not sufficient for event-sensitive or revision-sensitive research.

## 2. Required metadata

Canonical records should preserve, where applicable:

```text
record_id
entity_type
security_id
exchange

effective_at
published_at
available_at
ingested_at

source
source_tier
source_snapshot_id
source_uri_or_locator
payload_hash

revision_id
supersedes_revision_id
is_current_revision

permitted_use
redistribution_allowed
retention_rule

strategy_visibility
```

### Timestamp meanings

`effective_at`
: Economic/market time the value describes. Example: 2026-H1 report period end, or quote timestamp.

`published_at`
: Time the source officially released the information, when such a timestamp exists.

`available_at`
: Earliest time the research system is allowed to treat the information as observable. It must not precede the official/public availability time.

`ingested_at`
: Time our system actually captured the record.

These timestamps are not interchangeable.

## 3. Information visibility vs tradability

`available_at` determines research visibility.

It does not automatically determine when an order could be executed.

For event trades:

```text
information visibility
→ available_at

execution eligibility
→ first_tradable_timestamp
```

`first_tradable_timestamp` continues to follow the session-aware execution contract and broker/exchange constraints.

## 4. Revisions

Financial, analyst, corporate-action and vendor datasets may be revised.

Historical replay must not silently replace a record that was visible at `T` with a later revision.

Store:

```text
revision_id
supersedes_revision_id
published_at
available_at
payload_hash
```

A stable `record_id` represents the same logical fact across revisions. A new revision uses a new `revision_id` and should link to the prior revision through `supersedes_revision_id` where lineage is known.

When historical revision lineage cannot be reconstructed, mark the affected test:

```text
PIT_STATUS = BIASED_OR_NON_PROMOTABLE
```

## 5. Source and permitted-use metadata

Being technically downloadable does not imply production or redistribution permission.

At minimum distinguish:

```text
RESEARCH_ONLY
INTERNAL_PRODUCTION_ALLOWED
REDISTRIBUTION_ALLOWED
UNRESOLVED_LICENSE
```

Critical production datasets must not be silently upgraded from public aggregation endpoints to broker/exchange truth without an explicit adapter and data contract.

`UNRESOLVED_LICENSE` may be usable for exploratory research when lawful, but must be surfaced before production deployment.

## 6. Strategy visibility

Shared facts may be visible to both strategies:

```text
strategy_visibility = [long, short_mid]
```

or restricted to a specialized dataset:

```text
strategy_visibility = [short_mid]
```

Visibility permits consumption of the fact; it does not permit one strategy engine to reuse the other strategy's decision state.

See `strategy-boundary-contract.md`.

## 7. Minimum entity families

The future canonical store should support at least:

```text
SECURITY_MASTER
TRADING_CALENDAR
MARKET_QUOTE
DAILY_BAR
CORPORATE_ACTION
DISCLOSURE
FINANCIAL_STATEMENT
GUIDANCE
CONSENSUS_EXPECTATION
INDEX_MEMBERSHIP
INDUSTRY_CLASSIFICATION
POSITIONING
BROKER_ACCOUNT_STATE
ORDER
FILL
```

The first active normalized schema subset is defined in `canonical-entity-schema-contract.md` and `src/data/entities.py`.

Not every source requires every timestamp, but absence must be explicit rather than filled with invented values.

## 8. Raw → normalized → feature → decision lineage

Target lineage:

```text
Immutable Raw Evidence
        ↓
Source Adapter
        ↓
Canonical Entity
        ↓
Normalized PIT Record
        ↓
Feature Snapshot
        ↓
Strategy Decision
        ↓
Order / Outcome
```

Every feature/decision used for promotion evidence should be traceable back to:

```text
data_snapshot_id
source_snapshot_id(s)
code/git version
config/model version
```

## 9. Replay invariants

For a historical replay at `replay_as_of = T`:

```text
record.available_at <= T
AND
selected revision was the latest revision observable at T
```

Future `ingested_at` backfills may reconstruct historical research only when the source's historical publication/revision timing is independently known. Otherwise the replay must disclose reconstruction uncertainty.

## 10. Production fail-closed rules

Do not create an executable research/order state when a required item has:

```text
future-dated availability
conflicting security identity
unresolved revision ambiguity
missing critical source timestamp
unresolved broker/account truth
unresolved license / permitted-use state required for production
invalid canonical entity payload
```

Research may continue with an explicit `UNRESOLVED` label when governance permits, but it cannot be silently promoted to executable evidence.

## 11. Active machine implementation

The executable implementation is now active under:

```text
src/core/pit.py
src/core/pit_store.py
src/data/entities.py
src/data/adapters.py
src/data/ingest.py
runtime/pit_snapshot.py
runtime/tests/test_pit_store.py
runtime/tests/test_canonical_entities.py
```

Current capabilities:

```text
PIT metadata validation
canonical entity validation
source-adapter normalization contract
append-only record/revision storage
payload SHA-256 integrity
immutable record_id + revision_id identity
revision lineage checks
strategy visibility
latest observable revision selection
intended-use / permitted-use gate
deterministic data_snapshot_id
snapshot manifest persistence
snapshot materialization integrity verification
```

This implementation does not yet mean the complete historical A-share dataset exists.

## 12. Reference store backend

The first backend is deliberately simple:

```text
records.jsonl
snapshots/<snapshot_id>.json
```

It is a **reference/research MVP**, selected to make replay semantics auditable before introducing a larger storage dependency.

It is not the final scaling decision for multi-year full-market price/financial history.

Expected evolution after contracts stabilize:

```text
append-only raw evidence
→ normalized columnar store (for example Parquet)
→ analytical query layer (for example DuckDB)
```

A backend migration must preserve snapshot/replay semantics and must not change strategy outputs merely because storage technology changed.

## 13. Deterministic snapshot contract

A snapshot identity is derived from:

```text
snapshot schema version
strategy_id
sleeve
as_of
intended_use
ordered selected record references
```

Each reference contains at least:

```text
record_id
revision_id
entity_type
security_id
available_at
source_snapshot_id
payload_hash
```

`created_at` is metadata and is not part of the identity hash.

Therefore:

```text
same store contents
+ same strategy context
+ same as_of
+ same filters
+ same intended_use
→ same snapshot_id
```

A completed snapshot manifest is not overwritten by a later run with the same identity.

## 14. Intended-use gate

Snapshot creation distinguishes:

```text
RESEARCH
INTERNAL_PRODUCTION
REDISTRIBUTION
```

Machine policy:

```text
RESEARCH
→ may consume research-labelled records subject to governance/law

INTERNAL_PRODUCTION
→ every selected required record must be explicitly
  INTERNAL_PRODUCTION_ALLOWED or REDISTRIBUTION_ALLOWED

REDISTRIBUTION
→ every selected required record must be REDISTRIBUTION_ALLOWED
```

This gate is a technical enforcement of repository metadata, not legal advice and not a substitute for reviewing exchange/vendor contracts.
