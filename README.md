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
Research / Model Governance
```

## 当前治理版本

```text
Capital / Risk:        v2.3
Automation / Execution: v1.2
Research / Model:       v3
```

版本号分别属于不同 artifact，优先级统一由 `shared/policy-precedence.md` 决定。

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
    │   │   ├── methodology.md
    │   │   ├── execution-template.md
    │   │   ├── expected-irr-total-return-benchmark.md
    │   │   └── ...
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
        │   ├── trade-ledger-mfe-mae-extension.md
        │   └── ...
        └── examples/
```

## 规则优先级

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

- Level 1A：资本、仓位、风险、建仓/补仓/止盈止损、账户级集中度；
- Level 1B：Paper/Live、Broker、虚拟子账、幂等、Kill Switch、自动化与合规；
- Level 1C：研究证据、point-in-time、Benchmark、Champion/Challenger 与模型晋级。

下层规则可以更保守，不能绕过上位规则。

## 统一账户分母

资本与账户级集中度统一使用：

```text
Stock Account Equity
= 长期股票市值
+ 短中期股票市值
+ 股票账户待配置现金
```

以下都以该分母计算：

- 长期 / 短中期 Size Cap；
- `Final Short Cap`；
- 账户级单只股票合计暴露；
- 账户级风险簇合计暴露。

长期仓内部的 Core/Growth、十股示例 `model_long_book_weight` 使用的是 **long-book 内部分母**，执行前必须先换算到账户级权重。

## 顶层资金策略

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

不得把 ±5pp 漂移带当作主动突破 Cap 的理由，也不要求在异常价格下机械市价砍仓。

## 跨策略同股 / 同因子

同一股票若同时被长期和短中期持有：

```text
Account Symbol Exposure
= Long Sleeve Exposure + Short/Mid-term Sleeve Exposure
```

风险簇同理：

```text
Account Cluster Exposure
= Long Cluster Exposure + Short/Mid-term Cluster Exposure
```

策略标签不能创造第二套风险额度。

Broker 执行时同时维护：

```text
Broker Net Position
Strategy Virtual Position: long
Strategy Virtual Position: short_mid
```

防止短中期卖单误卖长期逻辑份额。

## 建仓基线

```text
长期单股：默认 40/30/30
例外：60/40，或 30/25/25/20

短中期单股：默认 50/50
三级确认例外：50/30/20
```

这些是治理参数，不宣称数学最优。策略批次和大额订单执行拆单不是同一概念。

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

Hard Ceiling 是**计划风险上限**，不是跳空/跌停下的实际亏损保证。

回撤治理：4%降风险、6%停止新开仓、8%暂停策略并复核。

## Research / Model Governance

短中期当前 Champion 仍为：

```text
Technical 30
Capital Participation 30
Fundamentals 25
Catalyst 15
```

新的因果模型仍是：

```text
CHALLENGER / SHADOW ONLY
```

统一晋级路径：

```text
Champion
→ Challenger Shadow
→ Forward-Test
→ Cost / Risk / Regime / Bias Audit
→ Human Promotion Review
→ New Champion only if promoted
```

无法重建 point-in-time 输入的历史结果标记 `Biased / Non-promotable`，不能用于正式模型晋级。

## 长期研究升级

长期不把“距离历史高点很远”直接等同于便宜：

```text
Price Low != Valuation Low
```

长期估值优先使用 Bear/Base/Bull 逐期现金流 IRR：

```text
0 = -P0 + Σ[CF_t/(1+r)^t] + TV_T/(1+r)^T
```

Required Return：

```text
Point-in-time Risk-free Rate
+ Configured Required Risk Premium
```

风险溢价做敏感性分析，不写死为统一真理。

长期 Benchmark 优先使用 Total Return 口径，例如沪深300全收益指数 `H00300`，避免组合含分红而基准只看价格。

## 自动化执行原则

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
→ Human-confirmed Broker Execution
→ Limited Semi-auto
→ Full Auto only after Edge + Compliance + Reliability gates
```

每个运行 cohort / 决策 / 订单必须保存 Governance Bundle：

```text
capital_policy_version
automation_governance_version
research_model_governance_version
skill_version
strategy_version
model_version
```

模型晋级不等于自动化晋级。

## 两套系统边界

长期仓依赖企业价值、现金流、分红、估值与资本保全，默认使用投资逻辑止损；短中期仓使用价格/失效、逻辑与时间止损。

短中期亏损交易不得临时改名为长期持有；趋势/催化策略禁止机械摊低成本。长期价值仓只有在 Thesis / Balance / Valuation / Portfolio 四个 Gate 全部重新通过后才允许继续 ADD。

短中期已实现利润超出允许资本时，优先回流长期待配置池；长期没有合格机会则保持现金。短中期亏损缩水时不从长期仓自动补血。

## 当前验证案例

长期：十股养老模型组合 Forward-Test 示例。

短中期：2026-08-26 的 43 股最终研究 whitelist + machine-readable baseline；同日36股文件是较早中间快照。

所有 dated examples 都是 Level 4 历史证据，不是当前买入名单。真实交易前必须重新运行对应 Skill。

## 审计与证据

- 规则优先级：`shared/policy-precedence.md`
- 资本/风险：`shared/capital-allocation-and-entry-policy.md`
- 自动化/执行：`shared/automation-execution-governance.md`
- 研究/模型：`shared/research-model-governance.md`
- 研究证据与参数边界：`shared/research-validation-2026-08-26.md`
- 对抗审查：`shared/adversarial-research-review-2026-08-26.md`
- 全仓一致性扫描：`shared/consistency-audit-2026-08-26.md`

具体比例、阈值、评分权重和批次属于治理参数，后续通过 Forward/Live 数据持续校准。