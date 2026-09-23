# A股长期 / 短中期资金分配、建仓与风险管理策略 v2.6

> 本文件是仓库级最高**资本与风险**规则。执行前同时读取 `policy-precedence.md`；涉及 Paper/Live/自动化执行时同时读取 `automation-execution-governance.md`。
>
> 对**真实资金**计算任何新增股票仓位前，必须先读取 `capital-eligibility-and-investor-risk-philosophy.md`，完成 Capital Eligibility / Cash Need / Emergency Reserve / Debt-Leverage Gate。资金资格失败时，后文任何 Size/Risk/Edge Cap 都不能授权新风险。
>
> 在输出任何真实资金 `ENTRY` / `ADD` 的具体股数或金额前，必须再通过 `pre-trade-order-authorization-contract.md`。个人资金、账户暴露、风险预算或触发条件缺失时，只允许 WATCH/READY，不允许猜测股数。
>
> Paper 模式使用隔离的 `paper_capital_rmb`、模拟持仓和相同的 Level 1A 风险数学；不得要求或伪造个人应急金/近期现金需求答案，也不得把 Paper 授权冒充真实资金授权。
>
> 本文讨论的是**专门可用于股票投资、能够承受波动的股票资金**。若 10 万 / 100 万 / 1000 万代表全部金融资产，应先完成现金、固收、保险/保障等一级资产配置，再把分给 A 股股票系统的资金带入本规则。

## 0. 统一口径与分母

为了避免“长期模型权重、账户级上限、短中期策略 NAV”使用不同分母而互相误读，统一定义：

```text
Stock Account Equity
= 长期股票市值
+ 短中期股票市值
+ 股票账户待配置现金
```

### 0.1 账户级比例

以下比例统一以 `Stock Account Equity` 为分母：

- 长期 / 短中期 Size Cap；
- `Final Short Cap`；
- 长期单只股票账户级总暴露上限；
- 账户级单一风险簇总暴露上限；
- 同一股票跨长期/短中期的合计暴露。

### 0.2 长期仓内部比例

以下比例只在**长期已部署权益仓内部**计算：

- Core Dividend / Growth Satellite；
- synthetic long-book fixture 中的 `model_long_book_weight`。

因此：

```text
model_total_account_weight
= model_long_book_weight × planned_long_exposure
```

不能直接拿“长期仓内部 12%”与“账户级单股上限 10%–12%”做 `min()`，必须先统一分母。

### 0.3 短中期风险分母

短中期 `Operating Target / Hard Ceiling` 的单笔风险和 Heat 使用**当前短中期策略 NAV**作为风险计算分母；短中期策略 NAV 的增加不得通过长期仓自动补血完成。

### 0.4 Size Tier 的更新频率

Size Tier 不因日内小幅价格波动频繁切换。默认在以下时点重新判定：

- 月度/季度组合复核；
- 大额新增或提取资金后；
- 账户权益发生足以跨越资金档位的持续性变化时。

## 1. 第一性原理

资金规模变大不会让同一个百分比波动自动变大，但会改变：

1. 绝对损失金额；
2. 资本保全的重要性；
3. 可实现的分散度；
4. 流动性、滑点和冲击成本；
5. 主动交易 Alpha 是否有足够容量支撑更大资金。

因此：

```text
长期养老仓 = 财富复利与资本保全主引擎
短中期仓   = 有限风险预算下争取 Alpha 的卫星仓
现金待配置 = 当长期/短中期都没有合格机会时的合法状态
```

短中期仓必须用真实业绩“挣仓位”，不能随本金同比例无限放大。

## 2. Size Cap：资本规模对应的战略基线

以下仅针对**股票专用资金**：

| Stock Account Equity | 长期战略基线 | 短中期 Size Cap |
|---:|---:|---:|
| ≤5 万元 | 70% | 30% |
| 5–30 万元 | 75% | 25% |
| 30–200 万元 | 80% | 20% |
| 200–1000 万元 | 85% | 15% |
| ≥1000 万元 | 85%–90% | 10%–15% |

示例：

```text
10 万股票资金：  长期战略基线 7.5 万 / 短中期 Size Cap 2.5 万
100 万股票资金： 长期战略基线 80 万 / 短中期 Size Cap 20 万
1000 万股票资金：长期战略基线 850–900 万 / 短中期 Size Cap 100–150 万
```

### 重要语义

这张表不是“必须把股票资金 100% 当天投满”的指令。

账户允许存在：

```text
Stock Account Equity
= 已部署长期仓
+ 已部署短中期仓
+ 待配置现金
```

如果短中期因 Risk Cap / Edge Cap 被压低，差额**不自动强制转成长仓**；只有长期候选也通过质量、估值和组合 Gate 时才部署，否则保留现金。

这些比例是治理基线，不是学术研究证明的唯一最优比例。

## 3. 最终短中期上限：三重 Cap

```text
Final Short Cap
= min(
    Size Cap,
    Risk Cap,
    Edge Cap
  )
```

`Final Short Cap` 是**上限**，不是必须使用的目标仓位。

任何新订单在计划成交后必须满足：

```text
Planned Post-Trade Short Exposure <= Final Short Cap
```

### 市场价格导致的被动超限

市场上涨可能在没有新下单的情况下让实际短中期暴露暂时超过 Cap。因此不能把：

```text
Actual Short Exposure <= Final Short Cap
```

理解成“价格波动永远不可能造成瞬时超限”。

一旦发生被动超限：

```text
state = CAP_BREACH
→ 禁止继续增加该短中期暴露
→ 进入再平衡 / 利润回流评估
→ 在现实可执行窗口恢复到 Cap 内
```

除非 Hard Ceiling、流动性或其他紧急风控要求立即处理，否则不为了机械满足百分比在异常价格下无条件市价卖出。

### 3.1 Size Cap

使用第 2 节。

### 3.2 Risk Cap

若：

```text
允许短中期系统对总股票账户造成的最大压力损失 = B
短中期策略压力情景最大回撤 = D
```

则：

```text
Risk Cap <= B / D
```

例：只允许总股票账户被短中期拖累 5%，压力回撤假设 25%，则 Risk Cap ≤20%。

### 3.3 Edge Cap

提高主动仓位前至少检查：

- 有足够真实交易样本；
- 覆盖不同市场环境；
- 扣除费用、税费、滑点后仍有正期望；
- 最大回撤受控；
- 收益不是由极少数偶然交易贡献；
- 规则执行稳定。

没有充分验证时使用更保守 Edge Cap，不因为“最近行情好”提高风险。

## 4. 账户级长期单股与风险簇上限

以下上限以 `Stock Account Equity` 为分母，并按**账户总暴露**计算，不因策略标签拆开：

| Stock Account Equity | 长期仓参考持股数 | 账户级单只股票总暴露参考上限 | 账户级单一风险簇总暴露参考上限 |
|---:|---:|---:|---:|
| ≤5 万 | 2–4只或ETF辅助 | 约30% | 约40% |
| 5–30 万 | 5–8只 | 20% | 30%–35% |
| 30–200 万 | 8–12只 | 15% | 25%–30% |
| ≥200 万 | 10–15只 | 10%–12% | 20%–25% |

这些是治理上限，不要求为了凑数量买低质量公司。没有合格标的时允许保留现金或使用高度分散 ETF 过渡。

风险簇按经济驱动而非仅按行业标签划分。

### 4.1 同一股票跨策略合并

如果同一股票同时出现在长期和短中期系统：

```text
Account Symbol Exposure
= Long Sleeve Exposure
+ Short/Mid-term Sleeve Exposure
```

账户级单股上限检查使用合计值，不能因为“一个叫长期、一个叫短中期”而各算一次上限。

### 4.2 同一风险簇跨策略合并

账户级风险簇暴露同样聚合长期与短中期：

```text
Account Cluster Exposure
= Long Cluster Exposure
+ Short/Mid-term Cluster Exposure
```

短中期内部因子上限与账户级风险簇上限必须**同时**通过。

## 5. 长期建仓：默认 3 批

### 标准模式

```text
40% / 30% / 30%
```

通常建议约 1–3 个月完成。

### 2 批例外

```text
60% / 40%
```

适用于：

- 小资金受最小交易单位限制；
- 公司高度成熟、流动性强；
- 估值安全边际明显；
- 目标单股仓位较小。

### 4 批例外

```text
30% / 25% / 25% / 20%
```

适用于：

- 单股目标金额较大；
- 信息/事件不确定性较高；
- 流动性一般；
- 未来数周仍有重要财报/经营信息释放。

不因账户从 100 万变 1000 万就机械增加到 5–10 个**策略批次**。

### 每一批触发逻辑

- 第1批：质量、估值、组合适配度通过；
- 第2批：价格更有安全边际，或新事实继续验证；
- 第3/4批：强确认，且账户级单股/风险簇仍合格。

若价格超过 `Max Buy Price`，后续批次取消。

## 6. 长期补仓：四个 Gate

长期补仓必须同时通过：

```text
Thesis Gate      投资逻辑仍成立
Balance Gate     现金流/债务/监管资本未恶化
Valuation Gate   估值确实更有安全边际
Portfolio Gate   账户级单股和风险簇仓位仍合格
```

价格下跌不是自动买入信号。

内部复核触发：

```text
下跌约15%–20% → 强制重新研究
下跌约25%–30% → 深度 thesis review
```

这些不是机械补仓或止损线。

## 7. 长期止损与止盈

### 长期止损

默认不使用统一 5%/8%/10% 机械价格止损。主要 EXIT 触发：

- 商业模式或护城河结构性破坏；
- 正常化盈利能力永久下降；
- 分红削减背后是现金流/偿债/资本恶化；
- 重大审计、财务造假、治理问题；
- 债务/资本结构明显失控；
- 原始投资逻辑被事实证伪。

### 长期止盈

不使用“涨20%全卖”。TRIM 主要由：

```text
估值过高
+ 账户级单股/风险簇超配
+ 机会成本
```

触发。

## 8. 再平衡：Cap 优先于漂移区间

复核：

- 季度轻复核；
- 年报完整重估；
- 重大事件立即复核。

资金部署优先顺序：

```text
新增资金
→ 分红现金
→ 短中期已实现利润
→ 最后才考虑卖长期优质持仓做再平衡
```

### 漂移区间的正确语义

`±5 个百分点`只能作为**不必频繁微调的参考带**，绝不能授权新的订单主动突破任何 Cap。

若市场价格被动造成超限：

- 标记 `CAP_BREACH`；
- 禁止新增同方向风险；
- 进入现实可执行的再平衡流程；
- 不用“±5pp”给超限找理由。

短中期低于上限几百分点，可以不立即补足；因亏损低于基线时，不从长期仓自动补血。

## 9. 短中期风险：Operating Target 与 Hard Ceiling

### Operating Target

```text
单笔计划风险：0.5% × 当前短中期策略 NAV
全部未平仓初始风险：≤2%
单一行业/因子初始风险：≤1%
```

### Hard Ceiling

```text
单笔计划风险：≤1%
全部未平仓初始风险：≤3%
```

只有 Edge 已充分验证、市场环境友好、setup 高质量时，单笔风险才允许从 0.5% 向 1% 靠近。

默认不使用融资杠杆。

### 仓位公式

```text
单笔目标持仓金额
≈ 单笔允许亏损金额 / 初始止损距离
```

例：短中期策略 NAV 20 万，Operating Target 单笔风险 0.5%=1000 元，止损距离5%，理论目标金额约2万元，再叠加单股/因子/账户级暴露上限。

## 10. 短中期组合结构

正常情况下：

- 单只短中期股票资本暴露通常不超过短中期策略 NAV 的约20%；
- 同一高度相关板块/因子资本暴露通常不超过短中期策略 NAV 的约40%；
- 同时持仓通常3–5只；
- 同行业通常不超过2只；
- 同主导经济因子通常不超过2只。

同时必须满足：

```text
短中期内部资本暴露上限
AND
短中期风险 Heat 上限
AND
账户级单股/风险簇上限
AND
Final Short Cap
```

全部通过才允许交易。

## 11. 短中期建仓：默认 2 批

### 默认

```text
50% Setup Entry
50% Confirmation Entry
```

第二批只有在走势/事实证明第一笔越来越正确时才能加入，例如：

- 突破后站稳；
- 回踩关键位重新走强；
- 相对强度改善；
- 成交量/板块/催化继续确认；
- 新信息强化原 thesis。

### 三级确认例外

```text
50% / 30% / 20%
```

只用于策略确实有三层确认的情况。

### 禁止

```text
第一笔亏损
→ 为摊低成本买第二/第三笔
```

旧的“资金越大就机械 3/4/4 批”规则退役。

## 12. 策略批次 ≠ 执行拆单

- **策略批次**：新的投资判断得到确认；
- **执行拆单**：为了流动性、滑点、冲击成本把同一策略批次拆成多个订单。

百万、千万级账户可以把一个策略批次拆成多个执行订单，但不改变策略批次数。

## 13. 短中期止损

```text
先确定交易逻辑失效点
→ 得到止损距离
→ 用风险预算反推可买金额
→ Reward/Risk 不合理则跳过
```

硬规则：

- 入场前必须有止损/失效条件；
- 不把止损向更亏损方向放宽；
- 跳空/涨跌停可能使实际成交价劣于计划价；
- 逻辑失效后不把短中期仓改名为长期仓。

## 14. 短中期止盈

一级规则：

```text
R 倍数
+ 技术结构
+ 原始 setup 目标
```

优先选择现实 `Reward/Risk >= 2` 的交易。

持仓后：

- 约 +1.5R～+2R：可考虑兑现约1/3～1/2；
- 剩余仓位使用趋势结构或 trailing 管理；
- 不把保护线向下放宽。

历史百分比区间仅为辅助观察：

```text
传统/周期：约 +3%～+5%
成长/科技：约 +6%～+10%
```

若与 R/结构冲突，**R/结构优先**。

## 15. 时间止损

若计划为5–15个交易日：

- 到期仍未出现预期走势：重新评估；
- 3–5个交易日内明显不工作且相对强度/成交量恶化：可提前降仓或退出；
- 不因“还没碰到价格止损”无限延期。

## 16. 短中期账户熔断

从短中期策略账户权益高点计算：

```text
回撤4%
→ 降低总暴露
→ 新单风险回到 Operating Target 下端

回撤6%
→ 停止新开仓
→ 只管理已有仓位
→ 复盘市场环境和流程

回撤8%
→ 暂停短中期策略
→ 不从长期仓抽钱补血
→ 正式复核后再恢复
```

这些是内部治理参数，不是学术唯一最优阈值。

## 17. 长期 / 短中期资金纪律

### 短中期赚钱

若短中期策略 NAV 或股票暴露因盈利被动超过 `Final Short Cap`：

```text
标记 CAP_BREACH
→ 禁止继续增加短中期风险
→ 将可实现的超额利润 / 再平衡资金优先转入长期待配置池
→ 长期只有在自身 Gate 通过时才继续买入
→ 否则保留现金
```

### 短中期亏损

短中期策略 NAV 因亏损低于基线：

```text
禁止自动从长期仓提款补回
```

先复核策略。确认 Edge 仍有效后，才允许使用未来新增资金逐步补足，而且仍不得超过 `Final Short Cap`。

## 18. 大资金流动性

百万、千万级账户必须额外检查：

- 单股日均成交额；
- 买卖价差；
- 计划订单占成交额比例；
- 小市值、低流动性、涨跌停风险；
- 限价与执行拆单需求。

不能只按账户百分比线性放大订单。

## 19. 总表

| 模块 | 长期养老 | 短中期 |
|---|---|---|
| 角色 | 财富复利 / 资本保全主引擎 | Alpha 卫星仓 |
| 顶层占比 | 战略基线 + 合格机会部署，可留现金 | `Final Short Cap=min(Size,Risk,Edge)` |
| 默认建仓 | 3批40/30/30 | 2批50/50 |
| 例外建仓 | 2批60/40或4批30/25/25/20 | 三级确认50/30/20 |
| 补仓 | 四 Gate 同时通过 | 禁止向亏损仓位摊低成本 |
| 止损 | 投资逻辑止损 | 价格/逻辑/时间止损 |
| 止盈 | 估值/集中度/机会成本 | R倍数+结构优先 |
| 集中度 | 账户级单股/风险簇动态上限 | 短中期内部上限 + 账户级聚合上限 |
| 风险预算 | 无统一机械价格止损 | Operating 0.5%/2%，Hard 1%/3% |
| 熔断 | 事件驱动深度复核 | 4%/6%/8% |
| 利润处理 | 分红组合级再配置 | 超额利润回到长期待配置池/现金 |

## 20. 研究证据基线

### 资产配置与分散

- Investor.gov — Asset Allocation and Diversification
  https://www.investor.gov/introduction-investing/getting-started/asset-allocation
- Investor.gov — Beginners’ Guide to Asset Allocation, Diversification, and Rebalancing
  https://www.investor.gov/additional-resources/general-resources/publications-research/info-sheets/beginners-guide-asset

### 分批投入

- Vanguard — Cost averaging: Invest now or temporarily hold your cash?
  https://corporate.vanguard.com/content/dam/corp/research/pdf/cost_averaging_invest_now_or_temporarily_hold_your_cash.pdf

### 主动交易与过度交易

- Barber & Odean — Trading Is Hazardous to Your Wealth
- 深圳证券交易所 — 从容投资，避免过度交易
  https://investor.szse.cn/institute/products/t20220826_595591.html

### 交易风险与退出

- Charles Schwab — Elements of a Smart Trade Plan
  https://www.schwab.com/learn/story/5-elements-smart-trade-plan
- Fidelity — Position Sizing / Scaling In & Out
  https://www.fidelity.com/bin-public/060_www_fidelity_com/documents/learning-center/trading-volatility-slides.pdf
- Fidelity — Exit Strategies
  https://www.fidelity.com/learning-center/trading-investing/trading/exit-strategies
- Investor.gov — Stop, Stop-Limit, and Trailing Stop Orders
  https://www.investor.gov/introduction-investing/general-resources/news-alerts/alerts-bulletins/investor-bulletins-15

### A股交易规则

- 上海证券交易所《交易规则（2026年修订）》
  https://www.sse.com.cn/lawandrules/sselawsrules2025/stocks/exchange/c/c_20260424_10816482.shtml

## 21. 最终原则

```text
资金越大，不是交易次数越多、单笔越大；
而是越应该提高资本保全、分散和流动性约束。

所有策略标签最终都落到同一个账户风险：
同股要合并、同因子要合并、Cap 要用同一分母。

Cap 是新风险的上限；
被动超限要进入 CAP_BREACH 处理，不能用漂移带合理化继续加仓。

没机会时现金是合法仓位。
长期下跌先研究，不机械补；
短中期亏损不补仓，失效就退出；
短中期赚到的钱，逐步转化为长期资产或待配置现金。
```
