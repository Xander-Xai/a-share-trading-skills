# Trade Ledger — MFE / MAE Extension v1.1

> 本文件扩展短中期交易日志，使退出规则可以被数据反向校准，而不是只看最终盈亏。
>
> 参数修改受 `../../../shared/research-model-governance.md` 约束；风险受 shared capital policy 约束；Live 执行受 shared automation governance 约束。

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
strategy_id:
sleeve: short_mid
capital_policy_version:
automation_governance_version:
research_model_governance_version:
skill_version:
strategy_version:
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
initial_risk_pct_strategy_nav:
position_size:
account_symbol_exposure_at_entry:
account_cluster_exposure_at_entry:
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
cap_breach_event:
notes:
```

不得用一个模糊 `policy_version` 替代三类 shared governance 版本。

## 3. 派生指标

### MFE Capture Ratio

```text
MFE Capture Ratio = realized_R / MFE_R
```

仅在 `MFE_R > 0` 时计算。

长期过低可能提示止盈过早；很高但最终回撤大可能提示利润保护过松。必须按 setup/regime 聚合，不能判断单笔好坏。

### Giveback

```text
Giveback_R = MFE_R - realized_R
```

### Adverse Efficiency

```text
median(MAE_R | realized_R > 0)
```

用于研究止损宽度，但调整前仍需重新测试 gap/噪声风险。

## 4. 用 MFE / MAE 校准治理初值

### +1.5R / +2R

当前只是治理初值。

若大量交易：

```text
realized_R ≈ 1.5R
MFE_R >= 3R or 4R
```

可能说明 partial/trailing 过早。

若：

```text
MFE_R ≈ 1.6R
realized_R frequently turns negative
```

可能说明利润保护过松。

### 3–5日 Time Review

按持仓天数统计：

```text
P(MFE_R >= target | first_3d_behavior)
P(stop_out | first_3d_relative_weakness)
```

只有数据支持后，才提出新 Challenger 参数。

## 5. CAP_BREACH 与计划风险要分开

市场价格变化可能让资本暴露被动超 Cap；跳空也可能让实际亏损超过计划风险。

记录时区分：

```text
planned_risk_violation
passive_cap_breach
realized_tail_loss
```

不能把被动市场事件误记成主动规则违规，也不能因为被动越界曾发生就放宽未来新订单限制。

## 6. 禁止的调参方式

- 看3–5笔交易就改规则；
- 只研究亏损交易；
- 删除跳空、涨跌停坏样本；
- 只看平均值不看尾部；
- 用最终结果倒推当时“不该买”；
- Challenger 未晋级就改 Champion；
- 系统根据近期 MFE/MAE 自动提高仓位或风险。

## 7. 推荐聚合切片

```text
model_version
setup_type
market_regime
sector_regime
score_bucket
entry_extension_bucket
catalyst_type
holding_days
winner/loser
account_cluster_state
```

报告样本数，避免小样本误导。

## 8. 与自动化的关系

```text
MFE/MAE statistics
→ research hypothesis
→ Challenger
→ Forward-Test
→ human Promotion Review
```

不得：

```text
最近 MFE 变大
→ 自动提高止盈目标/仓位/风险
```

模型晋级和自动化晋级是独立 Gate。
