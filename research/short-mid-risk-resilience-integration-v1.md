# Short/Mid Risk-Resilience Methodology Integration v1

> Status: `INTEGRATED RESEARCH / GOVERNANCE DECISION RECORD`
>
> Date: 2026-08-29
>
> Scope: integrate lessons from the 600699 retrospective live sample, blind replay and theoretical adversarial audit into the short/mid-term methodology without hindsight-based production tuning.

## 1. Source artifacts

This integration abstracts the reusable methodology from:

- `skills/a-share-short-midterm-stock-selection/examples/2026-08-05-600699-retrospective-live-sample.json`
- `skills/a-share-short-midterm-stock-selection/examples/2026-08-05-600699-blind-replay-frozen.md`
- `skills/a-share-short-midterm-stock-selection/examples/2026-08-05-600699-blind-replay-frozen.json`
- `skills/a-share-short-midterm-stock-selection/examples/2026-08-29-600699-position-review.md`
- `research/short-mid-blind-replay-theoretical-audit-v1.md`

The stock-specific levels/outcomes are **not** generalized into methodology. Only reusable process principles are carried forward.

## 2. Missing layer identified

Before this integration, the repository already contained strong components:

```text
PIT discipline
Champion scoring
Entry Quality Gate
A-share execution gate
risk-based sizing
portfolio heat / caps
holding state machine
MFE / MAE
adversarial review
Champion / Challenger governance
```

The gap was orchestration under model uncertainty.

The previous architecture could answer:

```text
Is this stock eligible?
How strong is the setup?
Where is invalidation?
How much planned risk is allowed?
```

but did not express one unified contract for:

```text
What if short-horizon direction is uncertain?
What if technical reference levels fail?
What if the planned stop cannot fill?
What if early follow-through never appears?
What if a large position is justified only by conviction language?
What if the trader anchors to cost after the thesis changes?
What if retrospective analysis silently imports future information?
```

## 3. Integrated solution

New active reference:

- `skills/a-share-short-midterm-stock-selection/references/risk-resilience-layer.md`

New Shadow research protocol:

- `research/short-mid-risk-resilience-experiment-v1.md`

The layer is deliberately split into:

```text
ACTIVE governance / auditability
+
SHADOW alpha/risk hypotheses
```

so that anti-error improvements do not silently become unvalidated trading rules.

## 4. New cross-cutting architecture

Integrated human/process flow:

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

Expanded machine logic:

```text
PIT / Eligibility
→ Research State
→ Market / Sector Regime
→ Execution Geometry
→ Conditional Path Map
→ Stress / Tail Check
→ Risk Budget / Size
→ Entry Permission
→ Holding State / Follow-through Review
→ Re-underwriting
→ Outcome / MFE / MAE
→ Challenger / Promotion Review
```

## 5. What becomes active immediately

These are governance/auditability corrections and cannot increase production risk:

### 5.1 Conditional paths instead of fabricated probabilities

If no calibrated distribution exists:

```text
CONTINUATION condition
NEUTRAL / NO-FOLLOW-THROUGH condition
FAILURE condition
```

may be stated, but numeric probabilities are prohibited.

### 5.2 Reference levels are geometry, not predictions

Support/resistance/pivots may define:

```text
trigger
invalidation
retest
reward/risk geometry
```

They do not receive deterministic bounce/break claims.

### 5.3 PIT timestamp integrity

Later-published capital, earnings or price information cannot enter an earlier decision. A material PIT contamination invalidates the affected reconstruction.

### 5.4 Stop-fill stress

Planned stop loss and realistic executable loss remain separate. Gap/limit/delayed-exit risk must be considered before sizing.

### 5.5 Cost basis boundary

```text
cost basis = P&L / accounting fact
cost basis != market target
```

Holding decisions require fresh evidence/risk, not a break-even objective.

### 5.6 Large-position proof obligation

A high score or strong narrative cannot bypass the downstream risk budget. Uncertainty cannot be converted into larger size.

### 5.7 Retrospective evidence classification

A blind replay constructed after the outcome is known may verify PIT/process discipline but is not untouched forward alpha evidence.

## 6. What remains unproven / Shadow

The following ideas are not production rules:

```text
exact 3–5 day follow-through rule
MFE/RS early exit threshold
price_progress_per_RVOL threshold
automatic breakout/retest state transition
uncertainty-based sizing multiplier
calibrated continuation/reversal probabilities
```

They enter `SHORT_MID_RISK_RESILIENCE_V1` experiments only.

## 7. Why this improves anti-risk capability

The layer attacks five different kinds of loss that were previously easy to mix together:

```text
Selection Risk
= stock/setup thesis is wrong

Timing Risk
= right thesis, wrong entry/horizon

Execution Risk
= planned stop cannot be achieved

Sizing Risk
= reasonable trade, unreasonable capital concentration

Behavior / State-Drift Risk
= loss changes the strategy definition after entry
```

A single P&L number cannot diagnose these separately.

The new methodology requires the system to identify which risk is being managed rather than using one rule to solve every problem.

## 8. 600699-specific lesson that is NOT generalized

The following are case-only and must not become generic parameters:

- 21.85 / 22.00 continuation level;
- 20.60 / 20.00 invalidation geometry;
- later 19.xx / 18.xx levels;
- one stock's observed MFE / MAE;
- the user's specific 50% reported position;
- any uncalibrated scenario probabilities.

What is generalized is the **method used to derive and audit** such levels at the decision timestamp.

## 9. Required user-facing discipline

For money-risk decisions, future analysis should explicitly distinguish:

```text
PIT fact
research-supported principle
governance parameter
Challenger hypothesis
uncalibrated judgment
```

The assistant/research layer should not present an uncalibrated judgment with the same confidence as a fact or validated model output.

When a numeric probability is unavailable, say so rather than inventing one.

## 10. Required risk-resilience outputs

For executable or near-executable candidates, future reports should aim to include:

```text
as_of
research_state
score + confidence
market / sector regime
continuation condition
neutral / no-follow-through condition
failure condition
planned invalidation
stress execution scenario
planned loss / exposure
account-level symbol/cluster risk
holding review horizon
probability_calibration_status
resilience_gate
```

For open positions additionally:

```text
current position_state
fresh thesis state
fresh score when re-underwriting is required
MFE / MAE
holding days
strategy-type drift check
cost-basis anchoring check
```

## 11. Validation roadmap

The new Shadow protocol contains five tracks:

```text
R1 Early Follow-through
R2 Volume / Price Efficiency
R3 Stress-aware Sizing
R4 Holding Inertia / Cost Anchoring
R5 Conditional Path Calibration
```

Required validation order:

```text
Level A process/PIT validation
→ Level B historical PIT research
→ Level C untouched forward validation
→ statistical promotion review
→ human Promotion Review
```

## 12. Governance precedence

If this integration conflicts with higher-level policy:

```text
shared capital policy
shared automation governance
shared research-model governance
```

wins.

The risk-resilience layer may make a decision more conservative. It may not grant extra size, extra risk or new order permission.

## 13. Production status after integration

```text
Champion weights = unchanged
Champion thresholds = unchanged
shared risk caps = unchanged
entry tranche defaults = unchanged
3–5 day window = still governance / research parameter
new numeric forecast probabilities = NOT ENABLED
risk-resilience auditability = ACTIVE
risk-resilience alpha/risk experiments = SHADOW
```

## 14. Final design principle

The repository should not optimize for sounding correct after the fact.

It should optimize for:

```text
point-in-time honesty
+ bounded downside
+ explicit uncertainty
+ falsifiable conditions
+ state discipline
+ realistic execution
+ controlled concentration
+ forward learning
```

The objective is not to eliminate prediction error. The objective is to keep prediction error from becoming uncontrolled capital loss or untraceable model drift.
