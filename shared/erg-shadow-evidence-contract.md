# ERG Shadow Evidence Contract v0

> Status: `SHADOW RESEARCH IMPLEMENTATION CONTRACT`
>
> Scope: `a_share_short_mid / short_mid` only.
>
> This contract converts the existing Expectation-Reaction Gate specification into auditable machine evidence and a conservative research-state resolver. It does **not** authorize orders, replace Champion, or prove alpha.

## 1. Purpose

The production-research path is now:

```text
PIT Facts / Measurements
→ ERG Evidence Objects
→ content-addressed ERG Evidence Bundle
→ ERG Shadow State Machine v0
→ Research State
```

The state machine is intentionally separated from Position State:

```text
Research State
!= Position State
!= Order Authorization
```

Every v0 decision remains:

```text
position_state = FLAT
executable = false
```

## 2. Evidence bundle

The bundle contains five ERG evidence families plus hard-gate status:

```text
EligibilityEvidence
ExpectationEvidence
SurpriseEvidence
MaterialityEvidence
PrepricingEvidence
ReactionEvidence
```

The bundle identity is content-addressed:

```text
evidence_bundle_id = SHA256(canonical evidence content)
```

Any material change to evidence, source contract or classification contract changes the bundle identity.

## 3. Evidence references

Resolved evidence should preserve source lineage through `EvidenceRef`:

```text
ref
source_tier
source_snapshot_id
note
```

`ref` may point to a PIT record, disclosure, financial statement, guidance record, consensus record or other auditable artifact.

Source tiers remain:

```text
TIER1
TIER2
TIER3
TIER4
```

A higher source tier does not imply a stronger trading signal.

## 4. Hard-gate evidence

Allowed states:

```text
PASS
FAIL
UNRESOLVED
```

Rules:

```text
PASS
→ no failure reasons

FAIL / UNRESOLVED
→ explicit reasons required
```

The v0 state machine fails closed:

```text
FAIL or UNRESOLVED
→ research_state = REJECT
```

This reflects the existing Causal Challenger rule that unresolved critical PIT/data/execution gates cannot be compensated by other evidence.

## 5. Expectation evidence

Allowed baseline types follow the existing ERG contract:

```text
CONSENSUS_RECENT
COMPANY_GUIDANCE
EARNINGS_PREANNOUNCEMENT
BROKER_RANGE
MODEL_BASELINE
HISTORICAL_SEASONALITY
NONE
```

Confidence:

```text
HIGH
MEDIUM
LOW
```

Preserve when available:

```text
center
low
high
dispersion
coverage_count
coverage_flag
fiscal_period
metric
unit
evidence_refs
```

### Verified-surprise eligibility

v0 allows a surprise to be labeled `verified=true` only when the expectation baseline is sufficiently identified.

At minimum:

```text
baseline_type != NONE
confidence != LOW
coverage_flag != false
```

For `CONSENSUS_RECENT` specifically:

```text
coverage_count >= 2
```

This is not a claim that two analysts form an optimal consensus. It enforces the existing repository rule that one analyst estimate must not be relabeled as market consensus.

## 6. Surprise evidence

Allowed directions:

```text
POSITIVE
NEUTRAL
NEGATIVE
UNRESOLVED
```

Preserve rather than hide numerical logic:

```text
metric
actual
expected_center
delta
delta_pct
calculation_method
classification_contract_id
quarter_acceleration
evidence_refs
```

`verified=true` requires:

```text
direction != UNRESOLVED
calculation_method present
evidence_refs present
eligible expectation baseline
```

The machine does not convert high YoY growth into a positive surprise without an expectation baseline.

## 7. Materiality evidence

v0 intentionally uses a small categorical vocabulary:

```text
MATERIAL
LOW_MATERIALITY
UNRESOLVED
```

Resolved materiality requires:

```text
transmission_path
assessment_contract_id
```

`MATERIAL` additionally requires evidence references.

Optional quantified impact fields are stored as named metrics rather than compressed into one opaque score.

Examples:

```text
order_value_to_revenue
profit_delta_pct
margin_delta_bps
estimated_eps_delta
cash_flow_delta
```

Materiality may remain partly AI/human-assisted. The contract requires provenance and an explicit assessment contract; it does not pretend all economic transmission can be reduced to deterministic arithmetic.

## 8. Prepricing evidence

Allowed states:

```text
UNDERPRICED
PARTIALLY_PRICED
HEAVILY_PRICED
UNRESOLVED
```

A resolved state requires:

```text
event_measurement_id
classification_contract_id
```

The classification contract is required because the repository has not promoted arbitrary thresholds such as:

```text
CAR20 > X%
→ HEAVILY_PRICED
```

without prior validation.

## 9. Reaction evidence

Allowed states:

```text
POSITIVE_CONFIRMATION
MIXED
NEGATIVE_DISAGREEMENT
UNRESOLVED
```

A resolved state requires:

```text
event_measurement_id
classification_contract_id
```

Optional lineage includes:

```text
primary_reaction_window_sessions
benchmark_id
benchmark_selection_contract_id
metrics
```

Prepricing and Reaction must reference the same event measurement when both are resolved.

## 10. Conservative ERG Shadow State Machine v0

The state machine implements only relationships already supported by the ERG governance. It does not invent new numerical thresholds.

### 10.1 Hard gate

```text
Eligibility != PASS
→ REJECT
```

### 10.2 Materiality

```text
LOW_MATERIALITY
→ WATCH

UNRESOLVED materiality
→ WATCH
```

v0 deliberately refuses to promote an event to `CANDIDATE` before economic materiality is established.

### 10.3 Incomplete expectation / reaction evidence

When materiality is `MATERIAL`:

```text
surprise not verified
→ CANDIDATE

reaction UNRESOLVED
→ CANDIDATE

prepricing UNRESOLVED
→ CANDIDATE
```

### 10.4 Expectation-Reaction matrix

With materiality resolved and Prepricing resolved:

```text
verified POSITIVE surprise
+ POSITIVE_CONFIRMATION reaction
→ CONFIRMED
→ confirmation_basis = EVENT_REACTION

verified NEGATIVE surprise
+ NEGATIVE_DISAGREEMENT reaction
→ INVALIDATED

verified POSITIVE surprise
+ NEGATIVE_DISAGREEMENT reaction
→ CANDIDATE
→ disagreement / priced-in re-underwrite

verified NEGATIVE surprise
+ POSITIVE_CONFIRMATION reaction
→ CANDIDATE
→ expectations may have been worse; re-underwrite

other mixed combinations
→ CANDIDATE
```

This is a **research-state** matrix only.

## 11. Why resolved Prepricing is required for v0 CONFIRMED

The ERG causal sequence explicitly includes:

```text
Expectation
→ Surprise
→ Materiality
→ Prepricing
→ Reaction
```

Therefore v0 does not permit:

```text
positive surprise + positive reaction + unknown prepricing
→ CONFIRMED
```

Instead it remains `CANDIDATE` until the missing causal layer is resolved.

This is intentionally conservative. Future research may revise this behavior only through a versioned experiment and governance change.

## 12. State-machine output

Every output preserves:

```text
decision_id
state_machine_version
evidence_bundle_id
strategy_id
sleeve
research_state
reason_code
reason
confirmation_basis
position_state
executable
```

Current machine version:

```text
ERG_SHADOW_STATE_V0
```

Decision identity is deterministic and content-addressed.

## 13. Strategy boundary

This implementation must reject:

```text
a_share_long_retirement / long
```

The long-term engine may share upstream facts such as financial statements, corporate actions and benchmark data, but it must not inherit:

```text
short-horizon Surprise/Reaction matrix
prepricing windows
post-event confirmation
ERG research-state transitions
R-based tactical risk
```

without a separate long-term contract.

## 14. What v0 does not do

v0 does not:

- choose the benchmark;
- choose the primary reaction window;
- invent Prepricing thresholds;
- invent Reaction thresholds;
- infer Materiality from headline sentiment;
- derive Position State;
- change risk budgets;
- send or recommend broker orders;
- replace Champion;
- prove ERG alpha.

## 15. Promotion boundary

The output remains Shadow evidence.

Any future expansion must still pass:

```text
PIT validation
→ Forward
→ Ablation
→ Placebo / negative control
→ Statistical Promotion Guard
→ human review
```

before any component can affect production strategy behavior.
