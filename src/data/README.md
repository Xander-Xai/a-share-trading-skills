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

official_disclosures.py
→ SSE/SZSE official-disclosure normalization v0
→ strict official-host provenance
→ FIRST_OBSERVED / OFFICIAL_TIMESTAMP visibility semantics
→ no undocumented live endpoint
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

## Official disclosure adapter status

SSE/SZSE disclosure normalization now has a v0 implementation, but **live network acquisition remains intentionally unresolved** because no stable documented public machine API has yet been frozen in this repository.

Current behavior:

```text
verified official row / capture
→ official host validation
→ exact timestamp or first-observed visibility
→ canonical Disclosure
→ PITStore
```

The adapter never converts a date-only listing into an invented intra-day publication time.

Default:

```text
source_tier = TIER1
permitted_use = UNRESOLVED_LICENSE
```

Evidence authority and data-use permission are independent.

See `shared/official-disclosure-source-contract.md`.

## Current status

The data layer now contains canonical schema, PIT store/snapshot, and official-disclosure normalization contracts. It still does not claim production-ready live adapters for official disclosure retrieval, licensed market data, corporate actions or consensus feeds.

Adapters should continue to be added one source at a time with frozen fixtures and point-in-time tests.
