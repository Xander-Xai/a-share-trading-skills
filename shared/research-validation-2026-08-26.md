# 资金分配与交易风控调研验证 — 2026-08-26

> 本文件记录 `capital-allocation-and-entry-policy.md` v2.0 的公开资料验证、参数边界与 2026-08-26 一致性迁移结果。

## 1. 研究能证明什么，不能证明什么

公开研究可以支持：

- 资产配置应根据期限、风险承受能力和目标变化；
- 个股组合需要分散；
- 分批投入可以降低部分择时压力，但现金长期等待也有机会成本；
- 主动交易需要风险预算、仓位计算、退出计划和回撤控制；
- 频繁交易可能侵蚀个人投资者长期表现；
- 止损价不保证成交价；
- 时间止损、Reward/Risk、分批退出等可以纳入交易计划。

公开研究**不能证明**：

- 70/30、80/20、85/15 是唯一最优资金比例；
- 40/30/30 或 50/50 是数学最优建仓比例；
- 0.5%、1%、2%、3%、4/6/8 是唯一正确风险阈值。

这些具体数字属于本仓库的治理参数，需要用真实实盘继续校准。

## 2. 当前动态资金框架

股票专用资金 Size Cap：

| 股票专用资金规模 | 长期养老仓 | 短中期仓 |
|---:|---:|---:|
| ≤5 万元 | 70% | 30% |
| 5–30 万元 | 75% | 25% |
| 30–200 万元 | 80% | 20% |
| 200–1000 万元 | 85% | 15% |
| ≥1000 万元 | 85%–90% | 10%–15% |

最终短中期比例：

```text
Short Allocation = min(Size Cap, Risk Cap, Edge Cap)
```

因此旧的“短中期永远不超过总储蓄30%”规则已经退役。

## 3. 资产配置与分散证据

### Investor.gov — Asset Allocation and Diversification

https://www.investor.gov/introduction-investing/getting-started/asset-allocation

支持：配置应与期限、风险承受能力和目标相匹配，并在不同资产和资产内部进行分散。

### Investor.gov — Beginners’ Guide to Asset Allocation, Diversification, and Rebalancing

https://www.investor.gov/additional-resources/general-resources/publications-research/info-sheets/beginners-guide-asset

支持：只持有少数几只个股通常不足以形成充分分散；需要跨公司、行业和经济驱动分散。

设计结果：随着资本增长，长期仓提高持股数量、降低单股与风险簇上限。

## 4. 长期建仓证据边界

### Vanguard — Cost averaging: Invest now or temporarily hold your cash?

https://corporate.vanguard.com/content/dam/corp/research/pdf/cost_averaging_invest_now_or_temporarily_hold_your_cash.pdf

其历史研究显示，一次性投入相对短期分批在多数样本期表现更好，说明现金等待存在机会成本。

本仓库因此使用：

```text
长期默认：40 / 30 / 30
例外：60 / 40
例外：30 / 25 / 25 / 20
```

旧的模糊“3–5批”规则已经退役。批次由资金规模、流动性、信息不确定性和估值安全边际共同决定，而不是越多越安全。

## 5. 主动交易与过度交易

### Barber & Odean — Trading Is Hazardous to Your Wealth

https://faculty.haas.berkeley.edu/odean/papers/returns/individual_investor_performance_final.pdf

样本研究显示高换手组长期表现显著落后市场。

这不能推出“所有短中期策略都失败”，但支持：

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

当前仓库统一区分：

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

## 7. 短中期建仓：旧 3/4/4 规则退役

当前统一：

```text
默认：50% Setup + 50% Confirmation
三级确认例外：50% / 30% / 20%
```

第二、第三批只能在正向确认后执行。

账户变大并不会机械增加“策略批次”。百万、千万级资金可以为了成交容量把单个策略批次拆成多个订单，这属于执行拆单，不是新增策略判断。

## 8. 补仓

### 长期仓

只有以下四个 Gate 同时通过才允许补仓：

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

不使用统一百分比止损。主要退出原因：

- 商业模式/护城河结构性破坏；
- 正常化盈利能力永久下降；
- 分红削减背后是现金流/偿债/资本恶化；
- 审计/治理红旗；
- 债务或监管资本失控；
- 原始 thesis 被事实证伪。

TRIM 主要由估值、集中度和机会成本驱动。

### 短中期

使用：

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

当前内部治理线：

```text
-4% → 降低风险
-6% → 停止新开仓并复盘
-8% → 暂停策略，正式复核后再恢复
```

这不是学术唯一最优阈值。

## 11. 大资金流动性

百万、千万级账户需要额外检查：

- 单股日均成交额；
- 买卖价差；
- 计划订单占成交额比例；
- 涨跌停与低流动性风险；
- 限价与订单拆分需求。

策略批次和执行拆单必须分开记录。

## 12. 当前规则迁移状态

2026-08-26 已完成一次仓库一致性迁移：

- 根 README 已更新为“两套 Skill 均已存在”；
- 增加 `policy-precedence.md`；
- 长期 Skill 移除固定 25% 单股上限和模糊 3–5 批旧规则；
- 长期 execution template 改为从 shared 动态读取仓位上限；
- 短中期 Skill 移除永久 30% 总储蓄规则；
- 短中期旧 3/4/4 建仓规则退役；
- 风险预算明确区分 Operating Target 与 Hard Ceiling；
- 止盈明确 R/结构优先于固定百分比观察区；
- evaluation cases 增加 policy precedence、动态配比、tranche 与 hard-ceiling 测试。

历史 snapshot/watchlist 保持原样，但只用于回溯，不能覆盖当前 policy。

## 13. 后续校准

建议持续记录：

- realized R；
- MAE/MFE；
- 滑点与费用；
- 胜率、平均盈亏比、Profit Factor；
- 最大回撤；
- 连续亏损长度；
- 持有天数；
- 规则违反率。

每季度和滚动 6–12 个月重新评估 `Edge Cap`。若主动策略没有正期望，应降低短中期资本，而不是通过扩大仓位弥补。
