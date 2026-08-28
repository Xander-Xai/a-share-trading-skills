# Official Trading Calendar Ingestion v1

> Status: `IMPLEMENTED SOURCE-BACKED CALENDAR PLAN / LIVE TRANSPORT NOT PROMOTED`

## Problem

The repository already had:

```text
TRADING_SESSION
→ TradingCalendarCoverageProducer
→ DAILY_BAR coverage reconciliation
```

but the upstream `TRADING_SESSION` facts were fixture/infrastructure only. That left a gap:

> Who creates the exchange calendar used to prove DAILY_BAR completeness?

## v1 implementation

Add:

```text
configs/data/trading_calendar/cn-a-share-2026-official.json
src/data/official_trading_calendar.py
runtime/ingest_official_trading_calendar.py
runtime/tests/test_official_trading_calendar.py
shared/official-trading-calendar-source-contract.md
```

The machine path is now:

```text
SSE/SZSE official annual closure notice
+ exchange weekday trading rule
→ reviewed 2026 plan
→ TRADING_SESSION (365 rows/exchange)
→ DATASET_COVERAGE(TRADING_SESSION)
→ PITStore
→ TradingCalendarCoverageProducer
→ DAILY_BAR coverage
```

## Why a reviewed plan instead of an undocumented API

The production objective is reproducibility and provenance, not maximum scraping cleverness.

No stable documented public calendar JSON endpoint has been frozen in this repository. v1 therefore converts public official source facts into a checked-in machine-readable plan rather than depending on an undocumented endpoint that may silently change.

A live transport remains a separate future promotion step.

## PIT treatment

The annual notices are dated `2025-12-22`, but the repository has not frozen an exact intra-day publication timestamp.

v1 uses:

```text
available_at = 2025-12-23T00:00:00+08:00
```

This is intentionally conservative for replay.

The current plan was ingested/reviewed later, but PIT visibility is based on when the official schedule was already publicly available, not when the repository happened to backfill it.

## Fail-closed boundaries

v1 rejects:

- non-official source hosts;
- closure ranges outside the plan year;
- overlapping closure ranges;
- naive timestamps;
- same-day fabricated `available_at` for a date-only notice;
- duplicate exchange/year plans.

The annual coverage assertion proves complete date enumeration, not absence of future emergency/ad-hoc closure revisions.

## No strategy logic change

This work changes shared data truth only.

It does not alter:

```text
Champion 30/30/25/15
ERG SHADOW status
short/mid score thresholds
long-term Quality/IRR logic
risk budget
AUTO_ORDER=false
```

## Next

After this PR, the next data-fact gap is corporate-action completeness.

Recommended next implementation:

```text
Official / licensed corporate-action enumeration
→ CORPORATE_ACTION canonical rows
→ DATASET_COVERAGE(CORPORATE_ACTION)
→ adjustment factor / adjusted-price research feature
```

Only after calendar + corporate-action coverage is reliable should relative-strength, abnormal-return and ERG reaction/prepricing automation be expanded.
