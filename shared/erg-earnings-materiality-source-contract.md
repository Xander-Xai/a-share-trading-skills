# ERG Earnings Materiality Source Contract v1

> Status: `SHORT_MID / SHADOW RESEARCH`
>
> This contract governs source-backed `MaterialityEvidence` for the `EARNINGS` event family. It does not change the Champion, authorize orders, or apply to the long-term retirement sleeve.

## 1. Purpose

Materiality is distinct from Surprise.

```text
Positive surprise
!= economically material change

Large negative earnings change
can also be MATERIAL
```

The v1 producer answers a narrower question:

> Did the reported earnings change, relative to a pre-event comparable financial statement, cross a predeclared materiality rule with auditable PIT evidence?

It does not decide whether the event is bullish, whether price confirmation exists, or whether a trade should be entered.

## 2. Strategy boundary

The producer requires:

```text
strategy_id = a_share_short_mid
sleeve = short_mid
```

The underlying `FINANCIAL_STATEMENT` records remain shared facts, but the tactical `MaterialityEvidence` state is not imported into:

```text
a_share_long_retirement / long
```

Long-term Quality / Cash Flow / Dividend / Expected IRR / Valuation rules remain separate.

## 3. PIT requirements

The frozen contract names the exact logical records:

```text
current_record_id
comparator_record_id
```

The machine requires:

```text
comparator.available_at < information_timestamp
current.available_at >= information_timestamp
current.available_at <= as_of
```

This blocks using a later comparison source or a future revision as if it were known before the earnings event.

Both statements must match the frozen:

```text
security_id
statement_scope
report_type
period_end
```

v1 requires monetary `FINANCIAL_STATEMENT` records with:

```text
currency = CNY
```

and normalizes values using `unit_scale`.

## 4. Frozen contract

The content-addressed contract freezes at least:

```text
current_record_id
comparator_record_id
security_id
current_period_end
comparator_period_end
statement_scope
report_type
primary_metric
transmission_path
rule_mode
classification_basis
low_base_floor_abs
```

Optional diagnostics can freeze:

```text
adjusted_metric
revenue_metric
cash_flow_metric
```

If deterministic classification is requested, thresholds are also frozen:

```text
min_primary_change_abs_pct
min_adjusted_change_abs_pct
```

Changing any frozen field changes `contract_id`.

## 5. No embedded materiality threshold

Code must not silently assume values such as:

```text
20% growth = MATERIAL
10% growth = LOW_MATERIALITY
```

v1 supports two modes.

### EVIDENCE_ONLY

```text
rule_mode = EVIDENCE_ONLY
```

The producer computes source-backed diagnostics but emits:

```text
materiality.state = UNRESOLVED
```

No threshold parameters are allowed in this mode.

### THRESHOLD_RULE_V1

```text
rule_mode = THRESHOLD_RULE_V1
```

All thresholds must be explicitly frozen in the contract. They are research parameters, not claims of empirical optimality.

## 6. Classification bases

### PRIMARY_CHANGE_ONLY

The machine uses the absolute magnitude of the comparable-period change:

```text
primary_change_pct
= (current - comparator) / abs(comparator)
```

A large deterioration can therefore be `MATERIAL`; Materiality is not direction.

### PRIMARY_AND_ADJUSTED_CHANGE

The primary metric must cross its frozen threshold and the adjusted metric must independently cross its own frozen threshold.

This mode can reduce false materiality caused by large headline changes that are not reflected in the selected adjusted-profit measure.

It is not a universal accounting-quality rule and must be validated before Promotion.

## 7. Low-base guard

If:

```text
abs(comparator primary metric) < low_base_floor_abs
```

or the comparator is zero, percentage growth is not trusted for rule classification.

The producer returns:

```text
UNRESOLVED
```

rather than turning a tiny prior-period denominator into an extreme materiality claim.

`low_base_floor_abs` itself is a frozen research parameter.

## 8. Diagnostics

v1 can preserve:

```text
primary_current
primary_comparator
primary_delta
primary_change_pct
primary_low_base

adjusted_current
adjusted_comparator
adjusted_change_pct
adjusted_low_base

revenue_current
revenue_comparator
revenue_change_pct

cash_flow_current
cash_flow_comparator
current_cash_conversion_ratio
comparator_cash_conversion_ratio

current_one_off_gap_ratio
```

Revenue, cash conversion and one-off-gap metrics are diagnostics in v1. They do not become hidden gates.

Industry-specific cash-flow rules are intentionally deferred because banks, brokers, insurers and industrial companies do not share one universal operating-cash-flow interpretation.

## 9. Output

The producer emits:

```text
EarningsMaterialityResult
  result_id
  contract_id
  exact current record revision
  exact comparator record revision
  diagnostics
  MaterialityEvidence
```

`MaterialityEvidence` preserves:

```text
state
transmission_path
assessment_contract_id
impact_metrics
evidence_refs
```

Resolved `MATERIAL` does not imply:

```text
CONFIRMED
READY
ENTRY
BUY
```

The ERG Shadow State Machine still requires the other evidence layers.

## 10. Promotion boundary

This implementation is infrastructure for Shadow research.

It does not establish that any threshold, metric combination or earnings materiality rule improves returns.

Future work must compare rule variants with PIT historical replay, untouched forward data, ablation, placebo/negative controls and model-selection safeguards before any Promotion proposal.
