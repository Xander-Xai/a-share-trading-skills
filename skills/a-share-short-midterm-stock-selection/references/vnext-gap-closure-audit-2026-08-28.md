# VNext Gap-Closure Audit — 2026-08-28

> Status: `ACTIVE AUDIT SNAPSHOT`
>
> Purpose: verify which items from the multi-round methodology review are already implemented, which were only partially represented, and which still require empirical work.

## 1. Audit principle

This audit separates four categories:

```text
IMPLEMENTED_GOVERNANCE
IMPLEMENTED_MEASUREMENT_INFRASTRUCTURE
EMPIRICAL_RESULT_PENDING
NOT_YET_IMPLEMENTED
```

A document or schema existing in the repository is not automatically evidence that a trading edge exists.

## 2. Items already completed before this audit

| Item | Status | Evidence path |
|---|---|---|
| ERG integrated into Challenger Shadow path | IMPLEMENTED_GOVERNANCE | `SKILL.md`, `causal-challenger-model.md` |
| State First, Rank Second | IMPLEMENTED_GOVERNANCE | `SKILL.md` |
| Research State / Position State separation | IMPLEMENTED_GOVERNANCE | `SKILL.md`, `erg-output-schema.md` |
| Strategy-type lock | IMPLEMENTED_GOVERNANCE | `SKILL.md` |
| Source provenance / `source_tier` | IMPLEMENTED_GOVERNANCE | `erg-output-schema.md` |
| Roadmap wired into active Skill path | IMPLEMENTED_GOVERNANCE | `SKILL.md` |
| Session-aware A-share execution calendar | IMPLEMENTED_GOVERNANCE | `session-aware-execution-calendar.md` |
| 2026-08-28 eight-stock Forward baseline | IMPLEMENTED_MEASUREMENT_INFRASTRUCTURE | `examples/2026-08-28-eight-stock-forward-cohort.*` |
| Disagreement Ledger | IMPLEMENTED_MEASUREMENT_INFRASTRUCTURE | `disagreement-ledger-and-negative-control.md` |
| Placebo / negative control | IMPLEMENTED_MEASUREMENT_INFRASTRUCTURE | `disagreement-ledger-and-negative-control.md` |
| No-trade opportunity-cost fields | IMPLEMENTED_MEASUREMENT_INFRASTRUCTURE | disagreement/forward protocols |
| A/B/C/D/E independent VNext tracks | IMPLEMENTED_GOVERNANCE | `vnext-experiment-directions.md/json` |
| Statistical promotion guard | IMPLEMENTED_GOVERNANCE | `statistical-promotion-guard.md` |

## 3. Gaps found in the methodology report that were not yet fully operationalized

### Gap A — Prior methods still lacked an explicit consolidation contract

The repository had Champion/Challenger governance, but the multi-round conclusion was not yet formalized as:

```text
broad analysis = research layer
Champion = active baseline/ranker
manual integrated method = explanation/execution support
V2/ERG = causal Challenger
validation system = final arbiter
```

Risk: future iterations could recreate pseudo-ensemble voting or add Method V5/V6/V7 without independent structure.

Action in this audit:

```text
methodology-consolidation-and-validation-contract.md = ADDED
```

### Gap B — Market-language insights were not separated from machine fields

The six non-equivalences and the human mnemonic `票—事—钱—位—错—仓` were useful, but not yet encoded as a presentation-only contract.

Risk: phrases such as "资金认可" or "位置不错" can drift back into subjective decision rules.

Action:

```text
human-language mapping = ADDED
machine-field separation = REQUIRED
```

### Gap C — Decision robustness and return validation were not explicitly separated

The eight-stock multi-method ranking showed high stability, but the repository did not yet explicitly prevent rank agreement from being interpreted as independent return evidence.

Action:

```text
Decision Robustness != Return Validation = FORMALIZED
rank/state stability diagnostics = ADDED
```

### Gap D — Benchmark selection remained a researcher degree of freedom

Track A described the issue, but there was no standalone active measurement contract requiring the benchmark to be frozen before outcomes.

Action:

```text
benchmark-and-reaction-window-contract.md = ADDED
```

### Gap E — Reaction-window selection remained a researcher degree of freedom

ERG stored D1/D3/D5-style outcomes but did not yet have a formal primary-window freeze rule.

Action:

```text
primary reaction-window contract = ADDED
current event-family primary windows = UNRESOLVED_RESEARCH
```

No D1/D3/D5 primary window was selected by intuition.

### Gap F — ERG schema did not carry benchmark/window provenance

Action:

```text
erg-output-schema.md v1.1 -> v1.2
benchmark_contract fields = ADDED
reaction_window_contract fields = ADDED
benchmark/window sensitivity fields = ADDED
expectation coverage flag = ADDED
```

### Gap G — R/R geometry versus expectancy was not formalized as a validation distinction

Action:

```text
R/R = entry geometry / governance parameter
Expectancy_R = outcome metric
future target = E[R | event_type, state, basis, regime, execution_state]
```

### Gap H — Validation maturity was described in conversation but not formalized

Action:

```text
Level A = Integration / Case Validation
Level B = Historical PIT Research Validation
Level C = Untouched Forward Validation
```

The repository now distinguishes `integration PASS` from `alpha NOT_PROVEN`.

## 4. Items intentionally not declared complete

### 4.1 Forward outcomes

Status:

```text
EMPIRICAL_RESULT_PENDING
```

The 2026-08-28 cohort is frozen, but +1D/+3D/+5D/+10D/+20D outcomes must occur and be appended later.

No outcome is fabricated in advance.

### 4.2 ERG ablation A→F

Status:

```text
EMPIRICAL_RESULT_PENDING
```

Infrastructure exists; results do not.

### 4.3 Track A benchmark and reaction-window efficacy

Status:

```text
measurement contract = IMPLEMENTED
primary event-family windows = UNRESOLVED_RESEARCH
expectation calibration = PENDING
alpha increment = NOT_PROVEN
```

The contract can be active before any benchmark/window choice is promoted.

### 4.4 Track C execution/overreaction fields

Status:

```text
NOT_YET_IMPLEMENTED
```

Still requires limit-hit density, extension/gap diagnostics, price-progress efficiency and stress-loss experiment fields.

### 4.5 Track E Champion simplification ablations

Status:

```text
NOT_YET_IMPLEMENTED
```

Requires reproducible baseline replay before one-at-a-time component removal.

### 4.6 Track B conditional participation

Status:

```text
NOT_YET_IMPLEMENTED
```

Blocked on PIT positioning/ownership data coverage and staleness audit.

### 4.7 Historical 5–10 year PIT validation dataset

Status:

```text
NOT_YET_COMPLETE
```

Required before broad historical inference. Must include survivorship handling, event timestamps, corporate actions, T+1, price limits, suspensions, costs and PIT benchmark membership/classification.

### 4.8 PBO / DSR / Reality Check numerical results

Status:

```text
GOVERNANCE_AVAILABLE
NUMERICAL_RESULT_PENDING
```

These diagnostics should not be invented before sufficient trial/performance history exists.

## 5. Legacy cohort protection

The 2026-08-28 Forward baseline predates the new benchmark/window contract.

Therefore:

```text
original baseline fields = immutable
new benchmark/window calculations = supplemental post-hoc diagnostics
new contract = required for future Forward cohorts
```

Do not retrofit the new contract into the old cohort and relabel it as pre-outcome evidence.

## 6. Track status after this audit

```text
D0 Disagreement Measurement = STARTED
A1 Benchmark Contract Infrastructure = ACTIVE / NO RESULT
A2 Reaction Window Contract Infrastructure = ACTIVE / PRIMARY WINDOWS UNRESOLVED
A3 Expectation Calibration = PENDING
A4 Prepricing Normalization = PENDING
C Execution Shield = PROPOSED
E Simplification = PROPOSED
B Conditional Participation = PROPOSED / DATA-AUDIT BLOCKED
```

## 7. Current maturity statement

Use this wording until evidence changes:

```text
Research framework: ACTIVE
Integration validation: PARTIALLY PASSED across implemented modules
Forward data: ACCUMULATING
Historical PIT validation: INCOMPLETE
Statistical promotion evidence: INCOMPLETE
Alpha promotion: NOT PROVEN
```

## 8. Next measurable work

Without adding another full methodology, the next work items are:

```text
1. Append future outcomes to the frozen 2026-08-28 cohort when they occur.
2. Build Track C fields and freeze C0→C4 experiments.
3. Use the new benchmark/window contract on the next event cohort.
4. Start Track A3 expectation-coverage calibration when PIT expectation data is available.
5. Start Track E one-at-a-time ablations after baseline replay is reproducible.
6. Audit PIT positioning data before Track B implementation.
7. Build historical Level-B PIT datasets and run ablation/placebo.
8. Apply DSR/PBO/Reality-Check-style controls only after enough trials exist.
```

The repository should prefer measurable closure of these items over adding additional narrative features.