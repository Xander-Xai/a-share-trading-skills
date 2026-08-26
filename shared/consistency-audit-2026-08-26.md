# Repository Consistency Audit — 2026-08-26

## Scope

This audit checks the current `main` branch for stale rules, contradictory parameters, and policy-precedence problems across:

- root `README.md`
- `shared/` governance files
- long-term retirement Skill
- short/mid-term trading Skill
- related methodology / execution / risk-management / research references

Historical dated snapshots are treated as records, not current policy.

## Governing hierarchy

The repository now uses:

```text
Level 1 — shared/capital-allocation-and-entry-policy.md
  ↓
Level 2 — skills/*/SKILL.md
  ↓
Level 3 — skills/*/references/*.md
  ↓
Level 4 — dated snapshot/watchlist files
```

Lower-level files may be more conservative, but may not loosen Level-1 risk limits.

## Migration checks completed

### 1. Root repository status

PASS.

- Both Skills are now listed as present.
- The root README no longer describes the short/mid-term Skill as merely “planned” or “still being organized”.
- Shared policy and research-validation files are linked explicitly.

### 2. Long/short capital allocation

PASS.

The retired fixed rule `70% long / 30% short for every capital size` is no longer the repository-wide policy.

Current allocation uses:

```text
Short Allocation = min(Size Cap, Risk Cap, Edge Cap)
```

with the dynamic Size-Cap baseline maintained only in the shared capital policy.

### 3. Short/mid-term legacy 30%-of-savings rule

PASS.

The old rule `short-term capital <= 30% of total savings` is explicitly retired in the short/mid-term Skill. Strategy capital must be derived from shared policy.

### 4. Long-term single-stock / cluster limits

PASS.

The old permanent `single stock <=25%` and `risk cluster <=30%-35%` defaults are retired as universal limits.

Long-term position caps are now derived dynamically from the current shared-policy capital tier.

### 5. Long-term entry tranches

PASS.

The vague old rule `3–5 tranches` is retired.

Current strategy-tranche policy:

```text
Default: 40% / 30% / 30%
Small/high-certainty exception: 60% / 40%
Large-position/higher-uncertainty exception: 30% / 25% / 25% / 20%
```

The long-term methodology and execution template now use this hierarchy.

### 6. Short/mid-term entry tranches

PASS.

The old account-size-based `3 / 4 / 4` strategy-tranche rule is retired.

Current policy:

```text
Default: 50% Setup + 50% Confirmation
Three-stage exception: 50% / 30% / 20%
```

Later tranches require positive confirmation. Averaging down merely to reduce cost is prohibited.

### 7. Strategy tranche vs execution slicing

PASS.

The repository now distinguishes:

- strategy tranche = new investment/trading decision,
- execution slicing = multiple child orders used to manage liquidity/slippage.

Large capital may require more child orders without creating extra strategy decisions.

### 8. Short/mid-term risk-budget conflict

PASS.

The previous apparent conflict between `0.5% / 2%` and `1% / 3%` has been resolved by defining two layers:

```text
Operating Target
- per trade: 0.5%
- aggregate open initial risk: <=2%
- one industry/factor: <=1%

Hard Ceiling
- per trade: <=1%
- aggregate open initial risk: <=3%
```

Lower-level Skill/reference files may stay at the Operating Target; they may never exceed the Hard Ceiling.

### 9. Short/mid-term profit-management conflict

PASS.

Primary hierarchy is now:

```text
R multiple + technical structure + original setup target
```

Historical percentage zones (`+3%-5%` traditional/cyclical and `+6%-10%` growth/technology) remain only secondary observation zones. If they conflict, R/structure wins.

### 10. Historical snapshots

PASS.

Dated stock-pool/watchlist files remain historical snapshots. They do not override current policy, current market data, or current scoring.

## Current Source-of-Truth map

| Topic | Source of Truth |
|---|---|
| long vs short capital allocation | `shared/capital-allocation-and-entry-policy.md` |
| Size/Risk/Edge Cap | `shared/capital-allocation-and-entry-policy.md` |
| Operating Target / Hard Ceiling | `shared/capital-allocation-and-entry-policy.md` |
| default entry tranches | `shared/capital-allocation-and-entry-policy.md` |
| policy precedence | `shared/policy-precedence.md` |
| long-term selection/valuation | `skills/a-share-retirement-investing/SKILL.md` |
| short/mid-term selection/execution | `skills/a-share-short-midterm-stock-selection/SKILL.md` |
| long-term detailed method | `skills/a-share-retirement-investing/references/methodology.md` |
| long-term execution template | `skills/a-share-retirement-investing/references/execution-template.md` |
| short/mid-term holding/risk | `skills/a-share-short-midterm-stock-selection/references/holding-risk-management.md` |
| short/mid-term research basis | `skills/a-share-short-midterm-stock-selection/references/research-basis.md` |
| historical candidate pools | dated snapshot/watchlist files only |

## Regression checks

Current repository passes these regression questions:

1. Does any active rule still require short/mid-term capital to remain exactly 30% for all account sizes? **No.**
2. Does any active long-term rule still permit a universal 25% single-stock cap regardless of capital size? **No.**
3. Does any active short/mid-term rule still require 3/4/4 strategy tranches by capital size? **No.**
4. Does any active long-term rule still leave tranche count as an undefined 3–5 range? **No.**
5. Are `0.5%/2%` and `1%/3%` still contradictory? **No; they are Operating Target vs Hard Ceiling.**
6. Can fixed percentage profit zones override R/structure in short/mid-term management? **No.**
7. Can a dated snapshot override current policy or current data? **No.**
8. If a lower-level reference conflicts with shared policy, is precedence explicit? **Yes.**

## Remaining caveat

The repository is internally consistent at this audit point, but the numeric governance parameters are still policy choices rather than universally optimal values. They should be recalibrated only with meaningful real trading/investment data, not after a handful of recent outcomes.

Any future Level-1 change must trigger a new consistency audit across both Skills and their references.
