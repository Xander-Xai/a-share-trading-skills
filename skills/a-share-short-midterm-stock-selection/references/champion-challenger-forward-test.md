# Champion vs Challenger Forward-Test Protocol v1.2

> 用于验证新短中期模型是否真的优于当前 Champion。研究晋级遵循 `../../../shared/research-model-governance.md`；资本/风险遵循 shared capital policy；自动执行遵循 shared automation governance。

## 1. 对照对象

### Champion

```text
Technical 30
Capital Participation 30
Fundamentals 25
Catalyst 15
```

### Challenger

`causal-challenger-model.md`，状态 `SHADOW ONLY`，直至正式 Promotion。

当前 Challenger 已接入 ERG 子模块：

- `expectation-reaction-gate.md`；
- `erg-forward-test-extension.md`；
- `statistical-promotion-guard.md`。

ERG 只能影响 Shadow 研究记录，不能直接改变 Champion / Paper / Live 订单。

## 2. 冻结条件

每个 Forward-Test cohort 开始前冻结：

```text
capital_policy_version
automation_governance_version
research_model_governance_version
champion_model_version
challenger_model_version
erg_version
strategy_version
feature_definition
score_weights
thresholds
universe_definition
benchmark
cost_assumptions
slippage_model
position_sizing_policy
entry/exit rules
risk caps
```

ERG cohort 还按 `erg-forward-test-extension.md` 冻结 expectation source/confidence、surprise、materiality、prepricing、reaction、state 与 strategy-type 规则。

测试中若实质修改参数，结束当前 cohort，创建新版本重新开始，不能把不同模型段静默拼接。

## 3. 公平比较

两模型必须使用：

- 相同股票池；
- 相同 `as_of`；
- 相同 point-in-time 数据源；
- 相同 T+1、涨跌停、停牌约束；
- 相同初始策略 NAV；
- 相同 shared risk budget；
- 相同成本、税费、滑点与 impact 模型；
- 相同账户级同股/风险簇 Cap；
- 相同最大持仓数、行业/因子限制。

不能给 Challenger 使用 Champion 当时不可见的信息。

对 ERG 尤其禁止：

- 用后来财报修正当时 expectation；
- 用后来价格反应升级过去的 research state；
- 在没有 point-in-time expectation baseline 时伪造“超预期”；
- 用公告后不可交易时段的价格作为可执行成交。

## 4. Shadow Mode

```text
Champion   → 当前生产研究 / Paper / Manual Live 路径
Challenger → Shadow portfolio only
ERG        → Challenger 内部 Shadow research layer only
```

Challenger/ERG 不影响真实下单，也不能借用独立账户风险额度。

## 5. Signal Ledger

每个交易日保存：

```text
as_of
capital_policy_version
research_model_governance_version
champion_model_version
challenger_model_version
erg_version
stock_code
stock_name
champion_score
champion_status
challenger_score
challenger_status
research_state
position_state
strategy_type
regime
sector
factor_cluster
entry_trigger
planned_entry
invalidation
planned_RR
planned_risk_R
account_symbol_exposure
account_cluster_exposure
actual_signal_action
```

事件驱动候选额外保存 `erg-forward-test-extension.md` 的字段，至少：

```text
information_timestamp
first_tradable_timestamp
source_tier
expectation_baseline_type
expectation_confidence
expectation_center
expectation_dispersion
surprise_direction
materiality_state
prepricing_state
reaction_state
post_event_RVOL
```

即使没有交易，也记录 `NO_TRADE`；即使 ERG 数据缺失，也记录 `null / UNRESOLVED`，避免只保留成功样本或偷偷填值。

## 6. Trade Ledger

每个闭环交易至少保存：

```text
model
strategy_version
entry_time
entry_price
exit_time
exit_price
position_size
fees
stamp_tax
slippage
impact_estimate
realized_R
MFE_R
MAE_R
holding_days
exit_reason
rule_violation
market_regime
sector_regime
```

若只做 Shadow，使用相同保守模拟成交逻辑。

`strategy_type` 在 Thesis 生命周期内锁定；如果从 EVENT_MOMENTUM/TREND 改成 MEAN_REVERSION 或其他策略，必须结束/重新承保原记录，不能把亏损交易静默改名。

## 7. Performance Metrics

必须比较：

```text
Net Return
Benchmark Return
Excess Return
Expectancy_R
Profit Factor
Max Drawdown
Calmar
Win Rate
Avg Win_R
Avg Loss_R
Payoff Ratio
Turnover
Cost Drag
Longest Losing Streak
MFE Capture Ratio
MAE Distribution
Rule Violation Rate
```

`MFE Capture Ratio = realized_R / MFE_R` 仅在 `MFE_R > 0` 时使用。

ERG 额外比较：

```text
candidate_to_confirmed_rate
confirmed_to_entry_rate
positive_surprise_negative_reaction_rate
negative_surprise_positive_reaction_rate
priced_in_false_positive_rate
invalidated_after_entry_rate
no_trade_rate
expectancy_by_event_type
expectancy_by_expectation_confidence
expectancy_by_prepricing_state
expectancy_by_reaction_state
```

## 8. ERG Ablation

必须在数据允许时按 `erg-forward-test-extension.md` 做增量消融：

```text
A: Eligibility only
B: A + Expectation / Surprise
C: B + Economic Materiality
D: C + Prepricing
E: D + Post-event Reaction
F: E + Regime / Participation / Execution / Risk
```

目的不是证明整套 ERG“看起来合理”，而是确定每个模块是否增加样本外/Forward 的有效区分、降低尾部风险或减少规则违规。

某个组件没有增益时，允许 `REMOVE_NONVALUE_COMPONENTS`，不强行保留。

## 9. Regime / Factor Breakdown

至少拆分：

```text
TREND_FRIENDLY
ROTATIONAL_NEUTRAL
MEAN_REVERTING
RISK_OFF
```

并检查：

- 大盘/小盘；
- 资源/周期；
- 科技/成长；
- 消费/防御；
- 事件驱动；
- 高换手/低换手；
- 账户级高相关因子拥挤状态。

禁止只报告总收益。

事件样本足够时还应按 Earnings / Preannouncement / Orders / Commodity / Policy / Capital Structure 分层。

## 10. Benchmark

至少保留：

```text
broad_market_benchmark
sector_benchmark
cash_no_trade_baseline
```

收益口径、分红/价格口径和持有期必须一致。

ERG 的 `AR` / relative reaction 使用的 benchmark 选择规则必须在 cohort 前冻结。

## 11. Cost

Net Performance 扣除：

```text
commission
stamp_tax
slippage
estimated_market_impact
```

成本数据不完整标记 `Partial`，不得作为正式晋级唯一证据。

## 12. Statistical Promotion Guard

读取 `statistical-promotion-guard.md`。

每个研究 family 至少记录：

```text
number_of_trials
parameter_stability_summary
selection_bias_risk
untouched_test_status
```

当样本结构与工具允许时，增加：

```text
DSR
PBO
reality_check_status
```

这些诊断不替代经济逻辑、执行和风险 Gate；但如果大量调参后仍缺少 model-selection 风险披露，Challenger 应保持 Shadow。

## 13. Promotion Review

不设“满 N 笔自动晋级”。至少要求：

- 足够样本支持 Regime / event type 分层；
- Challenger Forward 净优势不是一两个赢家造成；
- 回撤/尾部风险不显著恶化；
- 成本后优势仍存在；
- 参数没有追着行情频繁修改；
- point-in-time / survivorship audit 通过；
- 账户级集中度规则在两模型中一致；
- ERG 消融能够说明哪些组件真的增加价值；
- model-selection / data-snooping 风险已披露；
- 新复杂度有实际价值。

输出：

```text
PROMOTE
PROMOTE_ERG_COMPONENTS
KEEP_SHADOW
REMOVE_NONVALUE_COMPONENTS
REJECT
REVISE_AND_RESTART
```

## 14. Promotion 后仍不能直接 Full Auto

模型晋级只证明研究模型更值得成为新 Champion。

自动化执行仍需独立通过：

`../../../shared/automation-execution-governance.md`

```text
Model Promotion != Automation Promotion
```
