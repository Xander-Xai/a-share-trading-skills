# Adjustment Factor v1 Research Note

Status: `IMPLEMENTED / DATA CORRECTNESS INFRASTRUCTURE`

## Purpose

Close the remaining bridge between:

```text
UNADJUSTED DAILY_BAR
+ PIT-complete CORPORATE_ACTION
```

and future:

```text
adjusted returns
benchmark relative strength
abnormal return
prepricing / reaction
ERG automation
```

without treating a vendor-adjusted price series as unexplained truth.

## What changed

### CorporateAction economics are explicit

The canonical schema now distinguishes:

```text
cash_per_share
reference_cash_per_share
bonus_ratio
transfer_ratio
rights_ratio
rights_price
reference_total_share_change_ratio
```

The old generic `ratio` remains readable but cannot drive v1 adjustment calculations.

### Deterministic adjustment engine

`src/data/adjustments.py` adds:

```text
AdjustmentFactorBuilder
AdjustmentEvent
AdjustedPricePoint
AdjustmentSeries
```

The engine:

1. requires confirmed DAILY_BAR coverage;
2. requires confirmed CORPORATE_ACTION coverage;
3. groups PIT-visible actions by ex-date;
4. calculates exchange-reference prices from explicit economic terms;
5. derives backward event factors;
6. anchors the latest bar at factor 1.0;
7. produces adjusted OHLC plus source lineage;
8. creates a deterministic SHA-256 `adjustment_series_id`.

### Runtime CLI

```text
runtime/build_adjustment_series.py
```

builds a series from an existing `data_snapshot_id`.

## Formula basis

The v1 formula follows the common 2026 SSE/SZSE trading-rule reference-price algebra:

```text
reference
= ((previous_close - reference_cash)
   + rights_price * rights_ratio)
  / (1 + total_share_change_ratio)
```

The previous close is taken from the prior canonical DAILY_BAR, not from the ex-date `prev_close` field.

## Important distinction

This output is:

```text
BACKWARD_EXCHANGE_REFERENCE_V1
```

It is not claimed to be:

```text
after-tax total shareholder return
portfolio PnL
broker settlement accounting
```

## Special distributions

Differential distributions can preserve holder-facing economics while storing exchange-effective virtual terms separately:

```text
cash_per_share
!= reference_cash_per_share

actual share distribution ratios
!= reference_total_share_change_ratio
```

This is needed because issuer implementation notices can publish effective/virtual parameters for the exchange reference-price calculation.

Arbitrary issuer-approved custom formulas outside the standard algebra remain unresolved in v1.

## Tests

Coverage includes:

```text
cash dividend
bonus / capitalization transfer
rights issue
combined event
virtual/effective reference cash
reference share-change override
legacy ambiguous ratio rejection
missing coverage fail-closed
same-date standard-row aggregation
override ambiguity rejection
deterministic series identity
```

## What this enables next

After this layer is merged, the next research-data sequence is:

```text
Adjusted Price Series
→ Benchmark Data Contract
→ Broad / Sector Benchmark Series
→ Relative Strength
→ Abnormal Return
→ Prepricing / Reaction
→ ERG Engine
```

No feature-to-Champion score mapping is changed in this version.

## Governance unchanged

```text
Short/Mid Champion = unchanged
ERG                = SHADOW ONLY
Long-term logic    = unchanged
AUTO_ORDER         = false
Alpha              = NOT_PROVEN
```
