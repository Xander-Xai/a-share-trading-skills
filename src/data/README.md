# Canonical Data Layer

`src/data/` is the normalization boundary between source-specific data and strategy/replay code.

## Rule

```text
Vendor/API row
!= strategy input
```

The production path is:

```text
Raw Evidence
→ Source Adapter
→ Canonical Entity
→ NormalizedRecordCandidate
→ PITStore
→ data_snapshot_id
→ Feature / Strategy
```

## Files

```text
entities.py
→ canonical payload schemas and deterministic logical record IDs

adapters.py
→ source adapter protocol
→ NormalizedRecordCandidate
→ raw evidence lineage reference

ingest.py
→ fail-closed candidate ingestion into PITStore
```

## Current entities

```text
SecurityMaster
DailyBar
Disclosure
FinancialStatement
CompanyGuidance
CorporateAction
IndexMembership
IndustryMembership
ConsensusExpectation
```

These are shared facts. They do not contain Long/Short-Mid decision states.

## Key normalization choices

### Prices

`DailyBar` stores unadjusted prices only:

```text
price_basis = UNADJUSTED
```

Adjusted prices are derived research features so corporate-action handling remains explicit.

### Financials

Financial statements carry explicit:

```text
period_end
report_type
statement_scope
currency
unit_scale
metrics
```

Restatements are PIT revisions.

### Guidance vs consensus

```text
CompanyGuidance
!= ConsensusExpectation
```

They remain separate source families so ERG can assess expectation type/confidence rather than treating all expected values as equivalent.

## Adapter implementation rule

A source adapter is responsible for:

```text
vendor field mapping
security identity mapping
timestamp mapping
source tier
source snapshot id
revision id
permitted-use metadata
strategy visibility
```

The adapter must emit `NormalizedRecordCandidate` objects. Strategy code must not import provider-specific column names.

## Current status

This layer defines machine contracts. It does not yet include production adapters for exchange disclosures, licensed market data, corporate actions or consensus feeds.

Those adapters should be added one source at a time with fixtures and point-in-time tests.
