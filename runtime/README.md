# A-share Monitor Runtime MVP

`runtime/` 是仓库规则的**实现层**，不是新的 Policy、Skill 或交易模型 Source of Truth。

它目前只负责市场监控和研究状态生成：

```text
交易日识别
→ 全A实时/收盘行情
→ 涨停 / 跌停 / 炸板统计
→ A-Share Sentiment Score 0–100
→ Regime
→ 43股历史 whitelist 当日状态合并
→ 每日日报 JSON + Markdown
→ 市场成交额历史积累
```

默认：

```text
AUTO_MONITOR = true
AUTO_ORDER   = false
```

它不是券商交易机器人，也没有权限修改 shared policy、Skill 或 Champion。

## 上位治理

实现必须服从：

1. `../shared/policy-precedence.md`
2. `../shared/capital-allocation-and-entry-policy.md`
3. `../shared/research-model-governance.md`
4. `../shared/automation-execution-governance.md`
5. `../skills/a-share-short-midterm-stock-selection/SKILL.md`

情绪指数定义：

`../skills/a-share-short-midterm-stock-selection/references/a-share-sentiment-regime-index.md`

该指数当前状态是：

```text
RESEARCH / MONITOR INPUT
```

权重、阈值和 Regime 映射属于 Governance Parameter，不是已经验证的交易 Alpha。

## 数据 Provider

MVP 使用 AKShare 1.18.40：

```text
stock_zh_a_spot_em
stock_zt_pool_em
stock_zt_pool_dtgc_em
stock_zt_pool_zbgc_em
tool_trade_date_hist_sina
```

文档：
https://akshare.akfamily.xyz/data/stock/stock.html

AKShare 是聚合数据接口，不是交易所/Broker 真相源。进入 Manual Live / Semi-auto / Auto 前必须增加官方披露、券商行情和真实持仓交叉验证。

## 本地运行

```bash
python -m pip install -r runtime/requirements.txt
python -m compileall -q runtime
python -m unittest discover -s runtime/tests -v
python runtime/daily_monitor.py
```

输出：

```text
reports/daily/YYYY-MM-DD-market-monitor.json
reports/daily/YYYY-MM-DD-market-monitor.md
runtime/state/market_history.csv
```

这些输出属于**generated evidence / monitor state**，不是当前 Policy，也不是可直接执行的订单。

## 情绪指数

当前六个分量：

```text
Breadth                       25
Limit-up vs Limit-down        20
Board Quality / Broken Rate   15
Strong vs Weak Tail           15
Median Return                 10
Turnover Expansion            15
```

Regime：

```text
0–20   PANIC
20–40  RISK_OFF
40–60  NEUTRAL
60–80  RISK_ON
80–100 EUPHORIA
```

### RISK_OFF 的统一语义

`RISK_OFF` **不是仓库级绝对禁止交易状态**。

生产 Skill 的语义是：

```text
RISK_OFF
→ 提高入场质量要求
→ 风险使用更保守端
→ 更严格拒绝追高 / gap / 低质量突破
→ 仍需完整 Champion/approved-model + Reward/Risk + Risk Budget Gate
```

因此 Monitor 对 RISK_OFF 候选输出：

```text
RISK_REVIEW
```

而不是因为一个情绪分数直接生成永久 `NO_NEW_ENTRY`。

`PANIC` 或 `DATA_INSUFFICIENT` 则对当前趋势型新仓 fail closed。

## Candidate Pre-action 语义

日报可能产生：

```text
NO_NEW_ENTRY
WAIT_NO_CHASE
EVENT_REVIEW
REFRESH_FULL_GATES
REFRESH_SETUP
RISK_REVIEW
NO_ACTION_DATA_MISSING
```

全部只是研究/监控状态。

例如：

```text
REFRESH_FULL_GATES
```

只表示该股票值得重新获取当前财报、催化、技术、风险和账户状态并运行完整 Skill。

在以下信息没有全部刷新前，日报不能直接变成 BUY：

```text
current fundamentals
current catalyst/event
Champion / explicitly approved model
entry trigger
invalidation
Reward/Risk
position sizing
Final Short Cap
account symbol / cluster exposure
Broker state (when live)
```

## Report Governance References

日报保存：

```text
runtime_mode = MONITOR_ONLY
governance_refs:
  capital_policy
  automation_governance
  research_model_governance
  short_mid_skill
  sentiment_model
```

这里记录的是引用路径，不冒充真实 Broker 决策的完整 Governance Bundle。未来进入 Paper/Live cohort 时，再按 Level 1B 保存具体版本：

```text
capital_policy_version
automation_governance_version
research_model_governance_version
skill_version
strategy_version
model_version
```

## Fail Closed

以下任一情况不会补默认值后假装可以执行：

- 交易日历无法确认；
- 全A行情失败；
- 关键涨跌停数据严重缺失；
- 可用权重低于情绪指数最低要求；
- 股票当前行情缺失。

系统记录：

```text
provider_errors
DATA_INSUFFICIENT
NO_ACTION_DATA_MISSING
calendar_gate
```

即使为可观测性抓到了部分行情，交易日历未知时最终 Regime 仍会强制降级为 `DATA_INSUFFICIENT`。

## GitHub Actions

工作流：

`.github/workflows/a-share-daily-monitor.yml`

工作日北京时间15:40左右计划触发；GitHub cron 使用 UTC，实际有队列延迟。

当前流程：

```text
checkout
→ install pinned runtime dependencies
→ compileall
→ unit tests
→ run fail-closed monitor
→ commit generated report/history if changed
```

工作流的 `contents: write` 只用于提交生成的监控报告/历史状态；当前 runtime 不包含 Broker 下单模块。

## Runtime 测试

`runtime/tests/test_monitor.py` 至少回归：

- 缺核心数据 → `DATA_INSUFFICIENT`；
- PANIC 新仓 fail closed；
- RISK_OFF 不是自动硬否决；
- RISK_OFF 只有在更严格的 entry/risk gates 通过后才可能进入 READY；
- position thesis invalidated → EXIT。

## 下一阶段

Monitor MVP 之后才逐层研究：

```text
official disclosure adapter
current Champion scorer
Causal Challenger shadow scorer
account / strategy position ledger
paper broker
Broker read-only reconciliation
human-confirmed execution
```

每一步都必须重新通过 shared governance 和 consistency audit，不能从 Monitor 直接跳到 `AUTO_ORDER=true`。