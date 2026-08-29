# Earnings ERG End-to-End Contract v1

Status: **SHADOW RESEARCH ONLY**

Scope:

```text
a_share_short_mid / short_mid
EARNINGS only
```

This contract assembles already-governed PIT facts and measurements into one reproducible ERG Shadow run. It does not authorize Position State changes or orders.

## 1. Required lineage

Every run freezes and records:

```text
data_snapshot_id
expectation_surprise_contract_id
earnings_materiality_contract_id
event_measurement_id
assembly_contract_id
expectation_surprise_result_id
earnings_materiality_result_id
evidence_bundle_id
shadow_decision_id
run_id
```

Changing any frozen component creates a different identity.

## 2. Event identity

v1 requires the same:

```text
event_id
security_id
information_timestamp
first_tradable_timestamp
```

across the assembly contract and EventReactionMeasurement.

The event family is fixed to:

```text
EARNINGS
```

## 3. Surprise / Materiality source consistency

For v1:

```text
ExpectationSurpriseContract.actual_record_id
==
EarningsMaterialityContract.current_record_id
```

and:

```text
ExpectationSurpriseContract.metric
==
EarningsMaterialityContract.primary_metric
```

This prevents a run from calling one financial statement/metric the Surprise source while using a different statement/metric to justify Materiality.

## 4. Prepricing / Reaction classification

The pipeline does not invent thresholds.

Resolved Prepricing requires:

```text
prepricing_state != UNRESOLVED
prepricing_window_sessions
prepricing_classification_contract_id
```

The requested prepricing window must exist exactly once in the supplied EventReactionMeasurement.

Resolved Reaction requires:

```text
reaction_state != UNRESOLVED
reaction_classification_contract_id
```

and the EventReactionMeasurement must already contain a primary reaction window frozen by its reaction-window contract.

Therefore:

```text
measurement
!= classification
```

and:

```text
classification
!= promotion
```

## 5. Forward-clock guard

A run cannot consume EventReactionMeasurement windows extending beyond the run `as_of`.

```text
reaction_metric.end_date > as_of local date
-> reject
```

This is required even when the measurement id itself is valid, because a content-addressed artifact can still contain information that was not observable at the requested historical replay time.

## 6. Eligibility

Eligibility is explicit in the assembly contract:

```text
PASS
FAIL
UNRESOLVED
```

Non-PASS states require reasons. The ERG v0 state machine remains fail closed:

```text
Eligibility != PASS
-> REJECT
```

A later production phase should replace manually assembled eligibility with a source-backed eligibility producer. v1 makes the unresolved dependency visible rather than hiding it.

## 7. Research / execution separation

The pipeline consumes `ERGShadowStateMachine` and therefore preserves:

```text
position_state = FLAT
executable = false
```

Even:

```text
research_state = CONFIRMED
```

is not an order authorization.

## 8. Long-term boundary

Financial statements and other PIT facts are shared facts. The following v1 artifacts are tactical and must not mutate the long-term retirement sleeve:

```text
Expectation / Surprise classification
Earnings Materiality tactical classification
Prepricing
Reaction
ERG Research State
```

The long-term engine keeps separate Quality / Cash Flow / Dividend / Valuation / Expected IRR logic.

## 9. Persisted run artifact

The runtime writes one idempotent JSON artifact named:

```text
<run_id>.json
```

containing:

```text
run
expectation_surprise
earnings_materiality
event_measurement
artifact_id
```

If a file with the same run id already exists but bytes differ, the runtime refuses to overwrite it.

## 10. Non-claims

v1 does not prove:

- ERG alpha;
- optimal Materiality thresholds;
- optimal Prepricing thresholds;
- optimal Reaction thresholds;
- optimal reaction windows;
- execution edge.

Champion, shared risk caps and `AUTO_ORDER=false` remain unchanged.
