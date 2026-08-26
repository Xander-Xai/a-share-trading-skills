# 执行模板 v2.2

本模板用于每次真实运行长期养老 Skill，防止聊天上下文、行情波动或旧参数绕过 shared policy。

## A. 上位规则加载

执行前读取：

```text
../../../shared/policy-precedence.md
../../../shared/capital-allocation-and-entry-policy.md
../../../shared/research-model-governance.md
../SKILL.md
```

涉及 Paper / Live / 自动化额外读取：

```text
../../../shared/automation-execution-governance.md
```

若模板与上位规则冲突，以上位规则为准。

## B. 版本与账户口径

```yaml
as_of: 自动获取
capital_policy_version: 当前读取值
automation_governance_version: 当前读取值 | N/A if research-only
research_model_governance_version: 当前读取值
skill_version: 当前 SKILL frontmatter
strategy_version: 当前长期策略版本

stock_account_equity: 用户股票账户专用资金/权益
long_market_value:
short_mid_market_value:
pending_cash:
reconciliation_check: long + short_mid + cash == stock_account_equity
```

禁止只保存一个含义不明的 `policy_version`。

## C. 战略输入

```yaml
market: 沪深A股
universe: 用户给定股票池 | 全市场
objective: 长期养老权益仓
holding_horizon: 10年以上（用户另有说明则覆盖）

strategic_allocation:
  source: shared/capital-allocation-and-entry-policy.md
  long_baseline: derived
  short_size_cap: derived
  final_short_cap: derived_from_size_risk_edge
  cash_allowed: true

core_dividend_target_within_deployed_long_book: 75%-85%
growth_target_within_deployed_long_book: 15%-25%

account_single_stock_cap:
  derived_from_shared_policy: true

account_risk_cluster_cap:
  derived_from_shared_policy: true

entry_tranches:
  default: [40%, 30%, 30%]
  small_or_high_certainty: [60%, 40%]
  larger_or_higher_uncertainty: [30%, 25%, 25%, 20%]
```

## D. 权重分母转换

模型权重与账户 Cap 不能直接比较。

```text
model_long_book_weight
= 股票在长期已部署权益仓中的模型权重

planned_long_exposure
= 计划长期已部署权益 / Stock Account Equity

model_total_account_weight
= model_long_book_weight × planned_long_exposure
```

最终计划账户级权重：

```text
planned_total_account_weight
= min(
    model_total_account_weight,
    account_single_stock_cap,
    remaining_account_cluster_capacity,
    valuation_quality_allowance
  )
```

如果同一股票也存在短中期仓：

```text
post_trade_account_symbol_exposure
= long_exposure_after_trade + short_mid_exposure
```

必须再次通过账户级单股 Cap。

## E. 数据获取检查

逐项标记 `PASS / MISSING / CONFLICT`：

- [ ] 最新价格与日期
- [ ] 最新总市值
- [ ] 最新年报
- [ ] 最新半年报/季度报
- [ ] 最近5–10年普通现金分红
- [ ] 特别股息拆分
- [ ] 分红支付率
- [ ] OCF/行业替代指标
- [ ] Capex/监管资本
- [ ] 资产负债情况
- [ ] 审计意见
- [ ] 当前股东回报规划
- [ ] 当前估值
- [ ] 重大并购/增发/处罚/治理事件
- [ ] point-in-time 发布时间

关键项 MISSING/CONFLICT 时不得 ADD。

## F. 单股研究卡

```markdown
### 股票名（代码）

**角色**：Core / Growth
**as_of**：YYYY-MM-DD HH:MM
**数据质量**：High / Medium / Low

#### 1. 一句话投资逻辑
...

#### 2. 已披露事实 / 研究推论 / 治理参数
- Fact: ...
- Research-supported: ...
- Governance/model assumption: ...

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

#### 5. Bear / Base / Bull Expected IRR
- Cash-flow timing:
- Terminal value method:
- Required Return grid:
- Bear IRR:
- Base IRR:
- Bull IRR:
- Bear Max Buy Price:
- Base Max Buy Price:
- Bull Max Buy Price:
- Current Price:

#### 6. 压力测试
- Base:
- Profit -20%:
- Profit -30%:
- Capex/Interest stress:

#### 7. Bear Case
...

#### 8. 失效条件
1. ...
2. ...

#### 9. 决策
ADD / HOLD / WATCH / TRIM / EXIT

#### 10. 权重与账户聚合
- model_long_book_weight:
- planned_long_exposure:
- model_total_account_weight:
- current_long_exposure:
- current_short_mid_exposure_same_symbol:
- post_trade_account_symbol_exposure:
- account_single_stock_cap:
- post_trade_account_cluster_exposure:
- account_cluster_cap:
- cap_state: PASS | CAP_BREACH | BLOCKED

#### 11. 建仓批次
- Chosen mode: 2 / 3 / 4 strategy tranches
- Why:
- Tranche 1 trigger:
- Tranche 2 trigger:
- Tranche 3/4 trigger:

#### 12. 证据
- 官方报告/公告：...
- 行情：...
```

## G. 长期补仓 Gate

每次后续 ADD 前全部通过：

```text
Thesis Gate
Balance Gate
Valuation Gate
Portfolio Gate
```

检查：

- [ ] thesis 仍成立
- [ ] 现金流/资本/债务未恶化
- [ ] Bear/Base/Bull Expected IRR 已刷新
- [ ] 估值仍有安全边际
- [ ] 账户级同股上限未超
- [ ] 账户级风险簇上限未超
- [ ] 已聚合短中期同股/同因子暴露
- [ ] 不是因为“跌很多”机械补仓

## H. 组合研究卡

```markdown
# Portfolio Review — YYYY-MM-DD

## Governance bundle
- Capital policy version:
- Automation governance version:
- Research model governance version:
- Long Skill version:

## 顶层资本状态
- Stock Account Equity:
- Long strategic baseline:
- Final Short Cap:
- Actual long exposure:
- Actual short exposure:
- Cash / pending deployment:
- CAP_BREACH state:

## 长期已部署权益仓内部结构
- Core weight:
- Growth weight:

## 账户级集中度
| Symbol/Cluster | Long | Short/Mid | Total account exposure | Cap | State |
|---|---:|---:|---:|---:|---|

## Benchmark
- Portfolio Total Return:
- Broad Total Return Benchmark:
- Excess Return:

## 动作
| Stock | Previous | Current | Account Weight | Action | Why changed |
|---|---|---|---:|---|---|
```

## I. 再平衡检查

- [ ] 新订单的 Planned Post-Trade Short Exposure ≤ Final Short Cap？
- [ ] 市场被动超限是否正确标记 `CAP_BREACH`，而非伪装成允许主动超限？
- [ ] 是否错误用 ±5pp 漂移带突破 Cap？
- [ ] 短中期亏损后是否错误从长期仓补血？
- [ ] 短中期盈利回流后，长期是否重新通过 Gate？
- [ ] 同股/同因子是否跨策略合并？

## J. 对抗审查 Gate

- [ ] 是否误把特别分红当普通分红？
- [ ] 是否用景气高点利润计算可持续收益？
- [ ] 是否忽略 Capex/监管资本？
- [ ] 是否存在高负债 + 高分红？
- [ ] 是否存在利润增长但现金流恶化？
- [ ] 是否存在审计/治理红旗？
- [ ] 是否表面跨行业、实际同风险簇集中？
- [ ] 是否把“公司好”误等于“当前价格值得买”？
- [ ] Expected IRR 是否按逐期现金流计算？
- [ ] 是否把终值近似 CAGR 错写成精确 IRR？
- [ ] 是否明确 Fact / Research Principle / Governance Parameter？
- [ ] 是否给出最强 Bear Case 和失效条件？
- [ ] 是否允许现金而非强制满仓？

任一关键项未完成，结论降级为 WATCH / 继续研究。

## K. 推荐输出顺序

1. Governance bundle + `as_of`。
2. Stock Account Equity / Final Short Cap / 当前现金状态。
3. 候选/持仓状态。
4. 核心逻辑和证据等级。
5. Bear/Base/Bull Expected IRR 与 Max Buy Price。
6. 建仓/补仓条件。
7. long-book 模型权重 → account weight 转换。
8. 跨策略同股/风险簇聚合。
9. Bear Case / 失效条件。
10. Total Return Benchmark 与官方证据。
