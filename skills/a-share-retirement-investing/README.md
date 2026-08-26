# A-share Retirement Investing Skill

用于沪深A股长期养老型权益组合的：

- 长期分红核心股筛选
- 科技/成长卫星仓筛选
- 行业适配财务分析
- 合理价值与买入区间
- 动态仓位与分批建仓
- 补仓 Gate
- 分红复投
- 季度/年度持仓复核
- 对抗审查与退出条件

## 先读上位规则

执行本 Skill 前先读取：

1. `../../shared/policy-precedence.md`
2. `../../shared/capital-allocation-and-entry-policy.md`
3. `SKILL.md`

共享政策优先于本 Skill 内部任何通用仓位默认值。

## 当前长期/短中期 Size Cap 基线

| 股票专用资金规模 | 长期养老仓 | 短中期仓 |
|---:|---:|---:|
| ≤5 万 | 70% | 30% |
| 5–30 万 | 75% | 25% |
| 30–200 万 | 80% | 20% |
| 200–1000 万 | 85% | 15% |
| ≥1000 万 | 85%–90% | 10%–15% |

最终短中期占比还必须满足 `Risk Cap` 和 `Edge Cap`，不能机械满配。

## 长期仓内部

长期仓内部仍使用：

```text
Core Dividend：75%–85%
Growth Satellite：15%–25%
```

这不是全账户的长期/短中期比例。

## 长期个股建仓

```text
默认：3 批 40% / 30% / 30%
小资金/高确定性：2 批 60% / 40%
大单股金额/较高不确定性：4 批 30% / 25% / 25% / 20%
```

不再使用模糊的“3–5批都可以”。后续批次必须有新的价格/事实确认。

## 动态仓位

单股和风险簇上限不再永久写死为 25% / 30%–35%。执行时根据股票专用资金规模从 shared policy 动态读取。

长期后续加仓必须同时满足：

```text
Thesis Gate
+ Balance Gate
+ Valuation Gate
+ Portfolio Gate
```

## 止损与止盈

长期仓默认不用统一 5%/8%/10% 机械价格止损；大幅下跌是重新研究触发器。

止盈不按固定盈利百分比全部卖出，而由估值、单股/风险簇超配、机会成本和投资逻辑变化决定 `HOLD / TRIM / EXIT`。

## 文件结构

```text
skills/a-share-retirement-investing/
├── SKILL.md
├── README.md
└── references/
    ├── methodology.md
    ├── industry-checklists.md
    ├── execution-template.md
    └── seed-watchlist-2026-08-26.md
```

## 推荐使用顺序

1. `../../shared/policy-precedence.md`
2. `../../shared/capital-allocation-and-entry-policy.md`
3. `SKILL.md`
4. `references/methodology.md`
5. `references/industry-checklists.md`
6. `references/execution-template.md`
7. `references/seed-watchlist-2026-08-26.md`

研究依据与参数边界见 `../../shared/research-validation-2026-08-26.md`。

## 关键原则

```text
先看能不能长期活
→ 再看能不能长期赚
→ 再看利润能否转成现金/资本
→ 再看分红是否可持续
→ 再看是否有增长
→ 再看当前价格值不值得买
→ 最后才看当前股息率
```

任何时效性数字都必须联网重新验证，并标注 `as_of`。
