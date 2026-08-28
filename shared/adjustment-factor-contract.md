# Adjustment Factor Contract v1

Status: `ACTIVE DATA / RESEARCH INFRASTRUCTURE CONTRACT`

This contract defines how canonical unadjusted A-share prices and PIT-visible corporate actions are transformed into a deterministic backward-adjusted research price series.

It does **not** define a trading signal, Champion score, ERG state, long-term thesis, order price, tax-aware investor return, or broker accounting value.

## 1. Exchange rule basis

The 2026 SSE and SZSE trading rules use the same standard ex-right/ex-dividend reference-price algebra for ordinary equity distributions, bonus/capitalization shares and rights issues:

```text
reference_price
= ((previous_close - cash_component)
   + rights_price * rights_ratio)
  / (1 + total_share_change_ratio)
```

Official references:

- SSE 2026 Trading Rules, 4.3.1-4.3.3:
  https://www.sse.com.cn/lawandrules/sselawsrules2025/stocks/exchange/c/c_20260424_10816482.shtml
- SZSE 2026 Trading Rules, 4.4.1-4.4.3:
  https://docs.static.szse.cn/www/lawrules/rule/trade/current/W020260424690713155663.pdf

Issuer-approved special formulas may exist. v1 does not silently approximate arbitrary custom formulas.

## 2. Canonical corporate-action economics

`CorporateAction` now separates economically different terms:

```text
cash_per_share
reference_cash_per_share
bonus_ratio
transfer_ratio
rights_ratio
rights_price
reference_total_share_change_ratio
```

Definitions:

```text
cash_per_share
= holder-facing gross cash amount when known

reference_cash_per_share
= cash term actually used in exchange/issuer reference-price algebra
  when it differs from holder-facing cash, e.g. an effective/virtual amount

bonus_ratio
= free bonus shares per existing share

transfer_ratio
= capitalization-transfer shares per existing share

rights_ratio
= subscribed rights shares per existing share

rights_price
= subscription price per rights share

reference_total_share_change_ratio
= explicit effective denominator override when the issuer/exchange published
  a virtual/effective share-change ratio
```

Default denominator when no override exists:

```text
total_share_change_ratio
= bonus_ratio + transfer_ratio + rights_ratio
```

Default cash term when no effective override exists:

```text
reference_cash
= cash_per_share
```

## 3. Legacy `ratio`

The historical generic field:

```text
ratio
```

is retained temporarily only for backward-compatible record parsing.

It is **not accepted** by the adjustment engine because it cannot distinguish:

```text
bonus shares
capitalization transfer
rights subscription
other share-count changes
```

Therefore:

```text
legacy ratio present
→ adjustment factor = FAIL CLOSED
```

New source adapters must populate explicit terms.

## 4. Coverage gates

Adjustment is allowed only when both datasets are positively proven complete for the requested security/date range:

```text
DAILY_BAR
→ TRADING_CALENDAR_RECONCILED / accepted equivalent

CORPORATE_ACTION
→ OFFICIAL_SOURCE_ENUMERATION / accepted equivalent
```

No corporate-action rows without a complete enumeration do not prove that no action occurred.

## 5. Backward adjustment definition

For each ex-date event:

```text
event_factor
= reference_price / actual_previous_trading_close
```

The latest observed bar is the anchor:

```text
anchor adjustment_factor = 1.0
```

For an earlier bar:

```text
adjustment_factor(date)
= product(event_factor for all later ex-dates up to anchor)
```

Adjusted OHLC:

```text
adjusted_price
= canonical_unadjusted_price * adjustment_factor
```

This keeps the series continuous across mechanical ex-right/ex-dividend changes while retaining the actual market reaction against the exchange reference price.

## 6. Previous close source

The reference formula uses the actual close of the previous observed trading bar.

The engine does **not** use the ex-date bar's `prev_close` field because exchange market data may already expose the ex-right/ex-dividend reference price there.

## 7. Same-day multiple corporate-action rows

Standard rows sharing one ex-date are aggregated by economic component:

```text
cash terms      → sum
bonus ratios    → sum
transfer ratios → sum
rights ratios   → sum
rights value    → sum(rights_ratio * rights_price)
```

An explicit `reference_total_share_change_ratio` override requires one consolidated action row for that ex-date. This prevents ambiguous mixing of issuer-adjusted and standard terms.

## 8. Special / differential distributions

A published effective or virtual cash/share-change term may be represented with:

```text
reference_cash_per_share
reference_total_share_change_ratio
```

while preserving holder-facing economics separately.

If a corporate action requires an issuer-approved formula that cannot be represented by the standard algebra plus effective terms:

```text
ADJUSTMENT = UNRESOLVED
```

Do not reverse-engineer terms merely to force the standard formula to fit.

## 9. Output identity

`AdjustmentSeries` is content-addressed:

```text
adjustment_series_id
= SHA256(canonical series payload)
```

It records:

```text
security_id
exchange
start/end/anchor dates
DAILY_BAR coverage assertion ref
CORPORATE_ACTION coverage assertion ref
per-event source action refs
per-bar source DAILY_BAR ref
adjustment factors
adjusted OHLC
```

Same PIT input facts must produce the same series id and values.

## 10. Not total-return accounting

`BACKWARD_EXCHANGE_REFERENCE_V1` is a research price-adjustment basis.

It is not automatically equivalent to:

```text
after-tax investor total return
broker realized PnL
cash-ledger accounting
rights-subscription cash-flow accounting
```

Those require separate portfolio/accounting semantics.

## 11. Strategy boundary

Adjustment facts are shared infrastructure:

```text
long
short_mid
```

may both consume a properly constructed adjusted series.

However, downstream tactical features remain isolated:

```text
5/10/20-session momentum
MA / RVOL
Champion
ERG reaction / prepricing
R-based risk
```

remain `short_mid` unless a separate long-term contract explicitly defines another use.

## 12. Promotion boundary

This module becoming deterministic does not prove trading alpha.

```text
Adjustment Factor
→ data correctness infrastructure
!= signal improvement
!= Champion promotion
!= ERG promotion
```

Current governance remains:

```text
Champion unchanged
ERG SHADOW ONLY
AUTO_ORDER=false
Alpha NOT_PROVEN
```
