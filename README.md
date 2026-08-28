# A-share Trading Skills

A股一级资产配置、长期养老投资、短中期交易与自动化监控 Skill / Runtime 集合。

当前仓库形成“共享基础设施 + 双策略引擎”的演进方向：

```text
Multi-Asset Allocation Skill
→ 决定多少资本成为 Stock Account Equity

Shared Governance / Data / Account / Execution Core
        │
        ├─ Long Retirement Investing Skill
        │  → 长期质量 / 现金流 / 分红 / Expected IRR / Valuation
        │
        └─ Short/Mid Stock Selection Skill
           → Champion / ERG / Regime / Execution / Tactical Risk

Current Runtime
→ short_mid Monitor MVP only
```

核心边界：

```text
共享事实
+ 共享账户真相
+ 共享执行基础设施

但不共享：
时间尺度
决策逻辑
主要验证标准
```

## 当前治理版本

```text
Capital / Risk:          v2.3
Automation / Execution: v1.2
Research / Model:        v3.2
Strategy Boundary:       v1
Canonical PIT Data:      v1
```

版本号分别属于不同 artifact，优先级由 `shared/policy-precedence.md` 决定。

## 当前结构

```text
a-share-trading-skills/
├── README.md
├── shared/
│   ├── policy-precedence.md
│   ├── capital-allocation-and-entry-policy.md
│   ├── automation-execution-governance.md
│   ├── research-model-governance.md
│   ├── strategy-boundary-contract.md
│   ├── canonical-pit-data-contract.md
│   ├── research-validation-2026-08-26.md
│   ├── adversarial-research-review-2026-08-26.md
│   └── consistency-audit-2026-08-26.md
├── research/
│   ├── a-share-long-vs-tactical-empirical-study.md
│   └── production-system-evolution-report-2026-08-28.md
├── src/
│   └── core/
│       ├── strategy_boundary.py
│       └── pit.py
├── runtime/
│   ├── README.md
│   ├── requirements.txt
│   ├── monitor.py
│   ├── daily_monitor.py
│   ├── config/
│   │   └── short_mid_universe.json
│   └── tests/
├── .github/workflows/
│   └── a-share-daily-monitor.yml
└── skills/
    ├── a-share-multi-asset-allocation/
    ├── a-share-retirement-investing/
    └── a-share-short-midterm-stock-selection/
```

## 从全部金融资产到股票账户

Multi-Asset Allocation Skill 先解决：

```text
Total Financial Assets
→ Emergency / Liquidity Reserve
→ Near-term Liability Reserve
→ Fixed Income
→ Stock Account Equity
```

股票账户内部再进入：

```text
Stock Account Equity
→ Long Strategic Baseline
+ Short/Mid Final Cap
+ Stock-account Pending Cash
```

统一术语为 `Stock Account Equity`。

Multi-Asset Skill 只决定有多少资本进入股票账户，不得绕过股票账户 Level 1A 风险规则。

## 规则优先级

```text
Level 1A  shared/capital-allocation-and-entry-policy.md
Level 1B  shared/automation-execution-governance.md
Level 1C  shared/research-model-governance.md
    ↓
Level 2   skills/*/SKILL.md
    ↓
Level 3   skills/*/references/*.md + research/*.md
    ↓
Level 4   examples / case studies / dated snapshots / watchlists
```

另外：

```text
runtime/* + src/* + .github/workflows/*
= Implementation Layer
```

实现层必须服从当前 Policy / Skill / Champion，不能反过来定义生产规则；`reports/` 与 `runtime/state/` 属于 Generated Evidence / Runtime State。

## Strategy Boundary

稳定机器身份：

```text
strategy_id = a_share_long_retirement
sleeve      = long

strategy_id = a_share_short_mid
sleeve      = short_mid
```

长期与短中期共享：

```text
security master
PIT data
calendar/session
filings
prices
corporate actions
account equity
broker positions
orders/fills
cross-sleeve exposure
reconciliation
audit
```

但不能共享一个决策脑。

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

### Short/Mid

```text
Eligibility
→ Expectation / Surprise
→ Materiality
→ Prepricing
→ Reaction / Participation
→ Regime
→ Execution Geometry
→ Tactical Risk
```

明确禁止：

```text
short_mid ERG INVALIDATED
!= automatic long EXIT

5/10/20-day tactical outcome
!= long-term model promotion gate

long Base IRR attractive
!= automatic short_mid ENTRY
```

详见 `shared/strategy-boundary-contract.md`。

## Canonical PIT Direction

生产研究逐步采用：

```text
Immutable Raw Evidence
→ Normalized PIT Record
→ Feature Snapshot
→ Strategy Decision
→ Outcome / Order
```

Canonical metadata 至少区分：

```text
effective_at
published_at
available_at
ingested_at
source / source_tier / source_snapshot_id
revision_id
payload_hash
permitted_use
strategy_visibility
```

`available_at` 表示研究可见性；`first_tradable_timestamp` 属于执行层，两者不得混用。

详见 `shared/canonical-pit-data-contract.md`。

## 统一股票账户分母

```text
Stock Account Equity
= 长期股票市值
+ 短中期股票市值
+ 股票账户待配置现金
```

以下统一以该分母计算：

- 长期 / 短中期 Size Cap；
- `Final Short Cap`；
- 账户级单股合计暴露；
- 账户级风险簇合计暴露。

长期仓内部 Core/Growth、模型 `model_long_book_weight` 使用 long-book 内部分母，执行前先换算到账户级权重。

## 顶层股票资金策略

| Stock Account Equity | 长期战略基线 | 短中期 Size Cap |
|---:|---:|---:|
| ≤5 万 | 70% | 30% |
| 5–30 万 | 75% | 25% |
| 30–200 万 | 80% | 20% |
| 200–1000 万 | 85% | 15% |
| ≥1000 万 | 85%–90% | 10%–15% |

最终短中期上限：

```text
Final Short Cap = min(Size Cap, Risk Cap, Edge Cap)
```

新订单必须满足：

```text
Planned Post-Trade Short Exposure <= Final Short Cap
```

股票资金不要求100%满仓。长期和短中期都没有合格机会时，待配置现金是合法状态。

### 被动 CAP_BREACH

若市场上涨导致已有仓位被动超过 Cap：

```text
CAP_BREACH
→ 禁止继续增加风险
→ 进入再平衡/利润回流评估
→ 在现实可执行窗口恢复
```

不得用 ±5pp 漂移带主动突破 Cap，也不要求在异常价格下机械市价砍仓。

## 跨策略同股 / 同因子

```text
Account Symbol Exposure
= Long Sleeve Exposure + Short/Mid-term Sleeve Exposure

Account Cluster Exposure
= Long Cluster Exposure + Short/Mid-term Cluster Exposure
```

策略标签不能创造第二套风险额度。

Broker 执行时维护：

```text
Broker Net Position
Strategy Virtual Position: long
Strategy Virtual Position: short_mid
```

防止一套策略的卖单误操作另一套策略的逻辑份额。

## 建仓基线

```text
长期单股：默认 40/30/30
例外：60/40，或 30/25/25/20

短中期单股：默认 50/50
三级确认例外：50/30/20
```

这些是治理参数，不宣称数学最优。策略批次和大额执行拆单不是同一概念。

## 短中期风险层级

```text
Operating Target
- 单笔计划风险：0.5% × 短中期策略 NAV
- 全部未平仓初始风险：≤2%
- 单一行业/因子初始风险：≤1%

Hard Ceiling
- 单笔计划风险：≤1%
- 全部未平仓初始风险：≤3%
```

Hard Ceiling 是计划风险上限，不是跳空/跌停下实际亏损保证。

回撤治理：4%降风险、6%停止新开仓、8%暂停策略并复核。

## Research / Model Governance

短中期当前 Champion：

```text
Technical 30
Capital Participation 30
Fundamentals 25
Catalyst 15
```

因果模型仍为：

```text
CHALLENGER / SHADOW ONLY
```

v3.2 开始，Promotion 指标正式拆分为：

```text
Common metrics
+ Short/Mid metrics
+ Long-term metrics
```

不会再要求长期系统通过短中期 `Expectancy_R / Profit Factor / MFE/MAE / 5–20日窗口` 才能晋级。

长期主要围绕 Total Return、Expected IRR calibration、估值/Thesis 错误、Dividend/FCF、永久性资本损失和组合适配验证。

短中期主要围绕 Expectancy_R、PF、MFE/MAE、FP/FN、Blocked MFE、Confirmation Delay、Regime/Event-family 等验证。

## A-Share Sentiment Regime Index

当前 Monitor 使用的研究状态变量：

```text
Breadth                       25
Limit-up vs Limit-down        20
Board Quality / Broken Rate   15
Strong vs Weak Tail           15
Median Return                 10
Turnover Expansion            15
```

Regime：

```text
0–20   PANIC
20–40  RISK_OFF
40–60  NEUTRAL
60–80  RISK_ON
80–100 EUPHORIA
```

统一语义：

- `PANIC` / `DATA_INSUFFICIENT`：当前趋势型新仓 fail closed；
- `RISK_OFF`：提高入场门槛、风险取保守端、严格拒绝追高，不是单凭情绪分数永久禁止所有交易；
- `EUPHORIA`：不等于加仓，额外检查拥挤与 extension。

该指数只属于 Short/Mid research context，不自动改变长期仓。

## 长期研究

```text
Price Low != Valuation Low
```

长期 Bear/Base/Bull IRR 使用逐期现金流：

```text
0 = -P0 + Σ[CF_t/(1+r)^t] + TV_T/(1+r)^T
```

Required Return：

```text
Point-in-time Risk-free Rate
+ Configured Required Risk Premium
```

长期 Benchmark 优先使用 Total Return 口径。

长期 ADD/HOLD/TRIM/EXIT 主要由 Thesis、Balance、Valuation、Portfolio Gate 与 Expected Return 决定，不使用短中期 ERG/Reaction Window/R-based tactical stop 替代。

## Active Forward Study

`research/a-share-long-vs-tactical-empirical-study.md`

对照：

```text
Long Retirement Book
vs Short/Mid Champion
vs Causal Challenger (Shadow)
vs Total Return Benchmark
vs Cash / Government-Bond Opportunity Cost
```

仓库自己的收益差必须从冻结的 point-in-time baseline 开始积累 Forward 证据，禁止制造后见之明历史业绩。

## Daily Monitor Runtime

可运行 MVP：

`runtime/daily_monitor.py`

它现在明确是：

```text
strategy_id = a_share_short_mid
sleeve      = short_mid
runtime_mode = SHORT_MID_MONITOR_ONLY
```

默认 universe：

`runtime/config/short_mid_universe.json`

不再把 Level-4 dated example 作为 runtime 默认 universe。

当前流程：

```text
交易日识别
→ 全A行情
→ 涨停/跌停/炸板
→ Sentiment Score / Regime
→ runtime short_mid universe
→ pre_action 研究状态
→ JSON + Markdown 日报
→ 成交额历史留档
```

运行前：

```text
compileall runtime + src
→ unit tests
→ fail-closed monitor
```

默认：

```text
AUTO_MONITOR = true
AUTO_ORDER   = false
```

日报 `REFRESH_FULL_GATES / RISK_REVIEW / EVENT_REVIEW` 等都是 short_mid 研究状态，不是交易指令。

## Production Evolution

批准的架构基础：

`research/production-system-evolution-report-2026-08-28.md`

第一阶段目标不是自动下单，而是：

```text
PIT Reproducible Research Core
```

优先顺序：

```text
Strategy Boundary + PIT Data Contract
→ Canonical Data Store / Snapshot
→ Short/Mid Champion Engine
→ ERG Engine
→ Historical Replay
→ Forward / Ablation / Placebo
→ Paper Ledger / Broker Simulator
→ Reconciliation
→ Human-confirmed Live
→ Optional Semi-auto
```

长期独立演进：

```text
Long Quality Engine
→ Cash Flow / Dividend Engine
→ Expected IRR / Valuation Engine
→ Long Paper Portfolio
→ Automated Research / Manual Order can remain the end state
```

Qlib、vn.py、PostgreSQL、MLflow、Prefect、OpenTelemetry 等均为后续按实际需求引入的组件，不因为“生产系统应该现代化”而一次性堆栈。

## 自动化执行原则

```text
Research
→ Forward Paper
→ Manual Live
→ Automated Research / Manual Order
→ Human-confirmed Broker Execution
→ Limited Semi-auto
→ Full Auto only after Edge + Compliance + Reliability gates
```

进入 Paper/Live 后每个 cohort / 决策 / 订单保存：

```text
capital_policy_version
automation_governance_version
research_model_governance_version
skill_version
strategy_id
sleeve
strategy_version
model_version
```

模型晋级不等于自动化晋级。

## 三套 Skill 边界

### Multi-Asset

管理 Total Financial Assets → Stock Account Equity，强调流动性、负债匹配、固收久期和组合 Stress Budget。

### Long

依赖企业价值、现金流、分红、Expected IRR、估值与资本保全，默认使用投资逻辑止损。

### Short/Mid

使用价格/失效、逻辑与时间止损。亏损交易不得临时改名为长期持有；趋势/催化策略禁止机械摊低成本。

长期价值仓只有在 Thesis / Balance / Valuation / Portfolio 四个 Gate 全部重新通过后才允许继续 ADD。

短中期已实现利润超出允许资本时，优先回流长期待配置池；长期没有合格机会则保持现金。短中期亏损缩水时不从长期仓自动补血。

## 审计与证据

- 规则优先级：`shared/policy-precedence.md`
- 资本/风险：`shared/capital-allocation-and-entry-policy.md`
- 自动化/执行：`shared/automation-execution-governance.md`
- 研究/模型：`shared/research-model-governance.md`
- 策略边界：`shared/strategy-boundary-contract.md`
- PIT 数据：`shared/canonical-pit-data-contract.md`
- Production 架构：`research/production-system-evolution-report-2026-08-28.md`
- 研究证据：`shared/research-validation-2026-08-26.md`
- 对抗审查：`shared/adversarial-research-review-2026-08-26.md`
- 跨策略实证研究：`research/a-share-long-vs-tactical-empirical-study.md`
- 一级资产配置：`skills/a-share-multi-asset-allocation/SKILL.md`
- Runtime：`runtime/README.md`
- 全仓一致性扫描：`shared/consistency-audit-2026-08-26.md`

具体比例、阈值、评分权重和批次属于治理参数，后续通过各自 sleeve 的 Forward/Live 数据持续校准。