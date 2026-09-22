# Forward Validation Metrics and Trade Ledger v3

> 定义短中期 Forward Paper / Live 的可审计记录结构。
>
> 上位规则：
> - `../../../shared/capital-allocation-and-entry-policy.md`
> - `../../../shared/research-model-governance.md`
> - `../../../shared/automation-execution-governance.md`
> - `../SKILL.md`

## 1. Purpose

评估策略是否前瞻有效，同时保留决策、执行、风险、规则遵循、模型版本和 Paper/Live 差异。

Ledger 不只是 P&L 表。

## 2. 四种价格必须分开

```text
baseline_price = 历史研究快照价
planned_entry  = 交易计划价
simulated_fill = Paper 保守成交价
actual_fill    = Broker 真实成交价
```

历史截图收盘价不能自动变成 entry。

## 3. Paper Capital 与 Reporting NAV

```text
paper_capital_rmb
reporting_nav
```

- `paper_capital_rmb`：证券特定申报数量规则、股数、费用、滑点、仓位和风险计算；
- `reporting_nav`：通常100.00起始，用于标准化绩效比较。

禁止把100个 NAV 点当人民币100元执行本金。

## 4. Governance Bundle

每个决策/交易必须保存：

```yaml
capital_policy_version:
automation_governance_version:
research_model_governance_version:
skill_version:
strategy_version:
model_version:
```

不得只写一个模糊 `policy_version`。

## 5. Strategy / Broker Position Identity

Live 与跨策略场景增加：

```yaml
strategy_id:
sleeve: long | short_mid
stock_code:
strategy_virtual_shares_before:
strategy_virtual_shares_after:
broker_account_total_shares_before:
broker_account_total_shares_after:
```

Broker 净持仓是执行层真相源；策略虚拟子账用于区分长期与短中期逻辑归属。

同一股票跨策略时必须保存：

```yaml
long_account_exposure:
short_mid_account_exposure:
account_symbol_exposure_total:
account_symbol_cap:
account_cluster_exposure_total:
account_cluster_cap:
```

## 6. Trade Lifecycle ID

```text
trade_id = YYYYMMDD-code-sequence
```

同一 thesis：

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

confirmation tranche 不新建 trade_id，除非 thesis 真正改变。

## 7. Required Pre-trade Fields

### Identity / provenance

```yaml
trade_id:
strategy_id:
mode: paper | live_manual | assisted | semi_auto | auto
code:
name:
analysis_as_of:
universe_snapshot_id:
source_provenance:
```

### Research state

```yaml
champion_or_challenger:
model_version:
industry:
factor_cluster:
role:
market_regime:
sector_regime:
technical_score:
capital_score:
fundamental_score:
catalyst_score:
challenger_score:
penalties:
final_score:
data_completeness: Complete | Partial | Insufficient
```

Challenger Shadow 交易必须明确标记，不能混入 Champion Live 业绩。

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

### Risk / size

```yaml
short_strategy_nav:
stock_account_equity:
final_short_cap:
actual_short_exposure_before:
planned_short_exposure_after:
allowed_loss_amount:
planned_stop_distance_pct:
planned_shares:
planned_exposure_rmb:
planned_trade_risk_pct:
portfolio_heat_before:
portfolio_heat_after:
industry_heat_after:
factor_heat_after:
account_symbol_exposure_after:
account_cluster_exposure_after:
cap_state: PASS | CAP_BREACH | BLOCKED
```

### Decision governance

```yaml
hard_veto_passed:
adversarial_review_passed:
policy_precedence_passed:
cross_sleeve_reconciliation_passed:
manual_override: false
manual_override_reason:
decision: enter | wait | reject | event_isolation | no_trade
```

## 8. Execution Fields

每个订单/批次：

```yaml
order_id:
client_order_id:
idempotency_key:
trade_id:
strategy_id:
tranche: setup | confirmation | reduction | exit
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

Paper 填等价 `simulated_*` 字段。

API timeout 后先 reconcile broker，不盲目重试。

## 9. Holding-state Event Log

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
account_symbol_exposure:
account_cluster_exposure:
cap_breach_event:
```

允许：

```text
strengthening
intact
weakening
invalidated
```

## 10. Exit Fields

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

gap/流动性导致实际成交更差时记录真实价，不写计划 stop 价。

## 11. MFE / MAE

```text
MFE = best unrealized move while open
MAE = worst unrealized move while open
```

同时记录 percent 与 R。

扩展指标见 `trade-ledger-mfe-mae-extension.md`。

## 12. Core Performance Metrics

```text
Expectancy_R = win_rate * avg_win_R - loss_rate * avg_loss_R
Profit Factor = gross_profit / abs(gross_loss)
```

还记录：

- total closed trades；
- win rate；
- median/average R；
- avg winner/loser；
- max drawdown；
- recovery time；
- consecutive losses；
- turnover；
- average holding days；
- cost drag；
- MFE capture；
- rule violation rate。

所有绩效使用成本后结果。

## 13. Segmentation

至少按：

- model_version / Champion vs Challenger；
- setup；
- market regime；
- sector/factor；
- score band；
- decision state；
- account cluster crowding；
- Paper vs Live。

聚合 P&L 不能掩盖失效子策略。

## 14. Rule-adherence Metrics

每笔标记：

```text
good process + good result
good process + bad result
bad process + good result
bad process + bad result
```

跟踪：

- 无预定义 invalidation；
- planned risk breach；
- Final Short Cap planned breach；
- account symbol/cluster breach；
- passive CAP_BREACH；
- same-factor breach；
- chase veto violation；
- blocked-event entry；
- averaging down without confirmation；
- stop widened；
- short→medium without re-underwriting；
- manual override；
- no-trade violation；
- cross-sleeve order conflict；
- duplicate order。

注意：`passive CAP_BREACH` 与主动 planned-policy violation 必须分开统计。

## 15. Paper vs Live

匹配同一信号比较：

```text
paper_fill vs live_fill
paper_slippage vs live_slippage
paper_R vs live_R
paper_holding_time vs live_holding_time
paper_exit_reason vs live_exit_reason
```

Paper edge 消失时先查：fill optimism、执行延迟、missed trades、override、费用/流动性、仓位差异、数据时点。

## 16. Champion vs Challenger

Challenger 的 Shadow ledger 与 Champion 分开，但使用相同：

- universe；
- as_of；
-成本；
-交易约束；
-risk limits；
-benchmark。

Promotion 见 `champion-challenger-forward-test.md` 和 shared research governance。

## 17. Daily Report

```markdown
# YYYY-MM-DD Short/Mid-term Daily Report

## Governance bundle
## Market regime
## Whitelist changes
## Champion top watchlist
## Challenger shadow disagreement
## Executable candidates
## Existing positions
## Account-level symbol / factor exposure
## Portfolio heat / Final Short Cap / CAP_BREACH
## Orders / fills / reconciliation
## Rule violations / system incidents
## Tomorrow triggers
```

## 18. Promotion / Rollback

从 Paper→Live 或更高自动化，只在：

- 策略证据改善；
- process error 低；
- 执行可复现；
- 风险控制完整；
- account/broker reconciliation 稳定。

以下情况立即降级：

- reconciliation failure；
- duplicate order；
- hard risk control failure；
- unexplained live/paper divergence；
- broker/regulatory change；
- drawdown review；
- 新模型未验证。

## 19. Suggested Storage

```text
runtime/
├── snapshots/
├── signals/
├── trades/
├── orders/
├── strategy_virtual_positions/
├── broker_reconciliation/
├── reports/
└── incidents/
```

高完整性 Live 状态使用事务型数据库作为 canonical runtime state；flat files 适合审计/导出，不作为唯一订单状态源。

## 20. Final Rule

```text
Positive expectancy after costs
+ no active risk-policy violation
+ point-in-time reproducibility
+ account-level aggregation
+ broker reconciliation
```

比单纯总收益更重要。
