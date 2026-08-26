---
name: a-share-multi-asset-allocation
description: 为现金、国债/高等级固收、长期A股权益和短中期卫星仓建立一级资产配置、风险预算、负债匹配与再平衡规则。它决定多少资本进入股票账户，但不替代股票账户内部选股与交易 Skill。
version: 1.0.0
---

# Multi-Asset Allocation Skill

## 0. 作用边界

本 Skill 解决的是：

```text
我的全部可投资金融资产里
多少应该留现金？
多少承担利率/固收风险？
多少进入长期股票？
多少允许进入短中期主动交易？
```

它位于股票账户两套 Skill 的上游。

```text
Total Financial Assets
→ Liquidity / Liability Reserve
→ Fixed Income
→ Equity Capital
   → a-share-trading-skills shared capital policy
      → Long Core + Short/Mid Tactical + Equity Cash
```

股票账户内部的 Size/Risk/Edge Cap 仍以：

`../../shared/capital-allocation-and-entry-policy.md`

为唯一 Source of Truth。

## 1. 第一性原理

资产配置优先回答四个问题：

1. 哪些钱不能亏、什么时候必须用？
2. 最大可接受永久损失和阶段性回撤是多少？
3. 每类资产的预期回报是否补偿其风险？
4. 多个资产是否真正由不同风险因子驱动？

因此顺序是：

```text
Liquidity
→ Liability Matching
→ Risk Budget
→ Expected Return
→ Diversification
→ Rebalancing
→ Security Selection
```

不是先挑股票，再想生活现金够不够。

## 2. 统一资产定义

```text
Total Financial Assets
= Emergency/Liquidity Reserve
+ Near-term Liability Reserve
+ Fixed Income
+ Equity Account Equity
+ Other Strategic Assets (if explicitly modeled)
```

本 v1 默认只管理：

```text
Cash / Cash-like
Government / High-grade Fixed Income
A-share Equity Account
```

黄金、海外权益、REITs 等以后作为独立 Challenger 资产层加入，不在 v1 静默混入。

## 3. Gate 1 — Liquidity Reserve

任何风险资产配置前先定义：

```text
essential_monthly_spending
emergency_months
known_liabilities_next_24m
```

初始治理范围：

```text
Emergency Reserve = 6–12 个月必要支出
```

6–12 个月是风险治理参数，不是所有人的唯一最优数字。

未来 24 个月内确定要使用、不能承受明显亏损的资金原则上不进入个股风险仓。

可使用：

- 银行现金/存款；
- 高流动性现金管理工具；
- 与使用期限匹配的短期限低信用风险固收工具。

禁止为了多几个百分点预期收益，把短期刚性支出暴露给股票市场回撤。

## 4. Gate 2 — Liability Matching

原则：

```text
Asset Duration <= Money-use Horizon
```

需要在 1 年内使用的钱，不使用长久期债券赌利率方向；需要在数月内使用的钱，不使用股票等待“总会涨回来”。

长期负债/养老目标才适合承担更长权益久期。

## 5. Gate 3 — Portfolio Stress Budget

先给定整个金融资产组合允许承受的压力损失：

```text
Portfolio Stress Loss Budget = B
```

为各资产设保守压力情景：

```text
Cash stress loss      = C
Bond stress loss      = D
Equity stress loss    = E
```

简单保守预算：

```text
w_cash*C + w_bond*D + w_equity*E <= B
```

这是比假设相关性永远稳定更保守的一级门禁。

示例只用于说明：

若允许组合压力损失 15%，权益压力情景按 45%，暂忽略现金/短债压力，则：

```text
Equity Weight <= 15% / 45% ≈ 33%
```

45% 不是固定历史预测，只是可配置 stress parameter。

## 6. Gate 4 — Opportunity Cost / Required Return

每个 `as_of` 读取中国国债收益率曲线作为风险较低机会成本参考。

例如 2026-08-25 财政部-中国国债收益率曲线中：

```text
1Y ≈ 1.20%
5Y ≈ 1.39%
10Y ≈ 1.68%
30Y ≈ 2.13%
```

Source:
https://yield.chinabond.com.cn/cbweb-czb-web/czb/czbIndexGks

这些只是当日快照，不能永久写死。

股票/长期风险资产需要满足：

```text
Expected Return > Relevant Risk-free / Low-risk Alternative + Required Risk Compensation
```

Required Risk Compensation 是配置参数，需要敏感性分析，不能写死一个所有股票通用的 ERP。

## 7. Fixed Income 的作用

固收不是为了“永远跑赢股票”，而是提供：

- 负债匹配；
- 流动性；
- 组合波动缓冲；
- 在股票估值过高或 Edge 不足时保存购买力；
- 再平衡弹药。

### 7.1 利率风险

长久期债券价格对利率变化更敏感。

因此：

```text
短期用钱 → 短久期优先
长期稳定资金 → 才评估更长久期
```

### 7.2 信用风险

本 v1 防守层默认优先国债/政策性或高信用等级工具研究，不为了提高一点票息自动下沉到不可理解的信用风险。

## 8. Equity Account Allocation

只有通过前 3 个 Gate 的长期风险资本才进入股票账户：

```text
Equity Account Equity
```

然后再调用 shared capital policy：

```text
Equity Account
→ Long Strategic Baseline
+ Short/Mid Final Cap
+ Equity Cash
```

特别重要：

```text
Short/Mid Final Cap
!= Total Financial Assets 的短线比例
```

它是股票账户内部上限。

## 9. Equity Allocation 的动态规则

不因单日涨跌改变战略资产配置。

重新评估触发：

```text
重大收入/支出变化
重大负债变化
投资期限变化
风险承受能力变化
季度/年度组合复核
资产权重明显漂移
长期 Expected Return 明显变化
```

## 10. 再平衡

优先使用现金流再平衡：

```text
新增储蓄
→ 利息/分红
→ 到期债券
→ 已实现短中期利润
→ 最后才主动卖出优质长期资产
```

初始治理参考：

```text
季度检查
年度正式重设 Strategic Allocation
```

可使用约 ±5 个百分点漂移带作为“无需频繁微调”的参考，但它不能覆盖流动性、负债或 Hard Risk Gate。

## 11. Risk-on / Risk-off 不直接重写长期战略比例

短期市场情绪指数只能影响：

- 短中期新仓节奏；
- 股票账户待配置现金部署速度；
- 风险预算的保守程度。

禁止：

```text
今天 PANIC
→ 自动把全部股票卖成债券

今天 EUPHORIA
→ 自动把债券全部换成股票
```

一级资产配置与短期情绪是不同时间尺度。

## 12. 输出合同

每次执行必须输出：

```yaml
as_of:
total_financial_assets:
essential_monthly_spending:
emergency_months:
emergency_reserve:
known_liabilities_24m:
liability_reserve:
investable_long_term_capital:
portfolio_stress_loss_budget:
cash_target:
fixed_income_target:
equity_account_target:
current_1y_gov_yield:
current_5y_gov_yield:
current_10y_gov_yield:
current_30y_gov_yield:
allocation_drift:
rebalance_action:
assumption_confidence:
```

如果关键个人输入缺失，不猜测精确比例，输出：

```text
INSUFFICIENT_PERSONAL_INPUT_FOR_FINAL_ALLOCATION
```

但仍可给出规则和敏感性区间。

## 13. 禁止事项

- 把应急金投入个股；
- 把两年内刚性支出用长期股票承担；
- 用股票短期上涨提高风险承受能力假设；
- 用短中期亏损从防守资产自动补仓；
- 把高票息等同于低风险；
- 用历史低波动假设未来债券/股票不会出现压力行情；
- 为凑满配置比例购买不理解的资产。

## 14. 与自动化关系

自动化可做：

```text
每日读取收益率曲线
每日计算当前资产权重
检测漂移和 Liquidity Gate
生成再平衡建议
```

但战略资产配置修改默认需要人工确认。

```text
AUTO_MONITOR = true
AUTO_STRATEGIC_REALLOCATION = false
```

除非后续单独通过资产配置自动化的 Edge / Reliability / Compliance 审查。
