# 长期养老组合：模拟仓 → 人工实盘 → 半自动 → 自动化交易路线图

> 目标：把长期养老 Skill 从研究方法升级为可持续运行、可审计、可前测、可逐步接入真实交易的完整系统。
>
> 上位规则：
>
> 1. `../../../shared/policy-precedence.md`
> 2. `../../../shared/capital-allocation-and-entry-policy.md`
> 3. `../../../shared/automation-execution-governance.md`
>
> 本文件属于 Level 4 示例/路线图，不得覆盖 shared policy。

## 1. 总体原则

自动化不是第一步。

```text
规则冻结
→ Forward Paper
→ 人工小规模实盘
→ 自动研究 + 人工下单
→ 人工确认后券商执行
→ 受约束半自动
→ 通过 Edge + Compliance + Reliability 门禁后才评估 Full Auto
```

默认：

```text
AUTO_MONITOR = true
AUTO_ORDER   = false
```

核心不是“尽快自动买卖”，而是证明：

- 数据 point-in-time 正确；
- Skill 判断可复现；
- shared policy 不会被绕过；
- 模拟与实盘可对账；
- 订单与持仓状态可恢复；
- 错误时系统 fail closed；
- 自动报单满足当期券商与程序化交易要求。

## 2. Phase 0 — 基线冻结

当前基线包括：

- 长期 `SKILL.md`；
- shared 资本/风险政策；
- shared 自动化执行治理；
- 十只养老股模型组合；
- 2026-08-26 历史市场验证快照。

案例：

`ten-stock-retirement-portfolio-2026-08-26.md`

任何规则或模型修改必须保存：

```text
旧版本
→ 修改原因 / hypothesis
→ 新版本
→ 预期改善
→ forward / live 验证
→ rollback 条件
```

禁止用未来结果静默改写旧判断。

## 3. Phase 1 — Forward Paper

### 3.1 目的

Paper 的第一目标是验证整个链路，而不是证明虚拟收益“好看”。

```text
研究
→ 估值
→ 目标权重
→ 建仓 Gate
→ 模拟成交
→ 持仓复核
→ 分红/公司行动
→ 调仓
→ 绩效归因
```

### 3.2 执行本金与标准化 NAV 必须分开

模拟系统同时保存：

```text
paper_capital_rmb = 用于真实股数、100股单位、费用、滑点、仓位计算
reporting_nav     = 100.00 起始的绩效指数，用于跨本金比较
```

不能只设置 `NAV=100` 后直接按 A 股 100 股交易单位模拟成交。

### 3.3 模拟建仓

十股案例的模型权重只是研究基线。每只股票只有在当时重新通过：

- 最新正式数据；
- 评分；
- 估值 / Max Buy Price；
- shared 单股与风险簇上限；
- Thesis / Balance / Valuation / Portfolio Gate；

之后才产生模拟订单。

策略批次从 shared policy 读取：

```text
默认：40 / 30 / 30
2批例外：60 / 40
4批例外：30 / 25 / 25 / 20
```

不能把 40/30/30 写成永远唯一模式。

如果没有合格买点：

```text
资金留在 paper cash pool
```

不为了满仓制造交易。

### 3.4 模拟成交约束

至少模拟：

- 100 股交易单位；
- 当期佣金、印花税等费用；
- 滑点；
- T+1 / 普通新买 A 股不能自由日内反向卖出；
- 涨跌停、跳空、停牌；
- 除权除息；
- 大额订单执行拆单。

必须区分：

```text
baseline / decision price
planned order price
simulated fill price
```

### 3.5 Paper 指标

组合：

- Total Return；
- Price Return；
- Dividend Return；
- Max Drawdown；
- Core / Growth Attribution；
- 单股贡献；
- 风险簇暴露；
- Turnover；
- Cash Drag；
- benchmark relative return。

单股：

- 决策时评分；
- 估值与 Max Buy Price；
- planned / simulated fill；
- MFE / MAE；
- 持有期回报；
- 分红贡献；
- thesis 状态；
- ADD/HOLD/WATCH/TRIM/EXIT 原因。

### 3.6 Paper → Manual Live 门禁

至少确认：

1. 数据抓取连续稳定；
2. 代码、复权、分红、财报时点正确；
3. 无未来数据泄漏；
4. 决策可由固定版本重复生成；
5. shared policy 未被绕过；
6. Paper 订单与绩效可解释；
7. 所有决策/成交有审计日志；
8. 错误状态能 fail closed。

长期策略建议先运行数月验证工程链路，并至少保留一个完整财报/分红周期继续观察策略本身。

## 4. Phase 2 — 人工实盘

### 4.1 原则

```text
系统：研究 + 估值 + 计算 + 订单建议
人：最终确认 + 券商下单
```

真实首笔仍遵循当时 shared policy 的策略批次，不自动一次买满目标仓位。

### 4.2 待确认订单卡

```yaml
as_of:
policy_version:
skill_version:
ticker:
action: BUY|ADD|TRIM|EXIT
reason:
current_price:
max_buy_price:
current_weight:
target_weight:
planned_tranche:
order_amount:
expected_shares:
post_trade_weight:
risk_cluster_after_trade:
thesis_gate:
balance_gate:
valuation_gate:
portfolio_gate:
data_state:
broker_state:
latest_official_sources:
human_approved:
```

### 4.3 Paper / Live 双轨

同时保留：

```text
Paper Portfolio
Live Portfolio
```

比较：

- 模拟与真实成交；
- 费用和滑点；
- 人工跳过/修改交易的影响；
- 纪律偏差；
- 分红到账与税费差异。

## 5. Phase 3 — 自动研究 + 人工下单

优先自动化：

- 行情/财报/公告/分红获取；
- point-in-time 校验；
- 财务评分；
- 估值；
- 目标权重和风险簇；
- Gate 检查；
- 订单建议；
- Paper 执行；
- 绩效与周报/季报。

保留人工：

- 最终买卖确认；
- 重大事件判断；
- 券商订单输入。

这是长期默认最值得优先实现的自动化阶段。

## 6. Phase 4 — 人工确认后的券商执行

```text
系统生成 Order Proposal
→ 人工检查 source / as_of / valuation / weight / tranche / cluster
→ explicit approval
→ broker adapter submit
→ broker acknowledgement / fill
→ reconcile
→ ledger append
```

Broker 实际成交和持仓是执行层真相源。

API 超时后不得盲目重复下单，必须先查询 broker 订单状态。

## 7. Phase 5 — 受约束半自动

仅允许预先批准的自动动作，例如：

- 执行已经人工批准的限价单；
- 取消超时未成交订单；
- 按预先批准规则缩小订单；
- 对账与告警；
- 预先定义的安全退出流程。

仍必须满足 shared automation governance 的：

- approved symbol；
- fresh data；
- current policy；
- position reconciliation；
- idempotency；
- Kill Switch；
- compliance state。

## 8. Phase 6 — Full Auto

默认关闭。

开启前至少要求：

1. Forward Paper 与真实 Live 有足够证据支持流程/策略；
2. broker adapter 通过 failure-injection；
3. restart/recovery 不会重复订单；
4. 本地持仓与 broker truth 可稳定 reconcile；
5. risk layer 独立于 strategy layer；
6. independent kill switch 可用；
7. 所有决定、订单、成交可审计；
8. 人工紧急干预仍然可用；
9. 实际账户的程序化交易/自动报单合规要求已重新核验。

技术上能报单不代表允许无人值守运行。

## 9. A 股程序化交易 / 券商合规门禁

跨策略统一规则见 `../../../shared/automation-execution-governance.md`。

当前研究基线包括：

- 中国证监会《证券市场程序化交易管理规定（试行）》
  https://www.csrc.gov.cn/csrc/c101954/c7480579/content.shtml
- 上海证券交易所程序化交易管理实施细则
  https://www.sse.com.cn/lawandrules/sselawsrules2025/trade/universal/c/c_20250612_10781696.shtml
- 深圳证券交易所程序化交易管理实施细则
  https://www.szse.cn/lawrules/rule/trade/t20250403_612770.html

进入任何自动报单阶段前，必须按**当时最新规则 + 实际券商 + 实际账户/API**重新确认报告、权限、频率、测试和接口要求。

本仓库不声称因为代码可用就已获得监管或券商许可。

## 10. Fail Closed / Kill Switch

以下任一异常默认停止新订单：

```text
行情过期/异常
官方披露抓取失败
代码/价格/复权冲突
policy / skill version 不一致
本地持仓 != broker 持仓
仓位/风险计算异常
重复订单检测
订单状态未知
broker connection 异常
连续下单失败
Hard Ceiling / circuit breaker
Policy Conflict
人工紧急停止
```

停止后只允许预定义安全动作；不得猜测状态后继续买入。

## 11. 核心系统架构

```text
Market / Disclosure / Corporate Actions
              ↓
Data Validation Layer
              ↓
Long-term Skill Engine
              ↓
Capital & Risk Policy Engine
              ↓
Decision State Engine
ADD / HOLD / WATCH / TRIM / EXIT
              ↓
Order Planner
              ↓
Paper / Human Approval / Broker Router
              ↓
Execution & Reconciliation Ledger
              ↓
Performance / Risk / Dividend Monitor
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
nav
cash
market_value
core_weight
growth_weight
max_drawdown
benchmark_nav
policy_version
skill_version
```

### positions

```text
timestamp
ticker
shares
avg_cost
market_price
market_value
target_weight
actual_weight
role
risk_cluster
action_state
score
max_buy_price
thesis_version
```

### decisions

```text
decision_id
timestamp
ticker
action
reason
source_snapshot
policy_version
skill_version
gates
human_approved
```

### orders

```text
order_id
client_order_id
decision_id
ticker
side
planned_price
planned_qty
actual_price
actual_qty
fees
taxes
slippage
status
broker
```

### dividends

```text
ticker
record_date
ex_date
pay_date
cash_per_share
shares_eligible
cash_received
tax
reinvest_decision_id
```

原始决策不能被后来结果覆盖，只能追加事件。

## 13. 运行节奏

### 每个交易日

- 更新价格和 NAV；
- 检查重大公告/风险事件；
- 权重漂移；
- 触发再研究条件；
- reconcile Paper/Live/Broker 状态。

### 每周

- 组合周报；
- Core/Growth 与风险簇；
- benchmark 对比；
- 待部署现金；
- 数据/订单异常统计。

### 财报季

- 自动发现新财报；
- 重做关键财务指标、评分和估值；
- 输出 `Previous -> Current` diff；
- 重大变化进入人工审批。

### 每年

- 完整养老组合复核；
- 更新长期/短中期 Size/Risk/Edge Cap；
- 重新评估 Core/Growth；
- 年度绩效归因；
- 决定是否升级 Skill / policy。

## 14. 从十股案例开始的实际路径

```text
Step 1  冻结 2026-08-26 十股模型基线
Step 2  建立 paper_capital_rmb + reporting_nav
Step 3  每日/每周更新价格、收益、权重和公告
Step 4  财报/重大事件触发 Skill 重评
Step 5  出现合格买点后，按当前 shared-policy 2/3/4 批模式模拟建仓
Step 6  Paper 工程链路稳定后，人工小规模实盘
Step 7  系统生成订单卡，人确认后执行
Step 8  积累真实成交、分红、滑点、回撤、override 数据
Step 9  Broker Adapter 先 Paper / Shadow，再 Human-confirmed Live
Step 10  完成合规、硬风控、对账、幂等、Kill Switch 后才评估 AUTO_ORDER
```

## 15. 成功标准

```text
研究可追溯
规则前后一致
数据 point-in-time 正确
模型权重不越过 shared policy
模拟股数与标准化 NAV 不混用
所有交易有决策记录
Paper / Live / Broker 可对账
绩效和分红可归因
异常 fail closed
策略升级有版本和 rollback
自动化不能绕过资本/风险/合规门禁
```

满足这些条件，才算形成从长期研究到真实交易的完整闭环。
