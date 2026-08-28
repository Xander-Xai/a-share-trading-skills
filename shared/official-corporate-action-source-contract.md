# Official Corporate Action Source Contract v1

> Status: `ACTIVE DATA SOURCE CONTRACT`
>
> Scope: shared factual infrastructure for `long` and `short_mid`.

## 1. Purpose

Adjustment-sensitive research cannot infer corporate-action completeness from row absence.

```text
zero CORPORATE_ACTION rows
!= proof that no ex-date event occurred
```

This contract defines a source-backed way to ingest implemented corporate actions and emit positive `DATASET_COVERAGE(CORPORATE_ACTION)` evidence.

## 2. Enumeration domain

v1 coverage is defined over **implemented corporate actions keyed by `ex_date`** inside an explicit scope/date range.

Examples include:

```text
cash dividend
stock dividend
capitalization / transfer
rights-related adjustment
other implemented action with an ex-date
```

Announcement-stage proposals that do not yet have an implementation ex-date are not counted as completed ex-date events for this coverage contract.

## 3. Approved source families

Official examples include:

### SSE

`https://www.sse.com.cn/market/stockdata/dividends/dividend/`

The exchange trading rules also define ex-right/ex-dividend treatment for implemented distributions.

### SZSE

Official periodic market statistics and company implementation disclosures under `szse.cn`, including official monthly dividend/bonus/rights tables where available.

A source locator must use an approved official exchange host.

## 4. Raw-evidence requirement for complete coverage

A `CONFIRMED_COMPLETE` enumeration requires:

```text
source_snapshot_id = RawEvidenceArchive SHA-256 id
```

The adapter rejects a human label such as:

```text
"downloaded-page-v1"
```

as sufficient proof of complete coverage.

This means a complete assertion must be anchored to an immutable captured source artifact.

## 5. Exact row-count reconciliation

A complete batch also requires:

```text
source_row_count == normalized row count
```

If the source says 37 rows were present but normalization emits 36 rows:

```text
CONFIRMED_COMPLETE
→ rejected
```

The system must investigate the missing row instead of silently declaring coverage complete.

## 6. Scope

Supported coverage scopes:

```text
SECURITY
EXCHANGE
```

A security-level complete empty enumeration can prove:

```text
no implemented ex-date corporate action
for that security
inside that date range
```

An exchange-level complete enumeration can provide broader absence evidence, subject to the captured source actually representing a complete exchange-wide surface.

## 7. PIT visibility

The batch has:

```text
observed_at
```

Coverage itself becomes available no earlier than `observed_at`.

For individual corporate-action rows:

```text
exact published_at available
→ row available_at = published_at

otherwise
→ row available_at = observed_at
```

This avoids backdating a current table observation into historical replay when the original publication timestamp is unknown.

## 8. Output

Each normalized action becomes canonical:

```text
CORPORATE_ACTION
security_id
action_id
action_type
announcement_date
record_date
ex_date
pay_date
cash_per_share
ratio
```

The batch additionally emits:

```text
dataset_family       = CORPORATE_ACTION
scope_type           = SECURITY | EXCHANGE
completeness_status  = CONFIRMED_COMPLETE | PARTIAL | UNRESOLVED
verification_method  = OFFICIAL_SOURCE_ENUMERATION
expected_count       = source_row_count
observed_count       = normalized row count
```

## 9. License and authority are separate

Default:

```text
source_tier   = TIER1
permitted_use = UNRESOLVED_LICENSE
```

Official authority does not automatically grant unrestricted production or redistribution rights.

## 10. Strategy boundary

Corporate actions are shared factual infrastructure.

They may support:

```text
long-term dividend accounting
short/mid adjusted-return research
benchmark normalization
portfolio accounting
```

But tactical features remain tactical:

```text
5/10/20-session return
MA / RVOL
gap / ERG reaction
R-based risk
```

They are not imported into the long-term retirement decision engine merely because both sleeves consume the same corporate-action facts.

## 11. Current limitation

v1 provides the source-batch normalization and completeness contract.

It does **not** yet promote a live SSE/SZSE network transport or claim a complete current corporate-action archive exists in the repository.

A real promoted producer still requires:

```text
lawful source acquisition
→ RawEvidenceArchive capture
→ parsed batch
→ row-count reconciliation
→ PIT ingest
```
