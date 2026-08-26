# A-share Retirement Investing Skill

用于沪深 A 股长期养老型权益组合的筛选、估值、组合构建、分红复投、持仓复核与逐步自动化验证。

## 先读上位规则

执行本 Skill 前按顺序读取：

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
Long Skill:              v2.2.0
```

## 统一账户口径

账户级资本与集中度使用：

```text
Stock Account Equity
= 长期股票市值
+ 短中期股票市值
+ 股票账户待配置现金
```

长期仓内部 Core/Growth、十股示例 `model_long_book_weight` 使用的是 **长期已部署权益仓内部分母**。

因此模型权重执行前必须换算：

```text
model_total_account_weight
= model_long_book_weight × planned_long_exposure
```

再与账户级单股/风险簇 Cap 比较。

## 长期 / 短中期战略基线

| Stock Account Equity | 长期战略基线 | 短中期 Size Cap |
|---:|---:|---:|
| ≤5 万 | 70% | 30% |
| 5–30 万 | 75% | 25% |
| 30–200 万 | 80% | 20% |
| 200–1000 万 | 85% | 15% |
| ≥1000 万 | 85%–90% | 10%–15% |

短中期最终上限：

```text
Final Short Cap = min(Size Cap, Risk Cap, Edge Cap)
```

这不是满仓要求。长期和短中期都没有合格机会时，待配置现金是合法状态。

## 长期仓内部结构

长期**已部署权益仓内部**默认：

```text
Core Dividend：75%–85%
Growth Satellite：15%–25%
```

这是长期仓内部功能划分，不是整个股票账户的长期/短中期比例。

## 跨策略同股 / 同风险簇

如果同一股票同时存在长期与短中期仓：

```text
Account Symbol Exposure
= Long Sleeve Exposure + Short/Mid-term Sleeve Exposure
```

风险簇同理：

```text
Account Cluster Exposure
= Long Cluster Exposure + Short/Mid-term Cluster Exposure
```

任何长期 ADD 都必须检查账户级合计暴露，不能因“长期”和“短中期”标签不同而各享受一套单股上限。

若市场上涨导致被动超限：

```text
CAP_BREACH
→ 禁止继续增加同方向风险
→ 再平衡评估
→ 在合理执行窗口恢复
```

## 长期“低位”定义

```text
Price Low != Valuation Low
```

股价离历史高点很远不能自动构成长期买点。

读取：

`references/expected-irr-total-return-benchmark.md`

每只长期候选至少输出：

```text
Bear IRR
Base IRR
Bull IRR
Required Return assumptions
Bear/Base/Bull Max Buy Price
Current Price
Margin of Safety
```

Expected IRR 使用逐期现金流：

```text
0 = -P0 + Σ[CF_t/(1+r)^t] + TV_T/(1+r)^T
```

Max Buy Price：

```text
Σ[CF_t/(1+k)^t] + TV_T/(1+k)^T
```

不得把累计分红全部塞到终点后仍称为精确 IRR。

## Required Return 与 Benchmark

```text
Required Return
= Point-in-time Risk-free Rate
+ Configured Required Risk Premium
```

Risk Premium 是模型参数，必须做敏感性分析。

长期绩效比较优先采用 Total Return Benchmark。例如沪深300：

```text
Price Index  = 000300
Total Return = H00300
```

禁止用组合含分红、Benchmark 不含分红的不同口径证明超额收益。

## 长期建仓

当前 Level 1A：

```text
默认：40 / 30 / 30
2批例外：60 / 40
4批例外：30 / 25 / 25 / 20
```

这些比例属于治理参数，不宣称数学最优。

后续批次必须有新的估值、价格或事实确认，不机械“越跌越买”。

长期 ADD 必须同时通过：

```text
Thesis Gate
Balance Gate
Valuation Gate
Portfolio Gate
```

并刷新 Bear/Base/Bull IRR。

## 长期止损 / 止盈

长期默认不使用统一 -5%/-8%/-10% 机械价格止损。

EXIT 主要来自：

- thesis 被事实证伪；
- 商业模式/护城河结构性破坏；
- 正常化盈利能力永久恶化；
- 现金流、债务或监管资本失控；
- 重大审计/治理问题。

TRIM 主要来自：

```text
Expected IRR下降
+ 估值过高
+ 单股/风险簇超配
+ 更优机会成本
```

## 十股养老模型组合示例

历史 Forward-Test 基线：

`examples/ten-stock-retirement-portfolio-2026-08-26.md`

十只股票：

```text
长江电力 / 招商银行 / 伊利股份
中国石油 / 中国电信 / 格力电器 / 中国神华
工业富联 / 立讯精密 / 中科曙光
```

历史 long-book 内部结构：

```text
Core Dividend = 80%
Growth Satellite = 20%
```

该案例属于 Level 4 历史证据，不是永久推荐名单。真实买入前必须重新运行 Skill、重新计算 Expected IRR / Max Buy Price / 账户级 Cap，并聚合短中期同股/同因子暴露。

## Paper → Live → Automation

路线图：

`examples/paper-live-automation-roadmap.md`

统一路径：

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

运行时必须维护：

```text
paper_capital_rmb
reporting_nav
Broker Net Position
Strategy Virtual Position
Governance Bundle
```

Governance Bundle：

```text
capital_policy_version
automation_governance_version
research_model_governance_version
skill_version
strategy_version
model_version
```

## 文件结构

```text
skills/a-share-retirement-investing/
├── SKILL.md
├── README.md
├── examples/
│   ├── ten-stock-retirement-portfolio-2026-08-26.md
│   └── paper-live-automation-roadmap.md
└── references/
    ├── methodology.md
    ├── industry-checklists.md
    ├── execution-template.md
    ├── expected-irr-total-return-benchmark.md
    └── seed-watchlist-2026-08-26.md
```

## 推荐阅读顺序

1. `../../shared/policy-precedence.md`
2. `../../shared/capital-allocation-and-entry-policy.md`
3. `../../shared/research-model-governance.md`
4. `../../shared/automation-execution-governance.md`（涉及执行链路时）
5. `SKILL.md`
6. `references/methodology.md`
7. `references/industry-checklists.md`
8. `references/expected-irr-total-return-benchmark.md`
9. `references/execution-template.md`
10. `examples/ten-stock-retirement-portfolio-2026-08-26.md`
11. `examples/paper-live-automation-roadmap.md`
12. `references/seed-watchlist-2026-08-26.md`

研究依据与审计：

- `../../shared/research-validation-2026-08-26.md`
- `../../shared/adversarial-research-review-2026-08-26.md`
- `../../shared/consistency-audit-2026-08-26.md`

## 关键原则

```text
先看能不能长期活
→ 再看能不能长期赚
→ 再看利润能否转成现金/资本
→ 再看分红是否可持续
→ 再看是否有增长
→ 再算 Bear/Base/Bull IRR
→ 再判断当前价格值不值得买
→ 最后才看当前股息率
```

所有时效性数据必须重新联网验证并标注 `as_of`。