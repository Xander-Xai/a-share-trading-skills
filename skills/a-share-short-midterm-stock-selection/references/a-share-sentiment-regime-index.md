# A-Share Sentiment Regime Index v1.0

> 目的：把“市场情绪”从主观感觉转成 0–100 的可重复状态变量。
>
> 状态：`RESEARCH / MONITOR INPUT`。权重和阈值属于 Governance Parameter，不宣称数学最优；必须通过 Forward 数据校准。

## 1. 为什么需要独立情绪层

A 股研究显示投资者结构、换手、涨跌停、极端收益与短期 momentum/reversal 之间存在显著关系，但这些关系高度依赖市场阶段。

因此情绪指数不负责“预测明天一定涨跌”，只负责回答：

```text
当前市场承担短中期风险的环境如何？
当前是恐慌、风险厌恶、中性、风险偏好还是亢奋？
```

外部研究基线：

- A 股更明显存在月度反转，而日频可观察到 momentum，说明时间尺度和投资者结构很重要：
  https://www.nber.org/papers/w29453
  https://www.nber.org/papers/w31839
- 涨停事件可能伴随过度反应：
  https://www.sciencedirect.com/science/article/pii/S0264999322001560
- turnover 在中国市场研究中经常被当作 sentiment/attention 的代理，但它同时包含流动性和分歧信息，因此不能单独作为情绪真相源。

## 2. 总分

```text
Sentiment Score = 0–100
```

六个分量：

| Component | Weight |
|---|---:|
| Breadth | 25 |
| Limit-up vs Limit-down Balance | 20 |
| Board Quality / Broken-limit Rate | 15 |
| Strong-tail vs Weak-tail Balance | 15 |
| Median Stock Return | 10 |
| Turnover Expansion | 15 |
| Total | 100 |

若某项缺失，按剩余可用权重重新归一化；可用原始权重不足 70% 时：

```text
state = DATA_INSUFFICIENT
```

禁止用缺数据的情绪分数自动放宽风险。

## 3. Breadth — 25

定义：

```text
advance = 涨幅 > 0 的有效 A 股数量
decline = 涨幅 < 0 的有效 A 股数量

breadth_score
= 100 × advance / (advance + decline)
```

平盘不进入分母。

解释：

- 只有少数权重股上涨而多数股票下跌时，指数上涨不能得到高 breadth 分；
- breadth 是市场扩散度，不是未来收益保证。

## 4. Limit Balance — 20

```text
U = 涨停家数
D = 跌停家数

limit_balance_score
= clip(50 + 50 × (U-D)/(U+D+10), 0, 100)
```

`+10` 是平滑项，避免家数很少时分数极端化；属于治理参数。

不同板块涨跌幅限制不同，因此优先使用数据源已经识别后的涨停/跌停池，而不是统一用 ±10% 自己判断。

## 5. Board Quality — 15

```text
U = 封住涨停家数
B = 炸板家数

board_quality_score
= 100 × (1 - B/(U+B+1))
```

高炸板率表示追涨承接质量弱。

注意：极低样本日该指标不稳定，因此必须和 Breadth、Tail、Turnover 一起使用。

## 6. Strong / Weak Tail — 15

MVP 定义：

```text
strong = 当日涨幅 >= +5% 的股票数
weak   = 当日跌幅 <= -5% 的股票数

tail_score
= clip(50 + 50 × (strong-weak)/(strong+weak+20), 0, 100)
```

+5%/-5% 与平滑项 20 均为治理参数。

## 7. Median Return — 10

市场平均值容易被极端股票影响，因此使用中位数：

```text
m = 全 A 有效股票当日涨跌幅中位数（%）

median_score
= clip(50 + 12.5 × m, 0, 100)
```

约 +4% 映射接近 100，-4% 映射接近 0。

## 8. Turnover Expansion — 15

定义当日全 A 成交额：

```text
T0 = 当日全 A 成交额
T20 = 最近 20 个有效交易日成交额中位数
```

若历史不足 10 个交易日：

```text
turnover_score = 50
confidence = LOW
```

否则：

```text
turnover_score
= clip(50 + 25 × ln(T0/T20), 0, 100)
```

成交额放大本身不是利好；该分量必须与 Breadth、涨跌停和价格方向联合解释。

## 9. Regime 映射

```text
0–20   PANIC
20–40  RISK_OFF
40–60  NEUTRAL
60–80  RISK_ON
80–100 EUPHORIA
```

边界采用左闭右开，100 属于 EUPHORIA。

### 特别规则：EUPHORIA != ALL_IN

高情绪可能意味着强趋势，也可能意味着拥挤和尾部风险。

如果：

```text
score >= 80
AND broken_limit_rate 上升
OR 强势股高位负反馈明显
```

则附加：

```text
crowding_flag = TRUE
```

并禁止把 EUPHORIA 自动解释为提高仓位。

## 10. 与短中期策略的关系

默认治理映射：

```text
PANIC
→ NO_NEW_TREND_ENTRY，除非策略明确支持恐慌反转

RISK_OFF
→ 提高入场阈值 / 降低单笔风险 / 拒绝追高

NEUTRAL
→ 正常按个股 Gate

RISK_ON
→ 正常寻找高质量 setup，但仍服从 Reward/Risk 与 Heat

EUPHORIA
→ 允许已有趋势持仓管理；新仓必须额外检查 extension/crowding
```

情绪指数绝不能覆盖：

- Hard Veto；
- Final Short Cap；
- 单股/风险簇 Cap；
- Stop/Invalidation；
- Broker/Automation Gate。

## 11. 数据字段

每日保存：

```yaml
date:
as_of:
valid_stock_count:
advance_count:
decline_count:
flat_count:
limit_up_count:
limit_down_count:
broken_limit_count:
strong_count:
weak_count:
median_return_pct:
total_turnover:
turnover_20d_median:
breadth_score:
limit_balance_score:
board_quality_score:
tail_score:
median_score:
turnover_score:
sentiment_score:
regime:
crowding_flag:
data_confidence:
provider_errors:
```

## 12. 数据源与实现

MVP 使用 AKShare 作为可替换 Provider，接口包括：

```text
stock_zh_a_spot_em
stock_zt_pool_em
stock_zt_pool_dtgc_em
stock_zt_pool_zbgc_em
tool_trade_date_hist_sina
```

AKShare 是聚合数据接口，不是交易所官方真相源。Live/Semi-auto 阶段必须增加官方/券商行情交叉验证，并遵循 fail closed。

接口文档：
https://akshare.akfamily.xyz/data/stock/stock.html

## 13. 校准规则

每月只做诊断，不自动改参数。

至少按未来 1/3/5/10 个交易日统计：

```text
future broad-index return
future median-stock return
max adverse excursion
breakout success rate
strategy expectancy_R
```

按 Sentiment bucket 分层。

只有形成新 hypothesis → Challenger → Forward-Test → Human Promotion Review 后，才能修改权重或阈值。
