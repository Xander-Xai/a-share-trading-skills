# Dataset Coverage v1 Implementation Note

> Status: `IMPLEMENTED RESOLUTION INFRASTRUCTURE / REAL COVERAGE PRODUCERS PENDING`

## Why this exists

The previous Short/Mid market-feature implementation intentionally refused to infer completeness from row presence. It still accepted caller-supplied booleans such as:

```text
daily_bar_coverage_confirmed=true
corporate_action_coverage_confirmed=true
```

That was acceptable as an intermediate fixture contract but unsafe as a production-facing runtime interface.

This implementation replaces the runtime trust boundary with PIT-backed evidence.

## Implemented

```text
src/data/coverage.py
src/features/short_mid_verified.py
runtime/tests/test_dataset_coverage.py
shared/dataset-coverage-contract.md
```

The runtime market-feature CLI now resolves coverage from `DATASET_COVERAGE` records inside the frozen `data_snapshot_id`.

## What is now deterministic

The resolver checks:

```text
dataset family
requested date containment
scope specificity
PIT-visible latest assertion
completeness status
accepted verification method
```

and returns an explicit reason such as:

```text
CONFIRMED
NO_APPLICABLE_COVERAGE_ASSERTION
VERIFICATION_METHOD_NOT_ACCEPTED
ASSERTION_NOT_COMPLETE
```

## Adversarial properties

The implementation explicitly rejects these shortcuts:

```text
empty action table => no action occurred
row count alone => complete calendar coverage
manual assumption => production-confirmed coverage
broader exchange complete => overrides newer security partial
```

## Current limitation

No real live coverage producer has been promoted yet.

So this PR improves the trust boundary but does not claim that live DAILY_BAR or CORPORATE_ACTION coverage is already production-complete.

The next concrete step is to implement real reconciliation producers and then use the same mechanism for benchmark/index series before relative-strength / abnormal-return automation.

## Strategy boundary

Coverage infrastructure is shared, but the consumer in this implementation is strictly:

```text
strategy_id = a_share_short_mid
sleeve = short_mid
```

Long-term logic remains separate. Short-horizon MA/return/RVOL semantics are not introduced into the long sleeve.
