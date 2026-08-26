# 执行模板 v2.1

本模板用于每次真实运行长期养老 Skill，防止聊天上下文、行情波动或旧参数绕过 shared policy。

## A. 上位规则加载

执行前必须读取：

```text
../../../shared/policy-precedence.md
../../../shared/capital-allocation-and-entry-policy.md
../SKILL.md
```

涉及 Paper / Live / 自动化时额外读取：

```text
../../../shared/automation-execution-governance.md
```

若模板与上位规则冲突，以上位规则为准。

## B. 输入

```yaml
as_of: 自动获取
market: 沪深A股
universe: 用户给定股票池 | 全市场
objective: 长期养老权益仓
holding_horizon: 10年以上（若用户另有说明则覆盖）

stock_capital_amount: 用户输入

strategic_allocation:
  source: shared/capital-allocation-and-entry-policy.md
  long_baseline: derived
  short_size_cap: derived
  final_short_cap: derived_from_size_risk_edge
  cash_allowed: true

core_dividend_target_within_long_book: 75%-85%
growth_target_within_long_book: 15%-25%

max_single_stock:
  derived_from_shared_policy: true

max_risk_cluster:
  derived_from_shared_policy: true

entry_tranches:
  default: [40%, 30%, 30%]
  small_or_high_certainty: [60%, 40%]
  larger_or_higher_uncertainty: [30%, 25%, 25%, 20%]

extra_filters:
  price_max: null
  market_cap_min: null
  industries: null
  excluded_industries: null
```

禁止在这里写死旧的 `25%` 单股上限或 `30%-35%` 风险簇上限。

同样禁止假设股票专用资金必须 100% 满仓：如果长期候选未通过质量/估值/组合 Gate，资金可以留在待配置现金池。

## C. 数据获取检查

对每只候选逐项标记 `PASS/MISSING/CONFLICT`：

- [ ] 最新价格与日期
- [ ] 最新总市值
- [ ] 最新年报
- [ ] 最新半年报/季度报
- [ ] 最近5–10年普通现金分红
- [ ] 特别股息拆分
- [ ] 分红支付率
- [ ] 经营现金流/行业替代指标
- [ ] Capex/监管资本
- [ ] 资产负债情况
- [ ] 审计意见
- [ ] 当前股东回报规划
- [ ] 当前估值
- [ ] 重大并购/增发/处罚/治理事件

关键项 MISSING 时，不得输出 ADD。

## D. 单股研究卡

```markdown
### 股票名（代码）

**角色**：Core / Growth
**as_of**：YYYY-MM-DD HH:MM
**数据质量**：High / Medium / Low

#### 1. 一句话投资逻辑
...

#### 2. 已披露事实
- ...

#### 3. 关键数字
- Revenue:
- Net Profit:
- Ex-item Profit:
- OCF / Industry Metric:
- ROE/ROIC:
- Debt/Capital:
- Ordinary DPS:
- Payout Ratio:
- Dividend CAGR:

#### 4. 评分
- Durability / Runway:
- Dividend / Growth quality:
- Cashflow:
- Balance sheet:
- Governance:
- Valuation:
- Portfolio fit:
- Total:

#### 5. 估值
- Conservative Fair Value:
- Base Fair Value:
- Max Buy Price:
- Current Price:

#### 6. 压力测试
- Base:
- Profit -20%:
- Profit -30%:
- Capex/Interest stress:

#### 7. Bull Case
...

#### 8. Bear Case
...

#### 9. 失效条件
1. ...
2. ...
3. ...

#### 10. 决策
ADD / HOLD / WATCH / TRIM / EXIT

#### 11. 动态仓位
- Current shared-policy tier:
- Model/desired weight:
- Maximum single-stock weight:
- Risk-cluster weight after trade:
- Deployable weight after all caps:

#### 12. 建仓批次
- Chosen mode: 2 / 3 / 4 strategy tranches
- Why this mode:
- Tranche 1 trigger:
- Tranche 2 trigger:
- Tranche 3/4 trigger:

#### 13. 证据
- 官方年报：...
- 官方公告：...
- 行情：...
```

## E. 长期补仓 Gate

每次后续 ADD 前必须全部通过：

```text
Thesis Gate
Balance Gate
Valuation Gate
Portfolio Gate
```

检查：

- [ ] 原投资逻辑仍成立
- [ ] 现金流/资本/债务未恶化
- [ ] 当前估值仍有安全边际
- [ ] 单股上限未超
- [ ] 风险簇上限未超
- [ ] 不是因为“已经跌很多”而机械补仓

若下跌约15%–20%，触发重新研究；约25%–30%，触发深度 thesis review。两者都不是自动买卖线。

## F. 组合研究卡

```markdown
# Portfolio Review — YYYY-MM-DD

## 顶层资本状态
- Stock capital amount:
- Long strategic baseline:
- Final Short Cap:
- Actual long exposure:
- Actual short exposure:
- Cash / pending deployment:
- Any cap violation: Yes/No

注意：Final Short Cap 是上限；未部署资金允许为现金，不能为了“回到比例”制造交易。

## 长期仓内部结构
- Core deployed weight within long book: xx%
- Growth deployed weight within long book: xx%
- Long-book cash pending deployment: xx%

## 动态集中度限制
- Current single-stock cap:
- Current risk-cluster cap:

## 风险簇
- Energy commodity: xx%
- Interest/Credit: xx%
- Utility: xx%
- Consumer: xx%
- AI Capex: xx%
- Export/Overseas customer: xx%

## 普通分红情景
- Trailing ordinary dividend yield: x.x%
- Stress dividend yield: x.x%
- 注意：非保证收益

## 动作
| Stock | Previous | Current | Weight | Action | Why changed |
|---|---|---|---:|---|---|

## 未来12个月观察
1. ...
2. ...
3. ...
```

### 再平衡检查

- [ ] Actual Short Exposure 是否 ≤ Final Short Cap？
- [ ] 是否错误使用 ±5pp 漂移带突破 Cap？
- [ ] 短中期亏损后是否错误从长期仓补血？
- [ ] 短中期盈利回流后，长期是否也重新通过 Gate，而不是机械买入？

## G. 对抗审查 Gate

只有以下关键问题完成后，才允许给出最终组合：

- [ ] 是否误把特别分红当普通分红？
- [ ] 是否用景气高点利润计算可持续收益？
- [ ] 是否忽略 Capex/监管资本？
- [ ] 是否存在高负债 + 高分红？
- [ ] 是否存在利润增长但现金流不增长？
- [ ] 是否存在审计/治理红旗？
- [ ] 是否存在表面跨行业、实际同风险簇集中？
- [ ] 是否把“公司好”误等于“当前价格值得买”？
- [ ] 是否给成长股做了估值反推？
- [ ] 是否明确区分事实、市场预测、模型估算？
- [ ] 是否给出了最强 Bear Case？
- [ ] 是否给出了可观察的退出/失效条件？
- [ ] 当前仓位上限是否来自 shared policy？
- [ ] 建仓是否使用当前 2/3/4 批规则，而不是旧“3–5批随意选择”？
- [ ] 是否允许现金，而不是强制把所有资金投满？

任一关键项未完成，结论降级为 WATCH 或继续研究。

## H. 推荐输出顺序

1. 当前上位资本规则、Final Short Cap 和动态仓位上限。
2. 当前长期已部署/现金状态。
3. 候选/持仓状态。
4. 核心逻辑。
5. 估值与买入区间。
6. 建仓/补仓条件。
7. 组合权重与风险簇。
8. Bear Case / 失效条件。
9. 官方证据和 `as_of`。
