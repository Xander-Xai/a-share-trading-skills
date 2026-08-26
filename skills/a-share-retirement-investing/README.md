# A-share Retirement Investing Skill

用于沪深A股长期养老型权益组合的：

- 长期分红核心股筛选
- 科技/成长卫星仓筛选
- 行业适配财务分析
- 合理价值与买入区间
- 分批建仓与仓位控制
- 分红复投
- 季度/年度持仓复核
- 对抗审查与退出条件

## 顶层资金与建仓规则

本 Skill 不单独决定“长期 vs 短中期”的总资金比例，统一遵循仓库共享规则：

`../../shared/capital-allocation-and-entry-policy.md`

当前默认基线：

```text
总股票资金：长期养老 70% / 短中期 30%

长期单股目标仓位：默认 3 批 40% / 30% / 30%
建议分批期：通常不超过约 3 个月
小资金或 100 股交易单位限制：可降为 2 批 60/40，必要时 1 批
```

长期后续批次不是机械“越跌越买”，必须满足估值仍有安全边际且基本面/投资逻辑未失效。

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

仓库共享规则：

```text
shared/
└── capital-allocation-and-entry-policy.md
```

## 推荐使用顺序

1. `../../shared/capital-allocation-and-entry-policy.md`：先确定长期/短中期资金隔离与建仓批次。
2. `SKILL.md`：执行长期养老股筛选、估值和持仓决策。
3. `references/methodology.md`：第一性原理、估值、压力测试和持仓哲学。
4. `references/industry-checklists.md`：按行业选择正确指标，避免一套财务指标机械套用。
5. `references/execution-template.md`：每次实盘研究的输入、数据检查、单股研究卡和组合研究卡。
6. `references/seed-watchlist-2026-08-26.md`：本轮讨论形成的研究种子，仅用于回溯，不是永久推荐名单。

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
