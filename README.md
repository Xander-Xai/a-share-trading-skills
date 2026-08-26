# A-share Trading Skills

A股长期养老投资与短中期交易 Skill 集合。

当前仓库已经包含两套独立策略：

```text
长期养老投资 Skill
+
短中期选股与交易 Skill
```

## 当前结构

```text
a-share-trading-skills/
├── README.md
├── shared/
│   ├── policy-precedence.md
│   ├── capital-allocation-and-entry-policy.md
│   ├── research-validation-2026-08-26.md
│   └── consistency-audit-2026-08-26.md
└── skills/
    ├── a-share-retirement-investing/
    └── a-share-short-midterm-stock-selection/
```

## 规则优先级

统一遵循 `shared/policy-precedence.md`：

```text
Level 1  shared/capital-allocation-and-entry-policy.md
   ↓
Level 2  skills/*/SKILL.md
   ↓
Level 3  skills/*/references/*.md
   ↓
Level 4  带日期的 snapshot / watchlist
```

下层规则可以更保守，但不得放宽上层风险限制。历史快照只用于回溯，不能覆盖当前 policy。

## 顶层资金策略

资金与风险规则见 `shared/capital-allocation-and-entry-policy.md`；调研证据与边界见 `shared/research-validation-2026-08-26.md`；一致性审计见 `shared/consistency-audit-2026-08-26.md`。

股票专用资金的 Size Cap 基线：

| 股票资金规模 | 长期养老仓 | 短中期仓 |
|---:|---:|---:|
| ≤5 万 | 70% | 30% |
| 5–30 万 | 75% | 25% |
| 30–200 万 | 80% | 20% |
| 200–1000 万 | 85% | 15% |
| ≥1000 万 | 85%–90% | 10%–15% |

最终短中期比例不是机械满配，而是：

```text
Short Allocation = min(Size Cap, Risk Cap, Edge Cap)
```

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

## 两套系统边界

长期仓主要依赖企业价值、现金流、分红、估值和资本保全，默认使用投资逻辑止损；短中期仓使用入场失效点、价格/逻辑/时间止损，并禁止把亏损交易临时改成长期持有。

短中期已实现利润超过战略上限时，优先逐步回流长期仓或待配置现金池；短中期因亏损缩水时，不自动从长期仓补足。

具体百分比属于当前仓库的风险治理参数，不宣称为唯一最优解，后续应使用真实实盘数据持续校准。
