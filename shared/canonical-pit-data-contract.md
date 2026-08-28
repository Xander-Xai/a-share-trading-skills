# Canonical Point-in-Time Data Contract v1

> Status: `ACTIVE DATA / REPLAY CONTRACT`
>
> Scope: data adapters, historical replay, Forward cohorts, Champion/Challenger research, long-term valuation research and future Paper/Live decision records.

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

Not every source requires every timestamp, but absence must be explicit rather than filled with invented values.

## 8. Raw → normalized → feature → decision lineage

Target lineage:

```text
Immutable Raw Evidence
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
```

Research may continue with an explicit `UNRESOLVED` label when governance permits, but it cannot be silently promoted to executable evidence.