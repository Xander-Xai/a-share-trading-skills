# Forward Validation Metrics and Trade Ledger

## Purpose

Define how to measure whether the short/mid-term skill works **prospectively** and how to keep paper/live results auditable.

The ledger is not just a P&L table. It must preserve the decision, the execution, the risk and the rule-adherence context.

---

## 1. Separate three price concepts

Never merge these fields:

1. `baseline_price` — research snapshot reference price.
2. `planned_entry` — price used when creating the trade plan.
3. `actual_fill` / `simulated_fill` — price actually achieved or conservatively simulated.

The 2026-08-26 screenshot close is a **baseline**, not an automatic entry.

---

## 2. Trade lifecycle IDs

Every potential trade receives a stable ID:

```text
trade_id = YYYYMMDD-code-sequence
```

Example:

```text
20260827-601138-01
```

One trade ID follows the entire lifecycle:

```text
signal
→ decision
→ order intent
→ fill
→ position updates
→ exit
→ post-trade review
```

Do not create a new trade ID merely because the position receives a confirmation tranche. Record tranches under the same trade thesis unless a genuinely new thesis is created.

---

## 3. Required pre-trade fields

### Identity / provenance

```yaml
trade_id:
strategy_version:
universe_snapshot_id:
mode: paper | live_manual | assisted | semi_auto | auto
code:
name:
analysis_as_of:
source_provenance:
```

### Research state

```yaml
industry:
factor_cluster:
role:
market_regime:
sector_regime:
technical_score:
capital_score:
fundamental_score:
catalyst_score:
penalties:
final_score:
data_completeness: Complete | Partial | Insufficient
```

### Thesis / setup

```yaml
thesis:
setup_type:
entry_trigger:
planned_entry:
invalidation:
time_stop:
expected_target_or_exit_logic:
expected_reward_risk:
event_risk:
```

### Risk / size

```yaml
strategy_nav:
allowed_loss_amount:
planned_stop_distance_pct:
planned_shares:
planned_exposure_rmb:
planned_trade_risk_pct:
portfolio_heat_before:
portfolio_heat_after:
industry_heat_after:
factor_heat_after:
```

### Decision governance

```yaml
hard_veto_passed:
adversarial_review_passed:
manual_override: false
manual_override_reason:
decision: enter | wait | reject | event_isolation
```

---

## 4. Execution fields

For every order/tranche:

```yaml
order_id:
trade_id:
tranche: setup | confirmation | reduction | exit
order_created_at:
submitted_at:
order_type:
limit_price:
requested_shares:
broker_status:
filled_at:
filled_shares:
fill_price:
fees:
taxes:
slippage_bps:
reject_reason:
```

Paper mode must populate equivalent `simulated_*` fields using conservative fill logic.

---

## 5. Holding-state event log

Do not store only the final exit. Append state transitions:

```yaml
event_time:
trade_id:
state_before:
state_after:
price:
score_refresh:
market_regime:
sector_regime:
new_information:
action:
action_reason:
```

Allowed thesis states:

- `strengthening`
- `intact`
- `weakening`
- `invalidated`

Examples:

```text
intact → strengthening
reason: breakout retest held + sector breadth improved

intact → weakening
reason: relative strength deteriorated for 3 sessions

weakening → invalidated
reason: key support lost + thesis event failed
```

---

## 6. Exit fields

```yaml
exit_decision_at:
exit_order_at:
exit_fill_at:
exit_price:
exit_shares:
exit_reason: invalidation | thesis | time_stop | partial_profit | trailing | event | portfolio_risk | other
holding_days:
realized_pnl_rmb:
realized_return_pct:
realized_R:
```

Record the real exit price, not the planned stop price, when a gap or liquidity constraint creates worse execution.

---

## 7. MFE and MAE

For each trade calculate:

### Maximum Favorable Excursion

```text
MFE = best unrealized move while position was open
```

### Maximum Adverse Excursion

```text
MAE = worst unrealized move while position was open
```

Record both in:

- percent;
- R multiples.

Use them to answer:

- Are stops too tight?
- Are exits too early?
- Are profitable trades experiencing excessive adverse excursion?
- Does the setup generate favorable movement soon enough for a 5–15 day strategy?

---

## 8. Core performance metrics

### Expectancy

```text
Expectancy_R = win_rate * average_win_R - loss_rate * average_loss_R
```

Use net results after actual or estimated transaction costs.

### Profit factor

```text
profit_factor = gross_profit / abs(gross_loss)
```

### Other required metrics

- total closed trades
- win rate
- median R
- average R
- average winner
- average loser
- best / worst trade
- max drawdown
- recovery time
- consecutive losses
- turnover
- average holding days

Do not rely on win rate alone.

---

## 9. Segment the data

Aggregate P&L can hide a broken process.

Review results by:

### Setup

- breakout
- first pullback
- reclaim
- sector-leader continuation
- event-post-confirmation

### Market regime

- Risk-On
- neutral / rotational
- Risk-Off

### Sector / factor

- commodity
- AI/datacenter capex
- consumer
- financial turnover
- utility
- defense
- shipping
- other

### Score band

- 80+
- 75–79
- 65–74 paper observations

### Decision state

- priority scan
- technical wait converted to entry
- event-isolation post-event entry
- downgrade name later restored

---

## 10. Rule-adherence metrics

Every trade must be labeled:

```text
good process + good result
good process + bad result
bad process + good result
bad process + bad result
```

A profitable trade with a hard-rule violation is **not** evidence that the rule should be removed.

Track:

- trades without predefined invalidation
- risk-limit breaches
- same-factor limit breaches
- chasing despite chase veto
- entry during blocked event window
- averaging down without positive confirmation
- stop widened in losing direction
- short-term trade converted to medium term without re-underwriting
- manual override count
- no-trade rule violations

---

## 11. Paper vs live comparison

For matched paper/live signals compare:

```text
paper_fill vs live_fill
paper_slippage vs live_slippage
paper_R vs live_R
paper_holding_time vs live_holding_time
paper_exit_reason vs live_exit_reason
```

If paper edge disappears live, investigate:

- fill optimism;
- late human execution;
- missed trades;
- emotional overrides;
- liquidity/fees;
- different position sizing;
- data timing.

Do not blame “bad luck” before checking execution mismatch.

---

## 12. Daily report

Recommended end-of-day report:

```markdown
# YYYY-MM-DD Short/Mid-term Daily Report

## Market regime

## 43-stock whitelist changes
- promoted
- downgraded
- event-isolated
- removed

## Top 10 watchlist

## Executable candidates

## Existing positions
- thesis state
- current R
- stop / invalidation
- event risk

## Portfolio risk
- strategy NAV
- open initial risk
- industry heat
- factor heat

## Orders / fills

## Rule violations / system incidents

## Tomorrow's triggers
```

---

## 13. Weekly review

At least weekly:

- recompute expectancy and drawdown;
- compare setup groups;
- inspect MFE/MAE;
- review every loss >1R equivalent;
- review every manual override;
- review missed trades only to improve process, not to create FOMO rules;
- check whether one factor dominates results;
- check whether current whitelist still reflects new fundamentals/events.

---

## 14. Promotion / rollback principle

### Promotion

Advance from paper to live or from manual to more automation only when:

- strategy evidence improves;
- process error rate is low;
- execution is reproducible;
- risk controls remain intact.

### Rollback

Immediately move to a safer phase if:

- reconciliation failures appear;
- duplicate orders occur;
- hard risk controls fail;
- unexplained live/paper divergence persists;
- regulatory/broker permission changes;
- drawdown triggers policy review;
- new strategy version has not been validated.

Automation maturity is reversible.

---

## 15. Suggested storage format

For future runtime implementation, prefer append-only structured records:

```text
runtime/
├── snapshots/
│   └── YYYY-MM-DD.json
├── signals/
│   └── YYYY-MM-DD.jsonl
├── trades/
│   ├── paper.jsonl
│   └── live.jsonl
├── orders/
│   └── orders.jsonl
├── positions/
│   └── daily-position-snapshots.jsonl
├── reports/
│   ├── daily/
│   ├── weekly/
│   └── monthly/
└── incidents/
    └── incidents.jsonl
```

For high-integrity execution systems, also use a transactional database for the canonical live state. Flat files are useful for audit/export but should not be the sole live-order state store.

---

## 16. Final rule

The system's most important performance metric is not raw return. It is:

> **Positive expectancy after costs, achieved without violating the risk policy, with decisions that can be reproduced from point-in-time data.**
