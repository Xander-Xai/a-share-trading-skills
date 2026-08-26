# A-share Short/Mid-term Stock Selection

本目录实现 A 股短中期选股、入场、仓位、持仓管理、Forward Paper、人工实盘和逐步自动化验证。

## 先读上位规则

1. `../../shared/policy-precedence.md`
2. `../../shared/capital-allocation-and-entry-policy.md`
3. `../../shared/research-model-governance.md`
4. `../../shared/automation-execution-governance.md`（涉及 Paper / Live / Broker / 自动化时）
5. `SKILL.md`

当前治理基线：

```text
Capital / Risk:         v2.3
Automation / Execution: v1.2
Research / Model:        v3
Short/Mid Skill:         v1.5.0
```

## 统一账户口径

账户级资本与集中度统一以：

```text
Stock Account Equity
= 长期股票市值
+ 短中期股票市值
+ 股票账户待配置现金
```

为分母。

短中期内部风险预算则使用当前**短中期策略 NAV**作为分母。

## 当前资本 / 风险规则

```text
Final Short Cap = min(Size Cap, Risk Cap, Edge Cap)
```

它是上限，不是满仓目标。

任何新订单必须满足：

```text
Planned Post-Trade Short Exposure <= Final Short Cap
```

没有合格 setup 时保留现金。

### Operating Target

```text
单笔计划风险：0.5% × 短中期策略 NAV
全部未平仓初始风险：≤2%
单一行业/因子初始风险：≤1%
```

### Hard Ceiling

```text
单笔计划风险：≤1%
全部未平仓初始风险：≤3%
```

Hard Ceiling 是计划风险上限；跳空、跌停等尾部场景可能造成实际亏损超过计划值，必须作为 risk event 记录，不能假设 stop 一定按计划价成交。

### 被动 CAP_BREACH

若已有仓位因上涨被动超过 Cap：

```text
CAP_BREACH
→ 禁止继续增加该方向风险
→ 进入再平衡/利润回流评估
→ 在可执行窗口恢复
```

不能用 ±5pp 漂移带合理化主动超限。

## 跨策略同股 / 同风险簇

同一股票若同时存在长期和短中期仓：

```text
Account Symbol Exposure
= Long Sleeve Exposure + Short/Mid-term Sleeve Exposure
```

风险簇：

```text
Account Cluster Exposure
= Long Cluster Exposure + Short/Mid-term Cluster Exposure
```

新订单必须同时通过：

```text
short internal capital limit
AND short risk heat
AND account symbol cap
AND account cluster cap
AND Final Short Cap
```

策略标签不能创造第二套风险额度。

Live/Broker 模式同时维护：

```text
Broker Net Position
Strategy Virtual Position: long
Strategy Virtual Position: short_mid
```

避免短中期 SELL 误卖长期逻辑份额。

## 建仓 / 补仓

默认：

```text
50% Setup
+ 50% Confirmation
```

三级确认例外：

```text
50% / 30% / 20%
```

第二、第三批必须由正向确认触发，禁止因为第一批亏损就机械摊低成本。

策略批次与大额 child-order 执行拆单不同。

## Champion / Challenger

### Champion — 当前生产研究模型

```text
Technical              30
Capital Participation  30
Fundamentals            25
Catalyst                15
```

见：`references/scoring-system.md`。

### Challenger — Shadow Only

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

Challenger 在完成 Forward-Test 和 Promotion Review 前：

- 不替换 Champion；
- 不改变真实订单；
- 不与 Champion Live 业绩混算。

公平对照：`references/champion-challenger-forward-test.md`。

## MFE / MAE 学习闭环

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

`+1.5R/+2R`、3–5日 time review 等继续作为当前治理初值，不宣称最优，后续由 Forward 数据和 MFE/MAE 校准。

## 36 股与 43 股历史文件

`references/core-pool-snapshot-2026-08-26.md`：同日较早的36股中间快照。

同日晚些时候形成43股最终研究 whitelist：

- `examples/2026-08-26-final-watchlist-case-study.md`
- `examples/2026-08-26-final-watchlist.json`

`36 → 43` 是历史研究流程演进，不是两个同时有效的当前名单。两者均为 Level 4 证据，当前执行必须重新运行 Skill。

## Paper → Live → Automation

默认：

```text
AUTO_MONITOR = true
AUTO_ORDER   = false
```

成熟路径：

```text
Research
→ Forward Paper
→ Small-size Manual Live
→ Automated Research / Manual Orders
→ Human-confirmed Broker Execution
→ Limited Semi-auto
→ Full Auto only after Edge + Compliance + Reliability gates
```

每个 cohort / 决策 / 订单保存：

```text
capital_policy_version
automation_governance_version
research_model_governance_version
skill_version
strategy_version
model_version
```

模型 Promotion 与 Automation Promotion 是不同 Gate。

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

1. `SKILL.md`
2. `references/scoring-system.md`
3. `references/causal-challenger-model.md`
4. `references/champion-challenger-forward-test.md`
5. `references/trade-ledger-mfe-mae-extension.md`
6. `references/holding-risk-management.md`
7. `references/data-source-policy.md`
8. `references/industry-coverage-audit.md`
9. `references/adversarial-review.md`
10. `references/evaluation-cases.md`
11. `references/research-basis.md`
12. `references/validation-metrics-and-trade-ledger.md`
13. `references/paper-live-automation-roadmap.md`
14. `examples/`

任何时候都优先错过交易，而不是在数据、规则、模型状态、持仓或 Broker 状态不确定时制造未知风险。