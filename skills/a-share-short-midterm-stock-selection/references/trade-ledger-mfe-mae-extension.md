# Trade Ledger — MFE / MAE Extension

> 本文件扩展现有交易日志，使退出规则可以被数据反向校准，而不是只看最终盈亏。

## 1. 为什么必须记录 MFE / MAE

只看最终 PnL 无法区分：

```text
选股错
入场错
止损错
止盈过早
止盈过晚
时间止损错误
执行滑点错误
```

因此每笔交易必须同时记录：

```text
MFE = Maximum Favorable Excursion
MAE = Maximum Adverse Excursion
```

并统一换算成 `R`。

## 2. 必填字段

```yaml
trade_id:
model_version:
stock_code:
stock_name:
setup_type:
market_regime:
sector_regime:
entry_timestamp:
entry_price:
invalidation_price:
initial_risk_amount:
initial_risk_pct_nav:
position_size:
exit_timestamp:
exit_price:
exit_reason:
realized_pnl:
realized_R:
MFE_price:
MFE_R:
MAE_price:
MAE_R:
max_unrealized_profit_pct:
max_unrealized_loss_pct:
holding_days:
commission:
stamp_tax:
slippage:
impact_estimate:
rule_violation:
notes:
```

## 3. 派生指标

### 3.1 MFE Capture Ratio

```text
MFE Capture Ratio = realized_R / MFE_R
```

仅在 `MFE_R > 0` 时计算。

解释：

- 长期过低：可能止盈过早；
- 很高但回撤显著：可能持有过久才退出；
- 不作为单笔好坏判断，必须按 setup/regime 聚合。

### 3.2 Giveback Ratio

```text
Giveback_R = MFE_R - realized_R
```

用于识别盈利回吐。

### 3.3 Adverse Efficiency

观察盈利交易通常需要承受多少 MAE：

```text
median(MAE_R | realized_R > 0)
```

若大多数赢家从未接近当前止损，而止损长期很宽，可研究缩小止损；但必须重新测 gap/噪声风险。

## 4. 用 MFE / MAE 校准规则

### +1.5R / +2R

当前只是治理初值。

若大量交易满足：

```text
realized_R ≈ 1.5R
MFE_R >= 3R or 4R
```

则说明 partial exit / trailing 可能过早。

反之若：

```text
MFE_R ≈ 1.6R
realized_R frequently turns negative
```

说明保护利润机制可能太松。

### 3–5 日 Time Review

按持仓天数统计：

```text
P(MFE_R >= target | first_3d_behavior)
P(stop_out | first_3d_relative_weakness)
```

只有数据支持后，才调整 time stop。

## 5. 禁止的调参方式

- 看 3–5 笔交易就改规则；
- 只研究亏损交易；
- 删除跳空止损、涨跌停等坏样本；
- 只看平均值，不看分布和尾部；
- 用最终结果倒推当时“不该买”。

## 6. 推荐聚合切片

至少按以下维度复盘：

```text
setup_type
market_regime
sector_regime
score_bucket
entry_extension_bucket
catalyst_type
holding_days
winner/loser
```

输出中同时报告样本数，避免小样本误导。

## 7. 与自动化的关系

自动监控可以实时更新 MFE/MAE，但：

```text
MFE/MAE statistics
→ 生成研究建议
→ 人工评审
→ 新 Challenger
```

不得：

```text
最近 MFE 变大
→ 系统自动扩大止盈目标/风险
```

策略参数修改仍受 shared model governance 与 automation governance 双重约束。
