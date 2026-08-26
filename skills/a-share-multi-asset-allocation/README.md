# A-share Multi-Asset Allocation

这个 Skill 管理的是**股票账户之前的一层**：现金、近期开支准备金、国债/高等级固收和可进入股票账户的长期风险资本。

## 使用顺序

```text
Total Financial Assets
→ Liquidity Reserve
→ Liability Matching
→ Portfolio Stress Budget
→ Fixed Income / Equity Allocation
→ Equity Account Equity
→ shared/capital-allocation-and-entry-policy.md
→ Long + Short/Mid + Equity Cash
```

## 核心原则

- 应急金和两年内刚性支出不拿去赌个股回撤；
- 固收首先用于负债匹配和组合缓冲，不是简单追求高票息；
- 长久期债券同样有价格风险；
- 进入股票账户的资金必须先通过组合压力损失预算；
- 股票的 Expected Return 要相对当期低风险收益率提供足够风险补偿；
- 一级资产配置不随短期市场情绪每天切换。

## 当前默认自动化边界

```text
AUTO_MONITOR = true
AUTO_STRATEGIC_REALLOCATION = false
```

自动化可以监控收益率曲线、资产权重和漂移，但战略资产配置变化默认需要人工确认。

完整规则见 `SKILL.md`。
