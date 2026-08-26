# A-share Trading Skills

A股交易 Skill 集合。仓库用于沉淀两套相互隔离、但共享顶层资金管理规则的投资体系：

```text
长期养老投资 Skill
+
短中期交易 Skill（整理中）
```

## 当前结构

```text
a-share-trading-skills/
├── README.md
├── shared/
│   └── capital-allocation-and-entry-policy.md
└── skills/
    └── a-share-retirement-investing/
        ├── SKILL.md
        ├── README.md
        └── references/
            ├── methodology.md
            ├── industry-checklists.md
            ├── execution-template.md
            └── seed-watchlist-2026-08-26.md
```

短中期 Skill 将在规则整理完成后单独加入 `skills/`，不会与长期 Skill 混写。

## 顶层资金策略

统一规则见：

`shared/capital-allocation-and-entry-policy.md`

当前默认基线：

```text
长期养老仓：70%
短中期交易仓：30%
```

建仓基线：

```text
长期单股：默认 3 批 40/30/30
短中期单股：默认 2 批 50/50
```

A股 100 股交易单位、小资金账户、估值变化和交易信号失效可以触发降批次；分批次数不得凌驾于风险预算和目标仓位之上。

## 核心原则

```text
长期资金靠时间、企业现金流和价值增长赚钱；
短中期资金靠可验证的交易优势赚钱；
两套系统不能互相为错误买单。
```
