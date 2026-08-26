# Expected IRR & Total Return Benchmark v1.1

> 用于把“相对低位”“好公司”转化为可比较的长期预期回报，而不是依赖股价距离高点或静态 PE。
>
> 本文件是估值方法 reference。资金、仓位和建仓批次仍以 shared capital policy 为准；研究参数与模型证据等级受 `../../../shared/research-model-governance.md` 约束。

## 1. 核心区别

```text
Good Company != Good Investment at Any Price
Price Low    != Valuation Low
```

股价从历史高点下跌很多，不能自动代表便宜。

## 2. Expected IRR：正式定义

建议用多情景 Expected IRR 作为长期买入共同语言，但 IRR 必须尊重现金流发生时间。

若：

```text
P0   = 当前买入价格
CF_t = 第 t 年预计可归属于股东的现金分配
TV_T = 第 T 年终值
r    = Expected IRR
```

则 `r` 满足：

```text
0
= -P0
+ CF_1/(1+r)^1
+ CF_2/(1+r)^2
+ ...
+ (CF_T + TV_T)/(1+r)^T
```

实际日期不规则时优先使用 XIRR/按日期折现，而不是把所有现金流假设发生在年末。

### 粗略终值近似的限制

```text
((TV_T + Cumulative Cash Distributions) / P0)^(1/T) - 1
```

只可作为粗略 sanity check，因为它隐含假设所有中间分红在终点收到。**不得把这个近似值标记成精确 IRR。**

注意：

- 若 Terminal Value 已处理 retained cash / ex-dividend 逻辑，避免现金双重计算；
- 回购通过股本和每股价值反映，不简单当额外现金分红；
- 银行、保险、周期股使用行业适配终值方法；
- Expected IRR 是估值模型，不是未来收益保证。

## 3. Bear / Base / Bull

每只长期候选至少建立三种情景。

### Bear

- 盈利低于预期；
- margin / ROE / commodity price / volume 使用保守假设；
- 终值估值倍数收缩；
- 分红增长下降或暂停增长；
- 必要时加入资本开支、监管资本或债务压力。

### Base

- 使用正常化盈利和合理经营假设；
- 终值估值不依赖极端乐观重估；
- 分红与现金流覆盖逻辑一致。

### Bull

- 允许经营改善和合理估值扩张；
- 不能仅用“热门赛道”提高倍数；
- 必须说明关键事实如何实现。

## 4. Required Return

```text
Required Return
= Point-in-time Risk-free Rate
+ Configured Required Risk Premium
```

禁止把某个固定 ERP 写成所有 A 股统一真理。

建议至少做敏感性网格：

```text
Required Risk Premium:
4%
6%
8%
```

网格是研究参数，可根据账户目标、行业风险和市场环境调整；任何修改需按 research-model-governance 记录。

## 5. Max Buy Price：逐期折现

给定 Required Return `k`：

```text
Max Buy Price
= Σ[CF_t / (1+k)^t]
+ TV_T / (1+k)^T
```

不能把所有累计分红与终值简单加总后统一只折现 T 年，除非明确标注那只是保守/粗略近似。

实际输出：

```text
Bear Max Buy Price
Base Max Buy Price
Bull Max Buy Price
Current Price
Margin of Safety vs Base
Bear IRR
Base IRR
Bull IRR
```

## 6. 示例

假设：

```text
Current Price = 20
T = 5 years
Annual Dividend = 1
Base Terminal Value at year 5 = 30
```

精确 Expected IRR 应解：

```text
20
= 1/(1+r)
+ 1/(1+r)^2
+ 1/(1+r)^3
+ 1/(1+r)^4
+ 31/(1+r)^5
```

而不是直接把 5 元累计分红全部视为第5年收到。

该示例只说明方法，不代表实际股票预测。

## 7. 不同行业的终值方法

### 银行

```text
Sustainable ROE
Capital Adequacy
Asset Quality
Dividend Capacity
PB-ROE relationship
```

### 公用事业 / 电信

```text
FCF
Capex cycle
Dividend capacity
Debt
Allowed return / tariff mechanism
```

### 周期 / 资源

必须使用中周期盈利：

```text
Normalized Commodity Price
Normalized Margin
Cost Curve
Capex Discipline
```

禁止使用周期高点 EPS × 低 PE 得出“非常便宜”。

### 消费

```text
Volume
Pricing Power
Margin
ROIC
Cash Conversion
Brand / Share
```

### 科技 / 成长

反推当前价格隐含增长：

```text
Revenue Growth
Margin Path
R&D Conversion
FCF Inflection
Terminal Multiple
```

若必须依赖极高持续增长才能达到 Required Return，降低安全边际评价。

## 8. 长期 Benchmark 必须使用 Total Return

长期策略不能只和价格指数比较，因为组合自身会收到现金分红。

例如沪深300：

```text
Price Index  = 000300
Total Return = H00300
```

长期报告优先：

```text
Portfolio Total Return
vs
Broad-market Total Return Benchmark
vs
Relevant Sector Total Return Benchmark
```

若指数没有可用全收益口径，必须明确标记口径差异，不能静默比较。

## 9. 分红复投口径

组合层面至少保存：

```text
price_return
cash_dividends_received
dividends_reinvested
total_return
benchmark_total_return
```

分红进入组合级现金池后，不要求机械买回原股票；策略执行仍按长期 Skill 的分红复投规则。

## 10. 长期 ADD 决策

价格下跌不直接触发补仓。

先重新计算：

```text
Bear/Base/Bull IRR
```

再同时检查：

```text
Thesis Gate
Balance Gate
Valuation Gate
Portfolio Gate
```

只有：

```text
Thesis unchanged or stronger
+ Expected IRR improves
+ Balance Sheet passes
+ Portfolio capacity exists
```

才允许 ADD。

## 11. SELL / TRIM

### HOLD

```text
Thesis intact
Expected Return acceptable
Portfolio concentration acceptable
```

### TRIM

```text
Expected IRR falls below required hurdle
OR concentration exceeds policy
OR clearly superior alternative exists
```

### EXIT

```text
Thesis invalidated
OR governance/accounting risk becomes unacceptable
OR permanent earnings power materially impaired
```

## 12. 模型误差治理

任何长期估值必须保存：

```text
as_of
data_sources
terminal_year
terminal_value_method
cash_flow_timing
bear/base/bull assumptions
required_return_grid
estimated_cash_distributions
actual subsequent results (later, separately)
research_model_governance_version
```

后续复盘不得用未来实际结果静默改写原始估值假设；保留原版本与 prediction error。
