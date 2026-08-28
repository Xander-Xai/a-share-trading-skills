# ERG External Research Rationale

> This file records research rationale, not proof that the repository strategy has positive alpha.

## 1. Earnings surprise and post-announcement reaction

A body of research on Chinese equities has documented post-earnings-announcement drift / earnings momentum in some samples, while other work shows that the sign and strength can depend on attention, pre-event pricing and market conditions.

Repository implication:

```text
reported growth alone is insufficient
→ reconstruct expectation when possible
→ measure whether price had already moved before the event
→ evaluate post-event relative reaction
```

## 2. Momentum is conditional, not a universal rule

Research on A-share momentum is mixed. Some studies find weak or unstable unconditional momentum, while stronger effects appear under conditioning variables such as institutional ownership, earnings information or participation.

Repository implication:

```text
generic price momentum != event confirmation
```

ERG therefore treats market confirmation as event-specific abnormal/relative reaction, with volume/turnover as participation evidence rather than directional truth.

## 3. Analyst expectations are imperfect

Analyst forecasts may be stale, dispersed or systematically biased.

Repository implication:

- expectation baseline must record source type;
- consensus must not be inferred from one estimate;
- confidence/dispersion should be preserved;
- low-confidence expectation data cannot support a strong verified-surprise claim.

## 4. Prepricing and reversal risk

A positive headline can produce weak or negative post-event returns when expectations were already embedded in price before publication.

Repository implication:

ERG explicitly separates:

```text
Surprise
from
Prepricing
from
Post-event Reaction
```

This prevents the strategy from automatically chasing apparently good news.

## 5. Stop/execution rules remain strategy-dependent

Research does not support a universal claim that any one stop-loss or ATR buffer is always optimal. The value of stop rules depends on the return process, strategy and execution constraints.

Repository implication:

ERG does not hard-code new ATR/stop parameters. Invalidation remains a governance parameter subject to forward calibration.

## 6. Backtest overfitting and multiple testing

Selecting the best result from many tried models can create a false impression of edge. Established approaches such as White-style reality checks, Probability of Backtest Overfitting and Deflated Sharpe Ratio address different aspects of this model-selection problem.

Repository implication:

`statistical-promotion-guard.md` requires a trial ledger, parameter-stability review and, when sample/tooling permit, DSR/PBO/reality-check diagnostics.

## 7. Evidence hierarchy

The rationale supports the *direction* of the module design. It does not establish repository-specific thresholds or guarantee future returns.

Therefore:

```text
external evidence → research plausibility
repository forward test → promotion evidence
```

Any production promotion remains governed by `shared/research-model-governance.md` and the Champion/Challenger forward-test protocol.
