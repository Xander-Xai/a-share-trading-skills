# Benchmark & Reaction Window Contract v1

> Status: `ACTIVE RESEARCH MEASUREMENT CONTRACT`
>
> Scope: ERG event research, abnormal-return calculations, placebo tests, Champion/Challenger comparisons, and Track A experiments.
>
> Purpose: remove researcher freedom to choose the benchmark or event window after outcomes are observed.

## 1. Core rule

Before an event cohort is evaluated, freeze both:

```text
Benchmark Contract
Reaction Window Contract
```

Do not inspect outcomes and then select the benchmark/window that produces the largest effect.

This contract changes measurement discipline only. It does not set an alpha threshold, change the Champion, or create an executable trade.

## 2. Benchmark Contract

Required fields:

```text
benchmark_contract_version
contract_frozen_at
stock_code
as_of
event_family
primary_benchmark
secondary_benchmark
sector_benchmark
peer_basket_rule
peer_basket_members_as_of
benchmark_selection_rule
benchmark_fallback_rule
benchmark_data_source
benchmark_pit_status
```

### 2.1 Primary benchmark

`primary_benchmark` is the benchmark used for the primary abnormal-return statistic.

It must be selected by a rule frozen before outcome observation.

Examples of admissible selection rules:

```text
predefined broad-market benchmark by board / market-cap family
predefined sector index using PIT industry classification
predefined factor-neutral benchmark if the full methodology is frozen
```

The repository does not currently assert that one benchmark family is universally optimal.

### 2.2 Secondary benchmark

Secondary benchmarks are diagnostics. They may test robustness but cannot replace the primary benchmark after outcomes are known.

If the primary and secondary benchmarks disagree materially, record the disagreement rather than switching the primary metric.

### 2.3 Sector benchmark

Sector classification must be point-in-time and follow the declared taxonomy/version.

Do not use a later reclassification to construct historical abnormal returns.

### 2.4 Peer basket

If peer-relative return is used, freeze:

```text
peer_basket_rule
peer_basket_members_as_of
peer_exclusion_rules
minimum_peer_count
fallback_rule
```

The peer basket must not be selected from ex-post winners/losers.

If peer data are unavailable or the basket is too small, preserve `UNRESOLVED` rather than substituting an ex-post convenient peer.

## 3. Reaction Window Contract

Required fields:

```text
reaction_window_contract_version
contract_frozen_at
event_family
reaction_anchor
primary_reaction_window
secondary_reaction_windows
window_selection_method
session_treatment
non_trading_day_rule
suspension_rule
price_limit_rule
```

### 3.1 Reaction anchor

Anchor event windows to the first market session that could legally incorporate the information under `session-aware-execution-calendar.md`.

Examples:

```text
same-day continuous session
same-day post-close fixed-price session
next valid trading session
post-resumption session
```

Do not anchor to a market price printed before the event became public.

### 3.2 Primary window

Each event family must eventually have one primary window used for the headline event-reaction metric.

Current policy:

```text
EARNINGS = UNRESOLVED_RESEARCH
EARNINGS_PREANNOUNCEMENT = UNRESOLVED_RESEARCH
ORDER_CONTRACT = UNRESOLVED_RESEARCH
COMMODITY_PRODUCT_PRICE = UNRESOLVED_RESEARCH
POLICY = UNRESOLVED_RESEARCH
CAPITAL_STRUCTURE = UNRESOLVED_RESEARCH
OTHER = UNRESOLVED_RESEARCH
```

The repository intentionally does not hard-code D1/D3/D5 by intuition.

Primary windows must be estimated and then frozen in a new experiment version using historical PIT research plus untouched validation.

### 3.3 Secondary windows

Secondary windows may include diagnostic horizons such as D1/D3/D5/D10/D20.

Rules:

- report them all if predeclared;
- do not promote the largest one as the primary result after inspection;
- if interpretation depends on one narrow window, flag parameter/window instability.

## 4. Abnormal-return calculation contract

At minimum preserve:

```text
stock_return
primary_benchmark_return
abnormal_return_primary
sector_benchmark_return
abnormal_return_sector
peer_basket_return
abnormal_return_peer
```

If any required return cannot be reconstructed point-in-time:

```text
metric_status = UNRESOLVED
```

Do not fill missing benchmark returns with zero.

## 5. Actual-event and placebo symmetry

Actual events and placebo/negative-control dates must use the same:

```text
benchmark contract
reaction-window contract
return calculation
cost treatment
session rules
```

Otherwise `Event_Increment_vs_Placebo` is not comparable.

## 6. Benchmark disagreement diagnostic

Record:

```text
primary_vs_sector_sign_disagreement
primary_vs_peer_sign_disagreement
primary_vs_secondary_magnitude_gap
```

These are robustness diagnostics, not alternate primary outcomes.

If the sign of the event reaction changes across reasonable predeclared benchmarks, classify the result as benchmark-sensitive.

Suggested label:

```text
BENCHMARK_SENSITIVE
```

Do not resolve sensitivity by selecting the benchmark that supports the original thesis.

## 7. Window sensitivity diagnostic

Record:

```text
primary_window_result
secondary_window_results
sign_stability_across_windows
magnitude_dispersion_across_windows
```

Suggested labels:

```text
WINDOW_STABLE
WINDOW_SENSITIVE
INSUFFICIENT_DATA
```

A model whose edge exists only at one narrow reaction window requires additional scrutiny under the statistical-promotion guard.

## 8. Versioning

Any change to these items starts a new contract version:

```text
primary benchmark rule
sector taxonomy rule
peer basket rule
fallback rule
primary reaction window
reaction anchor
suspension treatment
price-limit treatment
```

Historical cohort records keep the contract version that existed when they were frozen.

## 9. Legacy cohort handling

Do not retrofit a newly invented benchmark/window contract onto an immutable forward baseline and then call the result original evidence.

The synthetic forward-cohort fixture is not historical market evidence and does not establish when any private cohort used this contract.

Therefore:

```text
private cohort decision baseline = immutable in private storage
new benchmark/window analyses = supplemental post-hoc diagnostics unless separately versioned
```

A future Forward cohort should freeze this contract before outcomes are observed.

## 10. Track A mapping

Track A subexperiments now map to:

```text
A0 = current ERG baseline
A1 = A0 + frozen Benchmark Contract
A2 = A1 + frozen event-family Reaction Window Contract
A3 = A2 + expectation coverage/confidence calibration
A4 = A3 + normalized prepricing buckets
```

`A1/A2 infrastructure` can be active before any event window is promoted; unresolved values remain explicit until research provides evidence.

## 11. Required audit questions

Before accepting an event-reaction result, ask:

```text
Was the benchmark selected before outcomes?
Was the peer basket PIT-valid?
Was the reaction anchor tradable and information-valid?
Was the primary window frozen before results?
Were all predeclared secondary windows reported?
Would the sign change under another predeclared benchmark?
Would the interpretation disappear under a nearby window?
Was the exact same contract used for placebo dates?
```

Any unresolved answer must be disclosed in the experiment memo.
