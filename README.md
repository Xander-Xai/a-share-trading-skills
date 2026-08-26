# A-share Trading Skills

A股长期养老投资与短中期交易 Skill 集合。

当前仓库包含两套独立策略，并共享三类仓库级治理：

```text
长期养老投资 Skill
+
短中期选股与交易 Skill
+
Capital / Risk Governance
+
Automation / Execution Governance
+
Research / Model Governance v3
```

## 当前结构

```text
a-share-trading-skills/
├── README.md
├── shared/
│   ├── policy-precedence.md
│   ├── capital-allocation-and-entry-policy.md
│   ├── automation-execution-governance.md
│   ├── research-model-governance.md
│   ├── research-validation-2026-08-26.md
│   ├── adversarial-research-review-2026-08-26.md
│   └── consistency-audit-2026-08-26.md
└── skills/
    ├── a-share-retirement-investing/
    │   ├── README.md
    │   ├── SKILL.md
    │   ├── references/
    │   │   └── expected-irr-total-return-benchmark.md
    │   └── examples/
    │       ├── ten-stock-retirement-portfolio-2026-08-26.md
    │       └── paper-live-automation-roadmap.md
    └── a-share-short-midterm-stock-selection/
        ├── README.md
        ├── SKILL.md
        ├── references/
        │   ├── scoring-system.md
        │   ├── causal-challenger-model.md
        │   ├── champion-challenger-forward-test.md
        │   └── trade-ledger-mfe-mae-extension.md
        └── examples/
```

## 规则优先级

统一遵循 `shared/policy-precedence.md`：

```text
Level 1A  shared/capital-allocation-and-entry-policy.md
Level 1B  shared/automation-execution-governance.md
Level 1C  shared/research-model-governance.md
    ↓
Level 2   skills/*/SKILL.md
    ↓
Level 3   skills/*/references/*.md
    ↓
Level 4   examples / case studies / dated snapshots / watchlists
```

Level 1A 管资金与风险，Level 1B 管执行与自动化，Level 1C 管模型证据、回测偏差和 Champion/Challenger 晋级。

下层规则可以更保守，但不能放宽上位风险限制。Examples、case studies 和历史快照是证据记录，不是当前政策。

## v3 研究架构

本仓库不再因为“一个新模型听起来更合理”就直接覆盖旧模型。

统一采用：

```text
Champion
→ Challenger Shadow Score
→ Forward-Test
→ Cost / Risk / Regime / Bias Audit
→ Human Promotion Review
→ New Champion (only if promoted)
```

短中期当前 Champion 仍是：

```text
Technical 30
Capital Participation 30
Fundamentals 25
Catalyst 15
```

新因果评分只作为 Challenger：

```text
Business / Survival Quality
Valuation / Expectation Gap
Catalyst / Expectation Change
Market / Sector Regime
Participation / Relative Strength
Price Structure / Execution
```

在 Challenger 通过样本外/Forward、成本、回撤和 point-in-time 审查前，不能替换当前 Champion。

## 长期研究升级

长期“低位”不等于“离历史高点很远”。

新增：

```text
Bear / Base / Bull Expected IRR
+ Required Return sensitivity
+ Max Buy Price
+ Total Return Benchmark
```

长期比较优先使用含分红再投资的全收益指数口径。例如沪深300：

```text
Price Index  = 000300
Total Return = H00300
```

具体方法见：

`skills/a-share-retirement-investing/references/expected-irr-total-return-benchmark.md`

## 回测与历史复盘防偏差

模型晋级必须审计：

```text
Point-in-time data
Survivorship bias
Look-ahead bias
Historical ST/delisting state
Financial report publication time
Index constituent history
Suspension / price limits / T+1
Fees / tax / slippage / impact
```

无法重建当时真实输入的结果可以作为研究灵感，但不得作为模型晋级的主要证据。

## 顶层资金策略

当前资本/风险政策版本：`v2.2`。

股票专用资金的 Size Cap 基线：

| 股票资金规模 | 长期战略基线 | 短中期 Size Cap |
|---:|---:|---:|
| ≤5 万 | 70% | 30% |
| 5–30 万 | 75% | 25% |
| 30–200 万 | 80% | 20% |
| 200–1000 万 | 85% | 15% |
| ≥1000 万 | 85%–90% | 10%–15% |

最终短中期上限：

```text
Final Short Cap = min(Size Cap, Risk Cap, Edge Cap)
Actual Short Exposure <= Final Short Cap
```

股票专用资金不要求永远 100% 满仓：

```text
股票专用资金
= 已部署长期仓
+ 已部署短中期仓
+ 待配置现金
```

短中期被 Risk/Edge Cap 压低后的差额，不自动强制买入长期股；长期机会也必须通过自己的质量、估值与组合 Gate。

具体数值唯一以 `shared/capital-allocation-and-entry-policy.md` 为准。

## 建仓基线

```text
长期单股：默认 3 批 40/30/30
例外：2 批 60/40，或 4 批 30/25/25/20

短中期单股：默认 2 批 50/50
三级确认例外：50/30/20
```

这些比例属于当前治理参数，不宣称数学最优。

策略批次与大额订单的执行拆单是不同概念。

## 短中期风险层级

```text
Operating Target
- 单笔计划风险：0.5%
- 全部未平仓初始风险：2%
- 单一行业/因子初始风险：1%

Hard Ceiling
- 单笔计划风险：1%
- 全部未平仓初始风险：3%
```

回撤治理基线：4% 降风险、6% 停止新开仓、8% 暂停策略并复核。

任何“漂移区间”都不能突破 Final Short Cap、单股/风险簇上限或 Hard Ceiling。

## 短中期学习闭环

每笔交易除最终 PnL 外，新增强制研究字段：

```text
realized_R
MFE_R
MAE_R
holding_days
exit_reason
fees / tax / slippage / impact
regime
rule_violation
```

+1.5R/+2R、3–5 日 time review 等规则只作为当前治理初值，通过 MFE/MAE 与 Forward 数据校准。

## 自动化执行原则

统一执行治理见：

`shared/automation-execution-governance.md`

默认：

```text
AUTO_MONITOR = true
AUTO_ORDER   = false
```

成熟路径：

```text
Research
→ Forward Paper
→ Manual Live
→ Automated Research / Manual Order
→ Human-confirmed Execution
→ Limited Semi-auto
→ Full Auto only after Edge + Compliance + Reliability gates
```

模型晋级与自动化晋级是两个独立 Gate：

```text
Good Model != Safe Auto Execution
Safe Executor != Positive Edge
```

任何自动化都不能绕过 shared capital/risk policy、broker position reconciliation、Kill Switch 或当期程序化交易/券商合规要求。

## 两套系统边界

长期仓依赖企业价值、现金流、分红、估值与资本保全，默认使用投资逻辑止损；短中期仓使用价格/失效、逻辑与时间止损，禁止把亏损交易临时改名为长期持有。

趋势/催化短中期策略禁止因为亏损而机械摊低成本；长期价值仓则可以在 Thesis、Balance、Valuation、Portfolio 四个 Gate 全部重新通过后，利用更高安全边际继续分批。

短中期已实现利润超过 Final Short Cap 时，优先逐步回流长期待配置池；只有长期 Gate 通过才继续买入，否则保持现金。短中期因亏损缩水时，不自动从长期仓补足。

## 当前验证案例

长期 Skill 已保存十股养老模型组合作为 Forward-Test 示例；短中期 Skill 保存 2026-08-26 的 43 股最终研究 whitelist 与 machine-readable baseline。

这些示例只用于回溯和前测。真实买入前必须重新运行对应 Skill，并重新获取当时价格、财报、估值、事件与风险上限。

## 审计与证据

- 研究与参数边界：`shared/research-validation-2026-08-26.md`
- 对抗审查与纠错：`shared/adversarial-research-review-2026-08-26.md`
- 研究模型治理：`shared/research-model-governance.md`
- 全仓库一致性扫描：`shared/consistency-audit-2026-08-26.md`

具体比例、阈值、权重和批次属于当前风险/研究治理参数，不宣称为唯一最优解；后续应通过真实 Forward/Live 数据持续校准。
