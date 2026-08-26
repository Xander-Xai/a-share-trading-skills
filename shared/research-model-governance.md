# Research & Model Governance v3

> 本文件定义跨长期与短中期策略的研究模型治理、Champion/Challenger 晋级、回测防偏差、Benchmark 与参数证据等级。
>
> 本文件不替代资本/风险规则，也不替代自动化执行规则。资金与仓位仍受 `capital-allocation-and-entry-policy.md` 约束；Paper/Live/自动报单仍受 `automation-execution-governance.md` 约束。

## 1. 核心原则

仓库不以“预测下一根 K 线”为目标，而以可重复的概率决策为目标：

```text
Research Edge
+ Controlled Risk
+ Executable Rules
+ Point-in-time Evidence
+ Cost-aware Validation
```

长期与短中期必须分开证明 Edge：

```text
长期：Quality × Valuation × Time
短中期：Expectation Change × Participation × Regime × Execution
全局：Risk Control
```

技术、资金、基本面、消息、估值都不是单独的充分买入条件。

## 2. 事实、研究推论与治理参数必须分层

任何规则必须标记为以下三类之一：

### A. Fact / Regulation

可被官方公告、财报、交易规则、行情或可复现数据直接验证。

### B. Research-supported Principle

外部研究支持方向，但不能直接证明某个具体阈值或权重是唯一最优。

例如：

- 过度交易可能拖累个人投资者表现；
- 分批投入会降低部分择时与行为压力，但现金等待有机会成本；
- 技术规则的有效性依赖市场、时期、参数与交易成本；
- 长期个股回报高度偏态，生存并不等于创造股东价值。

### C. Governance Parameter

仓库为了可执行性设定的内部参数，例如：

- 40/30/30；
- 50/50；
- 0.5% / 1% 单笔风险；
- 4% / 6% / 8% 回撤治理线；
- +1.5R / +2R；
- 3–5 个交易日 time review；
- 具体评分权重与晋级阈值。

Governance Parameter 必须通过 Forward/Live 数据持续校准，不得写成“学术证明最优”。

## 3. Champion / Challenger 制度

### 3.1 Champion

当前已冻结、正在使用或正在 Forward-Test 的生产研究模型。

短中期现阶段 Champion 仍为：

```text
Technical 30
Capital Participation 30
Fundamentals 25
Catalyst 15
```

除非完成 Challenger 晋级流程，否则不得静默替换。

### 3.2 Challenger

任何新评分、因果模型、止盈止损、参数或特征组合，先作为 Challenger：

```text
相同股票池
相同 as_of
相同可用信息
相同交易约束
相同成本假设
相同风险预算
```

并行产生影子决策，不影响 Champion 的真实执行。

### 3.3 禁止事项

- 不能因为回看历史觉得新模型“更合理”就晋级；
- 不能只展示新模型赢的样本；
- 不能用未来财报、后来退市结果或后见之明修正历史输入；
- 不能在 Challenger 表现差时临时修改样本区间；
- 不能因为单个热门行情阶段胜出就替换长期生产规则。

## 4. Challenger 晋级门槛

晋级必须同时比较收益、风险、成本和稳定性。

至少记录：

```text
Net Return
Excess Return vs Benchmark
Expectancy (R)
Profit Factor
Max Drawdown
Calmar
Win Rate
Average Win / Average Loss
Turnover
Tax + Commission + Slippage + Impact
MFE / MAE
Holding Days
Rule Violation Rate
Regime Breakdown
Sector / Factor Breakdown
```

### 4.1 Promotion Gate

Challenger 只有在以下条件均满足时才可进入人工评审：

1. 样本外 / Forward 结果为正，不只样本内好看；
2. 扣除税费、佣金、滑点和合理冲击成本后仍保留优势；
3. 最大回撤不因追求收益而显著恶化；
4. 收益不由极少数偶然交易贡献；
5. 至少覆盖趋势、震荡、风险偏好下降等不同 Regime；
6. 无明显数据泄漏、幸存者偏差或 look-ahead；
7. 规则可执行，且符合 A 股 T+1、涨跌停、停牌、流动性等约束；
8. 人工复核确认新增复杂度值得引入。

没有固定交易笔数可以保证晋级安全。样本量属于评审输入，不是自动晋级开关。

## 5. Causal Research Layer

研究阶段采用以下因果顺序，而不是简单把所有指标混成一个分数：

```text
1. Survival / Governance
2. Business Economics
3. Valuation / Expectations
4. Catalyst / Expectation Change
5. Market & Sector Regime
6. Participation / Relative Strength
7. Price Structure / Execution
8. Portfolio Risk
```

### 5.1 长期

长期买入理由必须主要来自：

```text
Survival
→ Governance
→ Earnings / FCF Quality
→ Balance Sheet
→ Per-share Value Creation
→ Valuation
→ Portfolio Fit
```

“不会退市”“股价离高点很远”“股息率高”都不能单独构成长期买入理由。

### 5.2 短中期

短中期重点是：

```text
Expectation Change
→ Market Participation
→ Regime Fit
→ Price Confirmation
→ Reward/Risk
```

技术面主要承担状态识别、确认和执行职责；它可以包含统计预测信息，但任何 Alpha 必须由样本外净收益验证。

## 6. Point-in-time 与幸存者偏差治理

所有回测、历史复盘和 Challenger 对比必须保存当时真实可用信息。

最低要求：

```text
历史上市/退市股票
历史 ST/*ST 状态
历史指数成分
财报实际发布日期
公告实际发布日期
当时可获得的估值与行情
复权/分红口径
停牌
涨跌停
T+1
交易费用与滑点
```

禁止：

```text
用 2026 年仍存续股票倒推 2015 年股票池
用后来发布的年报解释更早交易
用最终修订财务值替代当时市场可见数据而不留版本
```

任何无法重建 point-in-time 输入的历史结果必须标记：

```text
Biased / Non-promotable
```

可以用于研究灵感，不得用于模型晋级证据。

## 7. Benchmark Governance

### 7.1 长期

长期组合优先使用 Total Return Benchmark，而不是只使用价格指数。

例如沪深 300：

```text
Price Index: 000300
Total Return Index: H00300
```

长期比较至少同时保留：

- 对应宽基全收益指数；
- 必要时对应行业全收益指数；
- 组合自身含分红再投资的 Total Return。

### 7.2 短中期

短中期根据策略持有期使用价格/全收益差异影响较小但口径必须一致的 Benchmark，并增加：

- 相同持有期宽基；
- 行业/因子基准；
- cash/no-trade baseline。

## 8. Required Return 不允许写死 ERP

长期估值采用：

```text
Required Return
= Point-in-time Risk-free Rate
+ Configured Required Risk Premium
```

风险溢价是模型参数，不是所有 A 股统一常数。

默认必须进行敏感性分析，例如同时测试：

```text
Risk Premium = 4% / 6% / 8%
```

具体网格可更新，但必须标记为参数，不得宣称某个固定值为真理。

## 9. 长期 Expected IRR

优先用现金流/终值框架表达“现在价格是否值得买”：

```text
Expected IRR
= ((Estimated Terminal Value + Cumulative Cash Distributions) / Current Price)^(1/T) - 1
```

实际执行必须使用 Bear / Base / Bull 情景，并说明终值、分红、盈利和估值假设。

由 Required Return 反推 Max Buy Price：

```text
Max Buy Price
≈ (Estimated Terminal Value + Cumulative Cash Distributions)
  / (1 + Required Return)^T
```

这只是估值框架，不允许重复计算已经包含在 Terminal Value 中的现金流。

## 10. 技术与资金因子的治理

### 技术

不使用“技术数据都是过去式，因此没有预测力”的绝对表述。

正确表述：

```text
技术信号的有效性具有市场、时期、参数与成本依赖；
其是否具备可交易 Alpha 必须样本外验证。
```

### 资金

不把 vendor 的“主力净流入”当作真实机构净买入的事实。

资金确认至少区分：

```text
Participation — 成交额/换手/流动性
Positioning — 融资、机构披露、席位等可验证证据
Price Confirmation — 相对强度、突破承接、价格进展
```

若“资金流入标签”与价格/相对强度长期冲突，降低资金证据权重。

## 11. MFE / MAE 必须进入学习闭环

每笔短中期交易至少记录：

```text
MFE_R
MAE_R
realized_R
max_unrealized_profit_pct
max_unrealized_loss_pct
entry_timestamp
exit_timestamp
holding_days
exit_reason
```

用途：

- 判断止盈是否系统性过早；
- 判断止损是否过宽/过窄；
- 区分“选股错误”和“退出错误”；
- 校准 trailing、partial exit 和 time stop。

不得只看最终 PnL 调参。

## 12. 参数修改纪律

任何生产参数修改必须记录：

```text
old_value
new_value
hypothesis
supporting_evidence
forward_test_start
promotion_decision
approver
```

禁止自动化系统根据近期盈亏自行改写策略文件或提升风险。

## 13. 研究到自动化的完整路径

```text
Hypothesis
→ Historical Research
→ Point-in-time Audit
→ Challenger Shadow Score
→ Forward Paper
→ Manual Live Validation
→ Champion Promotion Review
→ Assisted/Semi-auto
→ Full Auto only if execution governance also passes
```

研究模型晋级与自动化执行晋级是两个独立 Gate：

```text
Good Model ≠ Safe Auto Execution
Safe Executor ≠ Positive Edge
```

两者都通过才允许提高自动化程度。
