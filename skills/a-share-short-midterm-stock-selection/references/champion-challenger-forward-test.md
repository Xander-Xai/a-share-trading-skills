# Champion vs Challenger Forward-Test Protocol

> 用于验证新短中期模型是否真的优于当前 Champion。不得用回看历史后的主观印象替代本协议。

## 1. 对照对象

### Champion

当前生产研究评分：

```text
Technical 30
Capital Participation 30
Fundamentals 25
Catalyst 15
```

### Challenger

`causal-challenger-model.md`。

## 2. 冻结条件

每个 Forward-Test 周期开始前冻结：

```text
model_version
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

测试周期中不得因为近期结果随意改参数。若确需修改，结束当前 cohort，创建新版本重新开始。

## 3. 公平比较

两模型必须使用：

- 相同股票池；
- 相同 `as_of`；
- 相同数据源和发布时间约束；
- 相同 A 股 T+1、涨跌停、停牌约束；
- 相同初始策略 NAV；
- 相同 shared risk budget；
- 相同成本和滑点模型；
- 相同最大持仓数、行业/因子上限。

不能给 Challenger 使用 Champion 当时看不到的信息。

## 4. Shadow Mode

第一阶段 Challenger 只产生影子决策：

```text
Champion → 正常 Paper/Manual Live 路径
Challenger → Shadow portfolio only
```

Challenger 不影响真实下单。

## 5. Signal Ledger

每个交易日保存：

```text
as_of
stock_code
stock_name
champion_score
champion_status
challenger_score
challenger_status
regime
sector
factor_cluster
entry_trigger
planned_entry
invalidation
planned_RR
planned_risk_R
actual_signal_action
```

即使没有交易，也记录 `NO_TRADE`，避免只保留成功样本。

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

## 7. Performance Metrics

必须同时比较：

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
```

### MFE Capture Ratio

建议定义：

```text
MFE Capture Ratio = realized_R / MFE_R
```

仅在 `MFE_R > 0` 时使用，用于判断退出是否长期过早。

## 8. Regime Breakdown

至少按以下环境拆分：

```text
TREND_FRIENDLY
ROTATIONAL_NEUTRAL
MEAN_REVERTING
RISK_OFF
```

禁止只报告总收益。

还应拆分：

- 大盘/小盘；
- 资源/周期；
- 科技/成长；
- 消费/防御；
- 事件驱动；
- 高换手/低换手。

## 9. Benchmark

至少保留：

```text
broad_market_benchmark
sector_benchmark
cash_no_trade_baseline
```

短期 Benchmark 口径与策略收益口径保持一致。

## 10. 成本

Net Performance 必须扣除：

```text
commission
stamp_tax
slippage
estimated_market_impact
```

若成本数据不完整，结果标记 `Partial`，不得作为正式晋级的唯一证据。

## 11. Promotion Review

不设“满 N 笔自动晋级”。进入晋级评审至少要求：

- 有足够样本支持按 Regime 分层；
- Challenger 样本外/Forward 净优势不是一两个大赢家造成；
- 回撤和尾部风险不显著恶化；
- 成本后优势仍存在；
- 参数没有频繁追着行情改；
- point-in-time / survivorship audit 通过；
- 复杂度增加有实际收益。

评审输出：

```text
PROMOTE
KEEP_SHADOW
REJECT
REVISE_AND_RESTART
```

## 12. Promotion 后仍然不能直接 Full Auto

Champion 晋级只证明研究模型更值得采用。

自动化执行仍必须单独通过：

`../../../shared/automation-execution-governance.md`

即：

```text
Model Promotion != Automation Promotion
```
