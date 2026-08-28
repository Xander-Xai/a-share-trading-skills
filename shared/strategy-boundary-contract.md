# Strategy Boundary Contract v1

> Status: `ACTIVE CROSS-SLEEVE GOVERNANCE CONTRACT`
>
> Scope: all research, runtime, paper/live, replay, experiment and broker artifacts in this repository.

## 1. Why this contract exists

The repository contains two economically different stock strategies. They share account infrastructure, but they do not share a decision horizon or primary validation logic.

Canonical identities:

```text
strategy_id = a_share_long_retirement
sleeve      = long

strategy_id = a_share_short_mid
sleeve      = short_mid
```

`strategy_id` is stable across model versions. Store model/skill versions separately.

Every decision, replay record, paper/live position, proposed order and generated research artifact must identify both `strategy_id` and `sleeve` once it becomes machine-executable.

## 2. Shared platform vs separate decision engines

Allowed shared infrastructure:

```text
security master
market / exchange calendar
point-in-time data store
company filings and corporate actions
price data
source provenance and permitted-use metadata
account equity
broker net position
orders / fills / cash ledger
cross-sleeve symbol exposure
cross-sleeve factor / cluster exposure
audit log
CI / tests
broker reconciliation
```

Not shared as a single decision model:

```text
Short/Mid decision engine
!=
Long-term decision engine
```

### Short/Mid economic objective

```text
Expectation Change
→ Materiality
→ Prepricing
→ Market Reaction / Participation
→ Regime
→ Execution Geometry
→ bounded tactical risk
```

Primary horizon is defined by the short/mid Skill, not by the long-term system.

### Long-term economic objective

```text
Survival / Governance
→ Business Durability
→ Normalized Earnings / FCF
→ Balance Sheet
→ Dividend Sustainability
→ Per-share Value Creation
→ Valuation / Expected IRR
→ Portfolio Fit
```

Long-term decisions are not required to pass ERG, momentum confirmation, short-term reaction windows, planned-R entry geometry, or 5/10/20-day forward-return gates.

## 3. Explicit non-contamination rules

A `short_mid` module must not directly mutate a `long` decision state, target weight, thesis state or model promotion result.

A `long` module must not directly mutate a `short_mid` research state, position state, tactical trigger, invalidation or planned risk budget.

Examples:

```text
short_mid ERG INVALIDATED
!= automatic long EXIT

short_mid 5-day relative weakness
!= automatic long thesis failure

long Base IRR above required return
!= automatic short_mid ENTRY

long dividend sustainability
!= short_mid market confirmation
```

If the same factual event matters to both sleeves, both engines may consume the same source record but must independently interpret it under their own model.

## 4. Shared facts may trigger independent re-underwriting

A material event may create two separate tasks:

```text
same filing/event
├─ short_mid → expectation/reaction/execution review
└─ long      → thesis/normalized earnings/valuation review
```

The event record is shared. The state transition is not.

## 5. Account risk remains aggregated

Strategy separation does not create separate account-level risk allowances.

```text
Account Symbol Exposure
= Long Sleeve Exposure + Short/Mid Sleeve Exposure

Account Cluster Exposure
= Long Cluster Exposure + Short/Mid Cluster Exposure
```

Broker execution must maintain both:

```text
Broker Net Position
Strategy Virtual Position per sleeve
```

A sell from one sleeve must not silently consume the other sleeve's logical shares.

## 6. Validation metrics are sleeve-specific

Common validation concerns:

```text
point-in-time integrity
costs / taxes / slippage where applicable
benchmark correctness
max drawdown
turnover
rule violations
data coverage / missingness
source provenance
reproducibility
complexity / maintenance cost
```

Short/Mid primary diagnostics may include:

```text
Expectancy_R
Profit Factor
Win Rate
Average Win / Loss
MFE / MAE
Holding Days
Regime Breakdown
False Positive / False Negative
Blocked MFE
Confirmation Delay Cost
```

Long-term primary diagnostics instead emphasize:

```text
Total Return
Excess Total Return
Dividend Return / Growth / Coverage
Expected IRR calibration error
Bear/Base/Bull forecast error
Permanent impairment cases
Valuation error
Thesis failure rate
Cash drag
Capital-allocation contribution
```

Do not require a long-term model to prove itself through tactical R-multiple or 5–20 trading-day metrics.

## 7. Runtime enforcement

Machine implementations must fail closed on strategy-context mismatch.

Example:

```text
short_mid engine receives sleeve=long
→ NO_ACTION_STRATEGY_MISMATCH
```

A strategy-context failure is an implementation/configuration error, not a market signal.

## 8. Production architecture implication

Target architecture:

```text
Shared Governance + Shared Core Data
              │
      ┌───────┴────────┐
      │                │
Short/Mid Engine    Long Engine
      │                │
      └───────┬────────┘
              ↓
Account / Risk / Ledger / Execution
```

The system shares facts, account truth and execution plumbing. It does not share time scale, decision logic or primary evidence standard.