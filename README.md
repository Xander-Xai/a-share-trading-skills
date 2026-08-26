# A-share Trading Skills

A股长期养老投资与短中期交易 Skill 集合。

当前仓库包含两套独立策略，并共享同一套顶层资本、风险与自动化执行治理：

```text
长期养老投资 Skill
+
短中期选股与交易 Skill
+
Shared Capital / Risk / Automation Governance
```

## 当前结构

```text
a-share-trading-skills/
├── README.md
├── shared/
│   ├── policy-precedence.md
│   ├── capital-allocation-and-entry-policy.md
│   ├── automation-execution-governance.md
│   ├── research-validation-2026-08-26.md
│   └── consistency-audit-2026-08-26.md
└── skills/
    ├── a-share-retirement-investing/
    │   ├── README.md
    │   ├── SKILL.md
    │   ├── references/
    │   └── examples/
    │       ├── ten-stock-retirement-portfolio-2026-08-26.md
    │       └── paper-live-automation-roadmap.md
    └── a-share-short-midterm-stock-selection/
        ├── README.md
        ├── SKILL.md
        ├── references/
        └── examples/
```

## 规则优先级

统一遵循 `shared/policy-precedence.md`：

```text
Level 1A  shared/capital-allocation-and-entry-policy.md
Level 1B  shared/automation-execution-governance.md
    ↓
Level 2   skills/*/SKILL.md
    ↓
Level 3   skills/*/references/*.md
    ↓
Level 4   examples / case studies / dated snapshots / watchlists
```

下层规则可以更保守，但不能放宽上位风险限制。Examples、case studies 和历史快照是证据记录，不是当前政策。

## 顶层资金策略

当前资本/风险政策版本：`v2.1`。

股票专用资金的 Size Cap 基线：

| 股票资金规模 | 长期养老仓 | 短中期仓 |
|---:|---:|---:|
| ≤5 万 | 70% | 30% |
| 5–30 万 | 75% | 25% |
| 30–200 万 | 80% | 20% |
| 200–1000 万 | 85% | 15% |
| ≥1000 万 | 85%–90% | 10%–15% |

最终短中期比例不是机械满配：

```text
Short Allocation = min(Size Cap, Risk Cap, Edge Cap)
```

具体数值唯一以 `shared/capital-allocation-and-entry-policy.md` 为准。

## 建仓基线

```text
长期单股：默认 3 批 40/30/30
例外：2 批 60/40，或 4 批 30/25/25/20

短中期单股：默认 2 批 50/50
三级确认例外：50/30/20
```

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

任何自动化都不能绕过 shared capital/risk policy、broker position reconciliation、Kill Switch 或当期程序化交易/券商合规要求。

## 两套系统边界

长期仓依赖企业价值、现金流、分红、估值与资本保全，默认使用投资逻辑止损；短中期仓使用价格/失效、逻辑与时间止损，禁止把亏损交易临时改名为长期持有。

短中期已实现利润超过战略上限时，优先逐步回流长期仓或待配置现金池；短中期因亏损缩水时，不自动从长期仓补足。

## 当前验证案例

长期 Skill 已保存十股养老模型组合作为 forward-test 示例；短中期 Skill 保存 2026-08-26 的 43 股最终研究 whitelist 与 machine-readable baseline。

这些示例只用于回溯和前测。真实买入前必须重新运行对应 Skill，并重新获取当时价格、财报、估值、事件与风险上限。

## 审计与证据

- 研究与参数边界：`shared/research-validation-2026-08-26.md`
- 全仓库一致性扫描：`shared/consistency-audit-2026-08-26.md`

具体比例、阈值和批次属于当前风险治理参数，不宣称为唯一最优解；后续应通过真实 forward/live 数据持续校准。
