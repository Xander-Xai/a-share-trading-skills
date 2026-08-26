# Forward Validation Metrics and Trade Ledger v2

> 本文件定义短中期 Forward Paper / Live 的可审计记录结构。
>
> 上位规则：
>
> - `../../../shared/capital-allocation-and-entry-policy.md`
> - `../../../shared/automation-execution-governance.md`
> - `../SKILL.md`

## 1. Purpose

评估策略是否**前瞻有效**，同时保留决策、执行、风险、规则遵循和 Paper/Live 差异。

Ledger 不只是 P&L 表。

## 2. 必须分开的价格

```text
baseline_price  = 历史研究快照价格
planned_entry   = 交易计划价格
simulated_fill  = Paper 保守模拟成交
actual_fill     = Broker 真实成交
```

任何历史截图收盘价都不能自动变成实际 entry。

## 3. Paper Capital 与 Reporting NAV

Paper 模式必须同时保存：

```text
paper_capital_rmb
reporting_nav
```

- `paper_capital_rmb`：用于100股单位、真实股数、费用、滑点、仓位和风险计算；
- `reporting_nav`：通常以100.00为起点，用于标准化绩效比较。

禁止拿 `NAV=100` 直接模拟 A 股股数。

Live 模式保存 broker account/strategy NAV，但不得提交敏感账户标识到仓库。

## 4. Trade Lifecycle ID

```text
trade_id = YYYYMMDD-code-sequence
```

同一 thesis 生命周期：

```text
signal
→ decision
→ order intent
→ setup fill
→ confirmation fill(s)
→ holding-state events
→ exit
→ post-trade review
```

同一 thesis 的 confirmation tranche 不创建新 trade_id；新的独立 thesis 才创建新生命周期。

## 5. Required Pre-trade Fields

### Identity / provenance

```yaml
trade_id:
strategy_version:
policy_version:
universe_snapshot_id:
mode: paper | live_manual | assisted | semi_auto | auto
code:
name:
analysis_as_of:
source_provenance:
```

### Research state

```yaml
industry:
factor_cluster:
role:
market_regime:
sector_regime:
technical_score:
capital_score:
fundamental_score:
catalyst_score:
penalties:
final_score:
data_completeness: Complete | Partial | Insufficient
```

### Thesis / setup

```yaml
thesis:
setup_type:
entry_trigger:
planned_entry:
invalidation:
time_stop:
expected_target_or_exit_logic:
expected_reward_risk:
event_risk:
```

### Capital / Risk / Size

```yaml
paper_capital_rmb: null_if_live
reporting_nav:
strategy_nav_rmb:
size_cap_pct:
risk_cap_pct:
edge_cap_pct:
final_short_cap_pct:
actual_short_exposure_before_pct:
actual_short_exposure_after_pct:
allowed_loss_amount:
planned_stop_distance_pct:
planned_shares:
planned_exposure_rmb:
planned_trade_risk_pct:
portfolio_heat_before_pct:
portfolio_heat_after_pct:
industry_heat_after_pct:
factor_heat_after_pct:
```

Hard condition:

```text
actual_short_exposure_after_pct <= final_short_cap_pct
```

Being below the cap is allowed. No trade is required merely to “fill” unused capacity.

### Decision governance

```yaml
hard_veto_passed:
adversarial_review_passed:
policy_conflict: false
kill_switch_active: false
broker_reconciled: true_or_null_in_paper
manual_override: false
manual_override_reason:
decision: enter | wait | reject | event_isolation
```

## 6. Execution Fields

For every strategy tranche / execution order:

```yaml
order_id:
client_order_id:
trade_id:
strategy_tranche: setup | confirmation_1 | confirmation_2 | reduction | exit
execution_slice_no:
order_created_at:
submitted_at:
order_type:
limit_price:
requested_shares:
broker_status:
filled_at:
filled_shares:
fill_price:
fees:
taxes:
slippage_bps:
reject_reason:
```

`strategy_tranche` 与 `execution_slice_no` 必须分开，防止把大额拆单误记为更多策略批次。

Paper 模式使用等价 `simulated_*` 字段，并遵守保守成交逻辑。

## 7. Broker / Idempotency Fields

Live/Assisted/Semi-auto/Auto 至少保存：

```yaml
broker_order_id:
client_order_id:
idempotency_key:
acknowledged_at:
last_reconciled_at:
local_position_qty:
broker_position_qty:
reconciliation_status:
retry_count:
```

API 超时后先查询 broker 状态，不盲目重试。

## 8. Holding-state Event Log

只追加，不覆盖：

```yaml
event_time:
trade_id:
state_before:
state_after:
price:
score_refresh:
market_regime:
sector_regime:
new_information:
action:
action_reason:
```

状态：

- `strengthening`
- `intact`
- `weakening`
- `invalidated`

## 9. Exit Fields

```yaml
exit_decision_at:
exit_order_at:
exit_fill_at:
exit_price:
exit_shares:
exit_reason: invalidation | thesis | time_stop | partial_profit | trailing | event | portfolio_risk | cap_rebalance | other
holding_days:
realized_pnl_rmb:
realized_return_pct:
realized_R:
```

跳空/流动性导致更差成交时记录真实成交价，不用计划 stop 假装已成交。

## 10. MFE / MAE

```text
MFE = 持仓期间最大有利偏移
MAE = 持仓期间最大不利偏移
```

同时记录：

- percent；
- R multiple。

用于判断止损、退出、time-to-work 和 setup 质量。

## 11. Core Performance Metrics

### Expectancy

```text
Expectancy_R
= win_rate * average_win_R
- loss_rate * average_loss_R
```

必须扣除实际或合理估计的交易成本。

### Profit Factor

```text
profit_factor = gross_profit / abs(gross_loss)
```

还要统计：

- closed trades；
- win rate；
- median / average R；
- average winner / loser；
- best / worst trade；
- max drawdown / recovery；
- consecutive losses；
- turnover；
- average holding days。

不能只看胜率。

## 12. Segment the Data

按以下维度拆分：

### Setup

- breakout
- first pullback
- reclaim
- sector-leader continuation
- event-post-confirmation

### Market regime

- Risk-On
- Neutral / Rotational
- Risk-Off

### Factor

- commodity
- AI/datacenter capex
- consumer
- financial turnover
- utility
- defense
- shipping
- other

### Score band

- 80+
- 75–79
- 65–74 Paper observations

### Research state

- priority scan
- technical wait → entry
- event isolation → post-event entry
- downgrade → restored

## 13. Rule-adherence Metrics

每笔交易标记：

```text
good process + good result
good process + bad result
bad process + good result
bad process + bad result
```

盈利但违规不构成删除规则的证据。

跟踪：

- 无预定义 invalidation；
- per-trade / portfolio heat breach；
- `Final Short Cap` breach；
- same-factor breach；
- chase veto violation；
- blocked event entry；
- losing-position averaging down；
- stop widened in losing direction；
- 未重新承保就短转中；
- manual override；
- forced-trade / no-trade violation；
- stale data incident；
- reconciliation / duplicate-order incident。

## 14. Paper vs Live

匹配同一信号比较：

```text
paper_fill vs live_fill
paper_slippage vs live_slippage
paper_R vs live_R
paper_holding_time vs live_holding_time
paper_exit_reason vs live_exit_reason
```

若 Paper Edge 在 Live 消失，优先检查：

- fill optimism；
- 人工执行延迟；
- missed trades；
- emotional override；
- liquidity/fees；
- sizing differences；
- data timing；
- reconciliation error。

## 15. Daily Report

```markdown
# YYYY-MM-DD Short/Mid-term Daily Report

## Market regime

## Whitelist changes

## Top watch names

## Executable candidates

## Existing positions
- thesis state
- current R
- invalidation
- event risk

## Capital / Risk
- strategy NAV RMB
- Final Short Cap
- actual short exposure
- unused capacity / cash
- open initial risk
- industry heat
- factor heat

## Orders / fills / reconciliation

## Rule violations / incidents

## Next-session triggers
```

## 16. Weekly Review

至少：

- recompute expectancy / drawdown；
- setup/regime/factor split；
- inspect MFE/MAE；
- review every loss >1R equivalent；
- review manual override；
- check whether one factor dominates results；
- check whitelist fundamentals/events；
- check Paper/Live divergence；
- check cap, reconciliation and system incidents。

## 17. Promotion / Rollback

### Promotion

只有在：

- strategy evidence improves；
- process error rate low；
- execution reproducible；
- risk controls intact；
- shared automation governance gates passed；

时才向更高自动化阶段晋级。

### Rollback

出现以下任一情况，退回更安全阶段：

- reconciliation failure；
- duplicate order；
- hard risk control failure；
- persistent unexplained Live/Paper divergence；
- regulatory/broker permission change；
- circuit breaker / drawdown review；
- new strategy version not validated。

自动化成熟度必须可逆。

## 18. Suggested Storage

```text
runtime/
├── snapshots/
├── signals/
├── trades/
│   ├── paper.jsonl
│   └── live.jsonl
├── orders/
├── positions/
├── reports/
└── incidents/
```

Live canonical state 建议使用事务型数据库；Flat files 适合审计/导出，但不应成为唯一订单状态源。

## 19. Final Rule

最重要的不是裸收益，而是：

> **扣成本后存在正期望，并且没有违反资本/风险/执行治理规则；任何结果都能从 point-in-time 数据、决策和真实/模拟成交记录中重建。**
