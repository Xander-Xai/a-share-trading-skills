# A-share Trading Skills

A 股一级资产配置、长期养老投资、短中期交易与自动化监控 / 研究实现仓库。

## Architecture

当前目标不是一套统一的“炒股模型”，而是：

```text
Multi-Asset Allocation
→ Stock Account Equity
→ Level-0 Capital Eligibility / Pre-Trade Authorization

Shared Governance + Shared Core Platform
                 │
       ┌─────────┴─────────┐
       │                   │
Long Retirement        Short/Mid Tactical
Decision Engine        Decision Engine
       │                   │
       └─────────┬─────────┘
                 ↓
Account / Risk / Ledger / Execution
```

核心原则：

```text
共享事实
+ 共享账户真相
+ 共享执行基础设施

但不共享：
时间尺度
决策逻辑
主要验证标准
```

## Current governance versions

```text
Capital Eligibility:    v2 (Level 0 hard veto)
Pre-Trade Authorization: v1.1 (Level 0 hard veto)
Capital / Risk:          v2.5
Automation / Execution: v1.4
Research / Model:        v3.2
Strategy Boundary:       v1
Canonical PIT Data:      v1.2
```

规则优先级读取 `shared/policy-precedence.md`。

## Real-money buy hard gate

本仓库现在把“买什么”和“能不能用这笔钱买”分开。任何真实资金 `ENTRY` / `ADD` 在输出具体股数前必须经过：

```text
个人现金安全
→ 闲钱资格
→ 应急金 / 近期现金需求 / 借款杠杆 Gate
→ 当前账户与策略暴露
→ 交易触发 / 失效点
→ 风险预算
→ 最严格约束反推股数
→ 按证券所属市场的最小申报数量/递增单位向下取整
```

关键输入缺失时：

```text
WATCH / READY allowed
executable buy shares = 0
```

Paper 模式复用相同的风险/仓位几何，但使用隔离的 `paper_capital_rmb` 与模拟持仓，不要求、也不得伪造个人应急金/现金需求答案。

核心文件：

- `shared/capital-eligibility-and-investor-risk-philosophy.md`
- `shared/pre-trade-order-authorization-contract.md`
- `src/core/pretrade_risk_gate.py`
- `runtime/pretrade_cli.py`

手工运行风险问卷：

```bash
python runtime/pretrade_cli.py
```

程序给出的股数是风险约束后的**最大/计划批次**，不是收益承诺；可以买得更少，买得更多必须重新授权。

## Strategy identities

```text
strategy_id = a_share_long_retirement
sleeve      = long

strategy_id = a_share_short_mid
sleeve      = short_mid
```

机器可执行 decision / replay / paper / order artifact 必须逐步统一保存 `strategy_id + sleeve`。

详见：

- `shared/strategy-boundary-contract.md`
- `shared/research-model-governance.md`

## Long vs Short/Mid

### Long

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

长期主要用 Total Return、Expected IRR calibration、估值/Thesis 错误、Dividend/FCF、永久性资本损失和组合适配验证。

以下短中期逻辑不得自动覆盖长期决策：

```text
ERG reaction window
momentum confirmation
5/10/20-day tactical forward return
planned-R tactical stop
short tactical time stop
```

### Short/Mid

```text
Eligibility
→ Expectation / Surprise
→ Materiality
→ Prepricing
→ Reaction / Participation
→ Regime
→ Execution Geometry
→ Risk Resilience Layer
→ Tactical Risk / Sizing
→ Position State / Re-underwriting
→ Outcome Validation
```

当前 Champion：

```text
Technical 30
Capital Participation 30
Fundamentals 25
Catalyst 15
```

ERG / Causal Challenger 仍为 `SHADOW ONLY`，Alpha 未证明。

短中期新增横向 `Risk Resilience Layer`，用于把 PIT、条件路径、执行压力、仓位集中、持仓状态漂移和验证分类串成统一抗错误流程。它可以使决策更保守，但不能增加生产仓位、风险额度或订单权限。

当前短中期风险韧性原则：

```text
Gate First
→ State Second
→ Geometry Third
→ Stress Fourth
→ Size Fifth
→ Confirm Sixth
→ Re-underwrite While Holding
→ Validate After Outcome
```

详见：

- `skills/a-share-short-midterm-stock-selection/references/risk-resilience-layer.md`
- `research/short-mid-risk-resilience-integration-v1.md`
- `research/short-mid-risk-resilience-experiment-v1.md`

## Short/Mid sample evidence pipeline

真实交易样本采用：

```text
User supplies private execution truth
        ↓
Sample Registry + Manual Trade Events
        ↓
Daily Market Monitor
        ↓
Sample Evidence Collector
        ├─ daily unadjusted OHLCV / turnover
        ├─ broad benchmark / relative strength
        ├─ market regime
        ├─ vendor-flow corroboration
        ├─ exchange margin detail when available
        ├─ disclosure scan
        └─ MFE / MAE + D1/D3/D5/D10/D15 checkpoints
        ↓
Sample Data Maturity Report
        ↓
Forward / retrospective research according to evidence class
```

用户不需要每天手工抄行情。默认只报告机器无法知道的真实成交/账户事实，例如：

```text
SYNTHETIC EXAMPLE
NOT REAL USER DATA

SYNTHETIC EXAMPLE
NOT REAL USER DATA

```

公开行情、成交、市场宽度、融资、公告和派生特征由系统按合同采集。数据覆盖率不等于 Alpha；成熟度报告只回答“证据是否完整、可审计”。

详见：

- `skills/a-share-short-midterm-stock-selection/references/sample-data-acquisition-contract.md`
- `runtime/config/sample_registry.json`
- `runtime/state/sample_evidence/manual_events/trade_events.jsonl`

## Shared account risk

```text
Stock Account Equity
= Long Stock Value
+ Short/Mid Stock Value
+ Pending Stock-account Cash
```

账户级风险跨策略聚合：

```text
Account Symbol Exposure
= Long Sleeve Exposure + Short/Mid Sleeve Exposure

Account Cluster Exposure
= Long Cluster Exposure + Short/Mid Cluster Exposure
```

策略标签不能创造第二套风险额度。

Broker 阶段必须同时维护：

```text
Broker Net Position
Strategy Virtual Position: long
Strategy Virtual Position: short_mid
```

## Canonical PIT direction

生产研究逐步采用：

```text
Immutable Raw Evidence
→ Normalized PIT Record
→ Feature Snapshot
→ Strategy Decision
→ Outcome / Order
```

核心元数据：

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

`available_at` 表示研究可见性；`first_tradable_timestamp` 属于执行层，两者不得混用。

详见 `shared/canonical-pit-data-contract.md`。

## Current runtime

当前可运行代码是 **Short/Mid Monitor + Sample Evidence MVP**，不是完整生产交易系统，也不是长期 Runtime。

```text
runtime/daily_monitor.py
runtime/sample_collector.py
runtime/sample_maturity.py
runtime/monitor.py
runtime/config/short_mid_universe.json
runtime/config/sample_registry.json
runtime/state/sample_evidence/
runtime/tests/
src/core/strategy_boundary.py
src/core/pit.py
.github/workflows/a-share-daily-monitor.yml
```

当前模式：

```text
strategy_id = a_share_short_mid
sleeve      = short_mid
runtime_mode = SHORT_MID_MONITOR_ONLY
AUTO_MONITOR = true
AUTO_ORDER   = false
```

默认 runtime universe 已从历史 `examples/` 解耦到：

`runtime/config/short_mid_universe.json`

真实/研究样本注册表独立维护于：

`runtime/config/sample_registry.json`

`examples/` 继续作为 Level-4 历史 / Forward / Replay evidence，不是未来 production-current universe 真相源。

### Local checks

```bash
python -m pip install -r runtime/requirements.txt
python -m pip check
python -m compileall -q runtime src
python -m unittest discover -s runtime/tests -v
python runtime/daily_monitor.py
python runtime/sample_collector.py
python runtime/sample_maturity.py
```

当前测试包括：

- 数据不足 fail closed；
- PANIC / RISK_OFF 语义；
- 长期 sleeve 不能进入 short/mid engine；
- PIT `available_at` 不得早于 `published_at`；
- replay 时间早于 `available_at` 时记录不可见；
- runtime universe 必须声明正确 `strategy_id / sleeve`；
- 默认 runtime universe 不再指向 Level-4 example；
- 买入日具体成交时刻未知时，不把买入日前/盘中未知高低点冒充成交后 MFE/MAE；
- 样本每日证据重复运行保持幂等，证据变化产生 revision；
- D1/D3/D5/D10/D15 checkpoint 使用固定交易会话窗口；
- 数据成熟度与 Alpha 验证语义分离。

## Production evolution

批准的生产演进依据：

`research/production-system-evolution-report-2026-08-28.md`

第一阶段目标不是自动下单，而是：

```text
PIT Reproducible Research Core
```

Short/Mid 实施顺序：

```text
Strategy Boundary + PIT Data Contract
→ Canonical Data Store / Snapshot
→ Champion Engine
→ ERG Engine
→ Historical Replay
→ Forward / Ablation / Placebo
→ Paper Ledger / Broker Simulator
→ Reconciliation
→ Human-confirmed Live
→ Optional Semi-auto
```

Risk Resilience 的当前实现首先是方法论/审计层；其 Follow-through、Volume/Price Efficiency、Stress-aware Sizing、Holding Inertia、Conditional Path Calibration 等新增假设必须留在 Shadow 研究协议，未经验证不得直接改生产引擎。

Sample Evidence Pipeline 当前首先解决：

```text
consistent user-input contract
+ automatic public-data accumulation
+ PIT-aware timestamps
+ immutable/revisioned evidence
+ checkpoint features
+ data-completeness reporting
```

它不等于完整历史数据库，也不等于已验证的交易 Alpha。

Long 单独演进：

```text
Long Quality Engine
→ Cash Flow / Dividend Engine
→ Expected IRR / Valuation Engine
→ Long Paper Portfolio
→ Automated Research / Manual Order can remain the end state
```

Qlib、vn.py、PostgreSQL、MLflow、Prefect、OpenTelemetry 等按真实需求逐步引入，不一次性堆栈。

## Repository map

```text
shared/
  policy-precedence.md
  capital-allocation-and-entry-policy.md
  automation-execution-governance.md
  research-model-governance.md
  strategy-boundary-contract.md
  canonical-pit-data-contract.md

research/
  a-share-long-vs-tactical-empirical-study.md
  production-system-evolution-report-2026-08-28.md
  short-mid-blind-replay-theoretical-audit-v1.md
  short-mid-risk-resilience-integration-v1.md
  short-mid-risk-resilience-experiment-v1.md

skills/
  a-share-multi-asset-allocation/
  a-share-retirement-investing/
  a-share-short-midterm-stock-selection/
    references/risk-resilience-layer.md
    references/sample-data-acquisition-contract.md

src/core/
  strategy_boundary.py
  pit.py

runtime/
  daily_monitor.py
  sample_collector.py
  sample_maturity.py
  monitor.py
  config/short_mid_universe.json
  config/sample_registry.json
  state/sample_evidence/
  tests/

reports/
  daily/
```

## Rule precedence

```text
Level 0   capital eligibility / pre-trade authorization
    ↓
Level 1A  capital / risk
Level 1B  automation / execution
Level 1C  research / model
    ↓
Level 2   skills/*/SKILL.md
    ↓
Level 3   references + research
    ↓
Level 4   examples / snapshots / dated watchlists
```

`runtime/* + src/* + workflows` 是 Implementation Layer，必须服从规则层；实现方便不能反过来改变生产语义。

## Automation principle

```text
Research
→ Forward Paper
→ Manual Live
→ Automated Research / Manual Order
→ Human-confirmed Broker Execution
→ Limited Semi-auto
→ Full Auto only after Edge + Compliance + Reliability gates
```

Full Auto 不是强制终点，尤其长期账户可长期停留在自动研究 + 人工确认。

任何 Paper/Live 决策逐步统一保存：

```text
capital_policy_version
automation_governance_version
research_model_governance_version
skill_version
strategy_id
sleeve
strategy_version
model_version
data_snapshot_id
```

模型晋级不等于自动化晋级。
