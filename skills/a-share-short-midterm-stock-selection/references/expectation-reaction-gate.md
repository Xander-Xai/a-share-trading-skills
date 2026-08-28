# Expectation–Reaction Gate (ERG) v1

> Status: `CHALLENGER / SHADOW ONLY`
>
> This module does not replace the current Champion. It operationalizes the causal research layer between fundamental eligibility and market/execution confirmation for short-to-medium-term A-share research.

## 1. Purpose

The ERG answers five distinct questions:

1. **Expectation** — What did the market reasonably expect before the new information arrived?
2. **Surprise** — How different was the realized/new information from that expectation?
3. **Materiality** — Can the information materially change revenue, margin, profit, cash flow, EPS/ROE or the relevant valuation regime?
4. **Prepricing** — How much of the information may already have been reflected in price before the event?
5. **Reaction** — After the information became public, did the stock outperform or underperform appropriate benchmarks with meaningful participation?

The core rule is:

```text
Good news != positive surprise
Positive surprise != unpriced surprise
Unpriced surprise != executable trade
```

Therefore the causal sequence is:

```text
Eligibility
→ Expectation Baseline
→ Surprise
→ Materiality
→ Prepricing
→ Post-event Reaction
→ Research State
→ Execution
→ Risk
```

## 2. Point-in-time requirement

Every ERG record must include:

```text
as_of
information_timestamp
first_tradable_timestamp
source_tier
```

Rules:

- Information published after market close cannot be used for an earlier same-day trade decision.
- Forecasts/guidance must never be rewritten later as reported results.
- Later price action must not be used to retroactively upgrade the original event.
- If the expectation baseline cannot be reconstructed point-in-time, mark it `LOW_CONFIDENCE` rather than inventing a surprise.

## 3. E1 — Expectation Baseline

### 3.1 Baseline types

Use the strongest available point-in-time baseline:

```text
CONSENSUS_RECENT
COMPANY_GUIDANCE
EARNINGS_PREANNOUNCEMENT
BROKER_RANGE
MODEL_BASELINE
HISTORICAL_SEASONALITY
NONE
```

### 3.2 Confidence

```text
HIGH
MEDIUM
LOW
```

Suggested interpretation:

- `HIGH`: recent, sufficiently broad and reasonably consistent expectation set, or company guidance/preannouncement with clear range.
- `MEDIUM`: limited analyst coverage, wider dispersion, or model/industry-derived baseline with reasonable evidence.
- `LOW`: sparse, stale, conflicting or reconstructed expectation.

Low-confidence expectation data may support research, but must not be described as a verified beat/miss.

### 3.3 Dispersion

When consensus data exists, record dispersion when available:

```text
expectation_center
expectation_low
expectation_high
expectation_dispersion
coverage_count
```

Do not treat a single analyst estimate as market consensus.

## 4. E2 — Surprise

Record direction and materiality separately.

Possible directions:

```text
POSITIVE
NEUTRAL
NEGATIVE
UNRESOLVED
```

For earnings, use the most decision-relevant available measures, for example:

- revenue;
- attributable profit;
- adjusted profit;
- margin;
- operating cash flow;
- single-quarter acceleration/deceleration;
- management guidance changes.

A high YoY growth rate caused by a low base is not automatically a strong positive surprise.

Where a defensible numerical baseline exists, preserve the formula and denominator explicitly rather than compressing everything into one opaque score.

## 5. E3 — Economic Materiality

The event must have a documented transmission path.

Examples:

### Earnings

```text
reported operating change
→ normalized earnings power
→ cash conversion / balance-sheet effect
→ valuation expectation
```

### Orders

At minimum record:

```text
order_value / annual_revenue
order_value / relevant_segment_revenue
expected_margin
recognition_window
cancellation / execution risk
```

### Commodity / product price

```text
product_price
→ realized selling price
→ input cost
→ unit margin
→ production volume
→ profit sensitivity
```

### Policy

```text
policy
→ demand / price / cost / capacity / competition
→ company exposure
→ earnings impact
```

### Capital structure

Check whether the action changes:

```text
EPS
ROE
leverage
cash flow
share count
capital cost
control / governance
```

A narrative with no credible earnings or cash-flow transmission receives `LOW_MATERIALITY`.

## 6. E4 — Prepricing

A positive surprise can still be a poor trade if price has already moved substantially before the information event.

Record, where data is available:

```text
pre_event_AR_1
pre_event_AR_5
pre_event_AR_20
pre_event_RVOL
pre_event_gap_or_limit_behavior
```

`AR` means abnormal/relative return versus the chosen benchmark set.

Interpretation states:

```text
UNDERPRICED
PARTIALLY_PRICED
HEAVILY_PRICED
UNRESOLVED
```

Do not infer `HEAVILY_PRICED` only from a high absolute price. The question is whether event-related expectations appear to have been incorporated before publication.

## 7. E5 — Post-event Reaction

The preferred confirmation is event-specific relative reaction, not generic momentum.

Record when feasible:

```text
overnight_AR
post_event_AR_1
post_event_AR_3
post_event_AR_5
relative_strength_vs_broad
relative_strength_vs_sector
relative_strength_vs_peer
post_event_RVOL
price_progress_vs_volume
```

Use the first legally executable A-share window after the information timestamp.

### Reaction states

```text
POSITIVE_CONFIRMATION
MIXED
NEGATIVE_DISAGREEMENT
UNRESOLVED
```

Volume is participation evidence, not directional truth. High volume without price progress can indicate supply/absorption rather than confirmation.

## 8. Expectation–Reaction Matrix

| Surprise | Reaction | Research interpretation |
|---|---|---|
| Positive | Positive | `CONFIRMED` candidate, subject to regime/execution/risk |
| Positive | Negative | `DISAGREEMENT / PRICED_IN`; do not force a long thesis |
| Negative | Positive | Re-underwrite; expectations may have been worse than the headline result |
| Negative | Negative | `INVALIDATED / AVOID` unless a separate mean-reversion strategy explicitly applies |
| Unresolved | Any | Remain `WATCH / CANDIDATE`, not a verified surprise trade |

The matrix is a research-state aid, not a standalone entry signal.

## 9. Research State

Research state is distinct from position/execution state.

```text
REJECT
WATCH
CANDIDATE
CONFIRMED
INVALIDATED
```

### REJECT

Fundamental/survival/data/execution hard gate fails.

### WATCH

Fundamental eligibility passes, but no sufficiently material new information or expectation baseline exists.

### CANDIDATE

Material new information exists, but expectation/reaction evidence is unresolved or incomplete.

### CONFIRMED

Information is economically material and market reaction supports the thesis, subject to regime and execution quality.

### INVALIDATED

The original short/mid-term thesis is materially contradicted by new facts or market reaction.

`INVALIDATED` refers to the active thesis, not a permanent judgment on company quality.

## 10. Position State

Keep position lifecycle separate:

```text
FLAT
READY
ENTRY
HOLD
ADD
TRIM
EXIT
COOLDOWN
```

Examples:

```text
research_state = CONFIRMED
position_state = FLAT
```

is valid when price is too extended or expected reward/risk is poor.

Likewise:

```text
research_state = CANDIDATE
position_state = FLAT
```

is the normal state while waiting for confirmation.

## 11. Strategy-type lock

Every trade record must declare a strategy type before entry:

```text
EVENT_MOMENTUM
TREND
MEAN_REVERSION
OTHER_EXPERIMENTAL
```

A losing `EVENT_MOMENTUM` or `TREND` trade may not be silently reclassified into `MEAN_REVERSION` or long-term investing to avoid recognizing invalidation.

Changing strategy type requires closing/re-underwriting the original thesis and creating a new research record.

## 12. ERG output contract

Each eligible event-driven candidate should preserve at least:

```text
as_of
information_timestamp
first_tradable_timestamp
expectation_baseline_type
expectation_confidence
expectation_center
expectation_dispersion
surprise_direction
surprise_evidence
materiality_state
transmission_path
prepricing_state
pre_event_AR_5
pre_event_AR_20
reaction_state
overnight_AR
post_event_AR_1
post_event_AR_3
post_event_AR_5
post_event_RVOL
research_state
research_state_reason
strategy_type
```

Missing fields may be `null/UNRESOLVED`, but must not be silently invented.

## 13. Ablation requirements

ERG must be tested as incremental modules rather than accepted as a narrative package.

Minimum ablations when data allows:

```text
A: Eligibility only
B: A + Expectation/Surprise
C: B + Materiality
D: C + Prepricing
E: D + Post-event Reaction
F: E + Regime/Participation/Execution/Risk
```

For each increment compare out-of-sample/forward:

- expectancy in R;
- excess return;
- profit factor;
- max drawdown;
- turnover/cost drag;
- tail loss;
- regime breakdown;
- event-type breakdown.

If a module does not improve robustness or useful discrimination after cost, remove or simplify it.

## 14. What ERG is not

ERG is not:

- a claim that PEAD always exists in A-shares;
- a guarantee that positive earnings surprises lead to positive returns;
- a replacement for portfolio risk management;
- a reason to chase post-event gaps;
- a license to use vendor `main-force inflow` as institutional truth;
- a fixed-threshold strategy before validation.

## 15. Promotion

ERG remains `SHADOW ONLY` until it passes the repository Champion/Challenger protocol.

Promotion requires point-in-time validity, cost-aware forward evidence, regime robustness, no material deterioration in drawdown/tail risk, and statistical review of model-selection/data-snooping risk.
