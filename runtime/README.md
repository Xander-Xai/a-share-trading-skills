# A-share Monitor Runtime MVP

这个目录把仓库里的“规则”落成最小可运行监控系统。

## 当前能力

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
AUTO_ORDER = false
```

它是 Monitor，不是券商交易机器人。

## 数据 Provider

MVP 使用 AKShare 1.18.40：

```text
stock_zh_a_spot_em
stock_zt_pool_em
stock_zt_pool_dtgc_em
stock_zt_pool_zbgc_em
tool_trade_date_hist_sina
```

官方文档：
https://akshare.akfamily.xyz/data/stock/stock.html

AKShare 是聚合数据接口。进入 Manual Live / Semi-auto / Auto 前必须增加官方披露和真实券商行情/持仓交叉验证。

## 本地运行

```bash
python -m pip install -r runtime/requirements.txt
python runtime/daily_monitor.py
```

输出：

```text
reports/daily/YYYY-MM-DD-market-monitor.json
reports/daily/YYYY-MM-DD-market-monitor.md
runtime/state/market_history.csv
```

## 情绪指数

完整定义：

`../skills/a-share-short-midterm-stock-selection/references/a-share-sentiment-regime-index.md`

当前六个分量：

```text
Breadth                       25
Limit-up vs Limit-down        20
Board Quality / Broken Rate   15
Strong vs Weak Tail           15
Median Return                 10
Turnover Expansion            15
```

分数映射：

```text
0–20   PANIC
20–40  RISK_OFF
40–60  NEUTRAL
60–80  RISK_ON
80–100 EUPHORIA
```

权重和阈值属于研究治理参数。

## 候选 Pre-action 的语义

日报可能产生：

```text
NO_NEW_ENTRY
WAIT_NO_CHASE
EVENT_REVIEW
REFRESH_FULL_GATES
REFRESH_SETUP
RISK_REVIEW
```

这些都不是券商订单。

例如：

```text
REFRESH_FULL_GATES
```

只表示该股票值得重新获取当前财报/催化/技术/风险数据并运行完整 Skill。

在以下信息没有全部刷新前，不允许从日报直接变成 BUY：

```text
current fundamentals
current catalyst/event
Champion/approved model score
entry trigger
invalidation
Reward/Risk
position sizing
account symbol/cluster exposure
broker state
```

## Fail Closed

以下任一情况不会“补一个默认值然后继续下单”：

- 交易日历无法获取；
- 全A行情失败；
- 关键涨跌停数据失败；
- 数据可用权重低于情绪指数最低要求；
- 股票当前行情缺失。

系统会记录 `provider_errors` 和 `DATA_INSUFFICIENT` / `NO_ACTION_DATA_MISSING`。

## GitHub Actions

`.github/workflows/a-share-daily-monitor.yml`

计划在工作日北京时间 15:40 左右触发。GitHub cron 使用 UTC，实际运行时间可能有队列延迟。

工作流：

```text
checkout
→ install frozen provider version
→ run monitor
→ commit generated report/history if changed
```

中国法定节假日由交易日历判断，市场关闭时不读取交易数据。

## 下一阶段

Monitor MVP 之后才是：

```text
official disclosure adapter
current Champion scorer
Causal Challenger shadow scorer
position ledger
paper broker
broker read-only reconciliation
human-confirmed execution
```

任何阶段都受 `shared/automation-execution-governance.md` 约束。
