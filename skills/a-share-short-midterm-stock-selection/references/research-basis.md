# Research Basis and Design Rationale v3

## Purpose

本文件记录短中期 Skill 的外部研究依据和设计边界，不覆盖当前 shared policy，也不把海外研究数字直接当成 A 股参数。

上位规则：

```text
../../../shared/policy-precedence.md
├─ capital-allocation-and-entry-policy.md
├─ automation-execution-governance.md
└─ research-model-governance.md
        ↓
../SKILL.md
        ↓
this reference
```

所有结论区分：

```text
Fact / Regulation
Research-supported Principle
Governance Parameter
```

具体百分比、评分权重、批次、time stop 和 R 阈值属于 Governance Parameter，除非明确有更强证据。

## 1. A-share execution constraints are real risk

普通 A 股执行存在 T+1、价格限制、gap、停牌/复牌、异常波动和流动性问题，理论 stop 不保证成交。

Sources:

- SSE Trading Rules, 2026 revision:
  https://www.sse.com.cn/lawandrules/sselawsrules2025/stocks/exchange/c/c_20260424_10816482.shtml
- SZSE Trading Rules, 2026 revision:
  https://www.szse.cn/lawrules/rule/trade/current/t20260424_620190.html

设计结论：

- 首批仓位必须能承受失效；
- stop 是 invalidation plan，不是 fill guarantee；
- gap/limit risk 通过仓位、事件隔离和现实成交模拟处理。

## 2. Material information requires official disclosure

Source:

- CSRC, Measures for the Administration of Information Disclosure by Listed Companies:
  https://www.csrc.gov.cn/csrc/c106256/c1653948/content.shtml

设计结论：

- 重大事实优先官方披露；
- 未披露报告是 event risk，不是事实；
- 全流程 point-in-time，禁止 look-ahead。

## 3. Risk-based sizing

Fidelity / Schwab 教育材料支持先定义风险和退出，再反推仓位：

```text
position size = allowed loss / risk per share
```

Sources:

- https://www.fidelity.com/bin-public/060_www_fidelity_com/documents/learning-center/Presentation_Exit%20Strategy.pdf
- https://www.fidelity.com/bin-public/060_www_fidelity_com/documents/WLP_User_Guide.pdf
- https://www.schwab.com/learn/story/5-elements-smart-trade-plan

当前仓库治理参数：

```text
Operating Target
- per trade: 0.5% of short-strategy NAV
- aggregate open initial risk: <=2%
- one industry/factor: <=1%

Hard Ceiling
- planned per trade: <=1%
- aggregate open initial risk: <=3%
```

这些是计划风险阈值，不保证 gap/跌停下最大实际亏损。

## 4. Account-level aggregation is a risk-governance decision

同一股票或经济因子同时存在于长期与短中期时，风险不会因为策略标签不同而消失。

因此仓库使用：

```text
Account Symbol Exposure
= Long + Short/Mid

Account Cluster Exposure
= Long Cluster + Short/Mid Cluster
```

这是风险治理原则。具体上限只由 shared capital policy 决定。

## 5. Entry tranches

公开研究不能证明 50/50 唯一最优。

当前治理：

```text
Default: 50% Setup + 50% Confirmation
Exception: 50% / 30% / 20%
```

大资金的多个 child orders 是 execution slicing，不是更多策略批次。

## 6. Earnings quality requires cash-flow and accrual checks

Sources:

- CFA Institute Research Foundation, Earnings Quality:
  https://rpc.cfainstitute.org/sites/default/files/-/media/documents/book/rf-publication/2004/rf-v2004-n3-3927-pdf.pdf
- CFA Institute, Evaluating Quality of Financial Reports:
  https://www.cfainstitute.org/sites/default/files/-/media/documents/book/curriculum-update/rr-v-2017-n2-1.pdf

设计结论：利润增长不能单独给满分；检查扣非、OCF、应收、存货、一次性项目和行业适配指标。

## 7. Quality is multidimensional

Sources:

- AQR, Quality Minus Junk:
  https://www.aqr.com/Insights/Research/Working-paper/Quality-minus-Junk
- Kenneth French Data Library:
  https://mba.tuck.dartmouth.edu/pages/faculty/ken.french/Data_Library/f-f_5_factors_2x3.html

这些支持质量维度的重要性，但不是 A 股短期择时参数校准。

## 8. Momentum / technical evidence has boundaries

Sources:

- Chan, Jegadeesh & Lakonishok:
  https://www.nber.org/papers/w5375
- Chabot, Ghysels & Jagannathan:
  https://www.nber.org/papers/w20660

统一结论：

```text
Technical / momentum information can contain conditional predictive content,
but tradable Alpha is regime-, parameter- and cost-dependent and must pass out-of-sample validation.
```

因此既不说“看线必然有效”，也不说“历史数据所以完全没用”。

## 9. Factor momentum and hidden concentration

Source:

- Ehsani & Linnainmaa:
  https://www.nber.org/papers/w25551

设计结论：formal industry 与 dominant economic factor 分开记录；实际持仓按因子相关性控制。

## 10. Exit design

Source:

- Fidelity Exit Strategies:
  https://www.fidelity.com/learning-center/trading-investing/trading/exit-strategies

当前治理：

```text
price/invalidation stop
+ thesis stop
+ time stop
```

R-multiple/结构优先于固定百分比观察区。

`+1.5R/+2R`、3–5日 time review 等是治理初值，必须通过 MFE/MAE 与 Forward 数据继续校准。

## 11. Frequent trading evidence does not prove all short strategies fail

Barber/Odean 等研究支持高换手个人投资者平均表现可能受交易成本和行为影响，但不能推出所有短中期策略必然无效。

当前设计结论：短中期仓必须通过真实成本后 Edge “挣仓位”，模型变化进入 Champion/Challenger，而不是靠近期表现直接放大风险。

## 12. Champion / Challenger is the correct model-change path

当前 Champion：

```text
Technical 30
Capital 30
Fundamentals 25
Catalyst 15
```

新因果模型只做 Challenger Shadow，见：

- `causal-challenger-model.md`
- `champion-challenger-forward-test.md`

晋级遵循 `../../../shared/research-model-governance.md`。

## 13. What research does NOT justify

不能据此：

- 假设海外历史关系在 A 股原样重复；
- 只因 momentum 买股；
- 宣称某 MA 参数普适最优；
- 把 vendor 主力流入当机构真实净买入；
- 用同一估值阈值横跨所有行业；
- 假设 stop 一定按 stop price 成交；
- 用账户规模机械增加策略批次；
- 将5–15日交易无限延期；
- 把0.5%、1%、2%、3%、4/6/8、50/50、+1.5R/+2R写成学术最优；
- 让 Challenger 在未晋级前影响生产订单。

## 14. Methodological conclusion

当前可辩护架构：

```text
locked universe
→ point-in-time hard eligibility
→ leader/authenticity + financial quality
→ current Champion score
→ market/sector regime
→ execution-risk check
→ risk-based sizing
→ account-level cross-sleeve aggregation
→ confirmation-based entry
→ explicit holding state
→ adversarial audit
→ MFE/MAE + Forward learning
→ Challenger only through promotion process
```

目标是减少可避免的流程错误并验证净期望，不是最大化交易次数。

## 15. Short-horizon continuation vs reversal — explicit boundary

The 5–15 trading-day sleeve must not borrow 3–12 month momentum evidence as if it directly proved 3–5 day continuation.

Supporting and adversarial evidence coexist:

- Jegadeesh & Titman (1993): intermediate-horizon momentum over 3–12 month holding periods.
  https://doi.org/10.1111/j.1540-6261.1993.tb04702.x
- Lo, Mamaysky & Wang (2000): some objectively defined technical patterns contain incremental conditional information.
  https://www.nber.org/papers/w7613
- Jegadeesh & Titman (1995): short-horizon reversals can arise from microstructure effects.
  https://doi.org/10.1006/jfin.1995.1006
- Yu, Fung & Leung (2019): significant weekly reversals in Chinese SSE/SZSE/GEM samples, with horizon-dependent results.
  https://doi.org/10.1016/j.iref.2019.03.006
- Jiang, Tong & Song (2019): some Chinese-market technical rules survived data-snooping controls in their sample.
  https://doi.org/10.1111/irfi.12161
- Chuang et al. (2024): after broad multiple-testing correction and out-of-sample transaction costs, most apparently profitable Chinese technical rules did not survive.
  https://doi.org/10.1016/j.pacfin.2024.102278

Therefore:

```text
recent strength
→ conditional continuation hypothesis
not
→ deterministic next-week forecast
```

The production system should use state transitions and conditional paths rather than uncalibrated probability statements.

## 16. Blind replay / scenario probability discipline

For retrospective PIT replay:

```text
conditional path = allowed
uncalibrated numeric path probability = prohibited
```

A probability such as `50% / 30% / 20%` may only enter a research artifact if it comes from a frozen calibration procedure with a declared cohort, horizon, costs, sample size and confidence interval.

A replay created after outcomes are known may test process/PIT discipline but is not Level-C forward evidence even when future data are manually hidden.

No standalone blind-replay theoretical-audit file is present in the tracked repository; the repository map does not claim a substitute artifact. The active blind-replay and probability-discipline rules are stated above and in the methodology consolidation contract.

Retrospective blind replay is useful for PIT/process testing, but is not untouched forward evidence. Public examples use only the anonymized methodology record `CASE-SM-001`; no security-specific replay or execution details are retained.

## 17. Reference-price / cost-basis boundary

Behavioral evidence on the disposition effect supports guarding against break-even anchoring, including Chinese retail-investor evidence. This does not imply an automatic sell rule for losing positions.

Sources:

- Odean (1998):
  https://doi.org/10.1111/0022-1082.00072
- Zhang et al. (2022), Chinese brokerage-account evidence:
  https://doi.org/10.1016/j.irfa.2022.102205
- Grinblatt & Han (2005), aggregate reference prices and momentum:
  https://doi.org/10.1016/j.jfineco.2004.10.006

Repository conclusion:

```text
cost basis = P&L / accounting fact
cost basis != market target
```

HOLD / ADD / EXIT must follow current thesis, invalidation, opportunity cost and risk budget rather than the desire to return to breakeven.

## 18. Stop and sizing theory boundary

- Kaminski & Lo (2014) show stop-loss value is conditional: under a random walk a stop can lower expected return; under momentum some policies can reduce losses and add value.
  https://doi.org/10.1016/j.finmar.2013.07.001
- Markowitz (1952) supports portfolio diversification / covariance-aware risk thinking.
  https://doi.org/10.1111/j.1540-6261.1952.tb01525.x
- Kelly (1956) supports the broad idea that optimal size depends on edge and downside distribution under known probabilities/odds.
  https://doi.org/10.1002/j.1538-7305.1956.tb03809.x

Repository conclusion:

```text
predefine invalidation before sizing = defensible risk principle
size decreases as downside distance / uncertainty rises = defensible risk principle
exact 0.5% / 1% / 20% / 50-50 values = governance parameters, not academic optima
```

Because real equity probabilities are unknown and A-share gap/limit risk is material, the repository must not interpret full-Kelly sizing as a production default.
