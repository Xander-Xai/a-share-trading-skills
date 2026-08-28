# ERG Shadow Evidence + State Machine v0

> Status: `IMPLEMENTED SHADOW RESEARCH INFRASTRUCTURE`

## Objective

Convert the existing ERG methodology from prose-only governance into a reproducible machine layer without introducing unvalidated numeric thresholds.

## Implementation

Added:

```text
src/features/erg_shadow.py
runtime/build_erg_shadow.py
runtime/tests/test_erg_shadow.py
shared/erg-shadow-evidence-contract.md
```

The implementation separates:

```text
Evidence
!= Research State
!= Position State
!= Execution
```

## Evidence objects

```text
EligibilityEvidence
ExpectationEvidence
SurpriseEvidence
MaterialityEvidence
PrepricingEvidence
ReactionEvidence
```

These are assembled into a deterministic:

```text
ERGEvidenceBundle
```

with SHA-256 identity.

## Key fail-closed rules

### Expectation

`NONE` / `LOW` expectation cannot support `verified=true` surprise.

For `CONSENSUS_RECENT`, one analyst estimate is rejected as consensus. A verified surprise requires at least two observations plus non-low confidence; this is a minimum semantic guard, not a claim that two analysts are statistically sufficient.

### Materiality

Resolved materiality requires:

```text
transmission_path
assessment_contract_id
```

`MATERIAL` additionally requires source evidence.

### Prepricing / Reaction

Resolved categorical states require explicit classification contract ids.

The code therefore does not silently create rules such as:

```text
CAR20 > 8%
→ HEAVILY_PRICED
```

or:

```text
AR1 > 2%
→ POSITIVE_CONFIRMATION
```

Those remain future experiment parameters.

## State machine v0

```text
Eligibility != PASS
→ REJECT

LOW_MATERIALITY
→ WATCH

UNRESOLVED materiality
→ WATCH

MATERIAL + unverified surprise
→ CANDIDATE

MATERIAL + verified surprise + unresolved reaction/prepricing
→ CANDIDATE

verified positive surprise
+ resolved prepricing
+ positive reaction
→ CONFIRMED / EVENT_REACTION

verified negative surprise
+ resolved prepricing
+ negative reaction
→ INVALIDATED

positive surprise + negative reaction
→ CANDIDATE / re-underwrite

negative surprise + positive reaction
→ CANDIDATE / re-underwrite
```

All outputs remain:

```text
position_state = FLAT
executable = false
```

## Deliberate conservatism

The existing ERG architecture places Prepricing before Reaction. v0 therefore requires resolved Prepricing before `EVENT_REACTION` confirmation.

This is a governance choice for the first executable state machine, not a claim that unresolved Prepricing is empirically proven to destroy alpha. If future ablation shows this rule is too restrictive, it should change only through a versioned Challenger experiment.

## Strategy boundary

The module enforces:

```text
a_share_short_mid / short_mid
```

It rejects the long-term retirement sleeve.

Shared financial facts remain reusable across sleeves, but event-reaction state logic remains tactical.

## Current limitations

The machine does not yet automatically construct all upstream evidence from PIT canonical records.

In particular, future work is still required for:

```text
ConsensusExpectation / Guidance -> ExpectationEvidence adapter
FinancialStatement / event payload -> Surprise calculation adapters
Event-family-specific Materiality assessment contracts
Prepricing classification calibration
Reaction classification calibration
```

Therefore the correct current label is:

```text
ERG machine evidence/state infrastructure = IMPLEMENTED
ERG fully automated evidence extraction     = INCOMPLETE
ERG alpha                                  = NOT_PROVEN
ERG production promotion                   = NOT AUTHORIZED
```

## Next engineering step

Build source-backed evidence adapters, starting with the least subjective path:

```text
PIT CompanyGuidance / EarningsPreannouncement / ConsensusExpectation
+ PIT reported metric
→ ExpectationEvidence
→ SurpriseEvidence
```

Then add event-family-specific Materiality contracts before attempting broader automatic ERG classification.
