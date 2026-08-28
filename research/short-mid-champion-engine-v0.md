# Short/Mid Champion Engine v0

> Status: `IMPLEMENTED AGGREGATION CORE / FEATURE COMPUTATION INCOMPLETE`
>
> Strategy: `a_share_short_mid`
>
> Sleeve: `short_mid`

## 1. What changed

The Short/Mid Champion is no longer only a prose scoring specification.

The repository now contains a machine-executable aggregation core:

```text
configs/short_mid/champion-v1.json
src/features/snapshot.py
src/strategies/short_mid/champion.py
runtime/tests/test_feature_snapshot_champion.py
```

This is intentionally **v0** because the system still does not automatically infer every qualitative Champion sub-score from canonical market/filing data.

## 2. Frozen current Champion contract

The machine config preserves the current production-research baseline:

```text
Technical 30
Capital Participation 30
Fundamentals 25
Catalyst 15
```

with the existing criterion caps, penalty caps and score thresholds.

The config validates both:

```text
criterion caps → exact section cap
section caps → exact 100-point base
```

so a malformed config cannot silently preserve a 100 total while changing the intended 30/30/25/15 structure.

## 3. Hard vetoes are non-compensatory

All frozen hard-veto families must be explicitly evaluated as booleans before scoring:

```text
universe_membership
identity_unresolved
st_delisting_risk
suspension_execution
regulatory_accounting_governance
concept_business_evidence
invalidation_undefined
gap_price_limit_risk_budget
portfolio_risk_limit
data_completeness
```

A 100-point raw/final score cannot override an active hard veto.

Missing a required veto field fails closed.

## 4. Confidence and regime behavior

The scorer preserves current governance semantics:

```text
High / Medium confidence
→ may pass the research-eligibility gate if other rules pass

Low confidence
→ not research-eligible for an executable candidate even if score is high
```

Risk-off regimes add the frozen practical entry-score buffer without rewriting the underlying Champion score.

This separates:

```text
ranking score
from
practical research eligibility
```

## 5. What v0 does not do

The current engine does **not** claim that these sub-scores are already fully automated:

```text
trend_quality = 7.2
industry_position = 2.0
catalyst.materiality = 4.0
...
```

Those values must come from a versioned `FeatureSnapshot` and are rejected when required values are missing or unresolved.

The next implementation layer must determine, one feature at a time, which inputs are:

```text
fully deterministic from canonical data
AI-assisted with evidence
human-reviewed
```

and then freeze each calculation/research contract.

## 6. Execution boundary

Champion v0 never authorizes a broker order:

```text
execution_authorized = false
```

A high score or `research_eligible=true` is not an execution command.

Portfolio sizing, account caps, T+1, broker truth, reconciliation and human/automation approval remain downstream governance layers.

## 7. Long-term isolation

The engine enforces:

```text
strategy_id = a_share_short_mid
sleeve = short_mid
```

A long-term feature snapshot cannot be scored by this Champion.

Nothing in this implementation changes the long-term retirement methodology or imports Short/Mid score thresholds, ERG state, R-based risk or short-horizon reaction semantics into the long sleeve.

## 8. Production significance

Before this change:

```text
Skill prose
→ human/AI interpretation
→ score
```

After v0:

```text
data_snapshot_id
→ feature_snapshot_id
→ frozen Champion config
→ deterministic aggregation/veto/confidence/regime logic
→ reproducible score result
```

The remaining major gap is feature computation, not score aggregation.

## 9. Next step

Implement a first deterministic Short/Mid feature-computation slice from canonical data, prioritizing low-subjectivity fields such as:

```text
price/return structure
relative strength
turnover / RVOL
basic trend geometry
price extension
session/execution facts
data completeness
```

Do not begin by automating highly subjective fields such as moat, business materiality or concept authenticity without an evidence/review contract.
