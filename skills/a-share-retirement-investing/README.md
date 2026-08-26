# A-share Retirement Investing Skill

用于沪深 A 股长期养老型权益组合的：

- 长期分红核心股筛选；
- 科技/成长卫星仓筛选；
- 行业适配财务分析；
- 合理价值与买入区间；
- Bear/Base/Bull Expected IRR；
- Total Return Benchmark；
- 动态仓位与分批建仓；
- 补仓 Gate；
- 分红复投；
- 季度/年度持仓复核；
- 对抗审查与退出条件；
- Forward Paper → 人工实盘 → 半自动 → 受约束自动执行的验证链路。

## 先读上位规则

执行本 Skill 前按顺序读取：

1. `../../shared/policy-precedence.md`
2. `../../shared/capital-allocation-and-entry-policy.md`
3. `../../shared/research-model-governance.md`
4. `../../shared/automation-execution-governance.md`（涉及 Paper / Live / 自动化时）
5. `SKILL.md`

共享政策优先于本 Skill、references 和 examples 中的通用规则。

## 长期 / 短中期战略基线

| 股票专用资金规模 | 长期战略基线 | 短中期 Size Cap |
|---:|---:|---:|
| ≤5 万 | 70% | 30% |
| 5–30 万 | 75% | 25% |
| 30–200 万 | 80% | 20% |
| 200–1000 万 | 85% | 15% |
| ≥1000 万 | 85%–90% | 10%–15% |

最终短中期：

```text
Final Short Cap = min(Size Cap, Risk Cap, Edge Cap)
Actual Short Exposure <= Final Short Cap
```

如果短中期被 Risk/Edge Cap 压低，差额不自动强制买入长期仓；长期候选也必须通过自身质量、估值和组合 Gate，没有合格机会时允许保留待配置现金。

具体数值以 shared capital policy 为唯一 Source of Truth。

## 长期仓内部结构

```text
Core Dividend：75%–85%
Growth Satellite：15%–25%
```

这是长期仓内部功能划分，不是全账户的长期/短中期比例。

## 长期“低位”定义升级

长期不把“离历史高点很远”直接当作便宜。

必须区分：

```text
Price Low
!=
Valuation Low
```

新增统一估值语言：

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

Required Return 使用 point-in-time 无风险利率加配置的 Required Risk Premium。风险溢价必须做敏感性分析，不把固定 4%–6% 写成所有 A 股通用真理。

## 长期 Benchmark

长期组合必须优先和含分红再投资的 Total Return Benchmark 比较。

例如沪深300：

```text
Price Index  = 000300
Total Return = H00300
```

组合至少保存：

```text
price_return
cash_dividends_received
dividends_reinvested
total_return
benchmark_total_return
```

禁止用“组合含分红、Benchmark 不含分红”的不同口径证明超额收益。

## 长期建仓

当前 shared policy 基线：

```text
默认：3 批 40% / 30% / 30%
2批例外：60% / 40%
4批例外：30% / 25% / 25% / 20%
```

这些比例是当前治理参数，不宣称数学最优。

后续批次必须有新的估值、价格或事实确认，不能机械“越跌越买”。

长期后续 ADD 必须同时通过：

```text
Thesis Gate
+ Balance Gate
+ Valuation Gate
+ Portfolio Gate
```

并重新计算 Bear/Base/Bull IRR。价格下跌只有在 thesis 未恶化且 Expected IRR 确实改善时，才可能提高安全边际。

## 动态仓位

单股和风险簇上限不永久写死。执行时根据股票专用资金规模从 shared policy 动态读取。

随着资金规模增长：

- 提高组合分散度；
- 降低单股目标上限；
- 降低单一风险簇上限；
- 大额成交额外考虑流动性与执行拆单。

任何漂移/再平衡参考带都不能突破 shared-policy Cap。

## 长期止损与止盈

```text
止损：
默认不用统一 5%/8%/10% 机械价格止损；
主要使用投资逻辑、盈利能力、现金流/资本、治理和商业模式失效条件。

止盈：
不用固定盈利百分比全卖；
使用 Expected IRR、估值、集中度、机会成本和 thesis 状态决定 HOLD / TRIM / EXIT。
```

如果价格上涨导致 Base Expected IRR 低于当前 Required Return，应触发估值复核，但是否 TRIM 仍需结合税费、组合集中度和替代机会。

## 十股养老组合示例

历史 Forward-Test 基线：

`examples/ten-stock-retirement-portfolio-2026-08-26.md`

十只股票：

```text
长江电力 / 招商银行 / 伊利股份
中国石油 / 中国电信 / 格力电器 / 中国神华
工业富联 / 立讯精密 / 中科曙光
```

模型内部结构：

```text
Core Dividend = 80%
Growth Satellite = 20%
```

该案例记录：

- 2026-08-26 历史价格基线；
- 当时已公开的最新财务/市场验证；
- 角色、模型权重和风险簇；
- 建仓、补仓、止损、止盈规则；
- Paper/Live 后续记录字段；
- 对 point-in-time 事实错误的 correction 规则。

**它属于 Level 4 历史案例，不是永久推荐名单。**

真实买入前必须重新运行 Skill。案例中的模型权重不能突破当前 shared-policy 单股/风险簇限制；如果某只处于 WATCH 或估值 Gate 未通过，对应资金可以继续留在现金池。

历史案例不会因为后来结果好坏被静默改写；后续实际结果必须单独记录，用于 prediction error 和 Forward validation。

## Paper → Live → Automation

路线图：

`examples/paper-live-automation-roadmap.md`

统一成熟路径：

```text
规则冻结
→ Forward Paper
→ 人工小规模实盘
→ 自动研究 + 人工下单
→ 人工确认后的 Broker 执行
→ 受约束 Semi-auto
→ Edge + Compliance + Reliability 通过后才评估 Full Auto
```

默认：

```text
AUTO_MONITOR = true
AUTO_ORDER   = false
```

跨策略自动化安全要求统一由：

`../../shared/automation-execution-governance.md`

管理，包括：

- `paper_capital_rmb` 与标准化 `reporting_nav` 分离；
- point-in-time 数据；
- Broker position reconciliation；
- idempotency / duplicate-order protection；
- Fail Closed / Kill Switch；
- 程序化交易与券商合规门禁；
- 审计日志；
- policy/Skill 版本治理。

研究模型晋级另受：

`../../shared/research-model-governance.md`

约束。Good Model 不等于 Safe Auto Execution。

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

## 推荐使用顺序

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

研究依据与参数边界见：

- `../../shared/research-validation-2026-08-26.md`
- `../../shared/adversarial-research-review-2026-08-26.md`

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

任何时效性数字都必须重新联网验证并标注 `as_of`。
