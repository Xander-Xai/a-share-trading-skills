# A股长期养老选股方法论 v2.1

> 本文解释长期养老 Skill 的第一性原理、估值、建仓、补仓与持仓哲学。
>
> 上位规则：
> - 资本/分母/仓位：`../../../shared/capital-allocation-and-entry-policy.md`
> - 研究/模型/Benchmark：`../../../shared/research-model-governance.md`
> - Paper/Live/自动化：`../../../shared/automation-execution-governance.md`

## 一、目标函数

长期养老型股票投资的目标不是“今年拿最多股息”，而是未来多年持续获得真实购买力可维持的股东现金流，同时尽量避免永久性资本损失。

```text
长期年化股东回报
≈ 起始普通股息率
+ 每股正常化盈利/分红增长
+ 估值变化
- 税费
- 永久性资本损失
```

优化：

```text
最大化：可持续真实现金流 + 合理资本增值
约束：永久损失、分红不可持续、估值过高、账户级集中、治理风险
```

## 二、高股息不等于高质量

高股息可能来自：

- 优质现金牛且价格合理；
- 周期高点利润；
- 股价因基本面恶化而暴跌；
- 特别分红或资产处置；
- 高支付率甚至新增负债维持分红。

长期养老核心优先寻找第一类。

## 三、长期已部署权益仓采用 Core + Growth

```text
Core Dividend 75%–85%
Growth Satellite 15%–25%
```

这是 long-book 内部权重，不是全账户权重。

账户级集中度使用：

```text
Stock Account Equity
= 长期股票市值 + 短中期股票市值 + 待配置现金
```

模型 long-book 权重必须先换算为账户权重，再检查 shared Cap。

## 四、核心分红股筛选漏斗

### Level 0：数据可信性

确认最新正式披露、股价、市值、普通/特别分红。无法验证就停止。

### Level 1：长期存在价值

1. 10–20年后需求是否仍存在？
2. 是否有资源、牌照、品牌、网络、成本、技术、规模或客户壁垒？
3. 维持业务是否需要不可持续资本投入？
4. 是否长期有能力赚取高于资本成本的回报？
5. 监管、技术替代、人口结构是否可能破坏商业模式？

### Level 2：利润质量

排查扣非、应收、存货、OCF、资本化支出和一次性收益。

### Level 3：分红可持续性

```text
普通现金分红 / 正常化归母净利润
普通现金分红 / 正常化自由现金流
过去5–10年每股普通分红轨迹
削减分红年份及原因
```

银行使用监管资本和资产质量替代普通 FCF 逻辑。

### Level 4：资产负债表

按行业检查净负债、利息覆盖、债务期限、Capex、融资成本、信用评级或监管资本。

### Level 5：价格与组合适配

```text
Quality：是不是长期好资产？
Price：当前价格是否提供足够 Expected Return？
Portfolio Fit：加入账户后是否通过同股/同因子聚合限制？
```

三者都合格才进入 ADD。

## 五、分红质量层级

1. 偶发分红
2. 高股息但波动大
3. 稳定金额分红
4. 稳定比例分红
5. 稳定且增长的分红
6. 稳定增长 + 良好资本配置

普通股息与特别股息分开：

```text
Ordinary Dividend Yield = 普通现金分红 / 当前股价
Special Dividend Yield  = 特别分红 / 当前股价
```

特别分红不得外推。

## 六、压力测试

### 非金融企业

至少测试：

| 情景 | 正常化利润 | 现金流/资本开支假设 |
|---|---:|---|
| Base | 100% | 正常 |
| Stress 1 | 80% | Capex +10% 或利息上升 |
| Stress 2 | 70% | Capex +20% 或现金转化下降 |

重算支付率、FCF覆盖、净债务和利息覆盖。

### 银行

测试 NIM、信用成本、ROE、不良率、CET1/资本缓冲。

### 周期资源股

使用中周期利润，不能把商品价格高点盈利外推为长期分红能力。

## 七、Expected IRR 与估值

读取 `expected-irr-total-return-benchmark.md`。

必须尊重现金流时点。正式 IRR `r` 满足：

```text
0 = -P0 + Σ[CF_t/(1+r)^t] + TV_T/(1+r)^T
```

给定 Required Return `k`：

```text
Max Buy Price
= Σ[CF_t/(1+k)^t] + TV_T/(1+k)^T
```

Bear/Base/Bull 至少同时输出：

```text
Expected IRR
Max Buy Price
关键盈利/分红/终值假设
Required Return sensitivity
```

“累计分红 + 终值全部放到最后一年”的 CAGR 只能作近似 sanity check，不称精确 IRR。

## 八、成长卫星仓

成长逻辑必须完成：

```text
产业需求增长
→ 公司获得订单/份额
→ 收入增长
→ 利润增长
→ 现金流改善
→ 每股价值增长
```

如果链条停留在“概念很热”，不能进入长期成长核心。

必须检查收入/利润质量、OCF、毛利率、客户集中、估值隐含增速、产业 Capex 周期和技术替代风险。

## 九、风险簇而不是只看行业名

示例：

- 能源商品：煤炭、石油、部分火电；
- 利率/信用：银行、保险、地产链；
- 公用事业：水电、核电、电网；
- 消费需求：食品饮料、家电、零售；
- AI Capex：AI服务器、数据中心、光通信、部分芯片；
- 出口/海外客户：消费电子、制造链。

申万行业不同不代表经济驱动不同。

并且风险簇必须跨策略聚合：

```text
Account Cluster Exposure
= Long Cluster Exposure + Short/Mid-term Cluster Exposure
```

## 十、动态仓位与同股聚合

仓位上限以 shared policy 为准。

同一股票跨策略：

```text
Account Symbol Exposure
= Long Sleeve Exposure + Short/Mid-term Sleeve Exposure
```

长期策略不得因为另一份仓位被标记为“短中期”就忽略账户真实集中度。

若市场上涨造成被动超限，标记 `CAP_BREACH`、停止新增并进入再平衡，而不是用漂移区间合理化继续加仓。

## 十一、建仓

默认：

```text
40% / 30% / 30%
```

例外：

```text
60% / 40%
30% / 25% / 25% / 20%
```

通常约1–3个月完成。分批管理估值误差和信息释放，不是无限期等待完美买点。

后续批次只有在：

- Expected IRR / 安全边际更好且 thesis 未坏；
- 新财报/经营事实继续验证；
- 账户级同股/风险簇仍有容量；

才触发。

## 十二、补仓：四个 Gate

```text
Thesis Gate
Balance Gate
Valuation Gate
Portfolio Gate
```

价格下跌不是补仓理由。

- 下跌约15%–20%：重新研究；
- 下跌约25%–30%：深度 thesis review。

这些是研究触发线，不是机械交易线。

## 十三、长期止损与止盈

### EXIT

- 商业模式/护城河结构性破坏；
- 正常化盈利能力永久下降；
- 分红削减背后是现金流/偿债/资本恶化；
- 审计、造假、治理红旗；
- 债务或资本结构失控；
- 原 thesis 被事实证伪。

### TRIM

```text
Expected IRR 明显低于 Required Return
+ 账户级单股/风险簇超配
+ 更优替代机会
```

不使用固定“涨20%全卖”。

## 十四、分红复投

分红进入组合现金池，重新评估全部持仓和候选。没有合格标的时允许持有现金。

## 十五、Benchmark

长期绩效优先使用 Total Return Benchmark。

组合自身 Total Return 与基准必须使用一致的分红再投资口径。若没有对应全收益指数，要明确口径差异。

## 十六、复核节奏

- 季度：轻复核；
- 年报：完整评分、正常化盈利、压力测试、IRR、集中度；
- 重大事件：立即复核。

## 十七、对抗审查

至少做：

- Yield Trap Test；
- Peak Cycle Test；
- Debt-funded Dividend Test；
- Governance Test；
- Correlation / Cross-sleeve Concentration Test；
- Reverse Valuation / Expected IRR Test；
- Replacement Test；
- Opportunity Cost Test；
- Point-in-time Test。

## 十八、记录格式

```yaml
as_of:
capital_policy_version:
research_model_governance_version:
skill_version:
portfolio_version:
stock:
  ticker:
  role: core|growth
  score:
  action: ADD|HOLD|WATCH|TRIM|EXIT
  bear_irr:
  base_irr:
  bull_irr:
  required_return:
  model_long_book_weight:
  model_total_account_weight:
  account_symbol_exposure:
  account_cluster_exposure:
  max_buy_price:
  thesis:
  bear_case:
  invalidation_triggers:
  sources:
```

下一轮必须说明什么变了、为什么变、是否足以改变仓位。

## 十九、证据原则

事实、研究支持原则和治理参数必须分层。具体资金比例、评分权重、仓位上限、建仓批次、Required Risk Premium 网格都不宣称为学术证明的唯一最优值；修改应遵循 research-model-governance 的版本与验证流程。
