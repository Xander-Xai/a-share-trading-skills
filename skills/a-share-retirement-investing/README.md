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
- 模拟仓 → 人工实盘 → 半自动 → 自动化交易的验证链路

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

## 十股养老组合示例

本仓库现在保存一个真实研究快照作为 forward-test 示例：

`examples/ten-stock-retirement-portfolio-2026-08-26.md`

十只股票：

```text
长江电力 / 招商银行 / 伊利股份
中国石油 / 中国电信 / 格力电器 / 中国神华
工业富联 / 立讯精密 / 中科曙光
```

示例模型结构：

```text
Core Dividend = 80%
Growth Satellite = 20%
```

该文件记录：

- 2026-08-26 初始价格快照；
- 每只股票在组合中的角色；
- 当时市场/财务验证；
- 模型目标权重；
- 风险簇；
- 建仓、补仓、止损、止盈与复核方式；
- 后续收益、分红、回撤和绩效归因的记录字段。

它是历史示例，不是永久推荐名单。任何真实买入前必须重新运行 Skill。

## 从模拟仓到自动化交易

完整系统路线见：

`examples/paper-live-automation-roadmap.md`

阶段：

```text
规则冻结
→ 模拟仓 Forward Test
→ 人工实盘
→ Agent 生成订单 + 人工确认
→ 受约束自动执行
→ 持续监控 / 绩效归因 / 版本升级
```

自动化的重点不是“快速自动下单”，而是建立：

- point-in-time 数据链路；
- 可复现的 Skill 决策；
- shared policy 风控；
- Paper / Live 双轨记录；
- 订单审计日志；
- Kill Switch；
- 财报/公告触发重评；
- 组合收益、分红和回撤归因；
- 规则升级后的 consistency audit。

## 文件结构

```text
skills/a-share-retirement-investing/
├── SKILL.md
├── README.md
├── examples/
│   ├── ten-stock-retirement-portfolio-2026-08-26.md
│   └── paper-live-automation-roadmap.md
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
7. `examples/ten-stock-retirement-portfolio-2026-08-26.md`：查看十股模型组合和 forward-test 基线
8. `examples/paper-live-automation-roadmap.md`：查看从模拟仓到自动交易的完整链路
9. `references/seed-watchlist-2026-08-26.md`：历史研究种子池

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
