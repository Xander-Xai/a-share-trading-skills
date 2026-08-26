# A股长期持有 vs 短中期/情绪交易：实证对照计划 v1.1

> 状态：`ACTIVE FORWARD STUDY`
>
> 目的：把“短期情绪交易和长期持有收益能差多少”从观点争论转成可重复、可审计的实验。历史研究只作为外部证据，不冒充本仓库策略自己的实盘/前测结果。
>
> 本文件属于研究计划，不覆盖三类 Level-1 governance 或任何 Skill。

## 1. Governance Bundle

每个研究 cohort 必须冻结并保存：

```text
capital_policy_version
automation_governance_version
research_model_governance_version
long_skill_version
short_mid_skill_version
long_model_version
short_champion_version
challenger_version
benchmark_definition
cost_assumptions
```

若治理或模型版本变化，结束当前 cohort 或明确记录版本切点，不能把不同规则时期的收益静默拼成一个不可解释的序列。

## 2. 已有外部量化证据

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

结论：涨停、换手、极端收益可以作为情绪/拥挤状态变量，但不能直接等价为可交易 Alpha。

## 3. 机会成本基线

任何权益策略都必须和无风险/低风险机会成本比较，而不能只比较两套股票策略。

截至 2026-08-25，财政部-中国国债收益率曲线显示 10 年期国债收益率约 1.68%。该值只是 point-in-time 历史快照，后续每个 `as_of` 必须重新获取。

Source:
https://yield.chinabond.com.cn/cbweb-czb-web/czb/czbIndexGks

## 4. 正式内部对照组

同一初始股票专用资金、同一时点、同一成本口径至少同时维护：

```text
A. Long Retirement Book
   Quality + Valuation + Expected IRR + Portfolio Fit
   包含 Core Dividend + Growth Satellite

B. Short/Mid Champion
   Technical 30 + Capital 30 + Fundamentals 25 + Catalyst 15

C. Causal Challenger
   Shadow only，直到正式 Promotion

D. Broad Total Return Benchmark
   优先沪深300全收益 H00300 / 与研究 universe 更匹配的全收益指数

E. Cash / Government-Bond Opportunity Cost
   point-in-time 无风险或低风险基线
```

“Long Retirement Book”不能写成纯 `Long Core`，因为当前长期 Skill 明确包含 Growth Satellite。

沪深300事实表确认：

```text
价格指数 000300
全收益指数 H00300
净收益指数 N00300
```

长期对照优先使用全收益口径。

Source:
https://oss-ch.csindex.com.cn/static/html/csindex/public/uploads/indices/detail/files/zh_CN/000300factsheet.pdf

## 5. 账户和策略分母必须分开

全账户：

```text
Stock Account Equity
= Long + Short/Mid + Pending Cash
```

长期研究组合权重使用 long-book 内部分母；短中期风险预算使用 short/mid strategy NAV。

比较收益时必须说明采用：

- standalone sleeve return；
- 还是按实际资本分配后的 total-account contribution。

不能把“短中期策略自身收益率”和“其对整个股票账户的贡献率”混为一谈。

## 6. 为什么不能伪造“2015–2026 本策略回测结果”

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
- 交易费用和滑点。

如果拿今天仍存续的公司、今天知道的财报结果回填过去，就产生 survivorship / look-ahead bias。

历史代理回测可以用于提出假设，但无法重建 point-in-time 输入时必须标记：

```text
Biased / Non-promotable
```

不得冒充 Production Model 的真实历史业绩或模型晋级证据。

## 7. Forward Study 起点

仓库已有两个 2026-08-26 point-in-time baseline：

```text
Long：十股养老模型 long-book
Short/Mid：43股最终研究 whitelist
```

它们都是 Level 4 历史起点，不是当前永久名单。

从该日之后保存真正的 Forward 证据。

每个研究日至少保存：

```text
as_of
governance_bundle
model_version
universe
signal / NO_TRADE
planned_entry
invalidation
position_size
market_sentiment_state
market_regime
fees/tax/slippage/impact assumptions
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

长期另外保存：

```text
Bear/Base/Bull IRR at decision time
Max Buy Price
cash dividends
prediction error
```

## 8. 统一绩效指标

至少比较：

```text
CAGR / annualized return
Total Return
Benchmark Excess Return
Max Drawdown
Calmar
Volatility
Sharpe（辅助，明确无风险利率口径）
Turnover
Cost Drag
Recovery Time
Worst Month / Worst Year
```

短中期另外：

```text
Expectancy_R
Profit Factor
Win Rate
Payoff Ratio
Longest Losing Streak
MFE / MAE
```

长期另外：

```text
price_return
cash_dividends_received
dividends_reinvested
total_return
benchmark_total_return
prediction_error
```

只报告收益、不报告回撤、成本和资本占用视为不合格。

## 9. “差多少”的正式回答格式

未来结论必须写明研究区间和版本：

```text
[start, end]
Governance Bundle = ...
Long model = ...
Short Champion = ...
Challenger = ...
Cost assumptions = ...
Benchmark = ...

Long Retirement Book CAGR = X
Short Champion CAGR = Y
Causal Challenger CAGR = Z
Benchmark Total Return CAGR = B
Risk-free/Bond baseline = Rf

Short - Long = Y - X
Long - Benchmark = X - B
Short - Benchmark = Y - B
```

同时报告 Max Drawdown、Turnover、Cash Exposure 和样本量。

若比较**整个股票账户贡献**，还必须乘以对应实际资本暴露，不能用 standalone sleeve CAGR 直接代表全账户结果。

## 10. 决策规则

如果短中期系统：

```text
扣成本后长期不能产生正 Excess Return
OR
收益主要由极少数偶然交易贡献
OR
回撤显著高于长期仓且没有足够收益补偿
```

则降低 `Edge Cap`，而不是提高仓位追回损失。

如果长期系统持续跑输合理 Total Return Benchmark，也必须重新审查选股、估值、集中度和现金拖累，不能因为“长期投资”标签而豁免绩效审计。

Challenger 表现优于 Champion 也不能自动 Promotion；仍需 Level 1C 的人工评审。

## 11. 当前结论

外部研究支持：高换手散户可能付出显著长期代价，但这不是本仓库短中期策略已经验证的固定损失。

本仓库自己的“短期 vs 长期到底差多少”从 2026-08-26 起进入可审计 Forward Study。最终数值只能由冻结版本、真实 point-in-time 数据、成本后结果和一致口径 Benchmark 回答。