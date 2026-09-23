# Short/Mid-term Examples

This directory contains public-safe fixtures for testing methodology and serialization. They are not recommendations, real market candidates or evidence of Alpha.

Every public case-like fixture must be explicitly labeled:

```text
SYNTHETIC EXAMPLE / NOT REAL USER DATA
```

## Current synthetic fixtures

- `synthetic-watchlist-case-study.md` and `synthetic-watchlist.json`: universe screening, factor overlap and fresh-gate separation.
- `synthetic-forward-cohort.md` and `synthetic-forward-cohort.json`: immutable baseline, evidence-state and research/position-state separation.

Real portfolio/trade instances and all row-level evidence derived from them belong only in ignored local private state. Do not publish user-selected security lists, actual fills, cost basis, shares, P&L, account facts or personal cash answers.

## Evidence rules

- Public market facts may be used only when no account or execution linkage is retained.
- Anonymized research cases must not be reasonably re-identifiable from securities, dates, levels or linked artifacts.
- Synthetic fixtures must use fictional case IDs and values, carry the marker above, and not be derived from a person's list or screenshots.
- Retrospective evidence cannot be counted as untouched forward validation.
- Future outcomes never rewrite frozen public-safe baselines.
