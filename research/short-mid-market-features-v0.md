# Short/Mid Market Features v0

> Status: `IMPLEMENTED FEATURE SLICE / DATA-COVERAGE DEPENDENCIES EXPLICIT`
>
> Strategy: `a_share_short_mid`

## Objective

Begin replacing prose-only Short/Mid inputs with reproducible PIT-linked measurements without introducing new Alpha thresholds.

## Implemented path

```text
PITStore data_snapshot_id
→ canonical DAILY_BAR / CORPORATE_ACTION
→ ShortMidMarketFeatureBuilder
→ FeatureSnapshot
→ feature_snapshot_id
```

Files:

```text
src/features/short_mid_market.py
runtime/short_mid_market_features.py
runtime/tests/test_short_mid_market_features.py
shared/short-mid-market-feature-contract.md
```

## Why this slice was chosen first

The selected fields have comparatively low researcher discretion:

```text
returns
moving averages
price distance
volume/turnover ratios
gap/range
suspension/action observations
```

The implementation deliberately does not start with subjective fields such as:

```text
moat
concept authenticity
economic materiality
industry leadership
```

because those require separate evidence and review contracts.

## Important adversarial finding

An early implementation assumption was rejected during review:

```text
no corporate-action row in the snapshot
→ assume no corporate action occurred
```

That inference is not valid unless source coverage is known to be complete.

The final implementation therefore requires explicit upstream assertions:

```text
daily_bar_coverage_confirmed
corporate_action_coverage_confirmed
```

Both default to `false`.

Without them, trailing adjustment-sensitive fields remain `UNRESOLVED` even when enough rows appear to exist.

This is intentionally conservative and prevents a false sense of historical continuity.

## Corporate-action handling

Canonical price data remains unadjusted.

Observed ex-date actions inside a lookback window invalidate continuity-sensitive calculations for that window.

The implementation does not synthesize adjustment factors from incomplete action metadata.

Future improvement should add a separately validated adjustment-factor series or equivalent corporate-action normalization layer.

## What this does not prove

The implementation proves that these calculations are reproducible under a frozen data snapshot and coverage contract.

It does **not** prove that:

```text
20-day return predicts future return
RVOL improves expectancy
MA distance deserves a particular Champion score
```

Those are empirical questions for Historical PIT + Forward/Ablation validation.

## Long-term isolation

The feature builder rejects Long strategy snapshots.

These fields are tactical diagnostics and are not promoted into the long-term retirement engine merely because the data infrastructure is shared.

## Next dependencies

Highest-value dependencies before automated score mapping:

1. trading calendar and bar-coverage verification;
2. corporate-action completeness / adjustment factors;
3. benchmark and sector price series;
4. relative-strength / abnormal-return computation;
5. board/ST/price-limit session facts;
6. only then, frozen feature-to-score mapping experiments.
