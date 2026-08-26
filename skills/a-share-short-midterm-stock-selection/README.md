# A-share Short/Mid-term Stock Selection

本目录实现 A 股短中期选股、入场、仓位、持仓管理、Forward Paper、人工实盘和逐步自动化验证。

## 先读上位规则

1. `../../shared/policy-precedence.md`
2. `../../shared/capital-allocation-and-entry-policy.md`
3. `../../shared/research-model-governance.md`
4. `../../shared/automation-execution-governance.md`（涉及 Paper / Live / 自动化时）
5. `SKILL.md`

跨策略资金比例、Size/Risk/Edge Cap、Operating Target/Hard Ceiling、默认策略批次和回撤熔断以 shared capital policy 为准。

Champion/Challenger、point-in-time、Benchmark、模型参数证据等级和 Promotion 以 shared research model governance 为准。

Paper/Live、Broker 对账、幂等、Kill Switch、程序化交易/券商合规和 `AUTO_ORDER` 晋级以 shared automation governance 为跨策略上位规则。

## 当前短中期核心规则

```text
Final Short Cap = min(Size Cap, Risk Cap, Edge Cap)
Actual Short Exposure <= Final Short Cap

Operating Target
- 单笔计划风险：0.5%
- 全部未平仓初始风险：≤2%
- 单一行业/因子初始风险：≤1%

Hard Ceiling
- 单笔计划风险：≤1%
- 全部未平仓初始风险：≤3%

默认建仓：50% Setup + 50% Confirmation
三级确认例外：50% / 30% / 20%
```

`Final Short Cap` 是上限，不是满仓要求。没有合格 setup 时允许保留现金。

后续批次只允许正向确认，禁止为了摊低成本向亏损趋势/催化仓位机械加码。

## Champion / Challenger

### Champion — 当前生产研究模型

```text
Technical 30
Capital Participation 30
Fundamentals 25
Catalyst 15
```

仍以 `references/scoring-system.md` 为准。

### Challenger — Shadow Only

新增：

`references/causal-challenger-model.md`

研究顺序强调：

```text
Eligibility
→ Expectation Change
→ Regime
→ Participation
→ Price Confirmation
→ Execution
→ Risk
```

Challenger 在完成 Forward-Test 和 Promotion Review 前不得替换 Champion，也不得改变真实订单。

对照协议：

`references/champion-challenger-forward-test.md`

## MFE / MAE 学习闭环

新增：

`references/trade-ledger-mfe-mae-extension.md`

每笔闭环交易除最终盈亏外至少记录：

```text
realized_R
MFE_R
MAE_R
holding_days
exit_reason
fees / tax / slippage / impact
market_regime
sector_regime
rule_violation
```

+1.5R/+2R、3–5 日 time review 继续作为当前治理初值，但不宣称最优；后续使用真实 MFE/MAE 分布校准。

## 当前文件结构

```text
skills/a-share-short-midterm-stock-selection/
├── README.md
├── SKILL.md
├── examples/
│   ├── README.md
│   ├── 2026-08-26-final-watchlist-case-study.md
│   └── 2026-08-26-final-watchlist.json
└── references/
    ├── scoring-system.md
    ├── causal-challenger-model.md
    ├── champion-challenger-forward-test.md
    ├── trade-ledger-mfe-mae-extension.md
    ├── holding-risk-management.md
    ├── industry-coverage-audit.md
    ├── data-source-policy.md
    ├── adversarial-review.md
    ├── evaluation-cases.md
    ├── research-basis.md
    ├── paper-live-automation-roadmap.md
    ├── validation-metrics-and-trade-ledger.md
    └── core-pool-snapshot-2026-08-26.md
```

## 推荐阅读顺序

1. `SKILL.md` — 当前 Champion 主流程、评分解释、入场/退出和输出合同。
2. `references/scoring-system.md` — 当前 Champion 30/30/25/15 评分。
3. `references/causal-challenger-model.md` — v3 因果 Challenger，Shadow Only。
4. `references/champion-challenger-forward-test.md` — 公平对照、成本、Regime 和 Promotion。
5. `references/trade-ledger-mfe-mae-extension.md` — 退出质量与 MFE/MAE。
6. `references/holding-risk-management.md` — risk sizing、持仓状态、止损、止盈、time stop、heat。
7. `references/data-source-policy.md` — point-in-time 和证据优先级。
8. `references/industry-coverage-audit.md` — 正式行业分类与覆盖率审计。
9. `references/adversarial-review.md` — red-team 审查。
10. `references/evaluation-cases.md` — 回归测试。
11. `references/research-basis.md` — 外部研究与监管依据。
12. `references/validation-metrics-and-trade-ledger.md` — Forward/Live 交易记录与评估指标。
13. `references/paper-live-automation-roadmap.md` — Paper→Live→Auto；仍受 shared automation governance 约束。
14. `examples/` — 历史案例，只用于 forward validation 和回溯。

## 36 股与 43 股两个历史文件的关系

`references/core-pool-snapshot-2026-08-26.md` 是**同日较早阶段的 36 股中间快照**。

随后经过行业覆盖、市场和事件进一步校验，形成同日较晚的 **43 股最终研究 whitelist**：

- `examples/2026-08-26-final-watchlist-case-study.md`
- `examples/2026-08-26-final-watchlist.json`

因此 `36 → 43` 是研究流程的版本演进，不是两个同时有效的当前名单。

这些文件都属于 Level 4 历史证据，当前执行必须重新运行 Skill。

## 自动化默认模式

```text
AUTO_MONITOR = true
AUTO_ORDER   = false
```

成熟路径：

```text
Research
→ Forward Paper
→ Manual Live
→ Automated Signals / Manual Orders
→ Human-confirmed Broker Execution
→ Limited Semi-auto
→ Full Auto only after Edge + Compliance + Reliability gates
```

模型 Promotion 与自动化 Promotion 分离。任何时候都优先错过交易，而不是在数据、持仓、券商状态或规则不确定时制造未知风险仓位。
