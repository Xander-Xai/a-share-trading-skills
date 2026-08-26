# 长期养老组合：模拟仓 → 人工实盘 → 半自动 → 自动化交易路线图

> 目标：把长期养老 Skill 从“研究方法”升级为一个可持续运行、可审计、可回测/前测、可逐步接入真实交易的完整系统。
>
> 上位规则：任何阶段都必须遵循 `../../../shared/policy-precedence.md` 与 `../../../shared/capital-allocation-and-entry-policy.md`。

## 1. 总体原则

自动化不是第一步。

正确顺序：

```text
规则冻结
→ 模拟仓验证
→ 人工小规模实盘
→ 人机协同执行
→ 受约束自动执行
→ 持续监控与版本迭代
```

核心目标不是“尽快自动买卖”，而是先证明：

- 数据是对的；
- Skill 给出的判断可以复现；
- 仓位、建仓、补仓、退出规则不会前后漂移；
- 模拟结果与真实成交差异可解释；
- 系统在错误数据、行情剧烈变化和接口故障时会主动停止，而不是继续交易。

## 2. Phase 0 — 基线冻结

本阶段已经建立：

- 长期 Skill；
- shared 资金和风险政策；
- 规则优先级；
- 十只养老股模型组合示例；
- 2026-08-26 初始市场验证快照。

基线文件：

`ten-stock-retirement-portfolio-2026-08-26.md`

以后任何模型、规则、目标权重修改都必须记录：

```text
旧版本
→ 修改原因
→ 新版本
→ 预期改善
→ 实际结果
```

不能用未来结果悄悄改写过去的投资判断。

## 3. Phase 1 — 模拟仓 / Forward Test

### 3.1 目的

模拟仓不是为了证明“虚拟收益很好”，而是验证整个执行链路：

```text
研究
→ 估值
→ 目标权重
→ 建仓触发
→ 持仓复核
→ 分红
→ 调仓
→ 绩效归因
```

### 3.2 建议运行方式

使用标准化 NAV，例如：

```text
初始 NAV = 100.00
```

这样不同真实本金都可以比较，不需要因为虚拟资金大小改变策略。

十只模型组合使用示例文件中的目标权重，但每只股票只有满足当时 `Max Buy Price`、评分和组合 Gate 后才记入模拟成交。

如果某只股票没有出现可接受买点：

```text
对应资金留在模拟现金池
```

不能为了让组合“满仓”而制造交易。

### 3.3 模拟成交必须考虑现实约束

不能简单用收盘价假设无成本成交。

至少加入：

- A股 100 股交易单位；
- 佣金；
- 印花税（卖出时按最新规则）；
- 滑点假设；
- 除权除息；
- 停牌；
- 涨跌停导致的不可成交；
- 大额订单的执行拆单。

模拟引擎必须区分：

```text
Decision Price
Planned Order Price
Actual Simulated Fill Price
```

### 3.4 模拟阶段重点指标

组合：

- Total Return；
- Price Return；
- Dividend Return；
- Max Drawdown；
- Core / Growth Attribution；
- 风险簇暴露；
- Turnover；
- Cash Drag；
- 相对宽基/红利类全收益基准的超额收益。

单股：

- 买入时评分；
- 买入时估值；
- Max Buy Price；
- MFE / MAE；
- 持有期回报；
- 分红贡献；
- 退出原因；
- thesis 是否正确；
- 执行是否正确。

### 3.5 模拟阶段通过标准

不使用“赚了多少钱”作为唯一门槛。

至少确认：

1. 数据抓取连续稳定；
2. 股票代码、复权、分红、财报时间点无明显错误；
3. 不出现未来数据泄漏；
4. 建仓/补仓/退出能由固定规则重复生成；
5. shared policy 没有被下层模块绕过；
6. 绩效计算能够解释；
7. 所有订单和决策都有审计日志。

建议至少先运行数月验证工程链路，同时保留至少一个完整年度/年报周期的数据来评价长期策略本身。

## 4. Phase 2 — 人工实盘验证

### 4.1 原则

进入真实资金后仍然保持：

```text
系统负责研究 + 计算 + 生成交易计划
人负责最终确认
```

第一阶段真实买入不直接一次完成全部目标仓位，而遵循长期 Skill：

```text
默认第一批 = 单股目标仓位的 40%
```

后续 30% / 30% 必须重新通过 Gate。

### 4.2 实盘订单卡

系统每次只生成“待确认订单”，包含：

```yaml
as_of:
ticker:
action: BUY|ADD|TRIM|EXIT
reason:
current_price:
max_buy_price:
target_weight:
current_weight:
planned_tranche:
order_amount:
expected_shares:
post_trade_weight:
risk_cluster_after_trade:
thesis_gate:
balance_gate:
valuation_gate:
portfolio_gate:
latest_official_sources:
```

用户确认后才在券商端执行。

### 4.3 实盘与模拟必须双轨记录

真实系统同时保留：

```text
Paper Portfolio
Live Portfolio
```

用于比较：

- 模拟成交与真实成交差异；
- 手续费和滑点；
- 人工跳过交易带来的影响；
- 情绪和纪律偏差；
- 实际分红到账差异。

## 5. Phase 3 — 半自动交易系统

当模拟和人工实盘链路稳定后，进入“Agent 生成、人工确认”的半自动阶段。

### 5.1 系统架构

```text
┌─────────────────────────────┐
│ Market / Disclosure Sources │
│ 行情 / 财报 / 公告 / 分红    │
└──────────────┬──────────────┘
               ↓
┌─────────────────────────────┐
│ Data Validation Layer       │
│ as_of / 复权 / 去重 / 冲突   │
└──────────────┬──────────────┘
               ↓
┌─────────────────────────────┐
│ Long-term Skill Engine      │
│ 筛选 / 评分 / 估值 / Thesis  │
└──────────────┬──────────────┘
               ↓
┌─────────────────────────────┐
│ Portfolio Policy Engine     │
│ shared policy / 动态仓位     │
│ 风险簇 / Core-Growth         │
└──────────────┬──────────────┘
               ↓
┌─────────────────────────────┐
│ Decision State Engine       │
│ ADD/HOLD/WATCH/TRIM/EXIT    │
└──────────────┬──────────────┘
               ↓
┌─────────────────────────────┐
│ Order Planner               │
│ 批次 / 100股 / 限价 / 拆单   │
└──────────────┬──────────────┘
               ↓
     ┌─────────┴─────────┐
     ↓                   ↓
Paper Broker       Human Approval
                         ↓
                    Live Broker
                         ↓
┌─────────────────────────────┐
│ Execution & Audit Ledger    │
│ 成交 / 费用 / 滑点 / 版本    │
└──────────────┬──────────────┘
               ↓
┌─────────────────────────────┐
│ Performance / Risk Monitor  │
│ NAV / 回撤 / 分红 / 归因     │
└──────────────┬──────────────┘
               ↓
         Review / Alerts
               ↓
         Research Engine
```

### 5.2 需要的核心模块

建议代码层未来拆成：

```text
src/
├── data/
│   ├── market_data.py
│   ├── disclosures.py
│   ├── corporate_actions.py
│   └── validators.py
├── research/
│   ├── retirement_skill.py
│   ├── valuation.py
│   └── scoring.py
├── portfolio/
│   ├── allocator.py
│   ├── risk_clusters.py
│   ├── rebalance.py
│   └── dividend_cash_pool.py
├── execution/
│   ├── order_planner.py
│   ├── paper_broker.py
│   ├── live_broker_adapter.py
│   └── execution_guard.py
├── monitoring/
│   ├── portfolio_metrics.py
│   ├── attribution.py
│   └── alerts.py
└── storage/
    ├── decision_log.py
    ├── order_log.py
    └── portfolio_snapshot.py
```

这只是未来系统结构建议，不要求现在一次实现全部模块。

## 6. Phase 4 — 受约束自动执行

只有前面阶段长期稳定后，才允许系统自动发单。

### 6.1 自动化不能拥有无限权限

自动执行必须有硬限制：

- 只能交易预先批准的股票池；
- 默认禁止融资杠杆；
- 不能突破 shared policy 单股/风险簇上限；
- 不能因为价格下跌自动补仓；
- 后续批次必须重新通过四个 Gate；
- 不能在关键数据 `MISSING / CONFLICT` 时买入；
- 不能使用过期 `Max Buy Price`；
- 不能覆盖 `EXIT` 级治理/财务风险；
- 所有自动操作必须写入不可缺失的审计日志。

### 6.2 Kill Switch

任何一个条件出现都应停止新订单：

```text
行情源异常
官方披露抓取失败
股票代码/价格冲突
组合权重计算异常
订单金额异常
券商接口状态未知
连续下单失败
规则版本不一致
Policy Conflict
```

停止之后只能：

```text
读取数据
管理已有订单
告警
等待人工恢复
```

不得自动猜测并继续运行。

### 6.3 双重确认模式

建议长期保留两种运行模式：

```text
AUTO_MONITOR = true
AUTO_ORDER = false
```

这是半自动默认。

只有长期验证后才允许：

```text
AUTO_ORDER = true
```

即使开启自动下单，也应保留高风险操作人工确认，例如：

- 新股票首次进入组合；
- 单笔金额超过设定阈值；
- EXIT 全清；
- 财报/监管重大事件后的第一笔交易；
- shared policy 版本刚升级后的首次执行。

## 7. Phase 5 — 持续学习与策略升级

自动化系统不能通过“自己修改规则”来追逐近期收益。

规则升级必须走版本化流程：

```text
发现问题
→ 建立 hypothesis
→ 历史回测 / forward test
→ 与旧规则并行比较
→ 人工审核
→ 更新 policy / Skill version
→ consistency audit
→ 再进入生产
```

禁止：

```text
最近三次亏损
→ 自动把仓位翻倍

最近某只股票大涨
→ 自动提高该类股票评分权重
```

## 8. 数据库 / 日志最小表结构

### portfolio_snapshots

```text
timestamp
portfolio_id
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
decision_id
ticker
side
planned_price
planned_qty
actual_price
actual_qty
fees
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

## 9. 定期任务

### 每个交易日

- 更新收盘价和组合 NAV；
- 检查重大公告和风险事件；
- 更新目标/实际权重漂移；
- 检查是否触发再研究条件。

### 每周

- 生成组合周报；
- Core/Growth 与风险簇暴露；
- 与基准比较；
- 检查待部署现金。

### 财报季

- 自动发现新财报；
- 重新计算关键财务指标；
- 重做评分和估值；
- 输出 `Previous -> Current` diff；
- 重大变化进入人工审批队列。

### 每年

- 完整养老组合深度复核；
- 重新检查长期/短中期 Size/Risk/Edge Cap；
- 重新评估 Core/Growth；
- 做年度绩效归因和规则复盘；
- 决定是否升级 Skill / policy。

## 10. 从本示例开始的实际路径

```text
Step 1
冻结 2026-08-26 十股模型组合

Step 2
建立模拟 NAV 和持仓记录

Step 3
每天/每周自动更新价格、收益、权重

Step 4
财报/公告触发 Skill 重新评分

Step 5
出现合格买点后，按 40/30/30 模拟建仓

Step 6
模拟链路稳定后，在真实账户人工执行第一批

Step 7
系统生成订单卡，人确认后执行

Step 8
积累真实成交、分红、滑点、回撤数据

Step 9
引入券商 Adapter，先 Paper，再 Live

Step 10
在硬风控、审计日志、Kill Switch 完成后，才评估 AUTO_ORDER
```

## 11. 成功标准

最终系统不是“能自动下单”就算成功，而应满足：

```text
研究可追溯
规则前后一致
数据 point-in-time 正确
所有仓位有风险理由
所有交易有决策记录
模拟和实盘可对账
绩效可归因
错误会停机
策略升级有版本
自动化不能绕过风险政策
```

达到这些条件，才算形成从长期研究到真实交易的完整闭环。
