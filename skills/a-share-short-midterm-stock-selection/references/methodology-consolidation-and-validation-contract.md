# Methodology Consolidation & Validation Contract v1

> Status: `ACTIVE RESEARCH GOVERNANCE CONTRACT`
>
> Scope: short/mid-term A-share research architecture, human-language mapping, robustness diagnostics, and validation maturity.
>
> This contract does not change the current Champion, ERG Shadow status, risk caps, or order permissions. It defines how the repository interprets the multiple methodologies developed during research and how claims are validated.

## 1. Consolidated architecture

The repository no longer treats prior analysis styles as independent votes.

Historical roles are consolidated as:

```text
Ordinary / broad analysis
→ Research and industry-understanding layer

Current GitHub Champion
→ Production research baseline / ranker

Manual integrated analysis
→ Explanation and execution-support layer

V2 / causal ERG logic
→ Structurally distinct Challenger / Shadow layer

Champion vs Challenger
→ Forward + Ablation + Placebo + Statistical Review
→ component promotion only after evidence
```

Target architecture:

```text
Universe / PIT
→ Fundamental Eligibility
→ Expectation / Surprise
→ Economic Materiality
→ Prepricing
→ Market Reaction / Participation / Regime
→ Research State
→ Intra-State Rank
→ Execution Geometry
→ Risk Budget
→ Position State
→ Portfolio / Factor Risk
→ Outcome / MFE / MAE
→ Disagreement / Ablation / Placebo
→ Statistical Promotion Review
```

Repository shorthand:

```text
Gate First
→ State Second
→ Rank Third
→ Execute Fourth
→ Validate Last
```

## 2. No pseudo-ensemble voting

Prior analysis methods share data, assumptions, and feature families. Agreement across them is therefore correlated evidence, not independent votes.

Prohibited interpretation:

```text
four methods agree
→ four independent confirmations
→ higher truth probability
```

Allowed interpretation:

```text
multiple related methods agree
→ decision robustness may be higher
→ return validity remains unproven
```

Going forward, the primary model comparison is:

```text
one active Champion
+
one structurally distinct Challenger family
+
one validation system
```

New ideas enter as modules or experiment tracks, not as Method V5 / V6 / V7 unless they represent a genuinely different strategy family with an explicit data and validation contract.

## 3. Six non-equivalences

Human-facing research must preserve these distinctions:

```text
A company with acceptable quality != an attractive trade
Positive news != positive surprise
Positive surprise != unpriced information
Unpriced information != market confirmation
Market confirmation != attractive entry geometry
Attractive entry geometry != permission to use large size
```

Machine consequence:

```text
Fundamental Gate
!= Information Gate
!= Market Confirmation
!= Execution Gate
!= Risk Budget
!= Position State
```

No stage may be skipped because another stage appears strong.

## 4. Human market language: 票—事—钱—位—错—仓

This is a presentation layer only.

| Human question | Meaning | Machine contract |
|---|---|---|
| 票行不行？ | Fundamental eligibility / survival quality | `fundamental_gate`, governance/audit/debt/cash-flow fields |
| 事新不新？ | New information relative to prior expectation | `expectation`, `surprise`, `information_timestamp` |
| 事大不大？ | Economic materiality | `materiality.state`, `transmission_path` |
| 钱认不认？ | Relative reaction / participation, not vendor "main force" | abnormal return, RS, RVOL, participation evidence |
| 位好不好？ | Prepricing + execution geometry | prepricing, gap/extension, entry, invalidation, realistic R/R |
| 错了怎么办？ | Thesis invalidation and risk budget | invalidation, risk budget, position sizing, state transition |
| 仓做多少？ | Result of risk budget and portfolio constraints | planned loss, shares, exposure, cluster heat |

Rules:

- Human shorthand must never replace structured fields.
- Phrases such as "资金认可" or "位置不错" require measurable evidence in the machine record.
- Vendor-labeled main-force flow remains corroboration only unless stronger evidence exists.

## 5. Decision robustness is not return validation

The repository distinguishes:

```text
Decision Robustness
= stability of ranks/states/decisions under related research formulations

Return Validation
= future cost-aware market outcomes under frozen rules
```

A stable ranking can still be wrong. An unstable ranking can reveal model sensitivity rather than market noise.

Never promote a model because rankings are stable across correlated methods.

## 6. Rank / state stability diagnostics

These are diagnostics, not alpha features and not promotion gates by themselves.

Recommended fields where repeated observations exist:

```text
rank_today
rank_5d_median
rank_dispersion_5d
rank_change_1d
research_state_today
research_state_changes_5d
position_state_changes_5d
champion_rank
challenger_rank
champion_challenger_rank_gap
champion_challenger_state_disagreement
```

Portfolio/universe-level diagnostics:

```text
spearman_champion_vs_challenger
rank_turnover
state_transition_count
confirmed_to_invalidated_rate
```

Interpretation:

- high rank stability = reproducibility signal;
- high rank dispersion = sensitivity diagnostic;
- large Champion/Challenger gap = disagreement research target;
- none of these imply positive expectancy without outcome validation.

Historical multi-method rank correlations may be preserved as case evidence, but should not become a voting engine because the methods are not independent.

## 7. R/R is geometry, not alpha

`Reward/Risk >= 2` is a governance/entry-quality parameter, not proof of positive expectancy.

Cost-aware expectancy is:

```text
Expectancy_R
= P(win) * AvgWin_R
- P(loss) * AvgLoss_R
- Cost_R
```

A future research target is conditional expectancy:

```text
E[R | event_type, research_state, confirmation_basis, regime, execution_state]
```

Until sample size supports such conditioning, fixed minimum R/R values remain governance parameters and must not be described as academically optimal.

## 8. Stop interpretation

The repository keeps three separate concepts:

```text
price / structure invalidation
thesis invalidation
time review / time stop
```

A stop is an invalidation and risk-control mechanism, not an independent alpha source.

Rules:

- define invalidation before sizing;
- do not widen invalidation after entry to avoid realizing a loss;
- do not convert a failed EVENT_MOMENTUM or TREND thesis into MEAN_REVERSION without closing and re-underwriting;
- calibrate stop buffers and time windows with MFE/MAE and forward data;
- preserve gap-through-stop and limit-down execution risk.

## 9. Validation maturity: three evidence levels

### Level A — Integration / Case Validation

Purpose: verify that the system follows its own rules.

Tests include:

```text
publication timestamp is correct
first_tradable_timestamp is session-aware
future information is not used
state transitions follow schema
positive headlines are not automatically treated as surprise
no-trade is represented correctly
Champion and Challenger do not contaminate each other
```

The 2026-08-28 eight-stock cohort is primarily a Level-A artifact.

Level A cannot establish alpha.

### Level B — Historical Point-in-Time Research Validation

Purpose: test statistical discrimination and robustness over historical data.

Requirements include:

```text
true PIT timestamps
survivorship-aware universe
corporate actions
T+1 / limits / suspension
transaction costs / slippage
frozen benchmark contract
frozen reaction-window contract
ablation
placebo / negative control
regime and event-family breakdown
trial ledger
```

Outputs include Expectancy_R, PF, MDD, CVaR, turnover, MFE/MAE, FP/FN, coverage and parameter stability.

Level B can reject hypotheses and estimate conditional effects, but heavily tuned results still require untouched evidence.

### Level C — Untouched Forward Validation

Purpose: evaluate decisions generated in real time before outcomes are known.

Requirements:

```text
immutable pre-outcome records
same production data timing
same execution assumptions
same risk budget
cost-aware outcomes
NO_TRADE opportunity cost
Champion/Challenger disagreement outcomes
```

Level C is the principal evidence source for component Promotion Review.

## 10. Acceptance matrix

Repository status must distinguish:

```text
DESIGN_COMPLETE
INTEGRATION_PASS
HISTORICAL_RESEARCH_PENDING
FORWARD_DATA_ACCUMULATING
STATISTICAL_REVIEW_PENDING
PROMOTION_NOT_PROVEN
```

A component may simultaneously be:

```text
integration = PASS
alpha_status = NOT_PROVEN
```

This wording is preferred to ambiguous statements such as "the model works".

## 11. Model disagreement is first-class research data

Agreement is correlated. Disagreement is where incremental information can be measured.

Use `disagreement-ledger-and-negative-control.md` to answer:

```text
Which disagreement type occurred?
Which model avoided a false positive?
Which model missed a valid opportunity?
What was the subsequent MFE/MAE/realized R?
Did stricter filtering reduce tail loss at the cost of blocked upside?
```

Primary discriminator:

```text
Net Disagreement Expectancy Delta
```

not raw agreement count.

## 12. Current research status

As of 2026-08-28 after the v1.7 integration work:

```text
Champion = ACTIVE
Causal Challenger / ERG = SHADOW ONLY
Session-aware PIT = ACTIVE
2026-08-28 Forward baseline = FROZEN
Disagreement Ledger = ACTIVE
Placebo / negative control protocol = ACTIVE
A/B/C/D/E VNext directions = ACTIVE RESEARCH CATALOG
Alpha promotion = NOT PROVEN
```

## 13. Governance rule for future additions

Every new concept must be classified as one of:

```text
FACT / EXECUTION CORRECTION
GOVERNANCE / AUDITABILITY
ALPHA HYPOTHESIS
RISK HYPOTHESIS
COMPLEXITY REDUCTION
PRESENTATION LANGUAGE
```

Only factual/execution corrections and governance/auditability changes may become active without alpha evidence, provided they do not silently increase production risk.

Alpha/risk hypotheses enter Challenger tracks and require frozen experiments.

Presentation language cannot change machine decisions.