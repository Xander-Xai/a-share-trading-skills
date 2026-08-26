# Short/Mid-term: Paper → Manual Live → Assisted → Automated Roadmap v2

> 本文件只定义短中期策略特有的 Forward/Live 验证方式。
>
> 跨策略自动化、Broker 执行、安全、幂等、Kill Switch、程序化交易/券商合规的最高规则是：
>
> `../../../shared/automation-execution-governance.md`
>
> 资金、仓位、Risk/Edge/Size Cap、Operating Target/Hard Ceiling、策略批次的最高规则是：
>
> `../../../shared/capital-allocation-and-entry-policy.md`
>
> 若本文件与 shared 冲突，以 shared 为准。

## 1. 目标

把短中期 Skill 变成可验证闭环，而不是从选股直接跳到无人值守下单。

```text
Research only
→ Forward Paper
→ Small-size Manual Live
→ Automated Research / Manual Orders
→ Human-confirmed Broker Execution
→ Limited Semi-auto
→ Full Auto only after Edge + Compliance + Reliability gates
```

默认：

```text
AUTO_MONITOR = true
AUTO_ORDER   = false
```

系统必须独立回答：

1. 什么能交易？
2. 今天什么值得观察？
3. 什么时点构成有效入场？
4. 最多能冒多少风险？
5. 持仓如何管理？
6. 真实数据是否证明策略具有 Edge？

## 2. 短中期闭环架构

```text
Locked Universe
      ↓
Data / Official Evidence
      ↓
Research Engine
Eligibility + 30/30/25/15 + Adversarial Review
      ↓
Signal / Intent
Trigger + Invalidation + R
      ↓
Risk Engine
Final Short Cap + Position Size + Heat + Factor Limits
      ↓
Paper / Human-approved Live Router
      ↓
Broker / Simulated Fill
      ↓
Position State
strengthening / intact / weakening / invalidated
      ↓
Ledger
MFE / MAE / R / Drawdown / Violations
      ↓
Evaluation / Governance
```

Research 不决定突破风险上限；Execution 不能绕过研究硬门禁。

## 3. Immutable Decision Record

每个 signal/trade 至少保存：

```text
strategy_version
policy_version
universe_snapshot_id
analysis_as_of
stock_code
stock_name
market_regime
sector_regime
industry
factor_cluster
technical_score
capital_score
fundamental_score
catalyst_score
penalties
final_score
source_evidence
entry_trigger
planned_entry
invalidation
planned_reward_risk
risk_budget
planned_shares
mode = paper | live_manual | assisted | semi_auto | auto
manual_override
```

成交后追加：

```text
order_id
order_time
fill_time
actual_fill
actual_shares
fees
taxes
slippage
exit_time
exit_fill
exit_reason
MFE
MAE
realized_R
rule_violations
```

绝不使用后来的结果覆盖原始决策。

## 4. Phase 0 — Research Baseline

当前历史基线：

- `../examples/2026-08-26-final-watchlist-case-study.md`
- `../examples/2026-08-26-final-watchlist.json`

这是同日较晚的 43 股最终 research whitelist；`core-pool-snapshot-2026-08-26.md` 是更早的 36 股中间快照。

退出 Phase 0 的最低要求：同样输入、同样 `as_of`、同样版本应产生实质一致的分类、评分与研究结论。

## 5. Phase 1 — Forward Paper

### 5.1 Paper 不是回测替代品

Forward Paper 从规则冻结之后观察未来数据，重点检查：

- look-ahead；
- 真实触发；
- T+1 / 涨跌停 / gap；
- 费用与滑点；
- 规则执行；
- 策略在不同 regime 下的表现。

### 5.2 Paper 资金与标准化 NAV

必须遵循 shared automation governance：

```text
paper_capital_rmb = 用于真实股数、100股单位、费用、风险计算
reporting_nav     = 100.00 起始标准化绩效指数
```

不能把 `NAV=100` 直接当人民币本金模拟 A 股交易。

### 5.3 每日流程

```text
收盘后
→ refresh market/sector
→ refresh official events
→ rescore whitelist
→ next-session trigger / invalidation
→ paper intents

下一交易日
→ trigger 成立才模拟成交
→ 执行 A 股现实约束
→ 更新 position state

收盘/事件后
→ stop / partial / time-stop management
→ append ledger
```

### 5.4 Conservative Fill

- gap 穿越信号时不假设刚好成交在信号价；
- 跌停不可卖时不假设止损已成交；
- 模拟费用、税费、滑点；
- 尊重100股单位；
- 尊重普通新买 A 股不能自由日内反向卖出；
- 除权除息不当成真实技术破位。

### 5.5 Paper → Manual Live 参考门槛

这只是治理起点，不是学术最优值：

- 至少约50笔已关闭 Forward Paper trades；
- 优先覆盖至少约8周；
- 尽可能覆盖不止一种 market regime；
- 扣成本后 Expectancy 为正；
- 无 unresolved hard-policy violation；
- drawdown 与策略政策相容；
- 结果不是一两笔极端赢家主导；
- 决策和成交可从 ledger 重建。

样本数达到不代表必须晋级。

## 6. Phase 2 — Small-size Manual Live

目标：验证 Paper Edge 与真实执行之间的差距。

规则：

- 人工完成每一笔真实订单；
- 风险使用 Operating Target 保守端；
- 不因 Paper 表现好就立即加风险；
- Paper 和 Live 尽量并行记录同一信号；
- 保存真实成交、费用、滑点、拒单、部分成交；
- 保存人工 override 及理由。

参考晋级条件：

- 至少约20–30笔已关闭真实交易作为初始观察样本；
- 无反复硬规则违规；
- Live/Paper 方向上可解释；
- 实际成本在模型容忍范围；
- risk engine 与 ledger 可对账；
- position state 无不明差异。

样本量只是必要信息之一，不是自动晋级开关。

## 7. Phase 3 — Automated Research / Manual Orders

优先自动化：

- 数据抓取；
- corporate-event checks；
- industry/factor tagging；
- technical calculations；
- scoring；
- factor heat；
- candidate ranking；
- trigger alerts；
- Paper execution；
- performance reports。

继续人工：

- 最终买卖确认；
- 异常事件判断；
- 券商下单。

这个阶段通常能获得大部分自动化效率，而不引入自动执行的最高风险。

## 8. Phase 4 — Human-confirmed Broker Execution

```text
executable setup
→ Risk Engine builds Order Proposal
→ human checks source/time/score/stop/size
→ explicit approval
→ broker adapter
→ acknowledgement/fill
→ reconciliation
```

Order Proposal 至少展示：

- code/name；
- quote timestamp；
- setup/trigger；
- acceptable price range；
- invalidation；
- Reward/Risk；
- shares/RMB exposure；
- planned trade risk；
- post-trade heat；
- industry/factor exposure；
- event risk；
- `Actual Short Exposure` vs `Final Short Cap`；
- data / broker / compliance / Kill-Switch state。

## 9. Phase 5 — Limited Semi-auto

只自动执行预先批准、边界清楚的动作，例如：

- 已人工批准的限价单；
- 已批准的退出规则；
- 超时未成交单取消；
- 实际价格使风险超限时自动缩小订单。

仍必须通过 shared automation governance 的：

```text
allowed symbols
order-type allowlist
max order value/shares
price collar / slippage guard
max daily order count
Final Short Cap
portfolio/factor heat
binary-event lockout
data freshness
position reconciliation
idempotency
broker health
Kill Switch
```

任何未知状态 fail closed。

## 10. Phase 6 — Full Auto

默认关闭。

开启前至少：

1. Forward Paper 和 Live 支持策略 Edge；
2. broker adapter 通过 failure injection；
3. risk layer 不能被 strategy layer 绕过；
4. restart/recovery 不重复订单；
5. broker position truth 已 reconcile；
6. independent Kill Switch 可用；
7. 决策/订单/成交完整可审计；
8. 人工紧急干预可用；
9. 实际账户/API 的程序化交易和券商要求已确认。

## 11. A股程序化交易 / 合规

跨策略统一见：

`../../../shared/automation-execution-governance.md`

当前研究基线：

- 中国证监会《证券市场程序化交易管理规定（试行）》
  https://www.csrc.gov.cn/csrc/c101954/c7480579/content.shtml
- 上海证券交易所程序化交易管理实施细则
  https://www.sse.com.cn/lawandrules/sselawsrules2025/trade/universal/c/c_20250612_10781696.shtml
- 深圳证券交易所程序化交易管理实施细则
  https://www.szse.cn/lawrules/rule/trade/t20250403_612770.html

进入实际自动报单前必须重新联网核验，并向实际券商确认账户/API/报告/测试/权限/频率要求。

## 12. Risk Engine Invariants

下单前拒绝条件包括：

- symbol 不在 approved universe；
- quote stale/unverified；
- event lockout；
- 无 invalidation；
- Reward/Risk 不合格且无正式例外；
- 单笔风险超 policy；
- portfolio/factor heat 超 policy；
- `Actual Short Exposure` 会超过 `Final Short Cap`；
- position/broker state 未对账；
- compliance/broker state invalid；
- Kill Switch active。

成交后：

- broker fill 先持久化；
- 以实际成交重算风险；
- 风险超限按预定义规则缩减；
- 不能因为成交差而向亏损方向放宽 stop。

## 13. Failure Injection

至少测试：

- 行情源中断/延迟；
- duplicated signal；
- broker 已接受订单但客户端超时；
- partial fill / reject；
- live order 时进程重启；
- broker position 与本地不一致；
- gap-through stop；
- limit-down 无法退出；
- suspension；
- ex-dividend 机械价格变化；
- signal 到 order 之间出现重大公告；
- 两个 worker 同时对同一标的发单；
- 同因子暴露超限。

系统必须宁愿错过交易，也不制造未知风险仓位。

## 14. Evaluation Metrics

### Strategy Edge

- closed trades；
- win rate；
- average/median R；
- average winner/loser；
- Expectancy R；
- Profit Factor；
- Max Drawdown / recovery；
- return by setup/regime/factor。

### Trade Quality

- MFE/MAE；
- entry/exit efficiency；
- time-stop outcomes；
- gap loss vs planned stop；
- event-isolation outcomes。

### Execution Quality

- modeled vs actual fill；
- slippage；
- fees/taxes；
- reject/partial-fill rate；
- stale-signal rate；
- duplicate-order count；
- reconciliation errors。

### Process Quality

- rule-violation rate；
- manual override rate；
- hard-veto override attempts；
- data/source incidents；
- no-trade rule adherence。

## 15. Parameter Governance

任何规则修改：

```text
proposal
→ mechanism / hypothesis
→ analysis sample
→ holdout / forward validation
→ overfitting risk
→ version bump
→ consistency audit
→ shadow/paper run
→ live promotion
```

不同重要版本的绩效必须分段，不能静默混合。

## 16. Ledger

详细字段使用：

`validation-metrics-and-trade-ledger.md`

关键原则：

```text
baseline_price != planned_entry != actual/simulated_fill
```

同一 thesis 的 confirmation tranche 继续使用同一 trade lifecycle，除非真的产生新的独立 thesis。

## 17. End-state Loop

```text
locked watchlist
→ scheduled refresh
→ official-event ingestion
→ market/sector regime
→ score + adversarial review
→ executable signal
→ risk engine
→ paper/live router
→ human confirmation when required
→ broker execution
→ fill reconciliation
→ position-state monitoring
→ exit management
→ immutable ledger
→ evaluation
→ version governance
```

最终原则：

> **Research decides eligibility. Risk decides size. Execution decides what can actually be done. Evidence decides whether the system earns the right to become more automated.**
