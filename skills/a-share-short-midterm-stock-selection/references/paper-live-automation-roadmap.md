# Short/Mid-term: Paper → Manual Live → Assisted → Automated Roadmap v3

> 本文件定义短中期策略特有的 Forward/Live 验证方式。
>
> 跨策略上位规则：
> - capital/risk：`../../../shared/capital-allocation-and-entry-policy.md`
> - research/model：`../../../shared/research-model-governance.md`
> - automation/execution：`../../../shared/automation-execution-governance.md`

若本文件冲突，以 shared 为准。

## 1. 目标与默认模式

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

模型 Promotion 与 Automation Promotion 分离。

## 2. Governance Bundle

任何 cohort、Paper、Live 和订单保存：

```text
capital_policy_version
automation_governance_version
research_model_governance_version
skill_version
strategy_version
model_version
```

不能只写一个 `policy_version`。

## 3. 闭环架构

```text
Locked Universe
      ↓
Point-in-time Data / Official Evidence
      ↓
Research Engine
Champion + Challenger Shadow
      ↓
Signal / Intent
Trigger + Invalidation + R
      ↓
Risk Engine
Final Short Cap + Heat + Account Symbol/Cluster Caps
      ↓
Paper / Human-approved Live Router
      ↓
Broker Net Position + Strategy Virtual Position
      ↓
Reconciliation / Fill
      ↓
Position State
      ↓
Ledger: MFE / MAE / R / Costs / Violations
      ↓
Evaluation / Model Governance
```

Research 不能突破风险；Execution 不能绕过研究 Hard Gate。

## 4. Phase 0 — Research Baseline

公开 baseline fixture（合成数据）：

- `../examples/synthetic-watchlist-case-study.md`
- `../examples/synthetic-watchlist.json`

真实 user-specific universe 和候选状态须留在本地 private runtime；公开 fixtures 不复刻任何历史个人证券列表。

当前 Champion 为30/30/25/15；Causal Challenger 只 Shadow。

Phase 0 最低要求：同输入、同 `as_of`、同治理版本应产生实质一致的分类与研究结论。

## 5. Phase 1 — Forward Paper

### Paper Capital / NAV

```text
paper_capital_rmb = 股数、证券特定申报数量规则、费用、风险和仓位
reporting_nav     = 100.00起始标准化绩效指数
```

不能把 `NAV=100` 当 RMB100 执行本金。

### 每日流程

```text
收盘后
→ refresh market/sector/events
→ Champion rescore
→ Challenger shadow score
→ define next-session trigger / invalidation
→ paper intents

下一交易日
→ trigger 成立才模拟成交
→ T+1 / 涨跌停 / gap / liquidity / fees / slippage
→ update position state

收盘/事件后
→ stop / partial / time-stop
→ MFE / MAE
→ append ledger
```

### Conservative Fill

- gap 穿越信号不假设刚好信号价成交；
- 跌停不可卖不假设 stop 已成交；
- 模拟税费/佣金/滑点/impact；
- 尊重证券所属市场/板块的最小买入数量与递增单位；
- 普通新买 A 股不能自由日内反向卖出；
- 除权除息不当真实技术破位。

### Cap / account aggregation

Paper 也必须模拟：

```text
Final Short Cap
Account Symbol Exposure = Long + Short/Mid
Account Cluster Exposure = Long + Short/Mid
```

若没有真实 long sleeve，可使用明确的 frozen mock long exposure；不得默认为0后在 Live 又忽略长期仓。

### Paper → Manual Live

治理参考，不是自动晋级：

- 有足够 Forward 闭环样本；
- 尽可能覆盖多个 regime；
- 成本后 Expectancy 为正；
- 无 unresolved hard-policy violation；
- drawdown 可接受；
- 结果非极少数赢家主导；
- 决策/成交可重建；
- account aggregation 和 CAP_BREACH 逻辑正确。

## 6. Phase 2 — Small-size Manual Live

目标：验证 Paper Edge 到真实执行的差距。

- 每笔真实订单人工完成；
- 风险使用 Operating Target 保守端；
- Paper/Live 尽量双轨；
- 保存真实 fill、费用、滑点、拒单、部分成交；
- 保存 override；
- Broker 净持仓与策略虚拟子账每日对账；
- 不因 Paper 好就加风险。

## 7. Phase 3 — Automated Research / Manual Orders

优先自动化：

- 数据获取；
- point-in-time / event checks；
- Champion scoring；
- Challenger shadow；
- factor exposure；
- trigger alerts；
- Paper fills；
- performance / MFE / MAE；
- daily/weekly reports。

保留人工：最终买卖确认、异常事件判断、券商订单输入。

## 8. Phase 4 — Human-confirmed Broker Execution

```text
system detects setup
→ risk engine creates Order Proposal
→ cross-sleeve / broker reconciliation
→ human reviews
→ explicit approval
→ broker adapter submit
→ acknowledgement/fill
→ reconcile
→ append ledger
```

Order Proposal 至少显示：

- code/name；
- quote timestamp；
- model/version；
- setup/trigger；
- acceptable entry；
- invalidation；
- expected R/R；
- shares/exposure；
- planned trade risk；
- Final Short Cap / post-trade short exposure；
- long same-symbol exposure；
- account symbol/cluster exposure after trade；
- portfolio/factor heat；
- event risk；
- compliance / kill switch；
- human approval。

## 9. Phase 5 — Limited Semi-auto

只自动执行预先批准动作，例如：

- 已人工批准的限价单；
- 已批准 stop/exit；
- stale order cancel；
- 因价格变化自动**缩小**订单以满足风险。

必须：

```text
approved symbols
allowed order types
max order value/shares
price collar / slippage
max daily orders
Final Short Cap
account symbol/cluster caps
strategy heat/factor heat
event lockout
data freshness
broker + virtual-position reconciliation
idempotency
kill switch
```

任何状态未知 fail closed。

## 10. Phase 6 — Full Auto

默认禁用。

Promotion 需要：

1. Champion Edge 由 Forward/Live 支持；
2. broker adapter 通过 failure injection；
3. restart/recovery 不重复单；
4. broker truth 与策略虚拟子账稳定 reconcile；
5. risk layer 不可被 strategy 绕过；
6. independent kill switch；
7. 决策/订单/成交全审计；
8. 人工 emergency intervention；
9. 实际账户程序化交易/券商合规重新核验。

模型晋级不等于自动执行晋级。

## 11. Cross-strategy Position / Order Conflict

同一股票可同时属于长期和短中期研究，但执行必须维护：

```text
Broker Net Position
Strategy Virtual Position: long
Strategy Virtual Position: short_mid
```

下单前检查：

- 同股账户合计暴露；
- 同因子账户合计暴露；
- short sell/reduction 是否会误卖 long virtual shares；
- long/short 两策略是否同时产生相反订单；
- 可卖股数 / T+1；
- netting 后是否仍需订单。

未解决冲突 → `Policy Conflict` / fail closed。

## 12. CAP_BREACH

新订单不得主动让计划暴露超过 Cap。

市场上涨导致被动超限：

```text
state = CAP_BREACH
→ no new increase
→ rebalance / profit-transfer review
```

记录为 passive breach，不与主动 planned-risk violation 混为一谈。

## 13. Regulatory / Compliance

自动提交 A 股指令前，按当时最新规则和实际券商确认程序化交易报告、接口、权限、测试和频率要求。

研究基线：

- CSRC《证券市场程序化交易管理规定（试行）》
  https://www.csrc.gov.cn/csrc/c101954/c7480579/content.shtml
- SSE 程序化交易管理实施细则
  https://www.sse.com.cn/lawandrules/sselawsrules2025/trade/universal/c/c_20250612_10781696.shtml
- SZSE 程序化交易管理实施细则
  https://www.szse.cn/lawrules/rule/trade/t20250403_612770.html

链接不是永久合规证明。

## 14. Fail Closed / Kill Switch

停止新订单条件包括：

```text
stale/broken data
filing fetch failure
code/price conflict
governance version mismatch
broker != local position
strategy virtual positions != broker net
cross-strategy order conflict
position/risk calculation error
duplicate order
unknown broker status
submission result unknown
repeated order failures
Hard Ceiling / circuit breaker
Policy Conflict
manual emergency stop
```

API timeout 后先查 broker order state，禁止盲目重试。

## 15. Metrics

### Strategy

- closed trades；
- Expectancy R；
- Profit Factor；
- Max Drawdown / Calmar；
- win/payoff；
- return by setup/regime/factor/model。

### Trade

- MFE/MAE；
- entry/exit efficiency；
- time-stop；
- gap loss；
- event isolation。

### Execution

- modeled vs actual fill；
- slippage / fees / tax / impact；
- reject/partial fill；
- duplicate/reconciliation errors。

### Process

- rule violations；
- manual override；
- data incidents；
- no-trade discipline；
- passive CAP_BREACH vs active cap violation。

## 16. Parameter Governance

任何新参数先进入 research hypothesis / Challenger：

```text
proposal
reason
mechanism
sample
holdout/forward plan
overfitting risk
version
rollback
```

生产模型不得根据近期收益自动改规则。

## 17. End-state Loop

```text
locked universe
→ point-in-time refresh
→ Champion + Challenger Shadow
→ executable signal
→ account-level risk engine
→ Paper/Live router
→ human confirmation if required
→ broker execution
→ reconciliation
→ holding-state monitor
→ exit
→ immutable ledger
→ MFE/MAE/report
→ model governance
```

核心原则：

```text
Research decides eligibility.
Risk decides size.
Account aggregation decides capacity.
Execution decides feasibility.
Evidence decides model/automation promotion.
```
