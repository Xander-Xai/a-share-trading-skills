---
name: a-share-short-midterm-stock-selection
description: Select, rank, size, and manage A-share stocks for short-to-medium-term holding from a user-supplied universe. Uses fresh public data, A-share execution constraints, risk-based sizing, industry-coverage auditing, adversarial review, and explicit entry/exit rules.
compatibility: Requires fresh public market data, official A-share disclosures, and web research.
metadata:
  author: yandexuanxuan
  version: "1.7.1"
  market: "China A-share"
---

# A-share Short/Mid-term Stock Selection

## 0. Governing policy

执行前读取：

1. `../../shared/policy-precedence.md`
2. `../../shared/capital-eligibility-and-investor-risk-philosophy.md`
3. `../../shared/capital-allocation-and-entry-policy.md`
4. `../../shared/research-model-governance.md`
5. 涉及 Paper / Live / Broker / 自动化时读取 `../../shared/automation-execution-governance.md`
6. 研究迭代、实验优先级与 Promotion 前置顺序读取 `references/iteration-roadmap.md`

职责：

- Level 1A：Stock Account Equity、Final Short Cap、Operating Target/Hard Ceiling、账户级同股/风险簇聚合、策略批次、熔断；
- Level 1C：当前 Champion、Challenger、point-in-time、Benchmark、模型 Promotion；
- Level 1B：Paper/Live、Broker 净持仓、策略虚拟子账、对账、幂等、Kill Switch、合规。

本 Skill 可以更保守，不能更激进。

## 1. Purpose

构建可重复、证据驱动的 A 股短中期流程。

默认：

- 短期：通常5–15个交易日；
- 中期延长：通常15–60个交易日，必须 fresh re-underwriting。

亏损短期交易不得仅因不愿止损而漂移成长持有。

五个独立决策：

1. Capital Eligibility
2. Security Eligibility
3. Timing
4. Execution
5. Sizing

## 2. Universe Lock

用户给出截图、watchlist 或固定股票池时：

- 提取 `stock_code + stock_name`；
- 按代码去重；
- 研究前冻结 universe；
- 未经明确授权不引入池外股票；
- 保留每只股票 provenance；
- 少于 N 只通过硬门禁时，返回更少，不强塞弱股。

## 3. Point-in-time Research

每次分析声明 `as_of`，只使用该时点已经公开的信息。

禁止：

- 用后来财报证明更早判断；
- 用后来价格行动证明更早入场；
- 把未发布报告当事实；
- 使用未来 ST/退市/指数成分。

关键数据不足标记 `Insufficient`，不能成为 executable trade。

事件驱动研究的 `first_tradable_timestamp` 必须按 `references/session-aware-execution-calendar.md` 解析，不得再机械使用“15:00 后公告 = 下一交易日”。至少区分：

```text
information_timestamp
first_exchange_tradable_timestamp
first_broker_executable_timestamp
first_tradable_timestamp
session_type
```

无法确认交易所时段、停牌状态、券商支持或可执行流动性时标记 `UNRESOLVED` 并 fail closed。

## 4. Capital Allocation、Risk 与统一分母

退休旧规则：

```text
short-term capital <= 30% of total savings
```

当前：

```text
Final Short Cap = min(Size Cap, Risk Cap, Edge Cap)
```

`Final Short Cap` 以 shared 定义的 `Stock Account Equity` 为分母，是**上限，不是满仓目标**。

新订单必须满足：

```text
Planned Post-Trade Short Exposure <= Final Short Cap
```

没有合格 setup：

```text
unused capacity → cash
```

### 被动 CAP_BREACH

市场上涨可能让实际暴露在无新订单情况下超过 Cap：

```text
state = CAP_BREACH
→ no new increase
→ rebalance/profit-transfer review
```

不能把这种被动越界解释为允许主动下单超限，也不能用 ±5pp 漂移带合理化新增风险。

### Operating Target

以当前短中期策略 NAV 为风险分母：

```text
planned loss per trade: 0.5%
aggregate open initial risk: <=2%
aggregate initial risk per industry/factor: <=1%
```

### Hard Ceiling

```text
planned loss per trade: <=1%
aggregate open initial risk: <=3%
```

Hard Ceiling 是**计划风险上限**，不保证跳空/跌停下实际亏损绝不超过。发生尾部超损必须记录 risk event。

### Portfolio structure

默认运营限制，shared 更严格时取 shared：

- 同时持仓最多5只；
- 同行业不超过2只；
- 同主导因子不超过2只；
- 不机械摊低亏损成本；
- 默认不用融资杠杆。

## 5. 跨策略同股 / 同因子聚合

如果同一股票同时存在长期与短中期：

```text
Account Symbol Exposure
= Long Sleeve Exposure + Short/Mid-term Sleeve Exposure
```

风险簇同理：

```text
Account Cluster Exposure
= Long Cluster Exposure + Short/Mid-term Cluster Exposure
```

任何短中期新订单必须同时通过：

```text
short internal capital limit
AND short risk Heat
AND account symbol cap
AND account cluster cap
AND Final Short Cap
```

策略标签不能创造第二套风险额度。

涉及 Broker 执行时，策略虚拟子账与 Broker 净持仓必须 reconcile，不能让短中期卖单误卖长期逻辑份额。

## 6. Champion / Challenger Governance

### Champion — 当前生产研究模型

当前 Champion：

```text
Technical: 30
Capital Participation: 30
Fundamentals: 25
Catalyst: 15
```

详细规则见 `references/scoring-system.md`。

### Challenger — Shadow Only

`references/causal-challenger-model.md` 只做 Shadow，并在 v1.1 接入 ERG：

```text
Eligibility
→ Business / Survival Quality
→ Expectation–Reaction Gate
   ├─ Expectation Baseline
   ├─ Surprise
   ├─ Economic Materiality
   ├─ Prepricing
   └─ Post-event Reaction
→ Market / Sector Regime
→ Participation / Relative Strength
→ Research State
→ Price Structure / Execution
→ Risk
→ Position State
```

ERG 读取：

- `references/expectation-reaction-gate.md`；
- `references/erg-output-schema.md`；
- `references/erg-validation-checklist.md`。

公平对照与增量验证读取：

- `references/champion-challenger-forward-test.md`；
- `references/erg-forward-test-extension.md`；
- `references/statistical-promotion-guard.md`；
- `references/disagreement-ledger-and-negative-control.md`。

ERG/Challenger 均为 Shadow。它们不能改变 Champion、Paper/Live 真实订单或 shared risk cap，除非完成 Level 1C Promotion。

对 Challenger 采用：

```text
State First, Rank Second
```

Research State 先决定资格；Score 仅用于可比较状态内部排序，不能覆盖 Hard Gate 或把未确认事件机械变成交易。

所有 `CONFIRMED` 状态必须同时记录：

```text
confirmation_basis =
EVENT_REACTION |
TREND_STRUCTURE |
REGIME_RELATIVE_STRENGTH |
MEAN_REVERSION_SETUP |
MULTI_EVIDENCE |
OTHER_EXPERIMENTAL
```

避免把“趋势已确认”与“事件预期差已确认”混成同一种语义。

## 7. Market / Sector Regime

分类：

- risk-on / trend-friendly；
- neutral / rotational；
- mean-reverting（如模型明确识别）；
- risk-off / high-failure-rate。

使用宽基结构、breadth、成交额、板块相对强度、龙头持续性、突破失败率。

Risk-off：提高入场质量、降低仓位、更加拒绝晚期突破和 gap chasing。

## 8. Industry、Factor、Role

每只股票标记：

1. formal industry；
2. dominant economic factor；
3. role：leader / sub-sector leader / quality second tier / cyclical beta / event-driven / turnaround。

行业标签不等于经济风险独立。

### Industry taxonomy

当用户要求行业覆盖率时，默认使用分析时点有效的申万2021一级行业分类，除非用户指定其他体系。

- 每只股票只计一个 primary Level-1 industry；
- factor tag 单独保存；
- 不把概念板块混入一级行业计数；
- 重组/转型时检查当前主营。

详细见 `references/industry-coverage-audit.md`。

## 9. Industry Coverage Audit

覆盖率是**研究完整性诊断，不是配额**。

必须区分：

```text
taxonomy_total
universe_industries
core_pool_industries
uncovered_but_available
absent_from_universe
```

对于 `uncovered_but_available`，只比较 in-universe 股票；没有通过硬 Gate 的候选就保持未覆盖。

维护：

```text
core quality pool
+ qualified coverage supplement pool
```

覆盖补充不自动成为同优先级交易候选。

## 10. Leader / Concept Authenticity Gate

Leader 至少需要两类可验证证据，例如市场份额/产能、利润规模、客户渠道、技术IP、资源成本、品牌标准。

热点主题必须有真实收入、利润、订单、产品、客户或产能证据。

Narrative adjacency 不得获得 leader/catalyst 溢价。

## 11. Fundamental Quality Gate

使用最新正式报告，检查：

- 收入；
- 归母/扣非；
- OCF 或行业替代指标；
- margin；
- 应收/存货；
- 杠杆/融资；
- 减值/商誉；
- 客户/供应商集中；
- 治理、调查、诉讼、质押、担保；
- 估值 sanity。

银行/券商/保险不机械套制造业现金流指标。

## 12. Champion Scoring

Base score = 100：

```text
Technical 30
Capital Participation 30
Fundamentals 25
Catalyst 15
```

解释：

- 80+：高优先研究候选，仍需入场不过度延伸；
- 75–79：带 trigger 的候选；
- 65–74：watch；
- <65：通常不开新仓。

总分不能覆盖 Hard Veto。行业覆盖不加分。

权重是 Governance Parameter，不宣称学术最优。

## 13. Entry Quality Gate

检查：

- MA5/MA10/key pivot 距离；
- gap/涨停行为；
- volume vs price progress；
- breakout/retest/reclaim；
- 附近阻力；
- stop distance；
- realistic Reward/Risk；
- 未来3–5个交易日事件风险；
- 板块周期位置。

偏好 confirmed breakout、first healthy pullback/retest、reclaim、整理后龙头加强。

避免情绪 gap chase、低量突破、放量滞涨、二元事件前盲买。

## 14. A-share Execution Risk Gate

读取 `references/session-aware-execution-calendar.md`。

考虑：

- 普通新买 A 股不能自由日内反向卖出；
- gap-through-stop；
- 涨跌停；
- 停牌/复牌；
- 除权除息图形扭曲；
- 流动性/滑点；
- 当前交易所是否存在 15:05–15:30 盘后固定价格交易窗口；
- 证券是否具备对应交易资格；
- 15:00 停牌状态；
- 券商/账户是否支持相应委托；
- 信息发布时间是否仍允许形成可执行决策。

Stop 是失效计划，不是保证成交价。真实 gap/limit stress 超预算时缩仓或拒绝。

事件发生在 15:00 之后时，必须通过 session-aware 路由求解 `first_tradable_timestamp`；不能仅凭“收盘后”三个字自动推到次日。

## 15. Position Sizing

```text
E = planned entry
S = invalidation
R_account = allowed currency loss
shares ≈ R_account / abs(E-S)
```

向下取可执行整手，再叠加：

- short internal exposure；
- Final Short Cap；
- account symbol cap；
- account cluster cap；
- risk Heat。

止损更宽 → 仓位更小；不能为了让仓位“有意义”而放宽失效点。

## 16. Entry Tranches

退休旧 `3/4/4`。

默认：

```text
50% Setup Entry
50% Confirmation Entry
```

三级确认例外：

```text
50% / 30% / 20%
```

后续批次只在正向确认后加入，例如 breakout holds、retest succeeds、相对强度改善、板块/量价/催化继续验证。

禁止：

```text
first tranche loses
→ buy more only to lower average cost
```

大订单 child orders 是执行拆单，不增加策略批次。

## 17. Holding States

```text
strengthening
intact
weakening
invalidated
```

详细见 `references/holding-risk-management.md`。

- 不机械摊低成本；
- 仅正向确认后 ADD；
- 约3–5日明显不工作且相对强度恶化，可考虑 time stop/reduction；
- 超15日必须重新写 thesis、score、stop、risk。

ERG Challenger 另外维护两个独立字段：

```text
research_state = REJECT / WATCH / CANDIDATE / CONFIRMED / INVALIDATED
position_state = FLAT / READY / ENTRY / HOLD / ADD / TRIM / EXIT / COOLDOWN
```

因此 `CONFIRMED` 不等于必须立即买入。

## 18. Stop Rules

```text
price / invalidation stop
+ thesis stop
+ time stop
```

顺序：

```text
define invalidation
→ stop distance
→ risk budget
→ shares
```

不得入场后才发明 stop，不得向更亏方向放宽。

对于 Challenger，每个交易在入场前还必须声明 `strategy_type`。EVENT_MOMENTUM / TREND 亏损后不得静默改名为 MEAN_REVERSION 或长期持有。

## 19. Profit Management

一级优先：

```text
R multiple
+ technical structure
+ original setup target
```

偏好现实 `Reward/Risk >=2`。

约 +1.5R～+2R 可考虑兑现约1/3–1/2，其余趋势/trailing。

历史百分比只作辅助：

- 传统/周期约 +3%～+5%；
- 成长/科技约 +6%～+10%。

冲突时 R/结构优先。

这些阈值是当前治理初值，通过 MFE/MAE Forward 数据校准，不宣称最优。

## 20. Portfolio Construction

```text
whitelist
→ daily rescore
→ 8–10 watch
→ 3–5 executable
→ 0–3 actual new entries
```

大 shortlist 不是同时持仓。

Portfolio heat 是计划失效点亏损，不是投入金额。

## 21. Circuit Breakers

从短中期策略账户高水位：

```text
-4% → reduce exposure / lower-end risk
-6% → no new positions; review
-8% → pause; formal review before resume
```

不重置高水位来消除信号。

## 22. Short-to-medium Transition

超过15个交易日必须重新：

- thesis；
- 官方财报/事件；
- Champion score；
- regime；
- invalidation；
- risk；
- 确认不是 loss aversion。

失败则按原计划减仓/退出。

## 23. Adversarial Review

至少运行：

- universe；identity；point-in-time；
- taxonomy / coverage；
- concept；accounting；event；
- technical；execution；
- portfolio/factor；source；alternative；
- no-trade；policy precedence；
- cross-sleeve symbol/cluster；
- Champion/Challenger contamination auditor。

ERG Challenger 额外运行：

- expectation baseline quality / consensus dispersion；
- positive-news prepricing / chase attack；
- event-specific reaction vs generic momentum；
- strategy-type drift；
- trial-count / data-snooping；
- ERG complexity / ablation attack；
- disagreement/opportunity-cost audit；
- placebo/negative-control audit；
- session-aware `first_tradable_timestamp` audit。

Hard Gate 失败就移除并重跑。

## 24. Source Policy

读取 `references/data-source-policy.md`。

- material facts 优先官方披露；
- 当前决策使用当前行情；
- 明确 `as_of`；
- unknown remains unknown；
- vendor “主力流入”仅辅助；
- 正式行业分类来自声明 taxonomy。

ERG 事件记录必须额外保留：

```text
information_timestamp
first_tradable_timestamp
source_tier
expectation_baseline_type
expectation_confidence
```

低置信 expectation 不得伪装为 verified surprise。

## 25. Required Output

筛选 universe 时报告：

1. data coverage + `as_of`；
2. market regime；
3. Champion ranked pool；
4. 若 Challenger 开启，独立 Shadow score/status、`research_state`、`position_state`、`confirmation_basis` 和 disagreement；
5. 若存在事件驱动候选，输出/保存 ERG 的 expectation、surprise、materiality、prepricing、reaction 与 `source_tier`；
6. 若事件发布时间影响可交易时点，输出 session route、`first_tradable_timestamp` 及 resolution status；
7. executable candidates：position_state、trigger、confirmation_basis、invalidation、gap risk、tranche、risk、time stop、交易摩擦；
8. 真实 ENTRY/ADD：capital_eligibility、cash_need_gate、emergency_reserve_gate、debt_leverage_gate；
9. near misses；
10. adversarial audit；
11. Stock Account Equity + Final Short Cap；
12. current short exposure / pending cash / CAP_BREACH；
13. account-level same-symbol / cluster exposure，包括长期仓。

行业覆盖任务额外报告 taxonomy/version、universe/core coverage、uncovered/absent、qualified supplements。

## 26. Learning Loop

读取：

- `references/iteration-roadmap.md`；
- `references/disagreement-ledger-and-negative-control.md`；
- `references/champion-challenger-forward-test.md`；
- `references/erg-forward-test-extension.md`。

每个闭环交易记录：

- model / strategy version；
- setup；
- entry score；
- market/sector regime；
- entry/exit/invalidation；
- MFE/MAE；
- realized R；
- slippage/fees/tax/impact；
- rule violations；
- thesis vs execution quality。

MFE/MAE 扩展见 `references/trade-ledger-mfe-mae-extension.md`。

ERG/Challenger 还记录：

- research_state / position_state / strategy_type / confirmation_basis；
- expectation/reaction event fields；
- ERG ablation cohort/version；
- Champion/Challenger disagreement type/reason；
- no-trade opportunity cost；
- placebo/negative-control diagnostics；
- number_of_trials / parameter stability / model-selection risk。

冻结 cohort 的原始决策字段不得因未来结果改写。2026-08-28 首个八股 Forward baseline 见：

- `examples/2026-08-28-eight-stock-forward-cohort.md`；
- `examples/2026-08-28-eight-stock-forward-cohort.json`。

参数不能在少量交易后自动修改；新想法进入 Challenger。

## 27. Paper / Live / Automation

读取：

- `../../shared/automation-execution-governance.md`；
- `references/session-aware-execution-calendar.md`；
- `references/validation-metrics-and-trade-ledger.md`；
- `references/paper-live-automation-roadmap.md`。

默认：

```text
AUTO_MONITOR = true
AUTO_ORDER   = false
```

Paper/Live 必须可审计、可对账，broker/data/policy 状态未知时 fail closed。

ERG 处于 Shadow 时不得改变真实报单。

## 28. Governance Version Fields

研究/执行记录至少分开保存：

```text
capital_policy_version
automation_governance_version
research_model_governance_version
skill_version
strategy_version / model_version
```

ERG Challenger 额外保存 `erg_version`；session-aware 记录保存 `session_rule_version`。

不得只写一个模糊 `policy_version`。

## 29. Reference / Historical Files

### Active references

- `references/iteration-roadmap.md` — 当前短中期研究迭代顺序与实验队列；
- `references/scoring-system.md` — 当前 Champion；
- `references/causal-challenger-model.md` — Challenger / Shadow Only；
- `references/expectation-reaction-gate.md` — ERG / Shadow Only；
- `references/erg-output-schema.md`；
- `references/erg-validation-checklist.md`；
- `references/erg-forward-test-extension.md`；
- `references/statistical-promotion-guard.md`；
- `references/disagreement-ledger-and-negative-control.md`；
- `references/session-aware-execution-calendar.md`；
- `references/erg-promotion-criteria.md`；
- `references/erg-adversarial-review-report.md`；
- `references/erg-research-rationale.md`；
- `references/champion-challenger-forward-test.md`；
- `references/trade-ledger-mfe-mae-extension.md`；
- `references/holding-risk-management.md`；
- `references/data-source-policy.md`；
- `references/industry-coverage-audit.md`；
- `references/adversarial-review.md`；
- `references/evaluation-cases.md`；
- `references/research-basis.md`；
- `references/validation-metrics-and-trade-ledger.md`；
- `references/paper-live-automation-roadmap.md`。

### Frozen forward evidence

- `examples/2026-08-28-eight-stock-forward-cohort.md` — 首个八股 ERG/Champion immutable baseline；
- `examples/2026-08-28-eight-stock-forward-cohort.json` — machine-readable baseline。

### Historical evidence

- `references/core-pool-snapshot-2026-08-26.md` — 中间36股历史快照；
- `examples/2026-08-26-final-watchlist-case-study.md` — 同日晚些时候43股最终研究状态；
- `examples/2026-08-26-final-watchlist.json` — 43股 machine-readable baseline。

36→43 是同日研究演进，不是两个当前有效 whitelist。历史文件不能覆盖 fresh Skill run。