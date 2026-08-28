# Official Corporate Action Coverage v1

> Status: `IMPLEMENTED NORMALIZATION/COVERAGE CORE / LIVE SOURCE CAPTURE PENDING`

## Problem

Short/Mid trailing features now fail closed when corporate-action coverage is not proven.

The remaining gap was that the repository could consume:

```text
DATASET_COVERAGE(CORPORATE_ACTION)
```

but had no official-source batch contract capable of producing that proof.

## v1 implementation

Add:

```text
src/data/official_corporate_actions.py
runtime/tests/test_official_corporate_actions.py
shared/official-corporate-action-source-contract.md
```

The new source path is:

```text
official SSE/SZSE implemented-action enumeration
→ RawEvidenceArchive snapshot
→ OfficialCorporateActionBatch
→ canonical CORPORATE_ACTION rows
→ DATASET_COVERAGE(CORPORATE_ACTION)
→ PITStore
→ VerifiedShortMidMarketFeatureBuilder
```

## Stronger completeness rule

A complete batch is not accepted just because a caller sets a boolean.

`CONFIRMED_COMPLETE` requires both:

```text
1. source_snapshot_id is a SHA-256 RawEvidenceArchive id
2. source_row_count == normalized row count
```

This closes two failure modes:

- row absence without evidence;
- parser/drop errors hidden behind a completeness flag.

## PIT behavior

Coverage becomes available only at `observed_at`.

An individual action can use an earlier exact `published_at` when that timestamp is known and no later than first observation.

Otherwise the action remains visible only from first observation.

This is intentionally conservative for historical replay.

## Scope semantics

v1 supports:

```text
SECURITY
EXCHANGE
```

A complete empty SECURITY batch is meaningful:

```text
source scope contains no implemented ex-date action
→ corporate-action absence can be proven for that security/range
```

Without such positive source coverage, zero normalized rows remain unresolved.

## What is not claimed

This PR does not claim that the repository already possesses a complete real 2026 corporate-action archive.

No live SSE/SZSE network transport is promoted here.

The next source step is to capture official/approved corporate-action surfaces into `RawEvidenceArchive`, then feed those immutable snapshots into the batch adapter.

## Downstream effect

Once real corporate-action coverage is present alongside DAILY_BAR coverage:

```text
unadjusted canonical prices
+ corporate-action facts
→ deterministic adjustment-factor research
→ adjusted return / MA / RS inputs
```

That should be completed before expanding benchmark abnormal-return, prepricing and ERG reaction automation.

## Governance unchanged

```text
Champion = unchanged
ERG = SHADOW ONLY
AUTO_ORDER = false
Alpha = NOT_PROVEN
```

Corporate-action facts are shared infrastructure; tactical return windows remain Short/Mid-only.
