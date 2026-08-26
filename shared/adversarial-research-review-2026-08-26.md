# Adversarial Research Review — 2026-08-26

> 目的：对仓库此前关于技术分析、资金、长期持有、分批买入、频繁交易、Benchmark 与自动化的结论进行反方审查。
>
> 本文件是研究证据记录，不是新的资金/风险 Source of Truth。生产规则以 shared policy / Skill 为准。

## 1. 审查方法

对每个结论分别问：

1. 这是事实、研究推论还是内部治理参数？
2. 有没有把相关性说成因果？
3. 有没有把海外研究数字直接套到 A 股？
4. 有没有幸存者偏差、look-ahead 或 data-snooping？
5. 有没有忽略交易成本和执行限制？
6. 有没有把“合理规则”说成“数学最优规则”？

## 2. 最终保留 / 修正矩阵

| 命题 | 结论 | 修正后表述 |
|---|---|---|
| 技术指标使用历史数据 | 保留 | 历史数据不等于没有条件预测信息 |
| 技术分析可作为执行层 | 保留但收缩 | 技术可用于状态、相对强弱、波动、结构和执行；Alpha 必须样本外验证 |
| 技术指标属于左侧交易 | 删除 | 左/右侧描述入场相对趋势确认的位置，不由数据是否历史决定 |
| 资金推动价格 | 修正 | 预期变化影响订单意愿，订单流与流动性参与价格发现；vendor 主力流入不是机构净买入事实 |
| 不退市即可长期拿 | 删除 | 生存只是 Gate；长期回报取决于每股价值创造、现金流、治理与买入价格 |
| 频繁交易通常拖累散户 | 保留 | 有强研究支持，但不能推出所有短线策略都必然失败 |
| 分批一定优于一次性投入 | 删除 | 分批主要管理择时/行为/个股尾部风险；现金等待存在机会成本 |
| 长期 Benchmark 应含分红 | 强保留 | 使用 Total Return 口径 |
| 只能给赢家加仓 | 限定 | 适用于趋势/催化策略；不推广到长期价值分批 |
| 固定新评分权重优于旧模型 | 删除 | 必须 Champion/Challenger 前测后晋级 |
| ERP 固定 4%–6% | 删除 | Required Risk Premium 是配置参数，应做敏感性分析 |
| +1.5R/+2R、3–5日 time stop 最优 | 删除“最优” | 可保留为当前治理初值，用 MFE/MAE 校准 |

## 3. 频繁交易证据

### Barber & Odean — Trading Is Hazardous to Your Wealth

Source:

https://faculty.haas.berkeley.edu/odean/papers/returns/individual_investor_performance_final.pdf

样本：66,465 个美国折扣券商家庭账户，1991–1996。

论文摘要报告：

```text
最高换手组年收益约 11.4%
市场约 17.9%
平均家庭约 16.4%
```

可以支持：高换手个人投资者平均表现明显更差。

不能支持：所有短线/量化/事件策略都必然跑输长期持有。

### Taiwan whole-market investor data

Source:

https://academic.oup.com/rfs/article-abstract/22/2/609/1595677

论文摘要报告个人投资者交易带来的年度 performance penalty 约 3.8 个百分点，并指出大量损失来自 aggressive orders。

可以支持：散户主动交易存在显著行为与交易成本风险。

不能直接把 3.8% 当成 A 股未来短线策略固定损失。

## 4. 长期个股回报高度偏态

### Bessembinder et al. — Long-Term Shareholder Returns

Source:

https://www.tandfonline.com/doi/full/10.1080/0015198X.2023.2188870

研究覆盖 1990–2020 年超过 64,000 只全球普通股。

摘要报告：

```text
55.2% 美国股票完整样本复合收益低于一个月美国国债
57.4% 非美国股票低于一个月美国国债
全球净财富创造由表现最好的约 2.4% 公司贡献
```

可以支持：长期“只要活着就拿”不是充分策略；个股长期结果高度偏态。

限制：这是全球研究，不得把上述比例直接当成 A 股精确概率。

## 5. 分批投入证据边界

### Vanguard — Cost averaging: Invest now or temporarily hold your cash?

Source:

https://corporate.vanguard.com/content/dam/corp/research/pdf/cost_averaging_invest_now_or_temporarily_hold_your_cash.pdf

研究支持：对于已经拥有、准备投入多元化风险资产的现金，一次性投入历史上多数时期优于暂时持有现金后分批投入，因为现金等待有机会成本。

不能直接推出：单只 A 股应该一次性满仓。

仓库结论：

```text
40/30/30 等批次属于个股风险治理参数
不是收益最大化定理
```

## 6. 技术分析证据边界

已有中国市场技术规则研究表明，某些技术策略在特定样本、参数和市场阶段可能有统计/经济意义，但在 data-snooping、交易成本与样本外检验后，可持续规则数量显著减少。

仓库不采用两种极端说法：

```text
“看线一定有用”
“所有技术指标完全无用”
```

统一表述：

```text
Technical Edge is regime-dependent, parameter-dependent, cost-sensitive and must be validated out of sample.
```

因此技术因子可以保留，但是否拥有 Alpha 必须由 Champion/Challenger 真实数据证明。

## 7. 资金与价格

不把“主力净流入”当作机构真实净买入。

统一采用：

```text
Participation
+ Positioning Evidence
+ Price Confirmation
```

如果 vendor flow 标签与价格/相对强度长期冲突，应降低该 flow 证据权重。

## 8. “相对低位”修正

禁止：

```text
距离历史高点 -30%
→ 自动判断便宜
```

必须分离：

```text
Price Low
Valuation Low
```

长期仓使用 Bear/Base/Bull IRR、正常化盈利、现金流和行业适配估值判断安全边际。

## 9. Total Return Benchmark

中证指数沪深300事实表列示：

```text
Price Index ticker: 000300
Total Return ticker: H00300
```

Source:

https://oss-ch.csindex.com.cn/static/html/csindex/public/uploads/indices/detail/files/en/000300factsheeten.pdf

长期策略必须和含分红的 Total Return 口径比较，避免组合含分红而 Benchmark 不含分红造成口径偏差。

## 10. 自动化与程序化交易监管

### 中国证监会

《证券市场程序化交易管理规定（试行）》自 2024-10-08 起实施，并明确落实“先报告、后交易”。

Source:

https://www.csrc.gov.cn/csrc/c100028/c7480577/content.shtml

### 上海证券交易所

《上海证券交易所程序化交易管理实施细则》自 2025-07-07 起施行，当前页面标注现行有效。

Source:

https://www.sse.com.cn/lawandrules/sselawsrules2025/trade/universal/c/c_20250612_10781696.shtml

### 深圳证券交易所

《深圳证券交易所程序化交易管理实施细则》自 2025-07-07 起施行。

Source:

https://www.szse.cn/lawrules/rule/trade/t20250403_612770.html

因此：

```text
AUTO_MONITOR = true
AUTO_ORDER = false
```

继续作为默认状态。

代码能下单不等于已满足报告、券商、账户、风控和交易所要求。

## 11. 本次对抗审查形成的 v3 架构

新增：

- `research-model-governance.md`
- 短中期 `causal-challenger-model.md`
- `champion-challenger-forward-test.md`
- `trade-ledger-mfe-mae-extension.md`
- 长期 `expected-irr-total-return-benchmark.md`

核心变化：

```text
旧模型不因理论争论直接退役
→ Champion 保留
→ 新模型 Shadow
→ Forward-Test
→ Cost/Risk/Regime 审查
→ 人工 Promotion Review
```

这避免把“更合理的故事”误当成“已经证明的 Alpha”。
