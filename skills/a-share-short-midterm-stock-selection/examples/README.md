# Short/Mid-term Examples

This directory contains **point-in-time case studies** produced by the short/mid-term stock-selection skill.

Examples are evidence records, not permanent recommendations.

## Rules

1. Every example must declare an `as_of` timestamp.
2. The original decision snapshot is immutable.
3. Future data must not be used to rewrite an earlier thesis.
4. Follow-up results are appended as new dated files or ledger events.
5. Baseline close is not automatically a trade entry.
6. Paper and live trades must record their own trigger, planned entry, actual/simulated fill, invalidation, size and exit.
7. Strategy-version changes start a new evaluation segment.

## Current example

- `2026-08-26-final-watchlist-case-study.md`
- `2026-08-26-final-watchlist.json`

This example freezes a 43-stock research whitelist derived only from the user's locked 357-stock universe.

## Recommended follow-up naming

```text
YYYY-MM-DD-daily-scorecard.md
YYYY-MM-DD-paper-trades.jsonl
YYYY-MM-DD-live-trades.jsonl
YYYY-MM-DD-position-review.md
```

For the future runtime system, execution records should move to the structured ledger described in:

- `../references/validation-metrics-and-trade-ledger.md`
- `../references/paper-live-automation-roadmap.md`
