# Short/Mid Sample Data Acquisition Contract v1

> Status: `ACTIVE DATA / AUDITABILITY CONTRACT`
>
> Scope: short/mid live-manual, paper, forward and retrospective research samples.
>
> Goal: make sample accumulation systematic. The user should report only private execution facts that public market data cannot supply; the runtime should collect and freeze public evidence automatically.
>
> This contract does **not** change Champion weights, entry thresholds, risk caps or order permissions.

## 1. Principle — user reports actions, system collects market evidence

The user should not be required to manually report daily price, volume, financing, announcements, market breadth or public financial data.

Default split:

```text
USER-ONLY DATA
= actual trade / account facts that public sources cannot know

SYSTEM-COLLECTED DATA
= public market / company / participation / event evidence

DERIVED DATA
= features, MFE/MAE, relative strength, follow-through labels and validation outcomes
```

This separation reduces missing fields, inconsistent timestamps and hindsight reconstruction.

## 2. Minimum user input for a new real trade sample

Minimum required:

```yaml
code:
trade_date:
action: BUY | ADD | TRIM | SELL
actual_average_fill_price:
```

Strongly preferred when available:

```yaml
name:
fill_time:                # optional; exact time improves intraday PIT reconstruction
shares:                   # optional
position_weight_pct:      # optional if shares/account equity not supplied
position_weight_denominator: STOCK_ACCOUNT_EQUITY | SHORT_STRATEGY_NAV | OTHER | UNKNOWN
```

Optional but valuable:

```yaml
fees_and_taxes:
manual_reason:
manual_override: true | false
original_thesis_in_own_words:
```

The system must never require the user to manually collect public market data.

## 3. What the system must collect automatically

### A. Price / liquidity path — REQUIRED DAILY

For every enrolled sample:

```text
trade_date
open
high
low
close
prev_close
volume
turnover
turnover_rate
suspension / missing-bar state
```

Canonical price basis for replay is unadjusted daily bar, with corporate actions stored separately.

### B. Broad market state — REQUIRED DAILY

Reuse the market monitor and preserve:

```text
advance / decline / flat
limit-up / limit-down / broken-limit counts
strong / weak tail counts
median A-share return
total turnover
20d turnover reference when available
sentiment score
regime
crowding flag
data confidence
spot provider state
```

### C. Benchmark / relative-strength evidence — REQUIRED WHEN DATA AVAILABLE

At minimum preserve a broad benchmark series appropriate to the security/exchange and calculate:

```text
stock_return_1d / 3d / 5d / 10d / 15d
benchmark_return_1d / 3d / 5d / 10d / 15d
excess_return_1d / 3d / 5d / 10d / 15d
```

Sector benchmark / peer basket should be added when a PIT-valid mapping exists. Missing sector benchmark must be explicit rather than replaced with a concept board after the fact.

### D. Volume / participation evidence — REQUIRED OR EXPLICITLY MISSING

Collect:

```text
volume_5d_mean
volume_20d_mean
RVOL_5d
RVOL_20d
turnover percentile / reference when available
```

Vendor large-order / main-force flow may be collected as corroborative evidence only:

```text
vendor_main_flow_net
vendor_super_large_net
vendor_large_net
vendor_medium_net
vendor_small_net
vendor_source
```

Never promote vendor flow to institutional truth.

### E. Financing / securities lending — REQUIRED WHEN THE SECURITY IS ELIGIBLE

Collect exchange-level stock detail when available:

```text
data_effective_date
financing_buy
financing_repayment       # where source provides it
financing_balance
financing_net_change
securities_lending_sell
securities_lending_balance / quantity
source_exchange
```

Important PIT rule:

```text
effective_date != available_at
```

If T-day financing data becomes observable only on T+1, the record remains economically effective on T but cannot be used in a T decision. `available_at` must reflect when the system could actually observe it.

### F. Disclosures / corporate events — REQUIRED DAILY SCAN

Scan official / official-aggregated disclosure sources for the sample security and preserve:

```text
disclosure_id or stable hash
title
category
published_at or source date
available_at
source locator
first_tradable_timestamp when resolvable
```

Material event families include, at minimum:

```text
earnings / guidance
major orders
buyback
shareholder reduction / increase
lock-up / unlock
restructuring
litigation / regulation
risk warning
corporate action
suspension / resumption
```

When exact publication time is unavailable, store date-only precision and use conservative `available_at=ingested_at`; do not invent an intraday timestamp.

### G. Financial / fundamental refresh — EVENT DRIVEN

Do not re-download the same financial statement every day. Refresh when a new official report/guidance/disclosure is published and preserve canonical PIT metadata.

### H. Strategy state snapshot — REQUIRED FOR PROSPECTIVE SAMPLES

For new forward/live samples generated after this contract, freeze when possible:

```text
analysis_as_of
Champion score and sub-scores
research_state
position_state
confirmation_basis
market_regime
sector_regime
setup_type
entry_trigger
planned_entry
invalidation
planned risk / size
resilience_gate
model / governance versions
data_snapshot_id
```

If a user reports an old trade after the fact and these fields did not exist at entry, they remain unknown. Do not reconstruct them as if they were original production state.

## 4. Derived fields — system computes, user does not report

For every open sample, derive after each valid trading-day bar:

```text
holding_trading_days
return_vs_entry
MFE_price / MFE_pct
MAE_price / MAE_pct
time_to_MFE
time_to_MAE
max_drawdown_from_post-entry_peak
MA5 / MA10 / MA20
rolling_high / rolling_low
RVOL
broad-market excess return
```

Checkpoint features:

```text
MFE_1d / MAE_1d
MFE_3d / MAE_3d
MFE_5d / MAE_5d
MFE_10d / MAE_10d
MFE_15d / MAE_15d
RS_1d / 3d / 5d / 10d / 15d
```

Where a valid original invalidation exists, also derive R-based fields:

```text
current_R
MFE_R
MAE_R
realized_R
```

Never invent R for retrospective trades with no original invalidation.

## 5. Follow-through labels

These are research labels, not production sell rules.

Store at fixed checkpoints:

```yaml
checkpoint: D1 | D3 | D5 | D10 | D15
price_progress:
relative_strength:
volume_confirmation:
MFE_pct:
MAE_pct:
state_if_current_rules_applied:
```

Candidate research labels:

```text
FOLLOW_THROUGH_CONFIRMED
NO_FOLLOW_THROUGH
ADVERSE_EARLY_PATH
MIXED
INSUFFICIENT_DATA
```

Exact classification thresholds remain Challenger research until frozen and validated.

## 6. Sample lifecycle

```text
REGISTERED
→ OPEN / OBSERVING
→ D1
→ D3
→ D5
→ D10
→ D15
→ REUNDERWRITTEN or CLOSED
→ OUTCOME_FROZEN
→ AGGREGATED_RESEARCH
```

For positions held beyond 15 trading days, continue daily collection, but mark the original short-horizon sample as having reached its mandatory re-underwriting boundary.

## 7. Evidence classes

### Prospective / forward sample

Registered before future outcomes are known, with immutable decision snapshot.

May become Level-C evidence if the rest of the forward contract is satisfied.

### Retrospective user-reported sample

Reported after part/all of the price path is already known.

Use for:

```text
holding-risk research
MFE/MAE research
position-sizing diagnostics
behavior / override research
PIT process testing
```

Do not count as Champion-generated forward win/loss.

## 8. Storage contract

Recommended runtime structure:

```text
runtime/state/sample_evidence/
  registry.json
  daily/
    YYYY-MM-DD.jsonl
  manual_events/
    trade_events.jsonl
  disclosures/
    YYYY-MM-DD.jsonl
  checkpoints/
    <sample_id>.json
```

Rules:

- daily evidence is append-only by logical record identity;
- later provider corrections create a revision, not silent overwrite, when revision lineage is observable;
- raw/public fields and derived fields remain distinguishable;
- source + effective_at + available_at + ingested_at are preserved where applicable;
- outcome/reveal does not rewrite the original decision snapshot.

Longer-term storage should migrate to the canonical PIT store / Parquet-DuckDB direction without changing sample semantics.

## 9. Daily collection cadence

### EOD — active minimum

Run after regular close on each exchange trading day (current repository schedule: approximately 15:40 Asia/Shanghai):

```text
market state
sample daily bars
relative/rolling features
vendor participation corroboration
latest already-available financing detail
new disclosures
MFE/MAE + checkpoint updates
```

### Pre-open — recommended maturity stage

A separate pre-open snapshot may later collect:

```text
previous-day financing that became available overnight
new overnight disclosures
event / first-tradable-time changes
```

Do not reuse the EOD market monitor unchanged for pre-open decisions; it needs a separate phase-aware collector.

## 10. Missing-data behavior

Every family gets a status:

```text
AVAILABLE
DELAYED
NOT_APPLICABLE
PROVIDER_ERROR
TIMESTAMP_UNRESOLVED
INSUFFICIENT_HISTORY
```

Missing data must not be converted to zero.

A provider failure on one field does not erase the whole sample, but required production gates still fail closed according to governance.

## 11. Minimum data-quality scorecard

For each sample/day track:

```text
price_complete
market_complete
benchmark_complete
participation_complete
financing_complete_or_not_applicable
disclosure_scan_complete
PIT_timestamp_quality
model_snapshot_complete
manual_execution_complete
```

Aggregate maturity metrics:

```text
sample_days_total
sample_days_price_complete_pct
sample_days_market_complete_pct
sample_days_participation_complete_pct
sample_days_financing_complete_pct
sample_days_disclosure_complete_pct
prospective_snapshot_complete_pct
PIT_error_rate
```

The repository should not say “dataset is mature” without reporting these coverage metrics.

## 12. What the user needs to tell ChatGPT going forward

For a new trade, a one-line report is enough:

```text
SYNTHETIC EXAMPLE
NOT REAL USER DATA

```

For a later action:

```text
SYNTHETIC EXAMPLE
NOT REAL USER DATA

```

Or:

```text
600699，2026-09-10全部卖出，均价20.35。
```

If no operation occurs, the user does **not** need to report anything daily. The system keeps collecting public evidence.

## 13. Fields the user should not be asked to collect manually

Do not ask the user to manually provide, unless correcting a provider error:

```text
daily close/high/low
volume / turnover
market index move
market breadth
sector daily move
financing public data
vendor fund flow
public announcements
financial statement numbers
moving averages
MFE / MAE
relative strength
```

## 14. Final rule

```text
User supplies private truth.
System supplies public evidence.
Derived features are reproducible.
Future outcomes never rewrite past decisions.
```
