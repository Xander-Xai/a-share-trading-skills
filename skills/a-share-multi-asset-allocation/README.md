# A-share Multi-Asset Allocation

这个 Skill 管理的是**股票账户之前的一层**：应急流动性、近期开支准备金、国债/高等级固收，以及最终可进入 A 股股票系统的长期风险资本。

## 使用顺序

```text
Total Financial Assets
→ Liquidity Reserve
→ Liability Matching
→ Portfolio Stress Budget
→ Cash / Fixed Income / Stock Allocation
→ Stock Account Equity
→ shared/capital-allocation-and-entry-policy.md
→ Long + Short/Mid + Stock-account Pending Cash
```

统一术语只有：

```text
Stock Account Equity
```

不再混用 `Equity Account Equity`。

## 与股票账户规则的边界

本 Skill 只决定：

> 全部可投资金融资产中，有多少资本可以成为 `Stock Account Equity`。

进入股票账户以后：

- 长期 / 短中期 Size Cap；
- `Final Short Cap`；
- 单股/风险簇上限；
- 长短策略同股聚合；
- 建仓批次；
- 短中期 Heat / circuit breaker；

全部由 `../../shared/capital-allocation-and-entry-policy.md` 管理。

## 核心原则

- 应急金和未来两年刚性支出不拿去承受个股回撤；
- 固收优先用于负债匹配和组合缓冲，不简单追求高票息；
- 长久期债券同样有价格风险；
- 进入股票账户的资金先通过组合压力损失预算；
- 股票 Expected Return 要相对当期低风险收益率提供足够风险补偿；
- 一级资产配置不随短期市场情绪每天切换；
- 一级资产的 ±5pp 漂移带不能被拿到股票账户内部突破 `Final Short Cap` 或账户级 Cap。

## 当前默认自动化边界

```text
AUTO_MONITOR = true
AUTO_STRATEGIC_REALLOCATION = false
```

自动化可以监控收益率曲线、资产权重、流动性 Gate 和配置漂移，但战略资产配置变化默认需要人工确认。

完整规则见 `SKILL.md`；仓库范围/优先级见 `../../shared/policy-precedence.md`。