# Canonical Entity Schema Contract v1

> Status: `ACTIVE NORMALIZATION CONTRACT`
>
> Scope: source adapters, normalized PIT records, historical replay, feature generation, Champion/ERG research, long-term valuation and future Paper/Live lineage.

## 1. Purpose

Vendor/API rows are not strategy inputs.

The production path is:

```text
Source-specific Raw Evidence
→ Adapter
→ Canonical Entity
→ PITMetadata
→ PITStore
→ Snapshot
→ Feature / Strategy
```

A strategy must not contain vendor-column parsing such as Eastmoney/Sina/other provider field names.

## 2. Active machine schemas

Implementation:

```text
src/data/entities.py
src/data/adapters.py
src/data/ingest.py
```

Current canonical entities:

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

This list is intentionally smaller than the eventual platform. New entities require a versioned contract and tests.

## 3. Stable logical record identity

Each canonical entity provides a deterministic stable `record_id`.

Examples:

```text
SECURITY_MASTER:601600
DAILY_BAR:601600:2026-08-28
DISCLOSURE:601600:<disclosure_id>
FINANCIAL_STATEMENT:601600:2026-06-30:H1:CONSOLIDATED
```

Revisions keep the same logical `record_id` and receive a new `revision_id` in PIT metadata.

## 4. Daily-bar policy

Canonical `DAILY_BAR` stores **unadjusted** market prices.

```text
price_basis = UNADJUSTED
```

Forward/backward adjusted prices are derived research features, not raw canonical market facts. This prevents corporate-action treatment from being silently embedded twice.

Minimum validation:

```text
price > 0
high >= open/close/low
low <= open/close/high
volume >= 0
turnover >= 0
valid trade_date
```

## 5. Financial-statement policy

Canonical financial records must preserve:

```text
security_id
period_end
report_type
statement_scope
currency
unit_scale
metrics
```

`metrics` may contain missing values explicitly, but metric names and unit scaling cannot be implicit vendor knowledge.

A later restatement is a PIT revision, not an overwrite of history.

## 6. Guidance / consensus separation

Company guidance and sell-side/model expectations are different evidence families.

```text
GUIDANCE
!=
CONSENSUS_EXPECTATION
```

ERG expectation logic may combine them according to its own confidence rules, but the data layer preserves their source distinction.

Consensus fields include where available:

```text
coverage_count
dispersion
baseline_type
```

No consensus coverage means the strategy must not manufacture a verified beat/miss from absent data.

## 7. Membership data is point-in-time

Index and industry membership records include effective periods.

```text
effective_from
effective_to
```

Historical research must use membership observable/effective at the historical time instead of current constituents/classifications.

## 8. Adapter boundary

Every source adapter implements the conceptual contract:

```text
collect(as_of)
→ Iterable[NormalizedRecordCandidate]
```

A normalized candidate contains:

```text
Canonical payload
+ PITMetadata
```

The adapter is responsible for source-specific parsing, field mapping, timestamp discovery, source tier and permitted-use metadata.

The strategy engine consumes canonical fields only.

## 9. Ingestion fail-closed rule

`src/data/ingest.py` deliberately does not silently drop malformed candidates.

```text
bad normalization
bad timestamp
bad revision lineage
bad payload identity
→ ingestion failure
```

Production ingestion may later quarantine bad rows, but quarantine must be explicit and auditable rather than silently converting them into valid evidence.

## 10. Cross-sleeve rule

Canonical entities are shared facts.

Their `PITMetadata.strategy_visibility` determines whether `long`, `short_mid`, or both may consume them.

Shared visibility does not share decision state.

See:

```text
shared/strategy-boundary-contract.md
```

## 11. Current non-goals

This contract does not yet implement:

```text
official exchange disclosure adapter
licensed market-data adapter
full financial taxonomy
intraday quote/tick schema
broker-account/order/fill schema
Parquet/DuckDB backend
feature store
```

Those are subsequent implementation steps.
