# Paper → Manual Live → Assisted → Automated Trading Roadmap

## Purpose

Turn the short/mid-term stock-selection skill into a **closed-loop trading system** without jumping directly from research to unattended execution.

The governing principle is:

> **Automation should automate a process that has already demonstrated reproducible edge and reliable risk control. It must not be used to hide an unvalidated strategy.**

This roadmap is deliberately staged:

```text
Research-only
→ Forward paper trading
→ Small-size manual live trading
→ Automated signals + manual orders
→ Human-confirmed broker execution
→ Limited semi-automation
→ Fully automated execution only after compliance + reliability gates
```

At every phase, the shared capital/risk policy remains the highest authority.

---

## 1. System objectives

The system must answer six different questions independently:

1. **What may be traded?** — Universe, leader, fundamental and event gates.
2. **What should be watched today?** — Market/sector regime + daily score.
3. **When is an entry valid?** — Setup and Reward/Risk.
4. **How much may be risked?** — Position sizing + portfolio heat.
5. **How should an open position be managed?** — Thesis state, stops, additions, exits.
6. **Has the process demonstrated real edge?** — Paper/live performance, execution quality and rule adherence.

The execution layer must never override research/risk gates.

---

## 2. Core architecture

```text
                ┌───────────────────────────┐
                │     Locked Universe        │
                │ screenshots / watchlists   │
                └─────────────┬─────────────┘
                              │
                              v
                ┌───────────────────────────┐
                │ Data & Evidence Layer      │
                │ price / volume / filings   │
                │ events / industry / factor │
                └─────────────┬─────────────┘
                              │
                              v
                ┌───────────────────────────┐
                │ Research Engine            │
                │ gates + 100-point scoring  │
                │ adversarial review         │
                └─────────────┬─────────────┘
                              │
                              v
                ┌───────────────────────────┐
                │ Signal / Intent Engine     │
                │ trigger / invalidation / R │
                └─────────────┬─────────────┘
                              │
                              v
                ┌───────────────────────────┐
                │ Risk Engine                │
                │ size / heat / factor caps  │
                │ event & execution stress   │
                └─────────────┬─────────────┘
                              │
          ┌───────────────────┴───────────────────┐
          │                                       │
          v                                       v
┌──────────────────────┐              ┌──────────────────────┐
│ Paper Execution      │              │ Live Execution       │
│ simulated fills      │              │ broker-approved path │
└──────────┬───────────┘              └──────────┬───────────┘
           │                                     │
           └───────────────────┬─────────────────┘
                               v
                  ┌───────────────────────────┐
                  │ Position State Engine      │
                  │ strengthen/intact/weakened │
                  │ invalidated                │
                  └─────────────┬─────────────┘
                                v
                  ┌───────────────────────────┐
                  │ Ledger & Evaluation        │
                  │ fills / MFE / MAE / R      │
                  │ drawdown / rule violations │
                  └─────────────┬─────────────┘
                                v
                  ┌───────────────────────────┐
                  │ Governance / Promotion     │
                  │ keep / rollback / advance  │
                  └───────────────────────────┘
```

---

## 3. Immutable decision records

Every signal/trade must be reconstructable after the fact.

Minimum immutable fields:

```text
strategy_version
universe_snapshot_id
analysis_as_of
stock_code
stock_name
market_regime
sector_regime
industry
factor_cluster
technical_score
capital_score
fundamental_score
catalyst_score
penalties
final_score
source_evidence
entry_trigger
planned_entry
invalidation
planned_reward_risk
risk_budget
planned_shares
mode = paper | live_manual | assisted | semi_auto | auto
manual_override
```

After execution add, without rewriting the original fields:

```text
order_time
fill_time
actual_fill
actual_shares
fees
slippage
exit_time
exit_fill
exit_reason
MFE
MAE
realized_R
rule_violations
```

**Never overwrite the original decision with later facts.** Append revisions/events instead.

---

## 4. Phase 0 — Research baseline

### Goal

Verify that the research pipeline is reproducible before pretending there is a tradable strategy.

### Current baseline

The first frozen example is:

- `../examples/2026-08-26-final-watchlist-case-study.md`
- `../examples/2026-08-26-final-watchlist.json`

### Required capabilities

- Universe Lock and provenance.
- Current industry classification.
- Leader and concept-authenticity gates.
- Latest fundamentals / events.
- Market and sector regime.
- 100-point score + penalties.
- Adversarial review.
- No-trade output.

### Exit criterion

The same input and same `as_of` data should produce materially consistent classification and reasoning.

---

## 5. Phase 1 — Forward paper trading

### Why paper first

Backtests can suffer from look-ahead, survivorship, bad fills and overfitting. Paper trading begins **after** the rules are frozen and observes future data prospectively.

### Daily process

```text
15:00–15:30 close
→ refresh market/sector data
→ refresh official events
→ rescore whitelist
→ select watch candidates
→ define next-session triggers/stops
→ create paper intents

next session
→ simulate fills only if trigger conditions occur
→ enforce A-share execution constraints
→ update paper positions

close / event time
→ update thesis state
→ manage stops/partials/time stops
→ append ledger
```

### Simulated-fill rules

Paper fills must be conservative.

- Do not assume a fill at the exact signal price when the market gaps through it.
- Do not assume a stop can execute through a locked limit-down.
- Respect board-lot rules.
- Model fees and slippage.
- Do not sell ordinary newly purchased shares as if unrestricted same-day reversal were available.
- Corporate-action adjustments must not be mistaken for true price moves.

### Default promotion gate to manual live

This is a governance starting point, not a proven optimum:

- at least **50 closed forward paper trades**;
- preferably at least **8 weeks** of forward operation;
- more than one market regime represented where practical;
- positive net expectancy after estimated costs;
- no unresolved hard-risk-policy violations;
- drawdown consistent with the strategy policy;
- no evidence that performance is dominated by one or two outliers;
- decisions and fills are reproducible from stored records.

If evidence is weak, remain in paper mode.

---

## 6. Phase 2 — Small-size manual live trading

### Goal

Measure the gap between simulated edge and real execution.

### Design

- Human places every order manually.
- Use risk below or at the conservative end of the normal Operating Target.
- Do not increase risk merely because paper results were strong.
- Record broker fills, fees, slippage and rejected/partial orders.
- Run the same signal in paper and live when possible for comparison.

### What this phase validates

- emotional discipline;
- real slippage;
- missed entries;
- partial fills;
- broker UI latency;
- gap behavior;
- whether discretionary overrides destroy or improve the model;
- whether the strategy remains positive after actual costs.

### Promotion gate

Before moving to broker-assisted execution, require a meaningful live sample and stable process. A reasonable starting governance target is:

- at least **20–30 closed live trades**;
- no repeated hard-rule violations;
- live and paper directionally consistent;
- realized slippage/costs within modeled tolerance;
- risk engine and ledger reconcile correctly;
- no unexplained position-state mismatch.

Sample size alone never forces promotion.

---

## 7. Phase 3 — Automated research/signals, manual orders

This should be the first major automation milestone.

### Automate

- data retrieval;
- corporate-event checks;
- industry/factor tagging;
- technical calculations;
- scoring;
- factor heat;
- candidate ranking;
- trigger alerts;
- paper execution;
- performance metrics;
- daily/weekly reports.

### Keep manual

- final buy/sell confirmation;
- exceptional-event judgment;
- broker order entry.

This phase captures most operational benefits with much lower execution risk.

---

## 8. Phase 4 — Human-confirmed execution

### Workflow

```text
system detects executable setup
→ risk engine creates Order Proposal
→ human reviews source/time/score/stop/size
→ human explicitly approves
→ broker adapter submits order
→ broker acknowledgement/fill reconciled
```

### Order Proposal must show

- stock/code;
- current quote timestamp;
- setup and trigger;
- entry limit/acceptable price range;
- invalidation;
- expected Reward/Risk;
- shares and RMB exposure;
- per-trade risk;
- post-trade portfolio heat;
- same-industry / same-factor exposure;
- upcoming event risk;
- compliance state;
- kill-switch state.

No proposal may hide a hard veto behind a high score.

---

## 9. Phase 5 — Limited semi-automation

Suitable only after Phase 4 proves reliable.

Examples of limited automation:

- execute a previously human-approved limit order;
- execute a previously human-approved stop/exit rule;
- cancel stale unfilled orders after a fixed window;
- reduce size automatically if live price makes planned risk exceed budget.

Still require strong guardrails:

```text
allowed symbols = current approved whitelist
allowed order types = explicit allowlist
max order value
max shares
max slippage / price collar
max daily order count
max strategy heat
max industry/factor heat
binary-event lockout
data-freshness check
position reconciliation
broker-connection health check
kill switch
```

Any stale data, position mismatch or broker error should fail closed: **no new order**.

---

## 10. Phase 6 — Fully automated trading

Full automation is **disabled by default**.

Promotion requires all of the following:

1. strategy edge is supported by forward paper and live samples;
2. execution adapter has passed failure-injection and reconciliation tests;
3. compliance/reporting obligations are confirmed with the broker and applicable exchange rules;
4. automatic risk controls cannot be bypassed by the strategy layer;
5. there is an independent kill switch;
6. every decision/order/fill is auditable;
7. restart/recovery does not duplicate orders;
8. position state is reconciled against broker truth before any new order;
9. manual emergency intervention remains available.

Do not deploy an unattended trading bot merely because an API technically allows order submission.

---

## 11. Regulatory / compliance gate for A-share program trading

This is a mandatory production gate, not an optional engineering detail.

China's securities rules define program trading broadly around computer programs automatically generating or submitting trading instructions. Program trading is subject to reporting and exchange supervision requirements.

Current key sources:

- CSRC — `证券市场程序化交易管理规定（试行）`, effective 2024-10-08:
  - https://www.csrc.gov.cn/csrc/c101954/c7480579/content.shtml
- Shanghai Stock Exchange — `上海证券交易所程序化交易管理实施细则`, effective 2025-07-07:
  - https://www.sse.com.cn/lawandrules/sselawsrules2025/trade/universal/c/c_20250612_10781696.shtml
- Shanghai Stock Exchange — stock program-trading reporting requirements:
  - https://www.sse.com.cn/lawandrules/sselawsrules2025/trade/universal/c/c_20250612_10781705.shtml
- Shenzhen Stock Exchange — `深圳证券交易所程序化交易管理实施细则`, effective 2025-07-07:
  - https://www.szse.cn/lawrules/rule/trade/t20250403_612770.html

Before Phase 4–6, confirm with the actual broker:

- whether the account/API usage is classified as program trading;
- reporting/registration requirements;
- permitted API/order channels;
- rate/order-frequency controls;
- testing requirements;
- account-specific permissions and restrictions.

The repository should never claim regulatory clearance merely because code passes tests.

---

## 12. Risk engine invariants

These rules must live in the risk layer, independent of strategy code.

### Before order

Reject if any condition fails:

- symbol is not in current approved universe;
- stale/unverified quote;
- event lockout is active;
- no invalidation exists;
- Reward/Risk is below required threshold without documented exception;
- per-trade risk exceeds current policy;
- portfolio heat exceeds current policy;
- industry/factor limit exceeded;
- account/position state is not reconciled;
- broker/compliance state invalid.

### After fill

- persist broker fill before updating strategy state;
- recompute actual risk using actual fill;
- if actual fill creates excessive risk, reduce/cancel according to predefined policy;
- never widen stop because fill was worse than expected.

### Kill switch

Must block new orders and optionally cancel outstanding orders when:

- risk-policy hard ceiling is reached;
- data feed is stale/broken;
- broker reconciliation fails;
- duplicate-order detection fires;
- strategy state is corrupted;
- exchange/broker reports abnormal status;
- operator manually activates emergency stop.

---

## 13. Failure modes to test before automation

At minimum inject/test:

- quote feed unavailable;
- quote delayed by 30–120 seconds;
- duplicated signal;
- repeated API retry after broker accepted order;
- partial fill;
- order rejected;
- order accepted but response lost;
- process restart while order is live;
- broker position differs from local state;
- stop gap-through;
- limit-down with no exit fill;
- suspension;
- ex-dividend mechanical price change;
- corporate event published between signal and execution;
- same stock simultaneously signaled by two strategy workers;
- same-factor portfolio limit breached by correlated symbols.

System must prefer **missing a trade** over creating an unknown-risk position.

---

## 14. Evaluation metrics

Do not evaluate the system only by total profit.

### Strategy edge

- closed trades;
- win rate;
- average win in R;
- average loss in R;
- expectancy in R;
- profit factor;
- median R;
- max drawdown;
- recovery time;
- return by setup;
- return by market regime;
- return by factor cluster.

### Trade quality

- MFE;
- MAE;
- entry efficiency;
- exit efficiency;
- time-stop outcomes;
- gap loss vs planned stop;
- event-isolation outcomes.

### Execution quality

- modeled vs actual fill;
- slippage;
- fees/taxes;
- rejection rate;
- partial-fill rate;
- stale-signal rate;
- duplicate-order count;
- reconciliation errors.

### Process quality

- rule-violation rate;
- manual override rate;
- overrides that helped vs hurt;
- missing-source/data incidents;
- hard-veto override attempts;
- no-trade days respected.

---

## 15. Parameter governance

Do not optimize thresholds directly on a tiny recent sample.

Every proposed rule change should include:

```text
proposal
reason
expected mechanism
affected setups
training/analysis sample
holdout or forward-validation plan
risk of overfitting
version change
rollback condition
```

Rules become versioned strategy artifacts.

A new version starts a new performance segment; do not silently merge results across materially different rules.

---

## 16. Repository layout for the future system

Recommended structure:

```text
skills/a-share-short-midterm-stock-selection/
├── SKILL.md
├── examples/
│   ├── 2026-08-26-final-watchlist-case-study.md
│   └── 2026-08-26-final-watchlist.json
├── references/
│   ├── scoring-system.md
│   ├── holding-risk-management.md
│   ├── industry-coverage-audit.md
│   ├── data-source-policy.md
│   ├── adversarial-review.md
│   ├── evaluation-cases.md
│   ├── research-basis.md
│   ├── paper-live-automation-roadmap.md
│   └── validation-metrics-and-trade-ledger.md
└── runtime/                     # future implementation, not required for the skill itself
    ├── configs/
    ├── snapshots/
    ├── signals/
    ├── paper/
    ├── live/
    ├── reports/
    └── logs/
```

Do not commit broker passwords, API secrets, account identifiers or other credentials.

---

## 17. End-state operating loop

The desired mature system is:

```text
locked watchlist
→ scheduled data refresh
→ official-event ingestion
→ market/sector regime
→ score + adversarial review
→ executable signal
→ risk engine
→ paper/live mode router
→ human confirmation if required
→ broker execution
→ fill reconciliation
→ position-state monitoring
→ exit management
→ immutable ledger
→ daily report
→ weekly/monthly evaluation
→ strategy-version governance
```

The most important design rule remains:

> **Research decides eligibility. Risk decides size. Execution decides what can actually be done. Evidence decides whether the system earns the right to become more automated.**
