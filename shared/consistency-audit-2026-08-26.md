# Repository Consistency Audit — 2026-08-26

## Scope

This audit checks the current `main` branch after the original-request completion upgrade. It covers:

- root `README.md`;
- Level 1A/1B/1C governance;
- upstream multi-asset allocation Skill;
- long-term retirement Skill;
- short/mid-term production Champion and Shadow Challenger;
- A-share Sentiment Regime Index;
- long-vs-tactical empirical Forward Study;
- MFE/MAE / Expected IRR / Total Return references;
- runnable Daily Monitor Runtime and GitHub Actions schedule;
- historical examples/snapshots.

Historical dated snapshots remain evidence records, not current policy.

## Governing hierarchy and scope

```text
Upstream scope:
Multi-Asset Allocation Skill
→ determines Equity Account Equity

Inside the stock account:
Level 1A — shared/capital-allocation-and-entry-policy.md
Level 1B — shared/automation-execution-governance.md
Level 1C — shared/research-model-governance.md
  ↓
Level 2  — skills/*/SKILL.md
  ↓
Level 3  — skills/*/references/*.md + research/*.md
  ↓
Level 4  — examples / dated snapshots / watchlists
```

The multi-asset Skill is upstream in scope, not higher in permission. Once money enters the stock account, Level 1A remains authoritative for capital/risk.

---

## Completion checks

### 1. Root architecture

**PASS.**

Root README now exposes:

- Multi-Asset Allocation;
- Long Retirement Investing;
- Short/Mid Stock Selection;
- A-share Sentiment Regime Index;
- Long-vs-Tactical Forward Study;
- Daily Monitor Runtime;
- Capital/Risk, Automation/Execution and Research/Model governance.

No new module is described as permission to bypass Level 1.

### 2. Multi-Asset Allocation upstream scope

**PASS.**

`skills/a-share-multi-asset-allocation/SKILL.md` manages:

```text
Total Financial Assets
→ Emergency/Liquidity Reserve
→ Near-term Liability Reserve
→ Fixed Income
→ Equity Account Equity
```

It explicitly does **not** redefine stock-account Final Short Cap, stock concentration, trade risk, strategy tranches or circuit breakers.

The policy-precedence file now records this boundary explicitly.

### 3. Liquidity / liability protection

**PASS as governance design.**

The multi-asset Skill requires emergency/liquidity and known near-term liabilities to be considered before equity allocation. The current `6–12 months` emergency-reserve range is labeled a Governance Parameter, not a universal optimum.

Final personal allocation cannot be generated without the user's actual spending/liability/risk inputs; the Skill returns `INSUFFICIENT_PERSONAL_INPUT_FOR_FINAL_ALLOCATION` instead of inventing precision.

### 4. Fixed-income opportunity cost

**PASS.**

The multi-asset and empirical-study documents use point-in-time government-bond yields as an opportunity-cost reference and explicitly prohibit permanently hard-coding the 2026-08-25 snapshot.

Fixed income is treated as liability matching / liquidity / volatility buffer, not as “risk-free high return.” Duration and credit risk are acknowledged.

### 5. Stock-account capital allocation

**PASS.**

No new upstream or sentiment module changes:

```text
Final Short Cap = min(Size Cap, Risk Cap, Edge Cap)
```

or the current Operating Target / Hard Ceiling.

The stock-account denominator and cross-strategy symbol/cluster aggregation remain governed by Level 1A.

### 6. Long-term valuation discipline

**PASS.**

Long-term still separates:

```text
Price Low != Valuation Low
```

and uses Bear/Base/Bull Expected IRR, Required Return sensitivity and Total Return benchmarks.

The multi-asset layer does not allow “cheap-looking stock” to override long-term Thesis / Balance / Valuation / Portfolio Gates.

### 7. Short/Mid Champion remains production model

**PASS.**

Current Champion remains:

```text
Technical 30
Capital Participation 30
Fundamentals 25
Catalyst 15
```

No sentiment or causal-model document silently replaces it.

### 8. Causal Challenger remains Shadow Only

**PASS.**

The Challenger remains research-only until formal Promotion Review.

Model Promotion remains separate from Automation Promotion.

### 9. A-Share Sentiment Regime Index

**PASS as a research/monitor layer.**

The new index is machine-readable and currently combines:

```text
Breadth                       25
Limit-up vs Limit-down        20
Board Quality / Broken Rate   15
Strong vs Weak Tail           15
Median Return                 10
Turnover Expansion            15
```

Regimes:

```text
PANIC / RISK_OFF / NEUTRAL / RISK_ON / EUPHORIA
```

Critical boundaries are explicit:

- `EUPHORIA != ALL_IN`;
- sentiment cannot bypass Hard Veto;
- sentiment cannot enlarge Final Short Cap or Hard Ceiling;
- missing data can return `DATA_INSUFFICIENT`;
- weights/thresholds are Governance Parameters requiring Forward calibration.

### 10. Sentiment integration into Short/Mid documentation

**PASS.**

The Short/Mid README now directly references `a-share-sentiment-regime-index.md`, documents its role and lists the runtime monitor path.

Sentiment is a market-state input, not an autonomous buy/sell engine.

### 11. Long-vs-Tactical empirical study

**PASS as an experiment design; outcome intentionally NOT YET CLAIMED.**

`research/a-share-long-vs-tactical-empirical-study.md` defines a fair comparison between:

```text
Long Core
Short/Mid Champion
Causal Challenger (Shadow)
Broad Total Return Benchmark
Cash / Government-Bond Opportunity Cost
```

It requires cost, drawdown, turnover and risk-adjusted metrics, not only return.

It explicitly rejects inventing a historical 2015–2026 strategy result using current survivors/future information.

The exact numerical answer to “our short-term system vs our long-term system differs by how much” is therefore a **Forward empirical result that must accrue through time**, not a number that can be honestly manufactured on 2026-08-26.

### 12. Total Return benchmark

**PASS.**

Long-term comparison uses total-return benchmarks where available; CSI300 is documented with price `000300` vs total-return `H00300`.

A dividend-receiving portfolio cannot silently claim excess return against price-only benchmark data.

### 13. Daily Monitor Runtime exists

**PASS architecturally.**

Runtime now includes:

```text
runtime/monitor.py
runtime/daily_monitor.py
runtime/tests/test_monitor.py
runtime/requirements.txt
runtime/README.md
```

The monitor performs:

```text
trade-calendar check
→ A-share spot market
→ limit-up / limit-down / broken-board pools
→ sentiment calculation
→ 43-stock watchlist price merge
→ pre_action monitor states
→ JSON / Markdown daily report
→ turnover-history ledger
```

### 14. Runtime does not auto-trade

**PASS.**

Runtime reports explicitly preserve:

```text
AUTO_MONITOR = true
AUTO_ORDER   = false
```

Pre-actions such as:

```text
REFRESH_FULL_GATES
REFRESH_SETUP
WAIT_NO_CHASE
EVENT_REVIEW
NO_NEW_ENTRY
```

are research states, not executable broker orders.

No broker credential, account ID or order submission adapter is present.

### 15. Runtime fail-closed calendar gate

**PASS by code review.**

If the trade calendar cannot be resolved:

```text
trading_day_status = TRADE_CALENDAR_UNKNOWN
sentiment_score = None
regime = DATA_INSUFFICIENT
calendar_gate = BLOCKED
```

Thus an apparently valid/stale market payload cannot unlock new risk when calendar state is unknown.

Market-closed days are similarly blocked.

### 16. Runtime missing-data handling

**PASS by code review.**

Sentiment components may reweight only when at least 70% of original factor weight is available. Otherwise:

```text
DATA_INSUFFICIENT
```

Missing stock-market data produces `NO_ACTION_DATA_MISSING` / blocked monitor states instead of guessed values.

Turnover history is explicitly flagged not ready until enough observations accumulate; confidence cannot be marked HIGH before that history exists.

### 17. Runtime deterministic action engine

**PASS by code review.**

The pure `decide_short_mid_action` engine prevents incomplete data from returning READY/ADD and implements conservative state transitions for risk-off, invalidation, risk breach and add confirmation.

It still does not bypass full production Skill / broker gates.

### 18. Runtime unit tests / compile gate

**PASS as repository configuration; first hosted run still pending at audit time.**

GitHub Actions runs:

```text
python -m compileall -q runtime
python -m unittest discover -s runtime/tests -v
python runtime/daily_monitor.py
```

The initial hosted workflow run created for this upgrade is currently **QUEUED**, so this audit does **not** claim hosted CI has passed yet.

The queued run is evidence that the workflow is registered, not evidence of test success.

### 19. Scheduled monitoring

**PASS as configuration.**

The workflow schedules weekdays at:

```text
07:40 UTC ≈ 15:40 Asia/Shanghai
```

Actual GitHub execution may have queue delay. Chinese holidays are handled by the market-calendar gate rather than cron alone.

### 20. Provider provenance

**PASS for MVP with explicit limitation.**

AKShare is treated as an aggregation Provider for research/monitor MVP.

The repository explicitly requires official disclosure / broker market and position cross-check before advancing to Live/Semi-auto/Auto execution.

### 21. Automatic strategic asset reallocation

**PASS — remains disabled.**

Multi-asset configuration uses:

```text
AUTO_MONITOR = true
AUTO_STRATEGIC_REALLOCATION = false
```

Short-term sentiment cannot automatically liquidate bonds into stocks or stocks into bonds.

### 22. Historical snapshots

**PASS.**

The 2026-08-26 43-stock whitelist and long-term ten-stock portfolio remain point-in-time Level-4 baselines.

Daily monitor merging with the 43-stock list does not turn that historical list into a permanent buy list: each candidate still requires fresh gates before execution.

---

## Current Source-of-Truth / Implementation map

| Topic | Current source |
|---|---|
| Upstream cash/bond/equity allocation | `skills/a-share-multi-asset-allocation/SKILL.md` |
| Stock-account capital/risk | `shared/capital-allocation-and-entry-policy.md` |
| Automation/Broker safety | `shared/automation-execution-governance.md` |
| Research/model governance | `shared/research-model-governance.md` |
| Policy precedence/scope | `shared/policy-precedence.md` |
| Long production Skill | `skills/a-share-retirement-investing/SKILL.md` |
| Long Expected IRR / Total Return | `skills/a-share-retirement-investing/references/expected-irr-total-return-benchmark.md` |
| Short/Mid production Skill | `skills/a-share-short-midterm-stock-selection/SKILL.md` |
| Short/Mid Champion score | `skills/a-share-short-midterm-stock-selection/references/scoring-system.md` |
| Sentiment model | `skills/a-share-short-midterm-stock-selection/references/a-share-sentiment-regime-index.md` |
| Causal Challenger | `skills/a-share-short-midterm-stock-selection/references/causal-challenger-model.md` |
| Champion/Challenger test | `skills/a-share-short-midterm-stock-selection/references/champion-challenger-forward-test.md` |
| Trade-learning ledger | `skills/a-share-short-midterm-stock-selection/references/trade-ledger-mfe-mae-extension.md` |
| Long-vs-Tactical empirical protocol | `research/a-share-long-vs-tactical-empirical-study.md` |
| Daily market/sentiment monitor | `runtime/daily_monitor.py` |
| Deterministic monitor logic | `runtime/monitor.py` |
| Runtime tests | `runtime/tests/test_monitor.py` |
| Scheduled runner | `.github/workflows/a-share-daily-monitor.yml` |

---

## Regression questions

1. Can Multi-Asset Allocation bypass stock-account Final Short Cap? **No.**
2. Can emergency/near-term liability money be silently counted as deployable individual-stock capital? **No.**
3. Can EUPHORIA automatically increase strategy risk? **No.**
4. Can sentiment override an accounting/governance Hard Veto? **No.**
5. Can an unknown trade calendar unlock READY? **No.**
6. Can missing core market data be silently imputed into a full-confidence sentiment score? **No.**
7. Can a monitor `pre_action` be treated as a broker order? **No.**
8. Is `AUTO_ORDER` enabled? **No.**
9. Can the Causal Challenger silently replace the Champion? **No.**
10. Can a short-term loser be renamed long-term to avoid realizing a loss? **No.**
11. Can a dividend portfolio use a price-only benchmark without disclosure? **No.**
12. Can the repository claim its own short-vs-long CAGR before Forward observations exist? **No.**
13. Can historical survivors/future filings be used to manufacture promotable backtest performance? **No.**
14. Can the scheduled monitor trade on a Chinese holiday merely because cron fired? **No; calendar gate blocks it.**
15. Can passing model research automatically enable Full Auto? **No.**

---

## Remaining empirical caveat

The missing **infrastructure** identified in the original-request acceptance review is now implemented:

```text
long-vs-tactical empirical protocol
+ sentiment model
+ multi-asset allocation layer
+ runnable/scheduled monitor MVP
```

One result cannot be honestly completed instantly:

```text
Our own realized/Forward numerical short-vs-long performance difference
```

That number requires future observations. The repository is now configured to accumulate the necessary evidence rather than fabricate it.

The first hosted GitHub Actions run is still queued at this audit timestamp; hosted test success must be recorded only after GitHub actually executes it.
