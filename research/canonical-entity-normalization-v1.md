# Canonical Entity Normalization — Implementation v1

> Status: `P1 NORMALIZATION CONTRACT STARTED`
>
> No strategy model or execution permission is changed by this work.

## Implemented

```text
Vendor/API row
→ SourceAdapter contract
→ Canonical Entity
→ NormalizedRecordCandidate
→ PITStore
→ Snapshot
```

Machine modules:

```text
src/data/entities.py
src/data/adapters.py
src/data/ingest.py
```

Active canonical entities:

```text
SECURITY_MASTER
DAILY_BAR
DISCLOSURE
FINANCIAL_STATEMENT
GUIDANCE
CORPORATE_ACTION
INDEX_MEMBERSHIP
INDUSTRY_CLASSIFICATION
CONSENSUS_EXPECTATION
```

## Why this matters

Before this layer, strategy/runtime code could eventually drift toward provider-specific fields.

The new boundary makes the intended architecture explicit:

```text
Provider schema
!= Canonical schema
!= Strategy decision schema
```

This is required for reproducible replay and provider replacement.

## Important choices

### Unadjusted price truth

Canonical daily bars store:

```text
UNADJUSTED
```

Adjusted prices remain derived features so dividends/splits are not silently double-counted.

### Guidance is not consensus

```text
Company Guidance
!= Sell-side / Model Consensus
```

This preserves the expectation-source distinction required by ERG.

### Membership is historical

Index/industry membership has effective periods and therefore can participate in point-in-time replay instead of using today's constituents to describe the past.

## Still pending

```text
real exchange disclosure adapter
real market-data adapter
financial statement mapping adapter
corporate-action adapter
historical security master ingestion
trading calendar entity/adapter
raw evidence archive
Parquet/DuckDB analytical backend
feature snapshots
```

The next data implementation should add **one real source adapter at a time**, backed by frozen fixtures and PIT tests, instead of building many unverified scrapers simultaneously.
