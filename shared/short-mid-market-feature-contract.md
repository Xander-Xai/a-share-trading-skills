# Short/Mid Market Feature Contract v0

> Status: `ACTIVE DETERMINISTIC FEATURE CONTRACT / PARTIAL FEATURE COVERAGE`
>
> Strategy: `a_share_short_mid`
>
> Sleeve: `short_mid`

## 1. Purpose

This contract defines the first low-subjectivity machine-computed feature slice for the Short/Mid strategy.

It intentionally does **not** convert raw market features directly into Champion sub-scores yet.

Current lineage:

```text
raw evidence
→ canonical DAILY_BAR / CORPORATE_ACTION
→ data_snapshot_id
→ short-mid market feature computation
→ feature_snapshot_id
```

## 2. Active implementation

```text
src/features/short_mid_market.py
runtime/short_mid_market_features.py
runtime/tests/test_short_mid_market_features.py
```

## 3. Current deterministic fields

The v0 slice includes:

```text
market.latest_trade_date
market.bar_count
market.close
market.volume
market.turnover
market.latest_suspended
market.close_vs_open_pct
market.return_1d_pct
market.gap_pct
market.range_pct
market.return_5d_pct
market.return_10d_pct
market.return_20d_pct
market.ma5
market.ma10
market.ma20
market.close_to_ma5_pct
market.close_to_ma10_pct
market.close_to_ma20_pct
market.distance_to_20d_high_pct
market.rvol_1_vs_20
market.turnover_ratio_1_vs_20
market.observed_suspension_count_20d
market.observed_corporate_action_in_20d_window
market.observed_latest_ex_date_action
```

These are measurements/diagnostics, not Alpha claims.

## 4. Coverage confirmation is explicit

Two machine flags are required before trailing adjustment-sensitive features may become `AVAILABLE`:

```text
market.daily_bar_coverage_confirmed
market.corporate_action_coverage_confirmed
```

The builder defaults both to `false`.

That means:

```text
21 observed bars
!= proof that 21-session history is complete

zero observed corporate actions
!= proof that no ex-date event occurred
```

If coverage is not independently verified, the affected feature remains:

```text
UNRESOLVED
```

rather than assuming completeness.

Coverage confirmation is a data-quality assertion from an upstream calendar/provider audit. It is not inferred from the absence of errors and should not be turned on merely to obtain a numeric result.

## 5. Unadjusted-price rule

Canonical `DAILY_BAR` stores:

```text
price_basis = UNADJUSTED
```

Therefore multi-session price continuity cannot be assumed across corporate actions.

If an observed corporate-action ex-date occurs inside the relevant lookback window, adjustment-sensitive features fail closed to `UNRESOLVED`, including:

```text
multi-session return
moving averages
close-to-MA distance
20-session high distance
RVOL / turnover ratios (conservatively blocked because some actions alter share count/activity comparability)
```

For the latest session, `prev_close`-based return/gap/range fields also remain `UNRESOLVED` if corporate-action coverage is unconfirmed or an ex-date action is observed on that date.

`close_vs_open_pct` does not depend on the previous close and remains available when the canonical latest bar itself is valid.

## 6. Missing vs unresolved

Use:

```text
MISSING
```

when the required number of bars is absent.

Use:

```text
UNRESOLVED
```

when enough rows exist but data continuity/coverage cannot be proven or an unadjusted corporate-action break exists.

Do not replace either state with zero, neutral score or a guessed value.

## 7. Definitions

### N-session return

```text
return_Nd_pct
= (close_t / close_t-N - 1) * 100
```

Requires `N + 1` bars and confirmed continuity.

### Moving average

```text
maN = arithmetic mean(last N closes)
```

### Close-to-MA distance

```text
(close_t / maN - 1) * 100
```

### Distance to 20-session high

```text
(close_t / max(high over last 20 bars) - 1) * 100
```

### RVOL 1 vs 20

```text
latest volume / mean(previous 20 session volumes)
```

This requires 21 bars.

### Turnover ratio 1 vs 20

```text
latest turnover / mean(previous 20 session turnovers)
```

The canonical field name remains `turnover`; this ratio is unitless and does not assume a particular vendor's display terminology beyond the canonical schema.

## 8. Strategy boundary

This feature set is explicitly Short/Mid.

It cannot consume a long-term data snapshot and must not be reused to drive long-term retirement buy/sell logic.

In particular:

```text
5/10/20-session returns
short moving-average distance
gap behavior
RVOL
```

are tactical diagnostics. Their existence in shared infrastructure does not make them long-term decision variables.

## 9. No automatic Champion mapping yet

The current feature slice does **not** declare rules such as:

```text
return_20d > X → trend_quality = 8
RVOL > Y → capital score = 8
```

Those thresholds would introduce new parameter choices and must be frozen/researched separately.

For now:

```text
market features
!= Champion sub-score
```

The Champion v0 aggregation engine remains able to consume explicit scored features, but this PR does not silently invent the mapping.

## 10. Current limitations

Not yet implemented in this slice:

```text
trading-calendar completeness service
corporate-action adjustment factor series
broad/sector/peer relative strength
price-limit / ST board-specific limit computation
benchmark abnormal return
intraday microstructure
full Technical/Capital score mapping
```

These should be added only with explicit data contracts and tests.
