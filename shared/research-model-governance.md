# Research & Model Governance v3.2

> 本文件定义跨长期与短中期策略的研究模型治理、Champion/Challenger 晋级、回测防偏差、Benchmark 与参数证据等级。
>
> 本文件不替代资本/风险规则，也不替代自动化执行规则。资金与仓位受 `capital-allocation-and-entry-policy.md` 约束；Paper/Live/自动报单受 `automation-execution-governance.md` 约束。
>
> 长期与短中期的机器边界读取 `strategy-boundary-contract.md`；PIT 数据元数据读取 `canonical-pit-data-contract.md`。

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

机器可执行 artifact 必须声明：

```text
strategy_id
sleeve = long | short_mid
```

共享事实不等于共享决策状态。短中期 ERG/Reaction/5–20日 Forward/R-based tactical rules 不得自动覆盖长期 Thesis/IRR/估值决策；长期估值结果也不得自动成为短中期入场信号。

## 2. 事实、研究推论与治理参数必须分层

### A. Fact / Regulation

可被官方公告、财报、交易规则、行情或可复现数据直接验证。

### B. Research-supported Principle

外部研究支持方向，但不能直接证明某个具体阈值或权重是唯一最优。

例如：

- 过度交易可能拖累个人投资者表现；
- 分批投入会降低部分择时与行为压力，但现金等待有机会成本；
- 技术规则有效性依赖市场、时期、参数与交易成本；
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

当前已冻结、正在使用或 Forward-Test 的生产研究模型。

短中期现阶段 Champion：

```text
Technical 30
Capital Participation 30
Fundamentals 25
Catalyst 15
```

除非完成 Challenger 晋级流程，否则不得静默替换。

长期模型由 `a-share-retirement-investing` Skill 的质量、估值、Expected IRR 与 Portfolio Fit 体系独立管理，不因短中期 Champion/ERG 晋级而改变。

### 3.2 Challenger

任何新评分、因果模型、止盈止损、参数或特征组合，先作为 Challenger：

```text
相同股票池 / 可比股票池规则
相同 as_of
相同可用信息
相同交易约束
相同成本假设
相同风险预算
同一 sleeve 内可比
```

并行产生影子决策，不影响当前生产模型的真实执行。

禁止把 Long 与 Short/Mid 当作彼此的 Champion/Challenger，因为两者目标函数、时间尺度和主要评价指标不同。

### 3.3 禁止事项

- 不能因为回看历史觉得新模型“更合理”就晋级；
- 不能只展示新模型赢的样本；
- 不能用未来财报、后来退市结果或后见之明修正历史输入；
- 不能在 Challenger 表现差时临时修改样本区间；
- 不能因为单个热门行情阶段胜出就替换长期生产规则；
- 不能用短中期 R 倍数/5–20日收益要求长期模型通过；
- 不能用长期 Expected IRR 直接为短中期 Entry 提供权限。

## 4. Challenger 晋级门槛：Common + Sleeve-specific

过去统一使用 `Expectancy(R) / Profit Factor / MFE/MAE` 等指标容易把短中期交易语言强加到长期系统。v3.2 起正式拆分。

### 4.1 Common metrics

两类策略都至少记录适用的公共质量指标：

```text
Net / Total Return as appropriate
Excess Return vs correct Benchmark
Max Drawdown
Turnover
Tax + Commission + Slippage + Impact where applicable
Data Coverage / Missing Rate
Rule Violation Rate
Point-in-time Audit Status
Source / Revision Provenance
Sector / Factor Concentration
Complexity / Maintenance Cost
Reproducibility Status
```

公共指标只解决“研究是否可信/执行是否稳健”，不强迫两个 sleeve 使用同一种 Alpha 定义。

### 4.2 Short/Mid promotion metrics

短中期重点评价：

```text
Expectancy (R)
Profit Factor
Win Rate
Average Win / Average Loss
MFE / MAE
Holding Days
Regime Breakdown
Event-family Breakdown
False Positive / False Negative
No-trade Opportunity Cost
Median / P90 Blocked MFE
Confirmation Delay Cost
Cost Drag
Gap / Tail-loss diagnostics
```

短中期 promotion 必须围绕其实际 5–60 交易日战术目标和当前 Skill/experiment contract 评价。

### 4.3 Long-term promotion metrics

长期重点评价：

```text
Total Return
Excess Total Return
Dividend Return
Dividend Growth / Coverage
Expected IRR Calibration Error
Bear/Base/Bull Forecast Error
Normalized Earnings / FCF Forecast Error
Max Drawdown
Permanent Impairment Cases
Valuation Error
Thesis Failure Rate
Cash Drag
Turnover
Capital-allocation Contribution
Benchmark Total Return
```

长期不要求通过以下短中期指标才能晋级：

```text
planned_RR
5/10/20-day forward return
short tactical Profit Factor
MFE/MAE as primary promotion gate
short tactical time stop
ERG reaction-window success
```

这些数据可以作为诊断信息，但不能成为长期模型主要裁决标准。

### 4.4 Promotion Gate — common requirements

任何 Challenger 进入人工评审至少同时满足：

1. 主要结论来自样本外 / Forward 或其他未被反复调参污染的证据，而不只样本内好看；
2. 使用与策略相匹配的成本、税费、Benchmark 和现金口径；
3. 风险不能因追求收益而无披露地显著恶化；
4. 结果不能由极少数偶然样本主导而不披露；
5. 无明显数据泄漏、幸存者偏差或 look-ahead；
6. 规则可执行且符合 A 股约束；
7. 人工复核确认新增复杂度值得引入；
8. 只在本 sleeve 内完成模型 Promotion，不跨 sleeve 自动传播。

### 4.5 Sleeve-specific Promotion Gate

短中期：

- 尽可能覆盖趋势、震荡、风险偏好下降等不同 Regime；
- 扣除成本后仍有正的战术期望或明确风险改进；
- 必须披露错过赢家成本和确认延迟成本；
- ERG/事件型模块需执行相应 Ablation/Placebo/Forward 协议。

长期：

- 使用 Total Return 口径与长期适配 Benchmark；
- Expected IRR / 估值假设必须可回溯并进行情景/敏感性分析；
- 需要跨财报、分红和经营变化周期持续验证；
- 重点检查永久性资本损失、估值错误和 thesis 失效，而不是追求短期高胜率。

没有固定交易笔数或持有年份可以自动保证晋级安全。样本量/时间跨度属于评审输入，不是自动开关。

## 5. Causal Research Layer

研究阶段采用因果顺序，而不是简单把所有指标混成一个分数：

### 长期

```text
Survival
→ Governance
→ Earnings / FCF Quality
→ Balance Sheet
→ Per-share Value Creation
→ Dividend Sustainability where relevant
→ Valuation / Expected IRR
→ Portfolio Fit
```

“不会退市”“股价离高点很远”“股息率高”都不能单独构成长期买入理由。

### 短中期

```text
Eligibility
→ Expectation Change
→ Materiality
→ Prepricing
→ Market Reaction / Participation
→ Regime Fit
→ Price Confirmation / Execution
→ Tactical Risk
```

技术面主要承担状态识别、确认和执行职责；任何可交易 Alpha 必须由样本外净收益或明确风险改进验证。

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

机器数据逐步迁移到 `canonical-pit-data-contract.md`，至少区分：

```text
effective_at
published_at
available_at
ingested_at
source / source_tier / source_snapshot_id
revision_id
permitted_use
strategy_visibility
```

禁止：

```text
用 2026 年仍存续股票倒推 2015 年股票池
用后来发布的年报解释更早交易
用最终修订财务值替代当时市场可见数据而不留版本
```

无法重建 point-in-time 输入的历史结果标记：

```text
Biased / Non-promotable
```

可用于研究灵感，不得用于模型晋级证据。

## 7. Benchmark Governance

### 长期

长期组合优先使用 Total Return Benchmark，而不是只使用价格指数。

例如沪深 300：

```text
Price Index: 000300
Total Return Index: H00300
```

至少保留：

- 对应宽基全收益指数；
- 必要时对应行业全收益指数；
- 组合自身含分红再投资的 Total Return。

### 短中期

根据策略持有期保持收益口径一致，并增加：

- 相同持有期宽基；
- 行业/因子基准；
- cash/no-trade baseline；
- ERG 事件研究使用事前冻结的 Benchmark / Reaction Window Contract。

## 8. Required Return 不允许写死 ERP

长期估值采用：

```text
Required Return
= Point-in-time Risk-free Rate
+ Configured Required Risk Premium
```

风险溢价是模型参数，不是所有 A 股统一常数。

默认必须做敏感性分析，例如：

```text
Risk Premium = 4% / 6% / 8%
```

具体网格可更新，但必须标记为参数。

## 9. 长期 Expected IRR：必须按现金流时点计算

### 9.1 正式定义

若买入价格为 `P0`，第 `t` 年预计收到股东现金分配 `CF_t`，第 `T` 年还有终值 `TV_T`，Expected IRR `r` 应满足：

```text
0
= -P0
+ CF_1/(1+r)^1
+ CF_2/(1+r)^2
+ ...
+ (CF_T + TV_T)/(1+r)^T
```

`r` 是使该 NPV 为 0 的内部收益率。

### 9.2 Max Buy Price

给定 Required Return `k`，最高可接受买价应按各现金流真实时点折现：

```text
Max Buy Price
= Σ[CF_t / (1+k)^t]
+ TV_T / (1+k)^T
```

### 9.3 终值合并近似只能作 sanity check

下面这种写法：

```text
((TV_T + Cumulative Cash Distributions) / P0)^(1/T) - 1
```

等价于假设所有中间分红都在终点才收到，只能在粗略 sanity check 中使用，**不得标记为精确 IRR**。

若分红金额显著或持有期较长，应使用逐期现金流 IRR/XIRR。

### 9.4 避免双重计算

- 若终值模型已经把 retained cash / ex-dividend 处理在每股价值中，不重复把同一现金加一次；
- 回购反映为股本/每股价值变化，不简单当成额外现金分红；
- 银行、保险、周期股使用行业适配终值方法。

实际执行使用 Bear / Base / Bull 情景，并保存终值、分红、盈利和估值假设。

## 10. 技术与资金因子的治理

### 技术

不使用“技术数据都是过去式，因此没有预测力”的绝对表述。

```text
技术信号有效性具有市场、时期、参数与成本依赖；
其是否具备可交易 Alpha 必须样本外验证。
```

技术/动量在长期 sleeve 中可以作为辅助上下文或执行参考，但不得自动替代长期质量、估值与 thesis。

### 资金

不把 vendor “主力净流入”当作真实机构净买入事实。

至少区分：

```text
Participation — 成交额/换手/流动性
Positioning — 融资、机构披露、席位等可验证证据
Price Confirmation — 相对强度、突破承接、价格进展
```

这些短中期证据不自动成为长期 ADD/EXIT 权限。

## 11. MFE / MAE 的作用域

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
- 区分选股错误和退出错误；
- 校准 trailing、partial exit 和 time stop。

不得只看最终 PnL 调参。

长期可以保留 MFE/MAE 作为诊断数据，但不把短期 MFE/MAE/R 倍数作为长期 thesis 或模型晋级的核心指标。

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
strategy_id
sleeve
```

禁止自动化系统根据近期盈亏自行改写策略文件或提升风险。

## 13. 版本记录

研究/执行记录不得只写一个含义不明的 `policy_version`。至少保存：

```text
capital_policy_version
automation_governance_version
research_model_governance_version
skill_version
strategy_id
sleeve
strategy_version / model_version
```

## 14. 研究到自动化完整路径

```text
Hypothesis
→ Historical Research
→ Point-in-time Audit
→ Challenger Shadow
→ Forward / Paper
→ Manual Live Validation where applicable
→ Champion Promotion Review within the same sleeve
→ Assisted/Semi-auto only if needed
→ Full Auto only if execution governance also passes
```

```text
Good Model ≠ Safe Auto Execution
Safe Executor ≠ Positive Edge
Long Model ≠ Short/Mid Model
```

模型、自动化与账户风险三道 Gate 分别通过后，才允许提高相应 sleeve 的真实执行权限。