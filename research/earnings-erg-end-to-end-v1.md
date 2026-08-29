# Earnings ERG End-to-End Pipeline v1

## Objective

Turn the already-implemented EARNINGS ERG components into one deterministic Shadow research run:

```text
Frozen PIT Snapshot
├─ Expectation / Surprise
├─ Earnings Materiality
└─ source-backed financial lineage

Frozen EventReactionMeasurement
├─ Prepricing measurement
└─ Reaction measurement

Frozen Assembly Contract
├─ Eligibility
├─ Prepricing classification lineage
└─ Reaction classification lineage

↓
ERGEvidenceBundle
↓
ERGShadowDecision
↓
EarningsERGRun
```

## Why this stage matters

Before v1, the component implementations could each be valid while an analyst still assembled them inconsistently. Examples:

- Surprise uses one earnings statement while Materiality uses another revision;
- event id or event clock differs between the price-reaction artifact and the accounting event;
- a later D5 reaction artifact is accidentally used in a D1 replay;
- resolved Prepricing/Reaction is supplied without a frozen classification-contract reference.

The pipeline makes these joins explicit and fail closed.

## Current guarantees

### Cross-component consistency

v1 requires:

```text
same security
same earnings event
same information timestamp
same first tradable timestamp
same current financial statement for Surprise and Materiality
same primary financial metric for Surprise and Materiality
```

### Historical replay clock

Every reaction window contained in the supplied measurement must end no later than the run `as_of` local date.

This prevents an otherwise valid measurement artifact from carrying future information into an earlier replay.

### Content-addressed identity

One run receives a deterministic `run_id` over:

```text
pipeline version
strategy / sleeve
data snapshot
as_of
assembly contract
component result ids
event measurement id
ERG evidence bundle
Shadow decision
```

A persisted package additionally receives an `artifact_id` over its full serialized contents.

## What remains manual

The pipeline is end-to-end orchestration, not yet fully automatic evidence discovery.

Still explicit/frozen upstream:

- exact expectation source selection;
- exact comparable financial statement;
- Materiality rule mode and thresholds if used;
- eligibility state;
- Prepricing categorical classification;
- Reaction categorical classification;
- reaction-window contract and benchmark-selection contract.

This is intentional. Hidden heuristics are worse than visible unresolved inputs.

## Promotion status

```text
ERG = SHADOW ONLY
Position State = FLAT
Executable = false
Alpha = NOT_PROVEN
```

The correct next research milestone is not broker integration. It is accumulation of immutable historical/forward `EarningsERGRun` artifacts so that disagreement, ablation, placebo and conditional expectancy can be evaluated under frozen contracts.
