# Dataset Coverage Contract v1

> Status: `ACTIVE DATA-QUALITY / PIT COVERAGE CONTRACT`
>
> Scope: canonical datasets shared by long and short/mid infrastructure. Tactical feature use remains sleeve-specific.

## 1. First principle

Absence of a row is not evidence of absence.

Examples:

```text
no CORPORATE_ACTION row
!=
proved no ex-date event occurred

21 DAILY_BAR rows
!=
proved all 21 expected trading sessions were captured
```

A production feature may claim dataset completeness only when a PIT-visible `DATASET_COVERAGE` assertion proves the relevant family, scope and date range.

## 2. Machine entity

Implementation:

```text
src/data/coverage.py
```

Entity:

```text
DATASET_COVERAGE
```

Required fields:

```text
coverage_id
dataset_family
scope_type
start_date
end_date
completeness_status
verification_method
```

Optional scope/count fields:

```text
security_id
exchange
expected_count
observed_count
note
```

## 3. Completeness states

```text
CONFIRMED_COMPLETE
PARTIAL
UNRESOLVED
```

Only `CONFIRMED_COMPLETE` can resolve `confirmed=true`.

When both `expected_count` and `observed_count` exist, `CONFIRMED_COMPLETE` requires exact equality.

## 4. Scope precedence

Coverage assertions may be:

```text
GLOBAL
EXCHANGE
SECURITY
```

Resolution priority:

```text
SECURITY > EXCHANGE > GLOBAL
```

Within the same scope, the latest PIT-visible applicable assertion wins.

This is deliberately conservative. A newer security-level `PARTIAL` assertion must override an older exchange-level `CONFIRMED_COMPLETE` assertion for that security.

## 5. Range containment

An assertion applies only when it fully contains the requested feature window:

```text
assertion.start_date <= requested_start
AND
assertion.end_date >= requested_end
```

A nearby or overlapping assertion is insufficient.

## 6. Verification method is part of trust

A coverage assertion can be syntactically complete yet still be unacceptable for a particular feature family.

Current Short/Mid production-facing accepted methods:

### DAILY_BAR

```text
TRADING_CALENDAR_RECONCILED
EXCHANGE_CALENDAR_RECONCILED
```

### CORPORATE_ACTION

```text
OFFICIAL_SOURCE_ENUMERATION
LICENSED_VENDOR_RECONCILED
OFFICIAL_VENDOR_RECONCILED
```

A method such as:

```text
MANUAL_ASSUMPTION
```

must not promote completeness for the production-facing Short/Mid feature path.

Changing accepted method lists is a data-governance change, not a trading-alpha parameter change.

## 7. PIT requirement

Coverage assertions are ordinary PIT records.

Therefore replay uses only assertions visible in the same `data_snapshot_id`.

A later discovered completeness fact must not silently rewrite an earlier frozen snapshot.

## 8. Production-facing Short/Mid path

Approved runtime path:

```text
data_snapshot_id
→ DATASET_COVERAGE resolution
→ VerifiedShortMidMarketFeatureBuilder
→ ShortMidMarketFeatureBuilder
→ feature_snapshot_id
```

Implementation:

```text
src/features/short_mid_verified.py
runtime/short_mid_market_features.py
```

The runtime CLI no longer accepts manual `--*-coverage-confirmed` switches.

This prevents a caller from turning unresolved adjustment-sensitive features into available features simply by supplying a boolean.

## 9. Coverage lineage

Coverage decisions are included in the resulting feature snapshot through:

```text
market.daily_bar_coverage_confirmed
market.daily_bar_coverage.status
market.daily_bar_coverage.reason

market.corporate_action_coverage_confirmed
market.corporate_action_coverage.status
market.corporate_action_coverage.reason

market.coverage.requested_start
market.coverage.requested_end
```

When an assertion exists, the feature points back to:

```text
DATASET_COVERAGE record_id@revision_id
```

Thus a trailing-return decision can be audited back to the data-completeness evidence that permitted the calculation.

## 10. Shared infrastructure, separate strategy meaning

`DATASET_COVERAGE` is shared infrastructure and may serve both sleeves.

However:

```text
shared data completeness
!= shared strategy horizon
```

The current 5/10/20-session return, MA, gap and RVOL consumers are Short/Mid features only.

Nothing in this contract promotes those tactical measurements into the long-term retirement engine.

## 11. What v1 does not prove

This contract does not itself create trustworthy coverage assertions.

The upstream job still must implement and test the actual proof mechanism, for example:

```text
exchange trading calendar
vs
observed DAILY_BAR dates
```

or:

```text
official corporate-action enumeration
vs
normalized action records
```

Until those reconciliation jobs exist for a real source, coverage remains unresolved.

## 12. Next implementation step

Build the first real coverage producers:

```text
TradingCalendarCoverageProducer
CorporateActionCoverageProducer
```

with frozen fixtures, PIT timestamps and source/permitted-use lineage.

Then add benchmark/index coverage before computing relative-strength and abnormal-return features.
