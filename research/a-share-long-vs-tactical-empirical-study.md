# A股长期持有 vs 短中期/情绪交易：实证对照计划 v1.0

> 状态：`ACTIVE FORWARD STUDY`
>
> 目的：把“短期情绪交易和长期持有收益能差多少”从观点争论转成可重复、可审计的实验。历史研究只作为外部证据，不冒充本仓库策略自己的实盘/前测结果。

## 1. 已有外部量化证据

### 高频/高换手散户的长期拖累

Barber & Odean 对 66,465 个美国折扣券商家庭账户（1991–1996）的研究报告：

```text
市场年收益约 17.9%
平均家庭约 16.4%
最高换手组约 11.4%
```

可支持：高换手个人投资者平均表现显著更差。

不可支持：所有短线、事件、趋势或量化策略必然失败。

Source:
https://faculty.haas.berkeley.edu/odean/papers/returns/individual_investor_performance_final.pdf

台湾全市场投资者数据研究报告个人投资者交易造成的年度 performance penalty 约 3.8 个百分点，大量损失来自 aggressive orders。

Source:
https://academic.oup.com/rfs/article-abstract/22/2/609/1595677

同样不能把 3.8% 直接当成未来 A 股策略固定损失。

### A股并不存在简单稳定的“强者恒强”

NBER 研究比较中国 A/B 股投资者结构后发现，A 股更明显表现月度反转，B 股更明显表现 momentum / earnings drift；投资者 clientele 会影响过去收益的可预测性。

Source:
https://www.nber.org/papers/w29453

另一项 NBER 研究发现中国市场存在日频 momentum，并将其与新投资者注意力和交易活动联系起来。

Source:
https://www.nber.org/papers/w31839

因此仓库不采用“技术必然有效”或“技术完全无效”两种极端结论。

### 涨停/情绪事件可能伴随过度反应

对 2000–2020 中国 A 股的研究发现，涨停事件存在价格过度反应，并影响传统 momentum 结果。

Source:
https://www.sciencedirect.com/science/article/pii/S0264999322001560

结论：涨停、换手、极端收益等可以作为情绪/拥挤状态变量，但不能直接等价为可交易 Alpha。

## 2. 机会成本基线

任何权益策略都必须和无风险/低风险机会成本比较，而不能只比较两套股票策略。

截至 2026-08-25，财政部-中国国债收益率曲线显示 10 年期国债收益率约 1.68%。该值只是 point-in-time 快照，后续每个 `as_of` 必须重新获取。

Source:
https://yield.chinabond.com.cn/cbweb-czb-web/czb/czbIndexGks

## 3. 正式内部对照组

同一初始资金、同一时点、同一成本口径至少同时维护：

```text
A. Long Core
   长期 Quality + Valuation + IRR 系统

B. Short/Mid Champion
   Technical 30 + Capital 30 + Fundamentals 25 + Catalyst 15

C. Causal Challenger
   Shadow only，直到 Promotion

D. Broad Total Return Benchmark
   优先沪深300全收益 H00300 / 与股票池更匹配的全收益指数

E. Cash / Government-Bond Opportunity Cost
   point-in-time 无风险或低风险基线
```

沪深300事实表确认：

```text
价格指数 000300
全收益指数 H00300
净收益指数 N00300
```

长期对照必须优先使用全收益口径。

Source:
https://oss-ch.csindex.com.cn/static/html/csindex/public/uploads/indices/detail/files/zh_CN/000300factsheet.pdf

## 4. 为什么不能伪造“2015–2026 本策略回测结果”

本仓库长期和短中期模型均依赖当时可见的：

- 财报发布日期；
- ST/退市状态；
- 行业/概念事实；
- 催化；
- 历史指数成分；
- 估值；
- 停复牌；
- 涨跌停；
- T+1；
- 成交费用和滑点。

如果拿今天仍存续的公司、今天知道的财报结果回填过去，就产生 survivorship / look-ahead bias。

因此历史代理回测可以用于提出假设，但不得冒充 Production Model 的真实历史业绩。

## 5. Forward Study 起点

仓库已有两个 2026-08-26 point-in-time baseline：

```text
Long：十股养老模型组合
Short/Mid：43 股最终研究 whitelist
```

从该日之后开始保存真正的 forward 证据。

每个交易日同时保存：

```text
as_of
model_version
universe
signal / NO_TRADE
planned_entry
invalidation
position_size
market_sentiment_score
market_regime
fees/tax/slippage assumptions
benchmark level
risk-free reference
```

闭环交易保存：

```text
realized_R
MFE_R
MAE_R
holding_days
turnover
cost_drag
rule_violation
```

## 6. 统一绩效指标

至少比较：

```text
CAGR / annualized return
Total Return
Benchmark Excess Return
Max Drawdown
Calmar
Volatility
Sharpe（只作辅助，明确无风险利率口径）
Expectancy_R
Profit Factor
Turnover
Cost Drag
Longest Losing Streak
Recovery Time
Worst Month / Worst Year
```

长期组合另外记录：

```text
cash_dividends_received
dividends_reinvested
price_return
total_return
```

## 7. “差多少”的正式回答格式

任何未来结论必须写成：

```text
在 [start, end]、[model_version]、[cost assumptions] 下：

Long Core CAGR = X
Short Champion CAGR = Y
Causal Challenger CAGR = Z
Benchmark Total Return CAGR = B
Risk-free/Bond baseline = Rf

Short - Long = Y - X
Long - Benchmark = X - B
Short - Benchmark = Y - B
```

同时必须报告 Max Drawdown 和 Turnover。只报告收益率视为不合格。

## 8. 决策规则

如果短中期系统：

```text
扣成本后长期不能产生正 Excess Return
OR
收益主要由极少数偶然交易贡献
OR
回撤显著高于长期仓且没有足够收益补偿
```

则降低 `Edge Cap`，而不是提高仓位追回损失。

如果长期系统长期跑输合理 Total Return Benchmark，也必须重新审查选股、估值和集中度，不能因为“长期投资”标签而豁免绩效审计。

## 9. 当前结论

外部研究已经证明：高换手散户可能付出每年数个百分点的长期代价；但这不是本仓库短中期策略的已验证损失。

本仓库自己的“短期 vs 长期到底差多少”从 2026-08-26 起进入可审计 Forward Study，只有真实积累的数据有资格回答最终数值。
