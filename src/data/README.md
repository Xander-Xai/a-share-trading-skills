# Canonical Data Layer

`src/data/` is the normalization boundary between source-specific data and strategy/replay code.

## Rule

```text
Vendor/API row
!= strategy input
```

The production path is:

```text
Raw Source Bytes
→ RawEvidenceArchive / raw_snapshot_id
→ Source Adapter
→ Canonical Entity
→ NormalizedRecordCandidate
→ PITStore
→ data_snapshot_id
→ DatasetCoverage proof
→ Adjustment / Feature / Strategy
```

## Files

```text
raw_archive.py
→ immutable content-addressed raw evidence
→ observation manifests / raw_snapshot_id

entities.py
→ canonical payload schemas and deterministic logical record IDs

trading_calendar.py
→ canonical TRADING_SESSION facts

official_trading_calendar.py
→ official SSE/SZSE annual calendar-plan normalization
→ conservative date-only visibility
→ exchange-level TRADING_SESSION coverage

official_corporate_actions.py
→ official implemented corporate-action batch normalization
→ RawEvidenceArchive-backed completeness requirements
→ explicit cash/bonus/transfer/rights economics
→ SECURITY / EXCHANGE CORPORATE_ACTION coverage

adjustments.py
→ deterministic exchange-reference adjustment factors
→ backward-adjusted OHLC research series
→ coverage + source-record lineage

coverage.py
→ DATASET_COVERAGE assertions
→ scope/date/method-aware completeness resolution

coverage_producers.py
→ deterministic dataset reconciliation producers
→ trading-calendar vs DAILY_BAR completeness checks

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
→ optional raw_snapshot_id lineage
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
TradingSession
DatasetCoverage
```

Shared facts and data-quality assertions do not contain Long/Short-Mid decision states.

## Raw evidence lineage

Preferred future live ingestion order:

```text
fetch
→ archive raw bytes
→ raw_snapshot_id
→ parse / normalize
→ PITMetadata.source_snapshot_id = raw_snapshot_id
→ PITStore
```

The archive separates:

```text
content_hash
= identity of source bytes

raw_snapshot_id
= identity of this source observation
```

so identical bytes observed at different times remain distinguishable for PIT audit.

See `shared/raw-evidence-archive-contract.md`.

## Dataset coverage

Row presence is not sufficient proof of dataset completeness.

Examples:

```text
21 DAILY_BAR rows
!= complete 21-session calendar coverage

zero CORPORATE_ACTION rows
!= proof that no corporate action occurred
```

`DATASET_COVERAGE` assertions provide explicit positive evidence for a dataset family, scope, date range, completeness state and verification method.

The production-facing Short/Mid feature path resolves coverage from the same PIT snapshot rather than accepting caller-supplied booleans.

See:

```text
shared/dataset-coverage-contract.md
src/features/short_mid_verified.py
```

## Official trading calendar

The 2026 SSE/SZSE annual trading calendar has a source-backed reviewed plan:

```text
configs/data/trading_calendar/cn-a-share-2026-official.json
```

The adapter enumerates canonical `TRADING_SESSION` rows and an exchange-level `DATASET_COVERAGE` assertion using:

```text
verification_method = EXCHANGE_CALENDAR_ENUMERATION
```

The source is based on official annual closure notices plus the exchange rule that ordinary trading days are Monday-Friday excluding statutory holidays/exchange-announced closures.

The annual notices expose dates but this repository has not frozen a reliable exact publication time. v1 therefore uses a conservative next-day `available_at` rather than inventing an intra-day timestamp.

This is a reviewed official-source plan, not an undocumented live API. Emergency/ad-hoc exchange closures must appear as later PIT revisions.

See `shared/official-trading-calendar-source-contract.md`.

## Official corporate actions

Implemented corporate-action completeness has a source-batch contract:

```text
RawEvidenceArchive snapshot
→ OfficialCorporateActionBatch
→ canonical CORPORATE_ACTION rows
→ DATASET_COVERAGE(CORPORATE_ACTION)
```

A `CONFIRMED_COMPLETE` official enumeration requires:

```text
source_snapshot_id = 64-char SHA-256 raw snapshot id
source_row_count    = normalized row count
```

Coverage is defined over implemented actions keyed by `ex_date` inside an explicit SECURITY or EXCHANGE scope/date range.

If the source snapshot is not complete, or the source row count does not match normalization output, the system cannot claim complete corporate-action coverage.

No live SSE/SZSE transport is promoted yet. The current module is the normalization/coverage boundary that future lawful official-source capture must feed.

See `shared/official-corporate-action-source-contract.md`.

## Adjustment factors

Canonical DAILY_BAR remains unadjusted. Derived price continuity now uses a separate deterministic layer:

```text
UNADJUSTED DAILY_BAR
+ confirmed DAILY_BAR coverage
+ confirmed CORPORATE_ACTION coverage
+ explicit corporate-action economics
↓
AdjustmentFactorBuilder
↓
BACKWARD_EXCHANGE_REFERENCE_V1
```

The canonical action schema distinguishes:

```text
cash_per_share
reference_cash_per_share
bonus_ratio
transfer_ratio
rights_ratio
rights_price
reference_total_share_change_ratio
```

The historical generic `ratio` remains readable for legacy records but is rejected by the adjustment engine because its economic meaning is ambiguous.

The engine uses the common SSE/SZSE ex-right/ex-dividend reference-price algebra and records coverage/source lineage in a deterministic `adjustment_series_id`.

This adjusted research series is not automatically equivalent to tax-aware investor total return, broker PnL, or execution prices.

See:

```text
shared/adjustment-factor-contract.md
src/data/adjustments.py
runtime/build_adjustment_series.py
```

## Key normalization choices

### Prices

`DailyBar` stores unadjusted prices only:

```text
price_basis = UNADJUSTED
```

Adjusted prices are derived so corporate-action handling remains explicit and auditable.

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

SSE/SZSE disclosure normalization has a v0 implementation, but **live network acquisition remains intentionally unresolved** because no stable documented public machine API has yet been frozen in this repository.

Current behavior:

```text
verified official row / capture
→ official host validation
→ exact timestamp or first-observed visibility
→ canonical Disclosure
→ PITStore
```

A future promoted live transport should archive its raw response first and pass the resulting `raw_snapshot_id` into the normalized record lineage.

The adapter never converts a date-only listing into an invented intra-day publication time.

Default:

```text
source_tier = TIER1
permitted_use = UNRESOLVED_LICENSE
```

Evidence authority and data-use permission are independent.

See `shared/official-disclosure-source-contract.md`.

## Current status

The data layer now contains raw-evidence archive, canonical schema, PIT store/snapshot, dataset-coverage resolution, official-disclosure normalization, a reviewed 2026 official trading-calendar plan, DAILY_BAR/calendar reconciliation, a RawEvidenceArchive-backed official corporate-action coverage boundary, and a deterministic exchange-reference adjustment-factor layer.

It still does not claim production-ready live adapters or complete real coverage producers for licensed market data, live corporate-action capture, benchmarks or consensus feeds.

Adapters and coverage producers should continue to be added one source at a time with frozen raw fixtures and point-in-time tests.
