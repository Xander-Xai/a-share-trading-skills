# 十只养老股模型组合示例 — 2026-08-26

> 类型：长期养老 Skill 的历史示例 / Forward-Test 模型组合基线。
>
> 快照时间：`as_of = 2026-08-26 21:08 China Standard Time (UTC+8)`，价格来自用户当晚同花顺自选截图。
>
> 本文件属于 Level 4 历史案例，不覆盖当前 shared policy、research model governance、automation governance 或长期 SKILL。任何真实下单前必须重新运行长期 Skill。

## 0. 事实修订与规则迁移说明

### 0.1 Point-in-time 事实纠错

本文件初版曾对两只股票引用较旧的 2026Q1 数据：

- 中国电信：快照前 2026H1 已披露；
- 格力电器：2026H1 报告在 2026-08-26 晚间、早于本截图时间披露。

因此本历史案例使用快照时点已经公开的 H1 信息。该修订是 point-in-time 事实纠错，不是未来数据回填。

### 0.2 规则迁移不改写历史模型

十股 `model_long_book_weight` 保留为 2026-08-26 的模型基线，但当前执行解释必须遵循最新 Level-1：

- long-book 权重先换算成账户级权重；
- 同一股票/风险簇必须跨长期和短中期聚合；
- Expected IRR 按逐期现金流计算；
- 被动超限标记 `CAP_BREACH`；
- Paper/Live 使用当前 governance bundle。

这些是**当前执行解释**，不意味着历史模型当时已经拥有后来加入的字段。

## 1. 十只股票与历史价格基线

| 代码 | 股票 | 2026-08-26 快照价 | 角色 |
|---|---|---:|---|
| 600900 | 长江电力 | 28.24 | Core Dividend / 公用事业 |
| 600036 | 招商银行 | 39.80 | Core Dividend / 银行 |
| 600887 | 伊利股份 | 26.10 | Core Dividend / 消费 |
| 601857 | 中国石油 | 11.01 | Core Dividend / 能源周期 |
| 601728 | 中国电信 | 6.42 | Core Dividend / 通信运营 |
| 000651 | 格力电器 | 41.58 | Core Dividend / 家电 |
| 601088 | 中国神华 | 47.26 | Core Dividend / 煤炭能源 |
| 601138 | 工业富联 | 60.57 | Growth Satellite / AI基础设施 |
| 002475 | 立讯精密 | 57.11 | Growth Satellite / 消费电子+汽车+数据中心 |
| 603019 | 中科曙光 | 84.25 | Growth Satellite / 国产算力 |

价格只用于历史基线：

```text
baseline_price != planned_entry != simulated/live_fill
```

## 2. 结构判断

```text
7 只 Core Dividend
+ 3 只 Growth Satellite
```

主要经济驱动：水电、银行利率/信用、食品消费、家电、石油、煤炭、电信运营、AI服务器/算力、消费电子/汽车电子/数据中心、国产算力。

显著风险簇：

```text
能源商品：
中国石油 + 中国神华

AI / 科技 Capex：
工业富联 + 立讯精密 + 中科曙光
```

正式行业不同不代表经济风险独立。

## 3. 历史模型 long-book 权重

| 股票 | model_long_book_weight | 历史研究角色 |
|---|---:|---|
| 长江电力 | 12% | Core 一级 |
| 招商银行 | 12% | Core 一级 |
| 伊利股份 | 12% | Core 一级 |
| 中国石油 | 11% | Core 二级 / 周期 |
| 中国电信 | 10% | Core 二级 / WATCH |
| 格力电器 | 11% | Core 二级 / WATCH |
| 中国神华 | 12% | Core 二级 / 周期 |
| 工业富联 | 10% | Growth 主仓 |
| 立讯精密 | 7% | Growth 副仓 |
| 中科曙光 | 3% | Growth 高弹性小仓 |
| **合计** | **100%** | |

内部结构：

```text
Core Dividend = 80%
Growth Satellite = 20%
```

这是**长期已部署权益仓内部**权重，不是全账户权重。

### 3.1 当前执行时必须先换算分母

```text
model_total_account_weight
= model_long_book_weight × planned_long_exposure
```

再计算：

```text
planned_total_account_weight
= min(
    model_total_account_weight,
    account_single_stock_cap,
    remaining_account_cluster_capacity,
    valuation_quality_allowance
  )
```

不能直接做：

```text
min(model_long_book_weight, account_single_stock_cap)
```

因为两个百分比的分母不同。

### 3.2 跨策略重叠必须合并

这十股中至少有股票也曾进入短中期研究池，例如：

```text
工业富联 601138
立讯精密 002475
格力电器 000651
```

若未来同一股票同时在长期与短中期持仓：

```text
Account Symbol Exposure
= Long Sleeve Exposure + Short/Mid-term Sleeve Exposure
```

AI/科技 Capex 等风险簇同样跨策略合并。不能给同一股票两套独立集中度额度。

## 4. 单股历史市场验证

### 4.1 长江电力 — Core 一级

2025 年普通现金分红约 1.00 元/股；按 28.24 元快照价，历史股息率约 3.54%。2026Q1 收入和利润仍增长，经营现金流未出现明显结构性恶化。

```text
主要优势：大型水电、现金流可预见性、资产寿命
主要风险：来水、电价、Capex、并购/杠杆、估值
历史状态：Core 一级；真实买入仍需估值/IRR Gate
```

### 4.2 招商银行 — Core 一级

2025 全年现金分红约 2.016 元/股；按 39.80 元约 5.07%。2026Q1 资产质量总体稳定，净息差承压。

```text
优势：零售/财富管理、资产质量、资本能力
风险：NIM、宏观信用、地产/地方信用、监管资本
历史状态：Core 一级
```

### 4.3 伊利股份 — Core 一级

2025 中期+年度普通现金分红约 1.38 元/股；按 26.10 元约 5.29%。2026Q1 营收、归母、扣非增长，OCF改善。

```text
优势：品牌/渠道、现金流、消费分散
风险：需求、原奶周期、渠道库存、竞争
历史状态：Core 一级
```

### 4.4 中国石油 — Core 二级 / 周期

2025 全年普通现金分红约 0.47 元/股；按 11.01 元约 4.27%。2026Q1 在油价承压环境下仍有盈利韧性。

```text
核心要求：使用中周期油价/正常化盈利
风险：油价、天然气价格、Capex、政策
历史状态：保留，受能源风险簇限制
```

### 4.5 中国电信 — Core 二级 / WATCH

2025 普通现金分红约 0.272 元/股；按 6.42 元约 4.24%。截至快照时点 2026H1 已公开：

- 营业收入约2590.10亿元，同比约 -3.9%；
- 归母净利润约195.88亿元，同比约 -14.9%；
- 扣非归母净利润约174.90亿元，同比约 -19.5%。

```text
分红：仍具研究价值
问题：H1收入和利润承压
需验证：ARPU、云/算力利润质量、Capex、现金流
历史状态：WATCH / HOLD 候选；新买入重新评分和估值
```

### 4.6 格力电器 — Core 二级 / WATCH

2025 普通现金分红约3.00元/股；按41.58元历史股息率约7.21%。快照前已公开的2026H1：

- 营收约893.98亿元，同比 -8.15%；
- 归母净利润约132.78亿元，同比 -7.87%；
- 扣非归母净利润约127.07亿元，同比 -8.89%；
- OCF约188.09亿元，同比约 -33.6%。

```text
历史股息率：高
当前经营：H1走弱
风险：需求、渠道、增长、现金流、资本配置
历史状态：WATCH；高股息不构成自动 ADD
```

### 4.7 中国神华 — Core 二级 / 周期

2025 中期+年度分红约2.01元/股；按47.26元约4.25%。2026Q1利润同比承压，长期评估需使用中周期煤价和正常化盈利。

```text
优势：煤电运一体化
风险：煤价、长协机制、周期盈利回落
历史状态：保留，不因历史分红机械加仓
```

### 4.8 工业富联 — Growth 主仓

2026H1 收入、归母、扣非与 OCF 强劲增长，AI服务器/算力基础设施需求进入财报。

```text
产业空间：高
增长质量：三只 Growth 中历史快照最强
风险：AI Capex、客户集中、地缘/供应链、制造利润率、估值
历史状态：Growth 第一研究优先级
```

### 4.9 立讯精密 — Growth 副仓

2026H1 收入增长快，汽车电子、通信/数据中心扩张明显，但扣非增速低于收入，OCF需持续验证。

```text
优势：消费电子 + 汽车 + 数据中心多引擎
风险：大客户集中、利润率、消费电子周期、并购整合
历史状态：Growth 第二研究优先级
```

### 4.10 中科曙光 — Growth 高弹性小仓

2026H1 收入、归母、扣非较高增长，OCF同比改善，但快照估值在三只 Growth 中最高。

```text
业务/增长：通过历史研究
核心风险：估值
其他风险：订单周期、国产算力节奏、技术迭代
历史状态：Growth 小仓，要求更高安全边际
```

## 5. 历史排序

```text
Core 第一研究优先级：
长江电力 / 招商银行 / 伊利股份

Core 第二研究优先级：
中国石油 / 中国神华

重点 WATCH：
中国电信 / 格力电器

Growth：
工业富联 > 立讯精密 > 中科曙光
```

排序只描述 2026-08-26 快照。

## 6. 真实购入前必须重算

每只股票真实执行前重新获取：

- current price；
- 最新正式财报/分红/治理事件；
- 当前评分；
- Bear/Base/Bull 现金流；
- Expected IRR；
- Required Return grid；
- Bear/Base/Bull Max Buy Price；
- Stock Account Equity；
- 当前账户级单股/风险簇上限；
- 当前长期与短中期同股/同因子暴露；
- governance bundle version。

Expected IRR 正式定义：

```text
0 = -P0 + Σ[CF_t/(1+r)^t] + TV_T/(1+r)^T
```

不能把累计分红全部放到终点后仍称精确 IRR。

## 7. 建仓、补仓、止损、止盈

### 策略批次

当前执行从 Level 1A 读取：

```text
默认：40% / 30% / 30%
2批例外：60% / 40%
4批例外：30% / 25% / 25% / 20%
```

### ADD Gate

```text
Thesis Gate
Balance Gate
Valuation Gate
Portfolio Gate
```

后续批次必须有新的估值、价格或事实确认，不能因为下跌机械补仓。

### EXIT / TRIM

长期不使用统一 -5%/-8%/-10% 自动止损，也不按固定盈利百分比全部卖出。

主要依据：

```text
thesis
Expected IRR / valuation
account concentration
opportunity cost
governance / balance sheet
```

## 8. CAP_BREACH 处理

新订单的计划成交后暴露不得突破 Cap。

如果市场上涨造成账户级同股、风险簇或短中期暴露被动越界：

```text
state = CAP_BREACH
→ 禁止继续增加同方向风险
→ 进入现实可执行的再平衡评估
```

不把 ±5pp 漂移带当成主动超限许可，也不为了机械满足比例在异常价格下无条件市价卖出。

## 9. Paper / Forward-Test

必须分开：

```text
paper_capital_rmb = 股数、100股单位、费用、滑点、风险计算
reporting_nav     = 100.00起始标准化绩效指数
```

每个持仓至少记录：

```text
baseline_price
planned_entry
simulated_fill / live_fill
shares
average_cost
current_market_value
dividends_received
price_return
total_return
MFE / MAE
current_weight
model_long_book_weight
model_total_account_weight
account_symbol_exposure
account_cluster_exposure
score
expected_irr
valuation_state
thesis_state
action
```

组合记录 Total Return、Dividend Return、Max Drawdown、Core/Growth attribution、风险簇、Cash Drag、Turnover、Total Return Benchmark。

## 10. 后续状态更新

历史快照不使用未来结果静默改写。

未来追加：

```text
YYYY-MM-DD-portfolio-snapshot
YYYY-MM-DD-position-review
YYYY-MM-DD-dividend-event
YYYY-MM-DD-thesis-change
YYYY-MM-DD-trade-ledger
```

当发现“快照当时已经公开但记录错误”的事实，可增加 correction/errata 并保留原因。

## 11. 结论

这10只股票是一个**可验证长期研究组合**，不是永久“十只必买股”。

验证的是：

```text
Quality Core + Growth
+ Expected IRR / Valuation Gate
+ account-level aggregated risk
+ dynamic sizing
+ staged entry
+ dividend reinvestment
+ point-in-time review
```

能否在真实时间序列中形成可重复、风险可解释、可审计的长期投资流程。
