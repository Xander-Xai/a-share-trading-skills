---
name: a-share-multi-asset-allocation
description: 为现金、国债/高等级固收和A股股票账户建立一级资产配置、风险预算、负债匹配与再平衡规则。它决定多少资本成为 Stock Account Equity，但不替代股票账户内部长期和短中期 Skill。
version: 1.1.0
---

# Multi-Asset Allocation Skill

## 0. 作用边界与上位规则

本 Skill 解决：

```text
Total Financial Assets
→ 多少留作应急/负债准备？
→ 多少配置现金/高等级固收？
→ 多少成为 Stock Account Equity？
```

然后股票账户内部再调用 Level 1A：

```text
Total Financial Assets
→ Multi-Asset Allocation Skill
→ Stock Account Equity
→ shared/capital-allocation-and-entry-policy.md
   → Long Strategic Baseline
   → Short/Mid Final Cap
   → Stock-account Pending Cash
```

执行前读取：

1. `../../shared/policy-precedence.md`
2. `../../shared/research-model-governance.md`
3. 涉及自动监控/再平衡执行时读取 `../../shared/automation-execution-governance.md`
4. 股票资金进入账户后，内部规则读取 `../../shared/capital-allocation-and-entry-policy.md`

### 关键边界

- 本 Skill 决定 **Stock Account Equity 的输入规模**；
- Level 1A 决定 Stock Account Equity 内部的长期/短中期/现金、单股/风险簇与交易风险；
- 本 Skill 不得直接覆盖 `Final Short Cap`、长期单股 Cap、短中期 Heat 或策略批次；
- Level 1A 也不应被误解为替用户决定全部金融资产应该有多少进入股票。

## 1. 第一性原理

资产配置先回答：

1. 哪些钱不能亏、什么时候必须用？
2. 最大可接受永久损失和阶段性回撤是多少？
3. 各类资产预期回报是否补偿其风险？
4. 多类资产是否真正由不同风险因子驱动？

顺序：

```text
Liquidity
→ Liability Matching
→ Risk Budget
→ Expected Return
→ Diversification
→ Strategic Allocation
→ Stock Account Allocation
→ Security Selection
```

不能先挑股票，再补想生活现金是否够用。

## 2. 统一资产定义

```text
Total Financial Assets
= Emergency / Liquidity Reserve
+ Near-term Liability Reserve
+ Fixed Income
+ Stock Account Equity
+ Other Strategic Assets (only if explicitly modeled)
```

本 v1.1 默认管理：

```text
Cash / Cash-like
Government / High-grade Fixed Income
A-share Stock Account
```

黄金、海外权益、REITs 等以后单独作为资产层 Challenger 研究，不静默混入当前生产配置。

## 3. Gate 1 — Liquidity Reserve

定义：

```text
essential_monthly_spending
emergency_months
known_liabilities_next_24m
```

当前治理初值：

```text
Emergency Reserve = 6–12个月必要支出
```

6–12个月是 Governance Parameter，不是所有人的唯一最优数字。

未来24个月内确定要使用、不能承受明显亏损的资金原则上不进入个股风险仓。

可研究：

- 银行现金/存款；
- 高流动性现金管理工具；
- 与使用期限匹配的短期限低信用风险固收工具。

## 4. Gate 2 — Liability Matching

原则：

```text
Asset Risk/Duration must fit Money-use Horizon
```

- 数月内使用的钱，不进入股票等待“总会涨回来”；
- 一年内刚性支出，不用长久期债券主动赌利率方向；
- 长期养老/财富目标才适合承担更长权益久期。

## 5. Gate 3 — Portfolio Stress Budget

先定义整个金融资产组合可接受的压力损失：

```text
Portfolio Stress Loss Budget = B
```

给资产层设可配置压力情景：

```text
Cash stress loss  = C
Bond stress loss  = D
Stock stress loss = E
```

保守门禁：

```text
w_cash*C + w_bond*D + w_stock*E <= B
```

示例：若允许组合压力损失15%，股票压力场景45%，暂忽略现金/短债压力：

```text
Stock Account Weight <= 15% / 45% ≈ 33%
```

45%只是 stress parameter，不是未来固定预测。

## 6. Gate 4 — Opportunity Cost / Required Return

每个 `as_of` 获取中国国债收益率曲线作为较低风险机会成本参考。

历史示例：2026-08-25 曲线约：

```text
1Y  ≈ 1.20%
5Y  ≈ 1.39%
10Y ≈ 1.68%
30Y ≈ 2.13%
```

Source:
https://yield.chinabond.com.cn/cbweb-czb-web/czb/czbIndexGks

这些只是历史快照，后续必须重新获取。

股票/长期风险资产至少要求：

```text
Expected Return
> Relevant Low-risk Alternative
+ Required Risk Compensation
```

Required Risk Compensation 是治理/模型参数，应做敏感性分析，并受 `research-model-governance.md` 约束。

## 7. Fixed Income 的作用

固收主要提供：

- 负债匹配；
- 流动性；
- 波动缓冲；
- 股票估值过高或 Edge 不足时保存购买力；
- 再平衡资金来源。

### 利率风险

```text
短期用钱 → 短久期优先
长期稳定资金 → 才评估更长久期
```

### 信用风险

防守层默认优先研究国债、政策性或高信用等级工具，不为了少量票息自动下沉到无法理解的信用风险。

## 8. 生成 Stock Account Equity

只有通过 Liquidity / Liability / Stress Gates 的长期风险资本，才进入：

```text
Stock Account Equity
```

进入后调用：

`../../shared/capital-allocation-and-entry-policy.md`

得到：

```text
Long Strategic Baseline
Short/Mid Size Cap
Final Short Cap
Stock-account Pending Cash
Account Symbol / Cluster Caps
```

特别重要：

```text
Final Short Cap
!= Total Financial Assets 的短线比例
```

它是 **Stock Account Equity 内部**的短中期上限。

## 9. Strategic Allocation 的动态规则

不因单日股价或情绪改变一级战略资产配置。

重新评估触发：

- 重大收入/支出变化；
- 重大负债变化；
- 投资期限变化；
- 风险承受能力变化；
- 季度/年度正式复核；
- 资产权重持续明显漂移；
- 长期 Expected Return / opportunity cost 明显变化。

## 10. 一级资产再平衡

优先使用自然现金流：

```text
新增储蓄
→ 利息/分红
→ 到期固收
→ 已实现短中期利润
→ 最后才主动卖出优质长期资产
```

当前治理参考：

```text
季度检查
年度正式重设 Strategic Allocation
```

一级资产配置可以使用约 ±5pp 漂移带作为“无需频繁微调”的参考，但：

- 不能突破 Liquidity / Liability / Stress Gates；
- 不能被带入 Level 1A 作为突破 `Final Short Cap` 或账户级单股/风险簇 Cap 的理由；
- 不同层级的漂移带不能互相借用。

## 11. Risk-on / Risk-off 不直接重写一级资产配置

短期市场情绪只能影响：

- 短中期新仓节奏；
- Stock Account Pending Cash 的部署速度；
- 风险预算的保守程度。

禁止：

```text
PANIC → 自动把全部股票卖成债券
EUPHORIA → 自动把全部固收换成股票
```

一级资产配置和短期情绪属于不同时间尺度。

## 12. 输出合同

```yaml
as_of:
research_model_governance_version:
strategy_version:
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
stock_account_equity_target:
current_1y_gov_yield:
current_5y_gov_yield:
current_10y_gov_yield:
current_30y_gov_yield:
allocation_drift:
rebalance_action:
assumption_confidence:
```

关键个人输入缺失时，不猜精确比例：

```text
INSUFFICIENT_PERSONAL_INPUT_FOR_FINAL_ALLOCATION
```

仍可输出规则和敏感性区间。

## 13. 禁止事项

- 把应急金投入个股；
- 把两年内刚性支出用长期股票承担；
- 用股票短期上涨提高风险承受能力假设；
- 用短中期亏损从防守资产自动补仓；
- 把高票息等同于低风险；
- 假设历史低波动代表未来不会出现压力行情；
- 为凑满配置比例购买不理解的资产；
- 在本 Skill 中重新定义股票账户内部 `Final Short Cap` / 策略批次 / 单股 Cap。

## 14. 与自动化关系

自动化可以：

```text
读取收益率曲线
计算当前资产权重
检测 Liquidity / Liability / Stress Gate
检测战略漂移
生成再平衡建议
```

默认：

```text
AUTO_MONITOR = true
AUTO_STRATEGIC_REALLOCATION = false
```

任何真实战略资产再配置默认需要人工确认，并受 `../../shared/automation-execution-governance.md` 的数据、审计、fail-closed 和执行安全原则约束。

## 15. 与仓库其他模块的关系

```text
Multi-Asset Skill
→ 产出 Stock Account Equity

Level 1A Capital Policy
→ 股票账户内分长期 / 短中期 / 现金

Long Skill
→ 长期选股、Expected IRR、持仓

Short/Mid Skill
→ Champion/Challenger、短中期执行

Runtime Monitor
→ 只监控/产生研究状态，不重写 Strategic Allocation
```
