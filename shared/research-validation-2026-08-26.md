# 资金、研究模型与执行治理调研验证 — 2026-08-26

> 当前对应治理基线：
>
> ```text
> Capital / Risk         v2.3
> Automation / Execution v1.2
> Research / Model        v3
> ```
>
> 本文件记录公开资料支持的原则、仓库治理参数的边界，以及当前一致性迁移结果。它不是新的 Source of Truth。

## 1. 研究能证明什么，不能证明什么

公开研究与监管资料可以支持：

- 资产配置应结合期限、目标和风险承受能力；
- 个股投资需要分散并管理集中度；
- 分批投入能降低部分择时/行为压力，但现金等待存在机会成本；
- 主动交易需要预先定义风险、仓位和退出；
- 频繁交易可能侵蚀个人投资者长期表现；
- 止损价不等于保证成交价；
- 技术/动量信号可能包含条件预测信息，但有效性依赖市场、时期、参数和成本；
- 长期个股回报高度偏态，“不退市”不等于创造长期股东价值；
- 自动化执行需要独立风控、审计、对账、幂等和合规门禁；
- 模型晋级必须防止 look-ahead、幸存者偏差和 data-snooping。

公开研究**不能证明**：

- 70/30、80/20、85/15 是唯一最优资金比例；
- 40/30/30、50/50 是数学最优建仓比例；
- 0.5%、1%、2%、3%、4/6/8 是唯一正确风险阈值；
- +1.5R/+2R 或3–5日 time review 是普适最优退出规则；
- 某一技术指标或“主力资金流”标签稳定产生 Alpha；
- Paper 达到固定笔数就必然可以实盘；
- 技术上能自动报单就等于已满足监管和券商要求。

以上具体数字属于 Governance Parameter，必须通过 Forward/Live 数据持续校准。

## 2. 三类治理 Source of Truth

```text
Level 1A — capital-allocation-and-entry-policy.md
Level 1B — automation-execution-governance.md
Level 1C — research-model-governance.md
```

分别管理：

- 1A：资本、仓位、风险、建仓/补仓/退出、账户级集中度；
- 1B：Paper/Live、Broker、虚拟子账、幂等、Kill Switch、自动化和合规；
- 1C：证据分层、point-in-time、Benchmark、Champion/Challenger、模型晋级。

多个 Level-1 同时涉及某个动作时必须**全部满足**。

## 3. v2.3 统一账户分母

当前统一定义：

```text
Stock Account Equity
= 长期股票市值
+ 短中期股票市值
+ 股票账户待配置现金
```

以下统一以该分母计算：

- 长期 / 短中期 Size Cap；
- `Final Short Cap`；
- 账户级单股合计暴露；
- 账户级风险簇合计暴露。

长期内部 Core/Growth、十股模型 `model_long_book_weight` 是 long-book 内部比例，必须先换算：

```text
model_total_account_weight
= model_long_book_weight × planned_long_exposure
```

再与账户级 Cap 比较。

这修复了“不同分母的百分比直接比较”的旧歧义。

## 4. 动态长期 / 短中期资本框架

| Stock Account Equity | 长期战略基线 | 短中期 Size Cap |
|---:|---:|---:|
| ≤5 万元 | 70% | 30% |
| 5–30 万元 | 75% | 25% |
| 30–200 万元 | 80% | 20% |
| 200–1000 万元 | 85% | 15% |
| ≥1000 万元 | 85%–90% | 10%–15% |

最终短中期上限：

```text
Final Short Cap = min(Size Cap, Risk Cap, Edge Cap)
```

它是**上限，不是满仓要求**。

新订单必须满足：

```text
Planned Post-Trade Short Exposure <= Final Short Cap
```

账户允许：

```text
Stock Account Equity
= 已部署长期仓
+ 已部署短中期仓
+ 待配置现金
```

若 Risk/Edge Cap 压低短中期，差额不会自动强制转成长仓；长期也必须通过自身 Gate。

## 5. CAP_BREACH：计划超限与市场被动超限分开

市场价格上涨可能让已有持仓在没有新订单的情况下超过 Cap。

因此当前规则不是“实际暴露在每一个瞬间永远不可能超限”，而是：

```text
新订单：
Planned Post-Trade Exposure <= applicable Cap

市场被动超限：
CAP_BREACH
→ no new risk increase
→ rebalance/profit-transfer review
→ return within Cap in an executable window
```

不能用 ±5pp 漂移带作为主动超限理由，也不要求在异常价格下机械市价卖出。

## 6. 跨策略同股 / 同因子必须聚合

```text
Account Symbol Exposure
= Long Sleeve Exposure + Short/Mid-term Sleeve Exposure

Account Cluster Exposure
= Long Cluster Exposure + Short/Mid-term Cluster Exposure
```

例如同一股票同时属于养老仓和短中期交易仓时，不能各自使用一套独立单股上限。

执行层进一步维护：

```text
Broker Net Position
Strategy Virtual Position: long
Strategy Virtual Position: short_mid
```

用于防止短中期 SELL 误卖长期逻辑份额，并支持跨策略 order-conflict / netting 检查。

## 7. 资产配置与分散证据

### Investor.gov — Asset Allocation and Diversification

https://www.investor.gov/introduction-investing/getting-started/asset-allocation

支持：配置应与期限、风险承受能力和目标匹配，并在资产类别内部进行分散。

### Investor.gov — Beginners’ Guide to Asset Allocation, Diversification, and Rebalancing

https://www.investor.gov/additional-resources/general-resources/publications-research/info-sheets/beginners-guide-asset

支持：只持有少数个股通常不足以形成充分分散。

仓库设计结果：资本越大，长期组合提高分散度、降低账户级单股和风险簇上限。

## 8. 长期建仓证据边界

### Vanguard — Cost averaging: Invest now or temporarily hold your cash?

https://corporate.vanguard.com/content/dam/corp/research/pdf/cost_averaging_invest_now_or_temporarily_hold_your_cash.pdf

研究支持：现金等待存在机会成本，不能把“分得越多、拖得越久”自动视为更优。

仓库治理初值：

```text
长期默认：40 / 30 / 30
例外：60 / 40
例外：30 / 25 / 25 / 20
```

这些比例用于管理单股估值/信息风险，不宣称收益最大化。

## 9. 主动交易与过度交易

### Barber & Odean — Trading Is Hazardous to Your Wealth

https://faculty.haas.berkeley.edu/odean/papers/returns/individual_investor_performance_final.pdf

研究支持：高换手与过度自信可能侵蚀个人投资者长期表现。

不能推出所有短中期策略都必然失败。因此本仓库采用：

```text
主动交易必须用真实 Edge 挣仓位
未验证策略不得成为核心财富账户主要风险源
```

## 10. 短中期风险与退出

### Charles Schwab — Elements of a Smart Trade Plan

https://www.schwab.com/learn/story/5-elements-smart-trade-plan

### Fidelity — Position Sizing / Exit Strategies

https://www.fidelity.com/bin-public/060_www_fidelity_com/documents/learning-center/trading-volatility-slides.pdf

https://www.fidelity.com/learning-center/trading-investing/trading/exit-strategies

当前 Governance Parameter：

```text
Operating Target
- 单笔：0.5% × 短中期策略 NAV
- 全部未平仓初始风险：≤2%
- 单一行业/因子初始风险：≤1%

Hard Ceiling
- 单笔：≤1%
- 全部未平仓初始风险：≤3%
```

Hard Ceiling 是**计划风险限制**，不是 gap/跌停下实际亏损绝不超过的保证。

## 11. 短中期建仓与亏损加仓

```text
默认：50% Setup + 50% Confirmation
三级确认例外：50% / 30% / 20%
```

第二、第三批只能在正向确认后执行。

旧的按账户规模机械3/4/4批规则已经退役。

趋势/催化策略禁止仅因亏损而摊低成本；长期价值 ADD 是另一套逻辑，必须通过 Thesis / Balance / Valuation / Portfolio Gates。

## 12. 长期 Expected IRR 与 Benchmark

长期“低位”必须分开：

```text
Price Low != Valuation Low
```

精确 IRR 使用逐期现金流：

```text
0
= -P0
+ CF1/(1+r)
+ ...
+ (CFT + Terminal Value)/(1+r)^T
```

给定 Required Return `k` 的 Max Buy Price：

```text
Σ[CF_t/(1+k)^t] + TV_T/(1+k)^T
```

把累计分红全部视为终点现金流只能算简化 CAGR sanity check，不能称精确 IRR。

长期 Benchmark 优先使用 Total Return 口径。例如沪深300：

```text
Price Index  = 000300
Total Return = H00300
```

## 13. Research / Model Governance

短中期当前 Champion：

```text
Technical 30
Capital Participation 30
Fundamentals 25
Catalyst 15
```

Causal 模型当前仍为：

```text
CHALLENGER / SHADOW ONLY
```

晋级必须在相同 universe、`as_of`、成本、风险预算和执行约束下完成 Forward 对照，并检查：

- 净收益 / 超额收益；
- Expectancy / Profit Factor；
- Max Drawdown / Calmar；
- turnover / cost drag；
- MFE / MAE；
- Regime 稳定性；
- 结果是否由少数 outlier 主导；
- point-in-time / survivorship / look-ahead。

无法重建历史真实输入的结果：

```text
Biased / Non-promotable
```

## 14. MFE / MAE 与退出参数校准

当前：

```text
+1.5R / +2R partial review
3–5 日 time review
```

只作为治理初值。

每笔交易记录：

```text
realized_R
MFE_R
MAE_R
holding_days
exit_reason
fees / tax / slippage / impact
```

参数修改必须先形成 Challenger/研究假设，不能因最近几笔交易自动改生产规则。

## 15. Paper / Live / Automation

Paper 模式同时保存：

```text
paper_capital_rmb
reporting_nav
```

所有 cohort / 决策 / 订单保存完整 Governance Bundle：

```text
capital_policy_version
automation_governance_version
research_model_governance_version
skill_version
strategy_version
model_version
```

自动化统一使用：

- Broker reconciliation；
- Strategy Virtual Position；
- idempotency / duplicate-order protection；
- fail closed；
- Kill Switch；
- current model status check；
- programmatic-trading / broker compliance gate。

默认：

```text
AUTO_MONITOR = true
AUTO_ORDER   = false
```

## 16. 程序化交易研究基线

- 中国证监会《证券市场程序化交易管理规定（试行）》
  https://www.csrc.gov.cn/csrc/c101954/c7480579/content.shtml
- 上海证券交易所程序化交易管理实施细则
  https://www.sse.com.cn/lawandrules/sselawsrules2025/trade/universal/c/c_20250612_10781696.shtml
- 深圳证券交易所程序化交易管理实施细则
  https://www.szse.cn/lawrules/rule/trade/t20250403_612770.html

进入任何实际自动报单阶段前，必须重新联网核验并与实际券商确认账户/API/报告/权限要求。

## 17. 当前迁移状态

截至本轮一致性修复，已完成：

- 旧固定70/30退役；
- 旧“短中期≤总储蓄30%”退役；
- 旧长期固定25%单股上限退役；
- 旧长期模糊3–5批退役；
- 旧短中期3/4/4批退役；
- Operating Target / Hard Ceiling 分层；
- R/结构优先于固定百分比止盈区；
- `Final Short Cap` 明确为新订单上限；
- `CAP_BREACH` 区分被动超限；
- 统一 `Stock Account Equity` 分母；
- 长/短同股与同因子账户级聚合；
- Broker Net Position 与 Strategy Virtual Position 分离；
- Expected IRR 改为逐期现金流；
- Total Return Benchmark 纳入长期验证；
- Champion/Challenger 与 Automation Promotion 分离；
- Governance Bundle 统一为三类 Level-1 版本。

## 18. 后续校准

持续记录：

- realized R；
- MFE/MAE；
- 滑点、费用、impact；
- 胜率、Payoff、Profit Factor；
- 最大回撤和连续亏损；
- holding days；
- rule violation；
- Paper vs Live 偏差；
- CAP_BREACH；
- cross-sleeve reconciliation；
- broker/error/kill-switch 事件；
- 长期 prediction error 与 Total Return excess return。

参数升级只通过正式治理流程，不因短期结果追着市场修改。