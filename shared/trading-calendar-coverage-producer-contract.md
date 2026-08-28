# Trading Calendar Coverage Producer Contract v1

> Status: `IMPLEMENTED RECONCILIATION CORE / LIVE CALENDAR SOURCE PENDING`
>
> Scope: shared data-quality infrastructure. Current downstream consumer is Short/Mid market features.

## 1. Purpose

A sequence of daily bars is not complete merely because it has enough rows.

The producer establishes:

```text
PIT-visible exchange trading calendar
+ confirmed calendar enumeration
+ observed DAILY_BAR dates
→ security-level DAILY_BAR coverage assertion
```

Implementation:

```text
src/data/trading_calendar.py
src/data/coverage_producers.py
```

## 2. Canonical calendar fact

`TRADING_SESSION` records contain:

```text
exchange
trade_date
is_open
session_rule_version
```

They are shared facts, not strategy signals.

## 3. Calendar rows alone are insufficient

The producer will not trust:

```text
some TRADING_SESSION rows exist
```

as proof that the calendar itself is complete.

Before DAILY_BAR coverage can become `CONFIRMED_COMPLETE`, the same PIT record set must contain an applicable:

```text
DATASET_COVERAGE
family = TRADING_SESSION
status = CONFIRMED_COMPLETE
verification_method = EXCHANGE_CALENDAR_ENUMERATION
```

If that assertion is missing or uses an unaccepted method, DAILY_BAR coverage remains `UNRESOLVED`.

## 4. Reconciliation

For the requested date range:

```text
expected_dates = TRADING_SESSION where is_open=true
observed_dates = DAILY_BAR dates for the security
```

Then:

```text
no missing open sessions
AND no bars on non-open dates
→ CONFIRMED_COMPLETE

otherwise
→ PARTIAL
```

The output is a security-level `DATASET_COVERAGE` assertion with:

```text
verification_method = TRADING_CALENDAR_RECONCILED
expected_count
observed_count
```

and a note containing missing/unexpected dates when present.

## 5. Snapshot integrity check

If the applicable calendar coverage assertion exactly matches the requested date range and declares an `observed_count`, the producer also checks that the materialized `TRADING_SESSION` row count matches that assertion.

This catches cases where a valid coverage assertion was included but the actual calendar records were accidentally filtered or lost before reconciliation.

## 6. Suspensions

The v1 contract expects a canonical `DAILY_BAR` row for each open session, including a row marked:

```text
suspended = true
```

when the selected market-data source represents suspended sessions this way.

If a source omits suspended rows entirely, its adapter/coverage producer must define and test a different explicit convention before promotion. The current producer does not silently guess that convention.

## 7. PIT semantics

Both calendar facts and their calendar-coverage assertion must be visible in the frozen PIT input used by the producer.

A later calendar correction must not rewrite an older strategy snapshot.

## 8. Strategy boundary

The producer is shared infrastructure.

Its output says only:

```text
these DAILY_BAR dates are complete for this range under this verified calendar
```

It does not say:

```text
trend is bullish
buy
sell
long-term thesis changed
```

The 5/10/20-session tactical consumers remain Short/Mid only.

## 9. Current limitation

The repository still lacks a promoted live adapter/producer that creates authoritative `TRADING_SESSION` rows plus `EXCHANGE_CALENDAR_ENUMERATION` coverage from an approved real source.

Until that exists, this module is a deterministic reconciliation core rather than proof of live production calendar completeness.

## 10. Next step

Implement and audit a real calendar ingestion path:

```text
raw calendar evidence
→ RawEvidenceArchive
→ TRADING_SESSION rows
→ TRADING_SESSION DATASET_COVERAGE
→ TradingCalendarCoverageProducer
→ DAILY_BAR DATASET_COVERAGE
```

Only after this chain is stable should benchmark-relative features rely on bar completeness automatically.
