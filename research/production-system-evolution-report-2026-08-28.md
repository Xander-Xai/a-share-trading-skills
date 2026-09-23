# A-share Methodology → Production System Evolution Report — 2026-08-28

> HISTORICAL SNAPSHOT / NOT CURRENT IMPLEMENTATION INVENTORY
>
> This report records the repository assessment as of 2026-08-28. Statements about components being planned or not yet implemented are historical and are not authoritative descriptions of current `main`; consult `configs/governance/current-state.json`, active contracts and the tracked implementation.

> Status: `APPROVED ARCHITECTURE BASIS`
>
> Scope: repository evolution from Skill/Governance-led research to reproducible research, Paper and optional Live execution.
>
> This report does not promote a trading model, change the current Champion, loosen risk limits, or authorize broker orders.

## 1. Executive conclusion

The repository should not evolve into one monolithic "A-share model".

The correct target is:

```text
Shared Governance + Shared Core Platform
                 │
       ┌─────────┴─────────┐
       │                   │
Short/Mid Tactical      Long-term Equity
Decision Engine         Decision Engine
       │                   │
       └─────────┬─────────┘
                 ↓
Account / Risk / Ledger / Execution
```

Core principle:

> Share facts, account truth and execution plumbing; do not share time scale, decision logic or primary validation metrics.

## 2. Current-state correction

The repository is no longer a pure Markdown methodology collection.

It already contains:

```text
runtime/daily_monitor.py
runtime/monitor.py
runtime/tests/
.github/workflows/a-share-daily-monitor.yml
reports/private/
runtime/state/
```

The runtime is, however, a Monitor MVP rather than a production trading engine.

Current practical state:

```text
Governance / policy                  = relatively mature specification
Short/Mid methodology               = relatively mature specification
Long-term methodology               = relatively mature specification
Market monitor                      = MVP code
Canonical PIT data store            = not yet implemented
Short/Mid Champion engine           = not yet fully implemented
ERG engine                          = not yet fully implemented
Long-term valuation engine          = not yet fully implemented
Historical replay                   = not yet implemented
Paper broker / accounting           = not yet implemented
Live reconciliation                 = not yet implemented
```

Avoid arbitrary percentage-complete claims because there is no objective denominator.

## 3. Why Skill/Markdown still matters

Skill and governance documents are not a defect by themselves. Their correct role is specification.

Target traceability:

```text
Human Rule
→ Machine Contract
→ Executable Implementation
→ Automated Test
→ Runtime Evidence
```

A production system should not replace all Markdown with Python. It should make important rules machine-checkable while retaining policy as the upstream source of truth.

## 4. Strategy boundary: long and short/mid are different systems

### 4.1 Short/Mid

Economic objective:

```text
Expectation Change
→ Materiality
→ Prepricing
→ Market Reaction / Participation
→ Regime
→ Execution Geometry
→ Tactical Risk
```

Typical evidence:

```text
Champion score
ERG state
confirmation basis
relative strength
RVOL / participation
trigger / invalidation
planned R/R
MFE / MAE
1/3/5/10/20-day forward outcomes
```

### 4.2 Long-term

Economic objective:

```text
Survival / Governance
→ Business Durability
→ Normalized Earnings / FCF
→ Balance Sheet
→ Dividend Sustainability
→ Per-share Value Creation
→ Expected IRR / Valuation
→ Portfolio Fit
```

Typical evidence:

```text
quality score
Bear/Base/Bull expected IRR
Max Buy Price
margin of safety
thesis state
normalised earnings / FCF
capital allocation quality
dividend sustainability
long-horizon total return
```

### 4.3 Prohibited cross-contamination

Do not force these Short/Mid concepts into long-term promotion/exit logic:

```text
ERG reaction window
momentum confirmation
short-term R-multiple stop
5/10/20-day forward return
short tactical time stop
```

Likewise, a high long-term Expected IRR is not a Short/Mid entry trigger.

## 5. Shared infrastructure that should be built once

The following should be shared:

```text
security master
exchange / trading calendar
session rules
company filings
financial statements
corporate actions
market data
point-in-time metadata
source provenance
permitted-use / data-license metadata
account equity
broker positions
orders / fills
cash ledger
cross-sleeve symbol exposure
cross-sleeve factor / cluster exposure
audit log
CI / tests
reconciliation
```

The decision engines remain separate.

## 6. First production milestone is not auto trading

Define production maturity by capabilities rather than `AUTO_ORDER=true`.

### P1 — Production Research

```text
automatic ingest
PIT-valid snapshots
reproducible strategy research
versioned outputs
auditable source lineage
no broker order
```

### P2 — Production Paper

Add:

```text
orders
fills
cash
positions
fees / taxes / slippage
T+1
price limits / suspension
corporate actions
```

### P3 — Production Assisted Live

```text
System proposes order
→ independent risk gate
→ human confirmation
→ broker execution
→ reconciliation
```

This can be a valid long-term end state.

### P4 — Optional Full Auto

Only after edge, compliance and execution reliability are independently validated.

## 7. Corrected implementation priorities

### P0 — Strategy and data correctness

1. Strategy Boundary Contract.
2. Canonical PIT Data Contract.
3. Data permitted-use / license metadata.
4. Separate common vs Short/Mid vs Long promotion metrics.
5. Remove historical Level-4 example files as runtime default production universe.

### P1 — Reproducible data core

Build:

```text
Immutable raw evidence
→ normalized PIT store
→ data snapshot id
→ feature snapshot
```

Minimum reusable entities:

```text
security master
calendar
quotes / daily bars
disclosures
financial statements
corporate actions
industry / index membership
expectation data when available
```

### P2 — Short/Mid Champion Engine

Code the current Champion as a versioned deterministic scorer/gate implementation.

Expected shape:

```text
src/strategies/short_mid/champion/
```

Output should preserve component scores, penalties, vetoes, status and model version.

### P3 — ERG Engine

Suggested components:

```text
Expectation
Surprise
Materiality
Prepricing
Reaction
Research State
```

Not every component should be forced into deterministic numeric code.

Use deterministic code for:

```text
timestamps
prices
abnormal returns
relative strength
RVOL
session eligibility
risk/account arithmetic
```

Use bounded AI/human research for:

```text
event classification
economic transmission
materiality rationale
business impact
```

AI-derived artifacts must preserve model/prompt/evidence versioning.

### P4 — Historical Replay / Time Machine

Replay must answer:

> What did the system know at historical time T?

Invariant:

```text
record.available_at <= replay_as_of
```

Then reconstruct:

```text
Data Snapshot
→ Strategy Engine
→ Decision
→ Future outcomes
```

This is the prerequisite for serious ablation, placebo, DSR/PBO-style statistical review and historical model comparison.

### P5 — Forward / Ablation / Placebo

Use the existing governance and frozen-cohort system.

Do not change benchmark, cost, reaction-window or model definition after outcomes.

### P6 — Paper Ledger / Broker Simulator

Add transactional state only when decisions are reproducible.

### P7 — Account / Position / Reconciliation

Maintain:

```text
Broker Net Position
Strategy Virtual Position: long
Strategy Virtual Position: short_mid
```

### P8 — Human-confirmed Live

Broker integration begins only after Paper accounting and reconciliation are stable.

### P9 — Optional Semi-auto / Auto

Not a required endpoint.

## 8. Runtime scope correction

Current `runtime/` monitor is economically a Short/Mid monitor because it consumes tactical watchlist state, market-regime/crowding logic and short tactical pre-actions.

It should not be interpreted as the future general runtime for the long-term sleeve.

Migration direction:

```text
src/core/
src/strategies/short_mid/
src/strategies/long_term/
runtime/jobs/
```

Do not perform a disruptive file move before imports/tests/workflows are ready. Migrate incrementally.

## 9. Universe correction

A dated example/watchlist is Level-4 evidence, not a production-current universe source.

Production runtime should consume a separate versioned runtime universe/config or database query.

Historical examples remain immutable replay/Forward evidence.

## 10. Data architecture

Recommended logical model:

```text
Raw Evidence
↓
Normalized PIT Record
↓
Feature Snapshot
↓
Strategy Decision
↓
Outcome / Order
```

Canonical PIT metadata should include:

```text
effective_at
published_at
available_at
ingested_at
source
source_tier
source_snapshot_id
revision_id
payload_hash
permitted_use
strategy_visibility
```

`available_at` is research visibility. `first_tradable_timestamp` is an execution concept and remains separate.

## 11. Technology stack: corrected, staged approach

Do not introduce infrastructure because it is fashionable.

### Research V1

Prefer a lightweight stack:

```text
Python
Parquet
DuckDB
Pydantic/dataclasses
pytest
Git / GitHub Actions
```

DuckDB can query Parquet directly and supports filter/projection pushdown, which is suitable for a small-team historical research store.

Reference:
https://duckdb.org/docs/current/guides/file_formats/query_parquet

### Add PostgreSQL later

When transactional state appears:

```text
orders
fills
positions
cash
reconciliation
```

### MLflow is optional

MLflow is useful when experiment count/lineage becomes difficult to manage. Until then a versioned experiment manifest containing Git SHA, data snapshot ID, config and metrics is sufficient.

Reference:
https://mlflow.org/docs/latest/ml/tracking/

### Prefect is optional

GitHub Actions is sufficient for coarse EOD CI/scheduled monitor jobs, but scheduled workflows can be delayed under load and are unsuitable for precision intraday execution timing.

Use a workflow orchestrator only when DAG/retry/backfill/concurrency requirements justify it.

References:
https://docs.github.com/en/actions/using-workflows/events-that-trigger-workflows#schedule
https://docs.prefect.io/v3/concepts/deployments

### Observability should grow with system complexity

Current priority:

```text
structured JSON logs
provider health
data freshness
job status
decision counts
```

OpenTelemetry / Prometheus / Grafana become useful when multiple persistent services exist.

Reference:
https://opentelemetry.io/docs/what-is-opentelemetry/

## 12. Qlib: useful component, not source of truth

Qlib is useful for research/backtest components and provides PIT-related tooling, portfolio strategy and recorder concepts.

However, its example China PIT collector documentation explicitly warns about public-source data quality. Therefore:

```text
Qlib != production A-share PIT truth source
```

Use it selectively for research infrastructure if it reduces implementation cost.

References:
https://qlib.readthedocs.io/en/stable/advanced/PIT.html
https://github.com/microsoft/qlib/blob/main/scripts/data_collector/pit/README.md

Our event/session-aware ERG replay will still require custom logic.

## 13. Broker framework: abstraction first

vn.py/VeighNa exposes multiple A-share gateways, but actual availability depends on broker, account, interface permission and testing access.

Target:

```text
Our Decision / Risk Engine
→ BrokerAdapter interface
→ optional vn.py gateway
→ actual broker
```

Do not make vn.py itself the strategy or governance source of truth.

References:
https://github.com/vnpy/vnpy
https://github.com/vnpy/vnpy_tora

## 14. Data-license and compliance are production concerns

A feed being technically accessible does not imply unrestricted production/redistribution rights.

Future data adapters must preserve permitted-use metadata and verify exchange/vendor terms where required.

Programmatic-order capability must also be separated from model quality. Before automated A-share order submission, re-check current CSRC/exchange rules and actual broker/account requirements.

Research baselines:

https://www.csrc.gov.cn/csrc/c100028/c7480577/content.shtml
https://www.sse.com.cn/lawandrules/sselawsrules2025/trade/universal/c/c_20250612_10781696.shtml
https://www.szse.cn/lawrules/rule/trade/t20250403_612770.html

These URLs are research baselines, not a substitute for fresh compliance review before Live.

## 15. Production acceptance criteria

The project becomes materially production-grade when it can answer YES to increasingly many of these questions:

```text
Can a decision be replayed?
Can every input be traced to a source/version?
Can a result be reproduced from snapshot + code + config?
Can long and short/mid states be proven not to contaminate each other?
Can a rule be automatically tested?
Can data staleness/conflict fail closed?
Can an experiment be reconstructed?
Can Paper positions be reconciled?
Can a duplicate order be prevented?
Can a restart recover state safely?
Can broker truth and strategy virtual books reconcile?
Can production use of the data be justified?
```

## 16. Immediate repository actions approved by this report

Implement now:

```text
1. strategy-boundary-contract.md
2. canonical-pit-data-contract.md
3. sleeve-specific research-promotion metrics
4. runtime strategy/sleeve tagging + mismatch fail-closed test
5. runtime universe config decoupled from historical examples
6. initial src/core machine contracts
```

Do not yet:

```text
replace current Champion
promote ERG
build auto-order
force long-term into tactical metrics
adopt Qlib/MLflow/Prefect/Postgres merely for architecture appearance
```

## 17. Final architecture principle

```text
Shared Facts
+ Shared Account Truth
+ Shared Execution Plumbing

BUT

Separate Time Scale
+ Separate Decision Engine
+ Separate Validation Standard
```

This is the production-system basis for subsequent implementation.
