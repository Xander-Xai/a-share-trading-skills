# Repository Consistency Audit — 2026-08-26

## Scope

This audit checks the current `main` branch after the v3 research-governance upgrade for stale rules, contradictory parameters, Champion/Challenger leakage, and policy-precedence problems across:

- root `README.md`
- `shared/` capital / automation / research governance
- long-term retirement Skill and README
- short/mid-term trading Skill and README
- new Challenger / Forward-Test / MFE-MAE / IRR references
- existing methodology / execution / scoring / research references

Historical dated snapshots are treated as records, not current policy.

## Governing hierarchy

The repository now uses:

```text
Level 1A — shared/capital-allocation-and-entry-policy.md
Level 1B — shared/automation-execution-governance.md
Level 1C — shared/research-model-governance.md
  ↓
Level 2  — skills/*/SKILL.md
  ↓
Level 3  — skills/*/references/*.md
  ↓
Level 4  — examples / dated snapshot / watchlist
```

Level 1A controls capital/risk, 1B controls execution/automation, and 1C controls research-model evidence, bias control and promotion.

## Migration checks completed

### 1. Root repository status

PASS.

- Both Skills are listed as active.
- Capital, automation and research governance are separately named.
- v3 explicitly uses Champion/Challenger instead of silently replacing current scoring.
- Long-term IRR / Total Return and short-term MFE/MAE are discoverable from the root README.

### 2. Long/short capital allocation

PASS.

Current allocation remains governed only by Level 1A:

```text
Final Short Cap = min(Size Cap, Risk Cap, Edge Cap)
Actual Short Exposure <= Final Short Cap
```

The v3 research upgrade does not modify capital tiers, Operating Target, Hard Ceiling or circuit breakers.

### 3. Research model governance separation

PASS.

`research-model-governance.md` does not override position sizing or broker execution.

It governs only:

- evidence classification;
- Champion/Challenger;
- point-in-time / survivorship / look-ahead controls;
- Benchmark;
- Required Return parameter discipline;
- model promotion;
- MFE/MAE learning.

### 4. Champion remains current production model

PASS.

The short/mid-term `SKILL.md` and `scoring-system.md` remain the production Champion.

Current Champion:

```text
Technical 30
Capital Participation 30
Fundamentals 25
Catalyst 15
```

The new `causal-challenger-model.md` explicitly declares:

```text
CHALLENGER / SHADOW ONLY
```

It cannot change real orders before Promotion Review.

### 5. Challenger weight conflict

PASS.

The v3 Challenger contains experimental weights, but labels them research parameters rather than replacing Champion thresholds.

No production rule claims that the new weights are proven optimal.

### 6. Champion / Challenger fair-comparison protocol

PASS.

`champion-challenger-forward-test.md` requires:

```text
same universe
same as_of
same available information
same risk budget
same A-share execution constraints
same cost/slippage assumptions
```

It also records NO_TRADE signals and prohibits look-ahead information.

### 7. Model Promotion vs Automation Promotion

PASS.

The repository now explicitly states:

```text
Good Model != Safe Auto Execution
Safe Executor != Positive Edge
```

Model promotion is governed by Level 1C; automation promotion remains governed by Level 1B.

`AUTO_ORDER=false` remains the default.

### 8. Point-in-time / survivorship bias

PASS.

Level 1C now requires historical handling of:

- listed/delisted stocks;
- historical ST/*ST state;
- actual filing publication dates;
- historical index constituents;
- suspension / limits / T+1;
- fees / tax / slippage / impact.

Historical results that cannot reconstruct point-in-time inputs are marked `Biased / Non-promotable`.

### 9. Long-term “low price” vs valuation

PASS.

The long-term README and new IRR reference now explicitly separate:

```text
Price Low
!=
Valuation Low
```

A large drawdown from the historical high does not automatically permit ADD.

### 10. Long-term Expected IRR

PASS.

The new framework uses Bear/Base/Bull scenarios and makes Required Risk Premium configurable.

It does not hard-code `ERP = 4%-6%` as universal truth.

The 4%/6%/8% values appear only as a sensitivity example / research grid.

### 11. Long-term Total Return Benchmark

PASS.

The repository now requires long-term performance comparison on a total-return basis where available.

沪深300 is explicitly documented as:

```text
Price Index  = 000300
Total Return = H00300
```

The repository rejects comparing a dividend-receiving portfolio against a price-only benchmark without disclosing the mismatch.

### 12. Long-term entry tranches

PASS.

Current strategy-tranche policy remains:

```text
Default: 40% / 30% / 30%
Small/high-certainty exception: 60% / 40%
Large-position/higher-uncertainty exception: 30% / 25% / 25% / 20%
```

The v3 docs explicitly label these as governance parameters, not mathematically optimal weights.

### 13. Short/mid-term entry tranches

PASS.

Current policy remains:

```text
Default: 50% Setup + 50% Confirmation
Three-stage exception: 50% / 30% / 20%
```

The Challenger preserves the prohibition on averaging down merely because a trend/catalyst position is losing.

Long-term value ADD remains separately allowed only after Thesis + Balance + Valuation + Portfolio Gates pass.

### 14. Strategy tranche vs execution slicing

PASS.

The repository still distinguishes:

- strategy tranche = new decision based on information/confirmation;
- execution slicing = child orders for liquidity/slippage.

### 15. Short/mid-term risk budget

PASS.

No v3 research document changes:

```text
Operating Target
- per trade: 0.5%
- aggregate open initial risk: <=2%
- one industry/factor: <=1%

Hard Ceiling
- per trade: <=1%
- aggregate open initial risk: <=3%
```

### 16. Profit-management parameter status

PASS.

+1.5R/+2R and 3–5 day time review remain usable governance starting points, but v3 removes any claim that they are universally optimal.

`trade-ledger-mfe-mae-extension.md` requires MFE/MAE evidence before changing them.

### 17. Vendor “main force inflow” interpretation

PASS.

The existing short-term scoring system already warns not to equate vendor-labeled main-force inflow with institutional conviction.

The Challenger strengthens this by separating:

```text
Participation
Positioning Evidence
Price Confirmation
```

No new rule treats vendor flow as a standalone buy signal.

### 18. Historical snapshots

PASS.

Dated candidate pools remain Level 4 evidence only.

No historical example is promoted to a permanent recommendation because of later price performance.

## Current Source-of-Truth map

| Topic | Source of Truth |
|---|---|
| long vs short capital allocation | `shared/capital-allocation-and-entry-policy.md` |
| Size/Risk/Edge Cap | `shared/capital-allocation-and-entry-policy.md` |
| Operating Target / Hard Ceiling | `shared/capital-allocation-and-entry-policy.md` |
| default entry tranches | `shared/capital-allocation-and-entry-policy.md` |
| automation / broker safety | `shared/automation-execution-governance.md` |
| research-model governance | `shared/research-model-governance.md` |
| policy precedence | `shared/policy-precedence.md` |
| long-term production selection/valuation | `skills/a-share-retirement-investing/SKILL.md` |
| long-term IRR / total-return method | `skills/a-share-retirement-investing/references/expected-irr-total-return-benchmark.md` |
| short/mid-term production selection/execution | `skills/a-share-short-midterm-stock-selection/SKILL.md` |
| current short-term Champion scoring | `skills/a-share-short-midterm-stock-selection/references/scoring-system.md` |
| v3 short-term Challenger | `skills/a-share-short-midterm-stock-selection/references/causal-challenger-model.md` |
| Champion/Challenger validation | `skills/a-share-short-midterm-stock-selection/references/champion-challenger-forward-test.md` |
| MFE/MAE extension | `skills/a-share-short-midterm-stock-selection/references/trade-ledger-mfe-mae-extension.md` |
| historical candidate pools | dated snapshot/watchlist files only |

## Regression checks

Current repository passes these regression questions:

1. Can the Challenger silently replace the 30/30/25/15 Champion? **No.**
2. Can a model promote itself because backtest results improved? **No.**
3. Can Forward-Test use later filings, later ST status or future delisting information? **No.**
4. Can a dividend portfolio claim excess return against a price-only benchmark without disclosure? **No.**
5. Is 4%–6% ERP treated as universal A-share truth? **No.**
6. Are +1.5R/+2R and 3–5 days described as mathematically optimal? **No.**
7. Can a vendor main-force-flow label independently create a buy signal? **No.**
8. Can a short-term loser be renamed long-term to avoid realizing a loss? **No.**
9. Does Level 1C change Level 1A risk ceilings? **No.**
10. Does passing Model Promotion automatically permit Full Auto? **No.**
11. Can dated snapshots override current policy or current data? **No.**
12. If a lower-level reference conflicts with Level 1, is precedence explicit? **Yes.**

## Remaining caveats

The repository is internally consistent at this audit point, but several numeric values remain governance parameters rather than universally optimal constants.

The most important unresolved empirical question is now explicit:

```text
Does the Causal Challenger produce better net, risk-adjusted, cost-aware Forward performance than the current Champion?
```

Until real Forward/Live evidence answers that question, the Champion remains unchanged and the Challenger remains Shadow Only.

Any future Level-1 change or Champion Promotion must trigger a new consistency audit across both Skills, references, examples and automation roadmaps.
