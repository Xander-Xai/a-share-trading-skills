# Short/Mid-term Risk Resilience Layer v1

> Status: `ACTIVE GOVERNANCE / AUDITABILITY LAYER`
>
> Scope: A-share short/mid-term research, entry planning, sizing, holding review and post-trade validation.
>
> This layer does **not** change the current Champion weights, score thresholds, shared capital caps, 0.5%/1% risk parameters, default tranche split, or order permissions. It integrates existing PIT, execution, sizing, holding-state and validation rules into one cross-cutting anti-error process.
>
> Theoretical provenance:
> - `research-basis.md`
> - `../../../research/short-mid-blind-replay-theoretical-audit-v1.md`
> - `methodology-consolidation-and-validation-contract.md`
> - `holding-risk-management.md`
> - `adversarial-review.md`

## 1. Objective

The purpose of this layer is not to make the model sound more certain. It is to make the portfolio more robust when the model is wrong.

Repository principle:

```text
Prediction Error is unavoidable.
Unbounded Prediction Error is optional.
```

A valid short/mid decision must therefore answer two separate questions:

```text
A. Why might this trade work?
B. What happens to capital if that reasoning is wrong?
```

A strong answer to A never substitutes for B.

## 2. Risk-resilience architecture

The short/mid architecture is extended as follows:

```text
Universe / PIT
→ Eligibility
→ Champion / Challenger research state
→ Market / Sector Regime
→ Execution Geometry
→ RISK RESILIENCE LAYER
   ├─ information integrity
   ├─ horizon / model uncertainty
   ├─ conditional path map
   ├─ invalidation geometry
   ├─ execution stress
   ├─ concentration / sizing proof
   ├─ holding-state transition
   └─ validation classification
→ Risk Budget / Position Size
→ Position State
→ Portfolio / Factor Risk
→ Outcome / MFE / MAE
```

This is a cross-cutting layer. It applies again during holding review, not only before entry.

## 3. Eight failure modes this layer must survive

### 3.1 Look-ahead / hindsight contamination

Risk:

- later price action is used to justify an earlier entry;
- later financing data is treated as known earlier;
- a later earnings report is backfilled into a prior decision;
- a retrospective replay is mistaken for untouched forward evidence.

Control:

```text
freeze as_of
freeze publication timestamp
freeze first_tradable_timestamp
future information embargo
immutable original decision snapshot
```

If a material PIT error is found, rerun the affected decision. Do not patch the narrative around it.

### 3.2 Horizon-sign uncertainty

Intermediate-horizon momentum evidence does not prove 3–5 day or 5–15 day continuation. Short-horizon reversal evidence also exists.

Control:

```text
recent strength
→ continuation hypothesis
not
→ deterministic forecast
```

When continuation-vs-reversal is unresolved, uncertainty cannot justify larger size.

### 3.3 Geometry-as-probability error

Old highs, pivots, support/resistance, MA levels and prior traded zones may help define entry/invalidation geometry, but they are not calibrated bounce/break probabilities.

Control:

```text
reference level = execution geometry
reference level != guaranteed support/resistance
```

A price level must be attached to an action/state transition, not to an invented probability.

### 3.4 Volume / participation misread

High volume alone is not bullish. Vendor “main force” flow is not institutional truth.

Control:

Require multi-source interpretation:

```text
volume / turnover
+ price progress
+ relative strength
+ financing / positioning where PIT-valid
+ sector participation
```

Candidate research diagnostic:

```text
price_progress_per_RVOL
```

Its formula/threshold remains Challenger research until validated.

### 3.5 Stop-fill illusion / execution tail

A planned invalidation price is not a guaranteed fill because of T+1, gaps, price limits, suspension and liquidity.

Control:

Before sizing, ask:

```text
planned invalidation loss
adverse-gap loss
historical-tail gap loss when available
price-limit / delayed-exit stress
```

If realistic stress loss breaches shared risk limits, reduce size or reject the trade.

### 3.6 Concentration / conviction substitution

A strong thesis or high score does not authorize large size by itself.

Control:

```text
Attractive Trade != Permission to Use Large Size
```

Position size remains downstream of:

```text
allowed planned loss
÷
entry-to-invalidation risk
```

then subject to shared symbol / cluster / Final Short Cap / Heat constraints.

Exact 0.5%, 1%, 20%, 50/50 values remain governance parameters, not academic optima.

### 3.7 Holding inertia / break-even anchoring

Cost basis is accounting information, not a market target.

Control:

During every material review ask:

```text
If this position were flat today,
would the current evidence justify holding this amount of risk now?
```

Do not HOLD, ADD or extend the horizon solely because the position is below cost.

A short-term thesis cannot silently become medium-term, mean-reversion or long-term.

### 3.8 Model / parameter uncertainty

A memorable winner or loser can create pressure to tune thresholds after the fact.

Control:

```text
case observation
→ hypothesis
→ Challenger / experiment
→ frozen validation
→ promotion review
```

Never:

```text
one memorable trade
→ production threshold change
```

## 4. Conditional Path Map — required uncertainty representation

When the strategy cannot support calibrated probabilities, use conditional paths rather than numeric forecasts.

Minimum structure:

```yaml
continuation:
  condition:
  required_confirmation:
  action_if_confirmed:

neutral_no_follow_through:
  condition:
  review_window:
  action_if_stagnant:

failure:
  first_invalidation_condition:
  broader_thesis_failure:
  action_if_failed:
```

Rules:

```text
conditional path = allowed
uncalibrated numeric probability = prohibited
```

Numeric probabilities may only be used when derived from a frozen cohort with declared:

- universe;
- horizon;
- signal definition;
- transaction costs;
- sample size;
- confidence / uncertainty interval;
- untouched or clearly labeled validation status.

## 5. Pre-trade Resilience Card

Every executable short/mid candidate should be able to populate:

```yaml
as_of:
strategy_id:
code:
research_state:
champion_score:
data_completeness:
market_regime:
sector_regime:

continuation_condition:
neutral_condition:
failure_condition:

planned_entry:
structure_invalidation:
thesis_invalidation:
time_review_window:

planned_stop_distance_pct:
allowed_loss_amount:
planned_exposure:

stress_gap_scenario:
stress_loss_amount:
stress_loss_pct_strategy_nav:

account_symbol_exposure_after:
account_cluster_exposure_after:
portfolio_heat_after:
final_short_cap_state:

probability_calibration_status:
PIT_integrity_status:
resilience_gate: PASS | REDUCE_SIZE | WAIT | REJECT
```

Missing numeric probability is **not** a data defect when the model is not calibrated to estimate one.

## 6. Decision rule under uncertainty

The system must not convert uncertainty into false precision.

Preferred responses:

```text
high uncertainty + weak confirmation
→ WAIT / smaller risk / no trade

high uncertainty + wide invalidation
→ smaller position

high uncertainty + binary gap risk
→ event isolation / reject / stress-size

high score + poor geometry
→ WAIT

strong narrative + no price/participation confirmation
→ WATCH / reject
```

The risk-resilience layer may make a decision more conservative. It may not increase production risk beyond shared policy or create a new entry permission.

## 7. Follow-through as a state-transition hypothesis

The repository retains the practical idea that a trade that fails to develop should be reviewed, but does **not** claim that exactly 3–5 trading days is universally optimal.

Current status:

```text
3–5 day review
= Governance Parameter / Challenger calibration variable
```

Candidate diagnostics:

```text
MFE_3d / MFE_5d
MAE_3d / MAE_5d
RS_3d / RS_5d
RVOL
price_progress_per_RVOL
breakout_hold
retest_success
```

The research question is not “did the stock go down later?” It is:

```text
P(future target / positive R | early behavior)
P(stop / large MAE | early weakness)
blocked-upside cost of early reduction
```

No production threshold changes until forward / PIT validation supports them.

## 8. Holding Resilience Review

For an open position, run the following sequence:

```text
1. Is the original thesis still the same strategy type?
2. Has new PIT-valid information strengthened or weakened it?
3. Has price/participation produced expected follow-through?
4. Is the position state strengthening / intact / weakening / invalidated?
5. Is current exposure still justified by current risk, not historical cost?
6. Has planned horizon expired?
7. Would current stress loss still fit account risk limits?
```

Possible actions remain:

```text
ADD only on positive confirmation and policy permission
HOLD when thesis/risk remain intact
TRIM when evidence/risk deteriorates
EXIT when invalidated
NO_TRADE for new risk when conditions are not met
```

## 9. Blind Replay Protocol

Retrospective cases may be used to test whether the process could have been executed without future leakage.

Required fields:

```text
analysis_as_of
constructed_at
future_data_embargo
PIT source timestamps
unknown-at-the-time fields
conditional paths
invalidation geometry
sizing under then-known geometry
adversarial corrections
```

A replay created after outcomes are known is:

```text
Level A / PIT process evidence
```

not:

```text
Level C untouched forward alpha evidence
```

Future reveal/outcome analysis must be stored separately and must not rewrite the frozen snapshot.

## 10. Risk-Resilience Adversarial Gate

Before finalizing an entry or holding recommendation, attack at least:

```text
PIT integrity
horizon mismatch
uncalibrated probability
support/resistance determinism
volume-without-price-progress
vendor-flow dependency
stop-fill illusion
gap/limit stress
concentration
cost-basis anchoring
holding inertia
strategy-type drift
parameter overfitting
no-trade willingness
```

Any material unresolved item lowers confidence, reduces allowable risk, moves the decision to WAIT, or rejects the trade depending on shared policy.

## 11. Validation metrics for resilience

Risk resilience must not be judged only by P&L.

Track:

```text
Expectancy_R
MaxDD
CVaR95
p95_single_trade_loss_R
MAE_R
MFE_R
MFE_capture
false_positive_rate
false_negative_rate
blocked_MFE
confirmation_delay_cost
gap_through_stop_rate
rule_violation_rate
holding_horizon_breach_rate
cost_anchor_override_rate
PIT_error_rate
```

A stricter layer is not automatically better if it eliminates tail losses but blocks most positive expectancy opportunities. Report both protection and opportunity cost.

## 12. Evidence / governance classification

### Active immediately as governance / auditability

These reduce process error without claiming alpha:

- PIT timestamp discipline;
- conditional paths instead of fabricated probabilities;
- reference levels as geometry rather than deterministic forecasts;
- cost basis not being a market target;
- invalidation before sizing;
- explicit gap/limit stress;
- explicit state transitions and horizon re-underwriting;
- immutable blind-replay snapshots;
- separation of retrospective case evidence from forward alpha evidence.

### Remain Governance Parameters

- exact 3–5 day review window;
- 0.5% / 1% risk thresholds;
- 50/50 or 50/30/20 tranche split;
- fixed minimum R/R threshold;
- approximate single-symbol guideline.

### Challenger / Risk Hypotheses only

- early follow-through filter;
- price-progress-per-RVOL threshold;
- exact breakout/retest confirmation rules;
- conditional sizing multipliers by uncertainty/regime;
- calibrated continuation/reversal probability model;
- automatic state-transition thresholds.

## 13. Promotion boundary

This layer cannot promote its own hypotheses.

```text
Governance / auditability correction
→ may become active if it cannot increase production risk

Alpha / risk hypothesis
→ frozen experiment
→ historical PIT validation
→ untouched forward validation
→ statistical review
→ human Promotion Review
```

If a risk filter reduces drawdown but materially destroys expectancy or coverage, keep it in Shadow or redesign it.

## 14. Repository shorthand

The integrated short/mid process can now be summarized as:

```text
Gate First
→ State Second
→ Geometry Third
→ Stress Fourth
→ Size Fifth
→ Confirm Sixth
→ Re-underwrite While Holding
→ Validate After Outcome
```

Human-language equivalent:

```text
票行不行？
事是不是真的新？
钱有没有真正认？
位置是否值得冒险？
如果判断错，会亏多少？
这个仓位是否配得上当前证据？
右侧没有按预期发展时什么时候承认模型没得到确认？
```

## 15. Final rule

```text
The model does not need to know the future.
It needs to remain solvent, auditable and adaptable when the future differs from the thesis.
```
