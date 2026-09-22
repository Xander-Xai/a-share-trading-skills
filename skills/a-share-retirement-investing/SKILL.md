---
name: a-share-retirement-investing
description: 用于沪深A股长期养老型股票的筛选、估值、组合构建、分红复投和持仓复核。核心目标不是追求最高当期股息率，而是建立可持续、可增长、可穿越周期的股东现金流；允许配置少量科技成长卫星仓。所有时效性数据必须联网重新验证。
version: 2.2.2
---

# A股长期养老选股与持仓 Skill

## 0. 上位规则

执行前必须读取：

1. `../../shared/policy-precedence.md`
2. `../../shared/capital-eligibility-and-investor-risk-philosophy.md`
3. `../../shared/pre-trade-order-authorization-contract.md`
4. `../../shared/capital-allocation-and-entry-policy.md`
5. `../../shared/research-model-governance.md`
6. 涉及 Paper / Live / Broker / 自动化时读取 `../../shared/automation-execution-governance.md`

职责：

- 资本分母、账户级单股/风险簇上限、建仓批次、跨策略聚合：Level 1A；
- 研究证据、Expected IRR、Benchmark、模型晋级：Level 1C；
- Broker/虚拟子账/自动化：Level 1B。

本 Skill 可以更保守，不得放宽 shared 限制。

长期真实买入的 Level 0 规则：即使公司质量、估值和 Expected IRR 均通过，只要闲钱资格、近期现金需求、应急金、负债/杠杆或账户暴露信息缺失/失败，就只能输出 WATCH/READY，不得给出可执行股数。实际股数必须由 approved target position + strategic tranche + account caps + available idle cash 的最小约束反推。

## 1. 目标

把“养老股”定义为长期股权现金流系统，而不是高股息排行榜。

优化目标：

- 降低永久性本金损失；
- 分红主要来自可重复盈利和现金流；
- 每股价值和分红具有长期增长能力；
- 买入估值提供合理预期回报；
- 组合不过度集中同一公司、行业或经济因子；
- 长期仓内部保留适量成长引擎。

> 本 Skill 管理长期养老股票仓，不等于全部金融资产。现金、固收、保险、应急金等一级资产配置需单独处理。

## 2. 第一性原理

```text
长期股东回报
≈ 初始普通股息率
+ 每股正常化盈利/分红增长
+ 估值变化
- 税费
- 永久性资本损失
```

筛选顺序：

```text
生存能力
→ 盈利质量
→ 现金流/资本约束
→ 分红可持续性
→ 增长
→ Expected Return / 估值
→ 当前股息率
```

禁止从“谁股息率最高”或“离历史高点最远”倒推投资结论。

## 3. 强制实时数据协议

每次执行必须记录 `as_of` 并联网验证最新信息。

数据源优先级：

1. 上交所 / 深交所 / 巨潮资讯 / 公司正式年报、半年报、季度报告、分红公告；
2. 公司官网投资者关系与正式业绩材料；
3. 证监会、财政部、税务总局、中证指数等官方机构；
4. 可靠行情服务商，用于价格、市值、估值交叉验证；
5. 主流财经媒体，仅作背景补充。

每只股票至少检查：

- 最新股价、总市值、总股本；
- 最近5–10年普通现金分红，区分特别分红；
- 最近3–5年营收、归母、扣非、ROE/ROIC；
- 经营现金流、Capex、自由现金流或行业替代指标；
- 债务、利息负担或监管资本；
- 分红政策、回购、增发、重大资本开支；
- 当前估值与自身历史分位；
- 审计、处罚、治理、关联交易异常。

关键数据 `MISSING / CONFLICT` 时标记 `数据不足，暂不推荐`，不得 ADD。

## 4. 分母与长期仓内部结构

### 4.1 账户级分母

资本和集中度必须使用 shared 定义：

```text
Stock Account Equity
= 长期股票市值
+ 短中期股票市值
+ 股票账户待配置现金
```

账户级单股/风险簇上限用这个分母。

### 4.2 长期仓内部结构

长期**已部署权益仓**内部默认：

```text
Core Dividend：75%–85%
Growth Satellite：15%–25%
```

这是 long-book 内部权重，不是全账户权重。

若模型给出：

```text
model_long_book_weight
```

则先换算：

```text
model_total_account_weight
= model_long_book_weight × planned_long_exposure
```

再与账户级单股/风险簇 Cap 比较。

没有合格长期买点时允许保留待配置现金，不为维持 Core/Growth 百分比强制买入。

## 5. 硬性排除项

任一项成立，原则上排除或降级：

- 重大审计、会计、治理、资金占用问题未解决；
- 长期依赖新增负债、出售资产或一次性收益维持高额分红；
- 非金融企业正常化盈利和 FCF 长期无法覆盖分红；
- 金融企业分红明显侵蚀资本安全边际；
- 商业模式存在明确结构性衰退且缺乏可信新增长来源；
- 压力情景下债务/利息负担不可承受；
- 核心结论只能依赖传闻或无法验证的二手信息。

## 6. 核心现金流仓评分

| 维度 | 权重 |
|---|---:|
| 商业耐久性与护城河 | 20 |
| 分红持续性与增长 | 20 |
| 盈利与现金流质量 | 15 |
| 资产负债表与生存能力 | 15 |
| 治理与股东回报纪律 | 10 |
| 估值与安全边际 | 15 |
| 组合适配度 | 5 |

- 80–100：核心研究候选，估值合格后才允许建仓；
- 70–79：观察候选；
- <70：原则上不进入核心仓；
- 硬性排除优先于总分。

评分权重属于当前治理参数，不宣称数学最优；重大修改需走 Level 1C 模型治理。

## 7. 成长卫星评分

| 维度 | 权重 |
|---|---:|
| 长期产业空间 | 20 |
| 收入/利润增长质量 | 20 |
| 技术、产品与竞争壁垒 | 15 |
| 现金流与资产负债表 | 15 |
| 周期与客户集中风险 | 10 |
| 估值 | 15 |
| 组合适配度 | 5 |

成长股必须反推当前估值隐含的3–5年增长要求，并判断是否现实。

## 8. 行业适配

读取 `references/industry-checklists.md`。

尤其注意：

- 银行：资本充足率、不良率、拨备、净息差、ROE、分红率；
- 水电/公用事业：利用小时、Capex、债务、OCF、资产寿命、电价机制；
- 电信：OCF、Capex强度、FCF、ARPU、云/算力利润质量、分红政策；
- 煤炭/石油：使用中周期盈利；
- 消费：品牌、份额、现金转化、库存、定价能力、ROIC/ROE；
- 科技/AI：真实订单、收入、扣非、毛利率、研发、现金流、客户集中和 AI Capex 周期。

## 9. Expected IRR、估值与买入区间

读取 `references/expected-irr-total-return-benchmark.md`。

至少交叉使用2–3种行业适配方法，并建立 Bear / Base / Bull。

Expected IRR 必须按现金流时点计算：

```text
0
= -P0
+ Σ[CF_t/(1+r)^t]
+ TV_T/(1+r)^T
```

给定 Required Return `k`：

```text
Max Buy Price
= Σ[CF_t/(1+k)^t]
+ TV_T/(1+k)^T
```

不能把累计分红全部假设在终点后仍称“精确 IRR”。

输出：

```text
Bear IRR / Base IRR / Bull IRR
Required Return assumptions
Bear/Base/Bull Max Buy Price
Current Price
Margin of Safety
```

Required Risk Premium 是模型参数，做敏感性分析，不写死成 A 股统一真理。

## 10. 仓位、跨策略聚合与分散

账户级上限由 shared policy 动态读取，禁止永久写死旧 `25% / 30%-35%`。

如果同一股票同时出现在长期与短中期：

```text
Account Symbol Exposure
= Long Sleeve Exposure
+ Short/Mid-term Sleeve Exposure
```

如果多个持仓共享同一经济驱动：

```text
Account Cluster Exposure
= Long Cluster Exposure
+ Short/Mid-term Cluster Exposure
```

长期下单必须同时维护两个不同字段：

```text
current_long_symbol_exposure
= 长期 sleeve 自己已经持有的该股暴露
→ 用于计算 remaining_long_target_position

account_symbol_exposure
= long + short_mid 的账户级同股总暴露
→ 用于检查账户级 single-symbol Cap
```

不能用账户总暴露替代长期 sleeve 已持仓，也不能反过来只看长期 sleeve 而忽略账户级集中度。

若价格被动造成 `CAP_BREACH`，禁止继续增加同方向风险并进入再平衡评估；不为机械恢复比例在异常价格下无条件卖出。

## 11. 长期建仓

策略批次从 shared policy 读取：

```text
默认：40% / 30% / 30%
小资金/高确定性例外：60% / 40%
大金额/高不确定性例外：30% / 25% / 25% / 20%
```

一般约1–3个月完成。

每批都是新判断：

- 第1批：质量、估值、组合适配通过；
- 第2批：更高安全边际或新事实继续验证；
- 第3/4批：强确认，且账户级单股/风险簇仍合格。

股价超过 `Max Buy Price` 时取消后续批次，不为“买满计划”追高。

真实下单股数还必须满足 security-specific minimum buy quantity / increment；不能把所有A股都写死成100股整手。

## 12. 长期补仓

价格下跌只是复核触发，不是买入信号。

必须同时通过：

```text
Thesis Gate
Balance Gate
Valuation Gate
Portfolio Gate
```

并重新计算 Bear/Base/Bull Expected IRR。

- 下跌约15%–20%：强制重新研究；
- 下跌约25%–30%：深度 thesis review。

这些不是自动止损或自动补仓线。

## 13. 长期止损、止盈与状态

### EXIT

- 商业模式/护城河结构性破坏；
- 正常化盈利能力永久下降；
- 分红削减且背后是现金流/偿债/资本恶化；
- 重大审计、造假、治理问题；
- 债务/资本结构明显失控；
- 原始 thesis 被事实证伪。

### TRIM

- 账户级单股/风险簇超限；
- Expected IRR 明显低于当前 Required Return；
- 估值极端乐观；
- 存在质量相近、安全边际明显更高的替代品。

### HOLD

Thesis 成立、Expected Return 和账户级暴露合理。

### ADD

Thesis 成立、Expected IRR/安全边际足够、四个 Gate 通过。

### WATCH

质量尚可，但价格、数据、估值或基本面需确认。

## 14. 分红复投

分红进入组合级现金池，不机械买回原股票。优先投向：

```text
仍通过硬性筛选
+ 评分高
+ Expected IRR / 安全边际更高
+ 组合适配度更好
```

没有合格标的时允许继续持有现金。

## 15. Benchmark 与复核节奏

长期绩效优先使用 Total Return Benchmark，避免组合含分红而 Benchmark 只看价格。

例如沪深300：价格指数 `000300`，全收益指数 `H00300`。使用时仍应重新核验当前指数口径。

复核：

- 季度：轻复核经营、现金流/资本、负债、分红政策、关键KPI；
- 年报：完整重做评分、正常化盈利、压力测试、IRR估值和集中度；
- 重大事件：立即复核。

## 16. 对抗审查

最终推荐前至少回答：

- 高股息是否来自基本面恶化？
- 当前是否处于周期盈利高点？
- 是否存在举债分红？
- 低PE/PB是否是价值陷阱？
- 组合是否表面分散、实际同因子？
- 长期与短中期是否持有同一股票/因子而未合并风险？
- 好公司是否已透支未来增长？
- Expected IRR 是否按现金流时点计算？
- 哪些数字是事实、研究推论、治理参数或模型估计？
- 最强 Bear Case 是什么？
- 如果今天没有持仓，是否仍愿以当前价格买入？
- 是否为了达到目标比例而忽略现金合法状态？

## 17. 输出合同

每只股票至少输出：

- 股票/代码；
- 角色 Core / Growth；
- 评分及关键分项；
- 当前价格/市值与 `as_of`；
- 投资逻辑；
- 普通股息率与分红覆盖；
- 5–10年分红趋势；
- 资产负债/资本质量；
- Bear/Base/Bull IRR 与 Required Return；
- Max Buy Price；
- ADD/HOLD/WATCH/TRIM/EXIT；
- `model_long_book_weight`；
- `model_total_account_weight`；
- 账户级同股/风险簇当前暴露与上限；
- Bear Case；
- 失效条件；
- 官方证据。

组合层面输出：

- Stock Account Equity；
- Long strategic baseline / Actual long exposure / pending cash；
- 长期已部署权益仓内部 Core/Growth；
- 账户级跨策略单股与风险簇暴露；
- 组合 Total Return / Benchmark Total Return；
- 未来12个月重点事件；
- 与上一轮结论 diff。

## 18. 历史示例与种子池

- `references/seed-watchlist-2026-08-26.md`：早期方法论种子快照；
- `examples/ten-stock-retirement-portfolio-2026-08-26.md`：十股 Forward-Test 模型组合；
- `examples/paper-live-automation-roadmap.md`：Paper→Live/Automation 路线。

它们均为 Level 4，不能覆盖当前 shared policy / Skill / 最新研究。

## 19. 参考材料

- `../../shared/policy-precedence.md`
- `../../shared/capital-allocation-and-entry-policy.md`
- `../../shared/research-model-governance.md`
- `../../shared/automation-execution-governance.md`
- `../../shared/research-validation-2026-08-26.md`
- `references/methodology.md`
- `references/industry-checklists.md`
- `references/expected-irr-total-return-benchmark.md`
- `references/execution-template.md`
- `references/seed-watchlist-2026-08-26.md`
- `examples/ten-stock-retirement-portfolio-2026-08-26.md`
- `examples/paper-live-automation-roadmap.md`
