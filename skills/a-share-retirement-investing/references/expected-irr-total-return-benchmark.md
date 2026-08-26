# Expected IRR & Total Return Benchmark

> 用于把“相对低位”“好公司”转化为可比较的长期预期回报，而不是依赖股价距离高点或静态 PE。
>
> 本文件是估值方法 reference。资金、仓位和建仓批次仍以 shared policy 为准。

## 1. 核心区别

必须分开：

```text
Good Company
!=
Good Investment at Any Price
```

以及：

```text
Price Low
!=
Valuation Low
```

股价从历史高点下跌很多，不能自动代表便宜。

## 2. Expected IRR

建议用多情景 IRR 作为长期买入的共同语言：

```text
Expected IRR
= ((Estimated Terminal Value + Cumulative Cash Distributions) / Current Price)^(1/T) - 1
```

注意：

- 若 Terminal Value 已经基于 ex-dividend / retained cash 假设，避免重复计算现金；
- 回购需要反映到每股价值/股本，而不是简单当成额外现金分红；
- 银行、保险、周期股应使用行业适配终值方法；
- 这是估值模型，不是未来收益保证。

## 3. Bear / Base / Bull

每只长期候选至少建立三种情景：

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

网格是研究参数，可根据账户目标、行业风险和市场环境调整。

## 5. Max Buy Price

用 Required Return 反推最高可接受买价：

```text
Max Buy Price
≈ (Estimated Terminal Value + Cumulative Cash Distributions)
  / (1 + Required Return)^T
```

实际使用时输出：

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
Base Terminal Value = 30
Cumulative Dividends = 5
```

则：

```text
Base IRR ≈ (35 / 20)^(1/5) - 1 ≈ 11.8%
```

该数字只用于说明计算方法，不代表任何实际股票预测。

## 7. 不同行业的终值方法

### 银行

优先考虑：

```text
Sustainable ROE
Capital Adequacy
Asset Quality
Dividend Capacity
PB-ROE relationship
```

### 公用事业 / 电信

重点：

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

重点：

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

例如沪深 300：

```text
Price Index      = 000300
Total Return     = H00300
```

长期报告优先：

```text
Portfolio Total Return
vs
Broad-market Total Return Benchmark
vs
Relevant Sector Total Return Benchmark
```

若某指数没有可用全收益口径，必须明确标记口径差异，不能静默比较。

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

长期不使用统一盈利百分比退出。

重新估值后：

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
bear/base/bull assumptions
required_return_grid
estimated_dividends
actual subsequent results (later, separately)
```

后续复盘不得用未来实际结果静默改写原始估值假设；需要保留原版本与 prediction error。
