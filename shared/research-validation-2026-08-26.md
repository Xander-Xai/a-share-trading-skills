# 资金分配与交易风控调研验证 — 2026-08-26

> 本文件记录 `capital-allocation-and-entry-policy.md` **v2.2** 的公开资料验证、参数边界与本仓库一致性迁移结果。
>
> 自动化执行安全与程序化交易门禁的跨策略治理见 `automation-execution-governance.md`。

## 1. 研究能证明什么，不能证明什么

公开研究可以支持：

- 资产配置应根据期限、风险承受能力和目标变化；
- 个股组合需要分散；
- 分批投入可以降低部分择时压力，但现金长期等待也有机会成本；
- 主动交易需要风险预算、仓位计算、退出计划和回撤控制；
- 频繁交易可能侵蚀个人投资者长期表现；
- 止损价不保证成交价；
- 时间止损、Reward/Risk、分批退出可以纳入交易计划；
- 自动化交易需要独立风控、审计和合规门禁。

公开研究**不能证明**：

- 70/30、80/20、85/15 是唯一最优资金比例；
- 40/30/30 或 50/50 是数学最优建仓比例；
- 0.5%、1%、2%、3%、4/6/8 是唯一正确风险阈值；
- Paper 达到某个固定样本数就必然可以安全转实盘；
- 技术上能自动报单就等于已满足程序化交易和券商要求。

具体数字和晋级门槛属于仓库治理参数，需要用真实 Forward/Live 数据持续校准。

## 2. 当前动态资金框架

股票专用资金 Size Cap：

| 股票专用资金规模 | 长期战略基线 | 短中期 Size Cap |
|---:|---:|---:|
| ≤5 万元 | 70% | 30% |
| 5–30 万元 | 75% | 25% |
| 30–200 万元 | 80% | 20% |
| 200–1000 万元 | 85% | 15% |
| ≥1000 万元 | 85%–90% | 10%–15% |

最终短中期上限：

```text
Final Short Cap = min(Size Cap, Risk Cap, Edge Cap)
Actual Short Exposure <= Final Short Cap
```

因此旧的“短中期永远30%”或“短中期永远不超过总储蓄30%”都不是当前仓库级规则。

### v2.2 语义修正

股票专用资金不要求 100% 始终满仓：

```text
股票专用资金
= 已部署长期仓
+ 已部署短中期仓
+ 待配置现金
```

如果 Risk Cap / Edge Cap 把短中期压低，差额不自动强制转成长仓。长期资产仍必须通过自己的质量、估值和组合 Gate；没有合格机会时现金是合法状态。

同样，任何 ±5 个百分点的再平衡“漂移参考带”都不能突破 `Final Short Cap`、单股/风险簇上限或 Hard Ceiling。

## 3. 资产配置与分散证据

### Investor.gov — Asset Allocation and Diversification

https://www.investor.gov/introduction-investing/getting-started/asset-allocation

支持：配置应与期限、风险承受能力和目标匹配，并在不同资产和同一资产类别内部进行分散。

### Investor.gov — Beginners’ Guide to Asset Allocation, Diversification, and Rebalancing

https://www.investor.gov/additional-resources/general-resources/publications-research/info-sheets/beginners-guide-asset

支持：只持有少数几只个股通常不足以形成充分分散，需要跨公司、行业和经济驱动分散。

设计结果：随着资本增长，长期仓提高持股数量并降低单股与风险簇上限。

## 4. 长期建仓证据边界

### Vanguard — Cost averaging: Invest now or temporarily hold your cash?

https://corporate.vanguard.com/content/dam/corp/research/pdf/cost_averaging_invest_now_or_temporarily_hold_your_cash.pdf

其历史研究说明现金等待存在机会成本，不能把“分得越多、拖得越久”自动等同于更安全。

仓库治理规则：

```text
长期默认：40 / 30 / 30
例外：60 / 40
例外：30 / 25 / 25 / 20
```

旧的模糊“3–5批”规则已经退役。策略批次与大额订单执行拆单必须分开。

## 5. 主动交易与过度交易

### Barber & Odean — Trading Is Hazardous to Your Wealth

https://faculty.haas.berkeley.edu/odean/papers/returns/individual_investor_performance_final.pdf

研究支持“高换手和过度自信可能侵蚀个人投资者表现”，但不能推出所有短中期策略必然失败。

因此：

```text
主动交易仓必须用真实 Edge 挣仓位；
未验证策略不得成为核心财富账户的主要风险来源。
```

## 6. 风险仓位与退出

### Charles Schwab — Elements of a Smart Trade Plan

https://www.schwab.com/learn/story/5-elements-smart-trade-plan

支持在交易前定义风险、仓位和退出。

### Fidelity — Position Sizing / Exit Strategies

https://www.fidelity.com/bin-public/060_www_fidelity_com/documents/learning-center/trading-volatility-slides.pdf

https://www.fidelity.com/learning-center/trading-investing/trading/exit-strategies

支持风险仓位、Profit/Loss Ratio、时间退出等框架。

当前仓库：

```text
Operating Target
- 单笔：0.5% × 短中期策略净值
- 全部未平仓初始风险：2%
- 单一行业/因子初始风险：1%

Hard Ceiling
- 单笔：1%
- 全部未平仓初始风险：3%
```

0.5% 是正常运行目标；1% 是硬上限，不是默认值。

## 7. 短中期建仓

```text
默认：50% Setup + 50% Confirmation
三级确认例外：50% / 30% / 20%
```

第二、第三批只能在正向确认后执行。旧的“资金越大就机械 3/4/4 批”规则已经退役。

## 8. 补仓

### 长期仓

只有以下四个 Gate 同时通过才允许 ADD：

```text
Thesis Gate
Balance Gate
Valuation Gate
Portfolio Gate
```

下跌约15%–20%和25%–30%仅作为重新研究触发线，不是自动买卖线。

### 短中期仓

禁止因亏损而摊低成本。后续批次必须是第一笔得到正向确认后的风险预算内加仓。

## 9. 止损与止盈分离

### 长期

不使用统一百分比止损。主要退出原因是投资逻辑、盈利能力、现金流/资本、治理或商业模式发生结构性破坏。

TRIM 主要由估值、集中度和机会成本驱动。

### 短中期

```text
价格/失效止损
+ 逻辑止损
+ 时间止损
```

利润管理优先级：

```text
R倍数 + 技术结构 + 原始目标
```

传统 +3%–5%、成长 +6%–10% 只保留为辅助观察区；与 R/结构冲突时，R/结构优先。

## 10. 回撤熔断

```text
-4% → 降低风险
-6% → 停止新开仓并复盘
-8% → 暂停策略，正式复核后再恢复
```

这是仓库治理参数，不是学术唯一最优阈值。

## 11. 大资金流动性

百万、千万级账户额外检查：

- 单股日均成交额；
- 买卖价差；
- 计划订单占成交额比例；
- 涨跌停与低流动性风险；
- 限价与订单拆分需求。

策略批次和执行拆单必须分开记录。

## 12. Paper / Live / Automation 证据边界

```text
Paper 证明流程可重复
Manual Live 证明真实成交与纪律可执行
Assisted / Semi-auto 证明执行系统可靠
Full Auto 还必须通过合规、故障恢复、对账与 Kill Switch
```

模拟仓使用 A 股执行约束时必须同时保存：

```text
paper_capital_rmb
reporting_nav = 100.00 起始指数
```

前者用于股数、100股单位、费用和滑点；后者用于标准化绩效比较。

## 13. 程序化交易与自动执行基线

当前研究基线：

- 中国证监会《证券市场程序化交易管理规定（试行）》
  https://www.csrc.gov.cn/csrc/c101954/c7480579/content.shtml
- 上海证券交易所程序化交易管理实施细则
  https://www.sse.com.cn/lawandrules/sselawsrules2025/trade/universal/c/c_20250612_10781696.shtml
- 深圳证券交易所程序化交易管理实施细则
  https://www.szse.cn/lawrules/rule/trade/t20250403_612770.html

进入任何实际自动报单阶段前，必须重新联网核验并与实际券商确认账户/API/报告/权限要求。本仓库不因为代码可运行就声称合规已完成。

## 14. 当前规则迁移状态

2026-08-26 已完成多轮一致性迁移：

- 根 README 已更新为两套 Skill 均存在；
- 增加 `policy-precedence.md`；
- 增加 `automation-execution-governance.md`；
- v2.2 明确 `Final Short Cap` 是上限，不是必须满配目标；
- v2.2 明确未部署差额可以留在待配置现金池；
- v2.2 明确任何漂移参考区间不能突破 Cap；
- 长期 Skill 移除固定25%单股上限和模糊3–5批旧规则；
- 长期 execution template 动态读取 shared policy；
- 短中期 Skill 移除永久30%总储蓄规则；
- 短中期旧3/4/4建仓规则退役；
- 风险预算区分 Operating Target 与 Hard Ceiling；
- 止盈明确 R/结构优先；
- examples / case studies / snapshots 被明确为非规范性证据记录；
- 自动化执行统一采用 fail closed、broker reconciliation、idempotency 和 Kill Switch 原则。

## 15. 后续校准

持续记录：

- realized R；
- MAE/MFE；
- 滑点与费用；
- 胜率、平均盈亏比、Profit Factor；
- 最大回撤；
- 连续亏损长度；
- 持有天数；
- 规则违反率；
- Paper vs Live 偏差；
- broker/reconciliation/error 事件。

每季度和滚动 6–12 个月重新评估 `Edge Cap`。若主动策略没有正期望，应降低短中期资本，而不是扩大仓位弥补。
