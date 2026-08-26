# 长期养老组合：Forward Paper → Manual Live → Semi-auto → Auto 路线图 v3

> 本文件属于 Level 4 示例/路线图，不覆盖 shared policy。
>
> 上位规则：
>
> 1. `../../../shared/policy-precedence.md`
> 2. `../../../shared/capital-allocation-and-entry-policy.md`
> 3. `../../../shared/research-model-governance.md`
> 4. `../../../shared/automation-execution-governance.md`

## 1. 目标与默认状态

把长期养老 Skill 从研究方法升级为可持续运行、可审计、可 Forward-Test、可逐步接入真实交易的系统。

```text
规则冻结
→ Forward Paper
→ 人工小规模实盘
→ 自动研究 + 人工下单
→ 人工确认 Broker 执行
→ Limited Semi-auto
→ Full Auto only after Edge + Compliance + Reliability gates
```

默认：

```text
AUTO_MONITOR = true
AUTO_ORDER   = false
```

自动化首先要证明**数据、研究、风险、对账和恢复机制正确**，而不是证明“代码可以下单”。

## 2. Governance Bundle

每个 cohort、决策和订单必须保存：

```text
capital_policy_version
automation_governance_version
research_model_governance_version
skill_version
strategy_version
model_version
```

当前历史基线在新运行时应读取当时最新值，不能只保存模糊 `policy_version`。

## 3. 账户口径与虚拟子账

账户级分母：

```text
Stock Account Equity
= 长期股票市值
+ 短中期股票市值
+ 股票账户待配置现金
```

若同一股票同时属于长期和短中期：

```text
Account Symbol Exposure
= Long Sleeve Exposure + Short/Mid-term Sleeve Exposure
```

风险簇同理聚合。

Broker 模式同时维护：

```text
Broker Net Position       = 券商实际持仓
Strategy Virtual Position = long / short_mid 逻辑子账
```

任何长期 SELL/TRIM/ADD 都必须避免误操作另一策略虚拟份额。

## 4. Phase 0 — 基线冻结

冻结：

- 当前长期 `SKILL.md`；
- 三类 Level-1 governance；
- 估值/Expected IRR 方法；
- 十股历史模型组合；
- benchmark 与成本假设；
- 数据源和 point-in-time 规则。

历史案例：

`ten-stock-retirement-portfolio-2026-08-26.md`

任何规则修改保存：

```text
old_version
hypothesis
new_version
supporting_evidence
forward_test_start
promotion_decision
rollback_condition
```

禁止用未来结果静默改写旧判断。

## 5. Phase 1 — Forward Paper

### 5.1 Paper 目标

Paper 首先验证链路：

```text
point-in-time data
→ quality / score
→ Bear/Base/Bull IRR
→ Max Buy Price
→ account-level caps
→ strategy tranche
→ simulated fill
→ position review
→ dividend/corporate action
→ rebalance
→ performance attribution
```

### 5.2 Paper Capital 与 Reporting NAV

必须分开：

```text
paper_capital_rmb = 股数、100股单位、费用、滑点、仓位、风险
reporting_nav     = 100.00 起始标准化绩效指数
```

不能用 `NAV=100` 直接模拟 A 股股数。

### 5.3 十股模型权重的正确解释

十股案例中的：

```text
model_long_book_weight
```

是长期已部署权益仓内部权重。

运行时先换算：

```text
model_total_account_weight
= model_long_book_weight × planned_long_exposure
```

再叠加：

```text
account_single_stock_cap
remaining_account_cluster_capacity
valuation / Expected IRR allowance
cross-sleeve same-symbol exposure
```

不能把 long-book 12% 直接和账户级10%–12%上限比较。

### 5.4 模拟建仓

每只股票只有在当前重新通过：

- 最新正式数据；
- score / hard exclusions；
- Bear/Base/Bull Expected IRR；
- Max Buy Price；
- Thesis / Balance / Valuation / Portfolio Gate；
- 账户级同股/风险簇 Cap；
- cross-sleeve exposure；

之后才产生 Paper order。

策略批次从 Level 1A 读取：

```text
默认：40 / 30 / 30
2批例外：60 / 40
4批例外：30 / 25 / 25 / 20
```

无合格买点：

```text
资金留在 paper cash pool
```

### 5.5 模拟成交约束

至少模拟：

- 100股单位；
- 当前佣金/印花税等费用；
- 滑点与必要时的 impact；
- T+1；
- 涨跌停/跳空/停牌；
- 除权除息；
- 分红到账；
- 大额订单执行拆单。

区分：

```text
baseline_price
planned_entry
simulated_fill
```

### 5.6 CAP_BREACH

Paper 同样模拟市场价格导致的被动超限：

```text
CAP_BREACH
→ no new increase
→ rebalance review
→ executable recovery
```

不能假设超限后一定在当日按理想价格成交减仓。

### 5.7 Paper 指标

组合：

- Total Return；
- Price Return；
- Dividend Return；
- Max Drawdown；
- Core/Growth attribution；
- 单股贡献；
- 风险簇贡献；
- Cash Drag；
- Turnover；
- Benchmark Total Return；
- Excess Return；
- CAP_BREACH 次数与处理结果。

单股：

- 原始 score；
- Bear/Base/Bull IRR；
- Max Buy Price；
- planned / simulated fill；
- MFE / MAE；
- price/dividend/total return；
- thesis state；
- ADD/HOLD/WATCH/TRIM/EXIT；
- prediction error。

### 5.8 Paper → Manual Live Gate

至少确认：

1. point-in-time 数据稳定；
2. 财报/分红/复权/代码时点正确；
3. 无未来数据泄漏；
4. 固定版本可重现决策；
5. Benchmark 采用一致的 Total Return 口径；
6. account-level symbol/cluster 聚合正确；
7. Paper order/费用/分红可解释；
8. Governance Bundle 完整；
9. fail closed 可工作。

长期策略需要继续跨财报与分红周期验证，不因数月收益好看就直接提高自动化等级。

## 6. Phase 2 — Manual Live

### 原则

```text
系统：研究 + 估值 + IRR + 仓位 + Order Proposal
人：最终确认 + 券商下单
```

真实首笔仍按当前 Level 1A 策略批次执行。

### Order Proposal

```yaml
as_of:
capital_policy_version:
automation_governance_version:
research_model_governance_version:
skill_version:
strategy_version:
model_version:
strategy_id:
sleeve: long
ticker:
action: BUY|ADD|TRIM|EXIT
reason:
current_price:
bear_irr:
base_irr:
bull_irr:
base_max_buy_price:
model_long_book_weight:
planned_long_exposure:
model_total_account_weight:
long_exposure_before:
short_mid_exposure_same_symbol:
account_symbol_exposure_after:
account_symbol_cap:
account_cluster_exposure_after:
account_cluster_cap:
planned_tranche:
planned_price:
planned_qty:
thesis_gate:
balance_gate:
valuation_gate:
portfolio_gate:
data_state:
broker_state:
model_status:
human_approved:
```

### Paper / Live 双轨

同时保存 Paper 和 Live，比较：

- 模拟 vs 实际 fill；
- 费用/滑点/impact；
- 人工 override；
- 纪律偏差；
- 分红税费与到账；
- Benchmark / Excess Return；
- 本地虚拟仓 vs Broker 净持仓。

## 7. Phase 3 — Automated Research / Manual Order

优先自动化：

- 行情/公告/财报/分红获取；
- point-in-time 校验；
- score；
- Expected IRR / Max Buy Price；
- 账户级单股/风险簇聚合；
- Gate 检查；
- Order Proposal；
- Paper execution；
- Benchmark / performance / attribution；
- 周报/季报。

保留人工：最终买卖确认、重大事件判断、券商订单输入。

这是长期账户最适合长期保留的默认自动化层。

## 8. Phase 4 — Human-confirmed Broker Execution

```text
Order Proposal
→ human review
→ explicit approval
→ cross-sleeve reconciliation
→ broker adapter submit
→ acknowledgement / fill
→ reconcile
→ append immutable ledger event
```

API timeout 后先查询 Broker 订单状态，不盲目重试。

## 9. Phase 5 — Limited Semi-auto

仅允许预先批准的自动动作，例如：

- 执行已经人工批准的限价单；
- 取消超时未成交单；
- 因价格变化自动**缩小**订单满足 Cap；
- 对账与告警；
- 预定义安全退出流程。

必须满足：

```text
current governance bundle
approved symbol
fresh data
point-in-time valid
current model status valid
Broker + virtual-position reconciliation
account symbol/cluster caps
idempotency
Kill Switch
compliance state
```

状态未知时 fail closed。

## 10. Phase 6 — Full Auto

默认关闭。

开启前至少要求：

1. 长期研究流程有足够 Forward/Live 证据；
2. broker adapter 通过 failure injection；
3. restart/recovery 不重复订单；
4. Broker truth 与策略虚拟子账稳定 reconcile；
5. risk layer 独立于 strategy layer；
6. independent Kill Switch 可用；
7. 决策/订单/成交全审计；
8. 人工 emergency intervention 保留；
9. 实际账户程序化交易/券商要求已重新核验。

技术上能报单不代表允许无人值守运行。

## 11. 系统架构

```text
Market / Disclosure / Corporate Actions
              ↓
Point-in-time Data Validation
              ↓
Long-term Skill Engine
              ↓
Expected IRR / Benchmark Engine
              ↓
Capital & Account Risk Engine
              ↓
ADD / HOLD / WATCH / TRIM / EXIT
              ↓
Order Planner
              ↓
Paper / Human Approval / Broker Router
              ↓
Broker Net Position + Strategy Virtual Ledger
              ↓
Execution / Reconciliation
              ↓
Performance / Risk / Dividend / Benchmark Monitor
              ↓
Review / Alerts / Research Refresh
```

建议代码结构：

```text
src/
├── data/
├── research/
├── portfolio/
├── execution/
├── monitoring/
└── storage/
```

## 12. 最小数据库 / Ledger

### portfolio_snapshots

```text
timestamp
portfolio_id
paper_or_live
stock_account_equity
long_market_value
short_mid_market_value
cash
reporting_nav
benchmark_nav
total_return
benchmark_total_return
max_drawdown
capital_policy_version
automation_governance_version
research_model_governance_version
skill_version
strategy_version
```

### positions

```text
timestamp
strategy_id
sleeve
stock_code
virtual_shares
broker_account_total_shares
avg_cost
market_price
market_value
account_symbol_exposure
account_cluster_exposure
model_long_book_weight
model_total_account_weight
action_state
score
base_irr
base_max_buy_price
thesis_version
```

### decisions

```text
decision_id
timestamp
strategy_id
stock_code
action
reason
source_snapshot
capital_policy_version
automation_governance_version
research_model_governance_version
skill_version
strategy_version
model_version
gates
human_approved
```

### orders

```text
order_id
client_order_id
idempotency_key
decision_id
strategy_id
stock_code
side
planned_price
planned_qty
actual_price
actual_qty
fees
taxes
slippage
impact
status
broker
```

### dividends

```text
stock_code
record_date
ex_date
pay_date
cash_per_share
shares_eligible
cash_received
tax
reinvest_decision_id
```

原始决策只能追加后续事件，不能被结果覆盖。

## 13. 运行节奏

### 每个交易日

- 更新价格、NAV、Benchmark；
- 检查重大公告；
- 检查账户权重与 CAP_BREACH；
- reconcile Broker / virtual positions；
- 触发必要再研究。

### 每周

- 组合周报；
- Core/Growth；
- 风险簇；
- 待配置现金；
- Benchmark / Excess Return；
- 数据/订单异常。

### 财报季

- 发现新财报；
- 重做 score / Expected IRR / Max Buy Price；
- 输出 Previous → Current diff；
- 重大变化人工复核。

### 每年

- 完整组合复核；
- 更新 Size/Risk/Edge Cap；
- 年度 Total Return attribution；
- 评估 Skill / governance 是否需要 Challenger/升级。

## 14. 从十股案例开始

实际路线：

```text
十股历史 baseline
→ 当前时点重新运行长期 Skill
→ 建立 paper_capital_rmb
→ 逐只按估值/Gate/Cap触发 Paper 建仓
→ 保存 reporting_nav 与 Total Return Benchmark
→ 连续 Forward 观察
→ 再决定是否进入小规模 Manual Live
```

十股不是“必须同时买满”的指令；WATCH、估值不足或账户 Cap 不允许时，对应资金保留现金。

## 15. 程序化交易 / 合规

统一以：

`../../../shared/automation-execution-governance.md`

为准。任何实际自动报单前必须重新联网核验当期监管规则，并向实际券商确认账户、接口、报告、测试、频率和权限要求。