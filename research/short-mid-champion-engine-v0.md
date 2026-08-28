# Short/Mid Champion Engine v0

> Status: `IMPLEMENTED AGGREGATION CORE / DETERMINISTIC MARKET FEATURE SLICE STARTED / FULL SCORE COMPUTATION INCOMPLETE`
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
runtime/champion_score.py
runtime/tests/test_feature_snapshot_champion.py
```

The first low-subjectivity market feature slice is also now implemented under:

```text
src/features/short_mid_market.py
runtime/short_mid_market_features.py
runtime/tests/test_short_mid_market_features.py
shared/short-mid-market-feature-contract.md
```

This remains **v0** because the system still does not automatically infer every qualitative Champion sub-score from canonical market/filing data.

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

## 5. What is now deterministic

The first market feature slice computes low-subjectivity fields from canonical PIT data, including:

```text
1/5/10/20-session return
MA5 / MA10 / MA20
close-to-MA distance
20-session high distance
RVOL 1 vs prior 20
turnover ratio 1 vs prior 20
gap / range / close-vs-open
suspension/action observations
```

These computations are not allowed to assume that an observed row set is complete.

Trailing features become `AVAILABLE` only when the caller explicitly supplies verified:

```text
daily_bar_coverage_confirmed = true
corporate_action_coverage_confirmed = true
```

Otherwise adjustment-sensitive fields remain `UNRESOLVED`.

This prevents:

```text
no observed corporate-action row
→ falsely conclude no corporate action occurred
```

and prevents unadjusted-price series from being treated as continuously adjusted without proof.

## 6. What v0 still does not do

The current engine does **not** claim that all Champion sub-scores are fully automated:

```text
trend_quality = 7.2
industry_position = 2.0
catalyst.materiality = 4.0
...
```

The current market features remain measurements:

```text
market.return_20d_pct
market.rvol_1_vs_20
market.close_to_ma10_pct
...
```

They are **not** silently mapped into score points.

For example, the repository does not currently assert:

```text
return_20d > X
→ trend_quality = 8
```

because that would introduce a new threshold/parameter choice requiring its own research and frozen validation contract.

The remaining feature families must be classified into:

```text
fully deterministic from canonical data
AI-assisted with evidence
human-reviewed
```

before their score mapping can be automated.

## 7. Execution boundary

Champion v0 never authorizes a broker order:

```text
execution_authorized = false
```

A high score or `research_eligible=true` is not an execution command.

Portfolio sizing, account caps, T+1, broker truth, reconciliation and human/automation approval remain downstream governance layers.

## 8. Long-term isolation

The engine enforces:

```text
strategy_id = a_share_short_mid
sleeve = short_mid
```

A long-term feature snapshot cannot be scored by this Champion or by the Short/Mid market-feature builder.

Nothing in this implementation changes the long-term retirement methodology or imports Short/Mid score thresholds, ERG state, R-based risk, gap logic, RVOL or short-horizon reaction semantics into the long sleeve.

## 9. Production significance

The current path has advanced from:

```text
Skill prose
→ human/AI interpretation
→ score
```

through:

```text
data_snapshot_id
→ feature_snapshot_id
→ frozen Champion config
→ deterministic aggregation/veto/confidence/regime logic
→ reproducible score result
```

and now begins replacing subjective inputs with machine-computed, PIT-linked measurements.

The remaining major gap is **feature-to-score mapping and non-market feature computation**, not score arithmetic.

## 10. Next step

Prioritize infrastructure that makes the current market features objectively usable before inventing thresholds:

```text
trading-calendar coverage verification
corporate-action completeness / adjustment factors
broad/sector benchmark series
relative strength / abnormal return
session / price-limit / board facts
```

Then research deterministic mapping candidates through frozen historical/forward experiments.

Do not begin by automating highly subjective fields such as moat, business materiality or concept authenticity without an evidence/review contract.
