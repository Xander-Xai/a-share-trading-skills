# 执行模板

本模板用于每次真实运行 Skill，确保不会因为聊天上下文、行情波动或主观偏好跳过关键步骤。

## A. 输入

```yaml
as_of: 自动获取
market: 沪深A股
universe: 用户给定股票池 | 全市场
objective: 长期养老权益仓
holding_horizon: 10年以上（若用户另有说明则覆盖）
core_dividend_target: 75%-85%
growth_target: 15%-25%
max_single_stock: 25%
max_risk_cluster: 30%-35%
extra_filters:
  price_max: null
  market_cap_min: null
  industries: null
  excluded_industries: null
```

## B. 数据获取检查

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

## C. 单股研究卡

```markdown
### 股票名（代码）

**角色**：Core / Growth
**as_of**：YYYY-MM-DD
**数据质量**：High / Medium / Low

#### 1. 一句话投资逻辑
...

#### 2. 已披露事实
- ...
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

#### 11. 最大建议仓位
...

#### 12. 证据
- 官方年报：...
- 官方公告：...
- 行情：...
```

## D. 组合研究卡

```markdown
# Portfolio Review — YYYY-MM-DD

## 结构
- Core: xx%
- Growth: xx%
- Cash pending deployment: xx%

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

## E. 对抗审查 Gate

只有以下全部回答完成后，才允许给出最终组合：

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

任一项未完成，结论应降级为 WATCH 或继续研究。

## F. 推荐输出顺序

1. 先给结论和候选/持仓状态。
2. 再给为什么。
3. 再给估值与买入区间。
4. 再给组合权重与风险簇。
5. 再给 Bear Case / 失效条件。
6. 最后列官方证据和 `as_of`。

不要从长篇宏观叙事开始，也不要只给“值得长期持有”这种不可执行判断。
