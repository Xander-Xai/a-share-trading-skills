# A-share Short/Mid Monitor Runtime MVP

`runtime/` 是当前仓库规则的**实现层**，不是新的 Policy、Skill 或交易模型 Source of Truth。

本目录当前主体仍是 **short_mid Monitor MVP**，并新增一个跨策略的**人工下单前风险授权辅助工具** `pretrade_cli.py`。它不是券商交易机器人，也不会自动下单。

当前职责：

```text
交易日识别
→ 全A实时/收盘行情
→ 涨停 / 跌停 / 炸板统计
→ A-Share Sentiment Score 0–100
→ Regime
→ short_mid runtime universe 当日状态合并
→ 每日日报 JSON + Markdown
→ 市场成交额历史积累
```

默认：

```text
strategy_id = a_share_short_mid
sleeve      = short_mid
AUTO_MONITOR = true
AUTO_ORDER   = false
```

它不是券商交易机器人，也没有权限修改 shared policy、长期 Skill、短中期 Skill 或 Champion。

## Strategy Boundary

读取：

- `../shared/strategy-boundary-contract.md`
- `../shared/canonical-pit-data-contract.md`

当前 Runtime 中的：

```text
Regime
crowding
Reward/Risk
short tactical state
```

只属于 `short_mid`。

如果 short/mid engine 收到：

```text
sleeve = long
```

必须 fail closed：

```text
NO_ACTION_STRATEGY_MISMATCH
```

长期系统未来将拥有独立的 Quality / Cash Flow / Expected IRR / Valuation Engine，不由本 Monitor 直接改变长期 ADD/HOLD/TRIM/EXIT。

## 上位治理

实现必须服从：

1. `../shared/policy-precedence.md`
2. `../shared/capital-eligibility-and-investor-risk-philosophy.md`
3. `../shared/pre-trade-order-authorization-contract.md`
4. `../shared/capital-allocation-and-entry-policy.md`
5. `../shared/research-model-governance.md`
6. `../shared/automation-execution-governance.md`
7. `../shared/strategy-boundary-contract.md`
8. `../shared/canonical-pit-data-contract.md`
9. `../skills/a-share-short-midterm-stock-selection/SKILL.md`

情绪指数定义：

`../skills/a-share-short-midterm-stock-selection/references/a-share-sentiment-regime-index.md`

状态：

```text
RESEARCH / MONITOR INPUT
```

权重、阈值和 Regime 映射属于 Governance Parameter，不是已经验证的交易 Alpha。

## Runtime Universe

默认配置：

```text
runtime/config/short_mid_universe.json
```

不再默认读取：

```text
skills/.../examples/<dated-watchlist>.json
```

原因：`examples/` 是 Level-4 历史证据，不能作为未来 production-current universe 的默认真相源。

Runtime universe 必须显式声明：

```text
strategy_id
sleeve
runtime_universe_version
as_of
source_type
stocks
```

当前配置是 2026-08-28 approved short/mid research set 的 runtime bootstrap。未来 Production Research 应由 current universe service/config/database 生成并版本化，而不是人工永久维护某个历史 snapshot。

仍保留 `--watchlist` CLI 参数名以兼容现有调用，但其输入现在应是 strategy-tagged runtime universe payload。

## 数据 Provider

MVP 使用固定版本：

```text
akshare==1.18.40
pandas>=2.2,<3.0
```

Spot 行情：

```text
Primary  : stock_zh_a_spot_em  / Eastmoney
Fallback : stock_zh_a_spot     / Sina
```

其他输入：

```text
stock_zt_pool_em
stock_zt_pool_dtgc_em
stock_zt_pool_zbgc_em
tool_trade_date_hist_sina
```

当 Eastmoney Spot 失败而 Sina fallback 可用时：

```text
spot_provider = SINA_FALLBACK
data_confidence <= MEDIUM
```

不同 Provider 股票代码统一为 6 位数字代码，例如：

```text
sh600000 → 600000
sz000001 → 000001
bj430017 → 430017
```

Primary 与 fallback 都不可用时：

```text
spot_provider = UNAVAILABLE
regime = DATA_INSUFFICIENT
```

Fallback 用于提高**监控可用性**，不是把聚合数据源升级为 Live 真相源。

AKShare 是聚合数据接口，不是交易所/Broker 真相源。进入 Manual Live / Semi-auto / Auto 前必须增加官方披露、券商行情和真实持仓交叉验证，并检查数据 permitted-use / license metadata。

文档：
https://akshare.akfamily.xyz/data/stock/stock.html

## 本地运行

```bash
python -m pip install -r runtime/requirements.txt
python -m pip check
python -m compileall -q runtime src
python -m unittest discover -s runtime/tests -v
python runtime/daily_monitor.py
```

输出：

```text
reports/daily/YYYY-MM-DD-market-monitor.json
reports/daily/YYYY-MM-DD-market-monitor.md
runtime/state/market_history.csv
```

`market_history.csv` 只有在有效交易日且成功取得全市场成交额时才创建/更新。即使 history 文件不存在，fail-closed 日报也必须独立保留。

这些输出属于 **Generated Evidence / Runtime State**，不是 Policy，也不是可直接执行的订单。

## Machine Contracts

生产实现开始从文档向机器契约迁移：

```text
src/core/strategy_boundary.py
→ strategy_id / sleeve 校验

src/core/pit.py
→ PIT metadata / replay visibility 校验
```

这两个模块只是第一批 Core Contract，不代表完整 Data Platform 已经完成。

## Pre-Trade Authorization CLI

当用户准备真实买入/加仓时，先运行：

```bash
python runtime/pretrade_cli.py
```

程序会先询问并校验：

- 本次真正可承担股票风险的闲钱；
- Stock Account Equity；
- 应急金是否独立；
- 计划持有期是否存在近期现金需求；
- 是否包含借款/融资/抵押资金；
- 主观风险意愿与客观风险承受能力；
- 当前该股/同风险簇/短中期总暴露；
- 当前已占用 Portfolio Heat / Factor Heat；
- 当前失效位下该笔交易已有仓位的 `current_trade_planned_risk_rmb`；
- Final Short Cap；
- ENTRY/ADD 触发是否确认；
- 短中期失效价和本次整笔交易最大可承受计划亏损；
- 证券板块及申报数量规则（MAIN / CHINEXT / STAR / BSE）。

输出状态：

```text
AUTHORIZED
NEED_USER_INPUT
BLOCKED
NO_TRADE_POSITION_TOO_SMALL_FOR_RISK_BUDGET
NO_TRADE_TRANCHE_ROUNDS_BELOW_MINIMUM
```

只在 `AUTHORIZED` 时输出非零的 `planned_entry_shares`。所有缺失关键输入默认 fail closed。

核心计算在：

`../src/core/pretrade_risk_gate.py`

回归测试：

`tests/test_pretrade_risk_gate.py`

注意：该 CLI 是**风险授权/仓位计算辅助**，不是 Broker 下单接口。仓库无法物理阻止用户绕过系统自行下单，因此任何未授权的增仓应记录为 `UNAUTHORIZED_MANUAL_RISK_INCREASE`。

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

`RISK_OFF` 不是仓库级绝对禁止交易状态。

生产 Short/Mid Skill 语义：

```text
RISK_OFF
→ 提高入场质量要求
→ 风险使用更保守端
→ 更严格拒绝追高 / gap / 低质量突破
→ 仍需完整 Champion/approved-model + Reward/Risk + Risk Budget Gate
```

Monitor 对 RISK_OFF 候选输出：

```text
RISK_REVIEW
```

而不是单凭情绪分数生成永久 `NO_NEW_ENTRY`。

`PANIC` 或 `DATA_INSUFFICIENT` 对当前趋势型新仓 fail closed。

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

全部只是 `short_mid` 研究/监控状态。

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

日报现在保存：

```text
strategy_id
sleeve
runtime_mode = SHORT_MID_MONITOR_ONLY
universe metadata

governance_refs:
  capital_policy
  automation_governance
  research_model_governance
  strategy_boundary
  pit_data_contract
  short_mid_skill
  sentiment_model
```

这里只记录引用路径，不冒充真实 Broker 决策的完整 Governance Bundle。进入 Paper/Live cohort 后必须保存具体版本：

```text
capital_policy_version
automation_governance_version
research_model_governance_version
skill_version
strategy_id
sleeve
strategy_version
model_version
```

## Fail Closed

以下任一情况不会补默认值后假装可执行：

- 交易日历无法确认；
- Primary/Fallback Spot 均失败；
- 关键涨跌停数据严重缺失；
- 可用权重低于情绪指数最低要求；
- 股票当前行情缺失；
- runtime universe 缺失；
- `strategy_id / sleeve` 不匹配。

系统记录：

```text
provider_errors
spot_provider
DATA_INSUFFICIENT
NO_ACTION_DATA_MISSING
calendar_gate
spot_provider_gate
strategy_context_gate
```

## GitHub Actions

工作流：

`.github/workflows/a-share-daily-monitor.yml`

工作日北京时间15:40左右计划触发；GitHub cron 使用 UTC，实际可能存在队列延迟，因此该机制适合 EOD research monitor，不应被理解为精确盘中 execution scheduler。

当前流程：

```text
checkout
→ install pinned runtime dependencies
→ pip check
→ compileall
→ unit tests
→ run fail-closed monitor
→ verify runtime/workflow did not change during run
→ commit generated report/history if changed
```

`contents: write` 只用于提交生成的报告/历史状态；当前 runtime 不包含 Broker 下单模块。

## Runtime 测试

`runtime/tests/` 当前至少回归：

- Eastmoney/Sina 代码标准化；
- 缺核心数据 → `DATA_INSUFFICIENT`；
- PANIC 新仓 fail closed；
- RISK_OFF 不是自动硬否决；
- RISK_OFF 只有在更严格的 entry/risk gates 通过后才可能进入 READY；
- position thesis invalidated → EXIT；
- long sleeve 不能进入 short/mid engine；
- PIT `available_at` 不能早于 `published_at`；
- replay 时间早于 `available_at` 时记录不可见；
- strategy visibility 必须被执行。

## 下一阶段

当前批准的 Production 演进基础见：

`../research/production-system-evolution-report-2026-08-28.md`

Short/Mid 优先顺序：

```text
Canonical PIT Data Store
→ current universe generation
→ current Champion engine
→ ERG engine
→ historical replay
→ Forward/Ablation/Placebo
→ Paper ledger / broker simulator
→ Broker read-only reconciliation
→ human-confirmed execution
→ optional semi-auto
```

长期系统单独演进：

```text
Long Quality Engine
→ Cash Flow / Dividend Engine
→ Expected IRR / Valuation Engine
→ Long Paper Portfolio
→ automated research / manual order as a valid end state
```

不能从 Monitor 直接跳到 `AUTO_ORDER=true`，也不能因为短中期系统代码化而把其时间尺度和验证标准强加给长期策略。

## Repository Consistency Audit

`runtime/repository_consistency_audit.py` 对当前生产治理做 fail-closed 静态检查，包括：

- Level 0 / Level 1A / Level 1B / Level 1C 当前版本；
- Long / Short-Mid Skill 当前版本；
- 两个生产 Skill 是否读取 Level 0；
- pretrade core 是否包含整笔交易剩余风险、长期 sleeve 暴露和证券特定申报数量规则；
- 当前 README 是否存在治理版本漂移；
- Daily Monitor / Repository Governance workflow 是否覆盖 `shared/**`、`skills/**`、`src/**`、`runtime/**` 与根 README。

本地运行：

```bash
python runtime/repository_consistency_audit.py
```

该审计只检查当前生产/治理契约。日期化历史审计、examples、历史 reports 可以保留当时版本，不因今天的规则升级而被静默改写。
