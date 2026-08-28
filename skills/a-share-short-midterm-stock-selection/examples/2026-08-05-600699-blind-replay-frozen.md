# 2026-08-05 均胜电子 Blind Replay — Frozen v1

> **Analysis as of:** 2026-08-05 15:00 CST  
> **Constructed:** 2026-08-29  
> **Type:** retrospective blind replay, frozen  
> **Forward-alpha eligibility:** **NO**  
>
> 本文件只允许使用 2026-08-05 15:00 以前已经公开、可获得的信息。任何 8 月 5 日收盘后的公告、两融、价格路径和后续财报均不得写回本文件。未来揭盲必须另建文件。

## 1. 为什么这不是 Level-C Forward 样本

这次 replay 虽然做了未来数据隔离，但研究者在 8 月 29 日已经知道真实后续走势，因此不可声称为真正“未见结果”的 Forward Test。

它的用途是：

- 检查 point-in-time 纪律；
- 检查当前系统在 8 月 5 日会如何描述状态；
- 检查仓位/失效位计算能否在事前成立；
- 把后见之明污染显式排除。

它**不能**证明模型有 Alpha。

## 2. 用户真实交易事实

```text
代码：600699
名称：均胜电子
交易日：2026-08-05
用户报告成本：21.525
用户报告仓位：约 50%
准确成交时间：未知
```

因为成交时间未知，本 replay 只能重建 **8 月 5 日收盘状态以及下一交易日决策**，不能声称重建了用户下单瞬间的全部信息集。

## 3. 8 月 5 日收盘时可知的市场事实

### 个股

```text
开盘 21.69
最高 21.85
最低 21.21
收盘 21.62
当日 +2.27%
成交量约 3849 万股
换手约 2.76%
```

已知的左侧结构包括：

```text
7/24 收盘 19.19
7/31 收盘 20.60
8/03 最低 20.60
8/04 收盘 21.14

更左侧：
7/03 收盘 23.45、最高 24.05
7/06 最高 23.69
7/10 收盘 21.55
7/17 收盘 20.00
```

因此 8 月 5 日的合理技术描述是：

> **从 19.19 一带恢复后的强势 reclaim / recovery，但尚未突破 7 月初 23.45–24.05 的主要前高区。**

不是“新高趋势已经确认”。

## 4. 当日市场 / 板块背景

8 月 5 日：

```text
上证 +1.47%
深成指 +1.86%
创业板 +1.32%
全市场成交约 2.68 万亿元
上涨股票约 3700 只
```

智能驾驶方向当日明显活跃，多只相关个股涨停或大涨。

因此：

```text
market regime = broad risk-on rebound
sector/theme = supportive
```

但“板块强”不能替代个股自身后续确认。

## 5. 当时可用的基本面

最新正式经营基础主要来自 2026Q1：

```text
营收约 138.15 亿元，同比 -5.22%
归母净利润约 4.02 亿元，同比 +18.11%
扣非净利润约 3.62 亿元，同比 +13.23%
经营现金流约 9.1 亿元
一季度全球新增全生命周期订单约 275 亿元，同比约 +75.2%
```

状态：

> **营收仍承压，但利润/扣非和现金流改善，订单较强。基本面提供支撑，但不足以单独证明未来 5–15 日上涨。**

## 6. 资金数据必须做 PIT 修正

2026-08-05 当天的融资数据是在 8 月 6 日才公开，因此不能放入 8 月 5 日 replay。

8 月 5 日 08:01 已公开、截至 8 月 4 日的数据为：

```text
融资买入 6700.95 万元
融资偿还 6334.81 万元
融资净买入 366.14 万元
融资余额 14.385806 亿元
融资余额处于近一年较低分位
```

因此当时更合理的结论是：

> **价格和成交量改善，但杠杆参与并没有提供很强的趋势性确认。**

## 7. Champion 事前状态

由于并没有完整、可机器复现的 8 月 5 日所有 PIT 特征，本 replay 不伪造一个精确生产分数。

人工研究估计：

```text
约 68–74
Data completeness = Partial
Confidence = Medium/Low for exact score
```

这个数字只是**排名区间**，不是上涨概率。

按照仓库当前正式阈值：

```text
80+    high priority
75–79 trade candidate with trigger
65–74 WATCH / WAIT FOR CONFIRMATION
<65    normally no new position
```

所以如果 8 月 5 日收盘时**尚未持仓**：

# 生产决策应是 `WATCH / WAIT FOR CONFIRMATION`

而不是立即建立大仓位。

## 8. 右侧只能写条件路径，不能写未经校准的概率

此前人工分析曾写过 50% / 30% / 20% 三种情景概率。对抗审查认为这些数字没有历史校准依据，因此本冻结样本删除所有路径概率。

### Path A — Continuation

触发条件：

```text
有效收复 / 站稳约 21.85–22.00
+ 有价格进展的量能
+ 板块/参与度不恶化
```

动作：

```text
重新跑 Champion
只有分数达到生产交易阈值、执行 Gate 和风险 Gate 同时通过，才允许考虑新仓。
```

更上方只把：

```text
22.5
23.45–24.05
```

作为执行几何 / 旧压力参考，不写成必达目标。

### Path B — Neutral / No Follow-through

```text
约 21.0–21.85 区间震荡
```

动作：

```text
不加仓
3–5 个交易日做 review
```

但“3–5 日”是治理参数和 Challenger 研究窗口，不是学术最优定律。

### Path C — Failure

第一结构参考：

```text
20.60
```

若失守：

```text
state -> weakening / re-underwrite
```

更宽的恢复结构参考：

```text
20.00
```

若明显失守：

```text
recovery thesis materially damaged
→ invalidation candidate
```

20.60 / 20.00 都只来自 8 月 5 日以前已经存在的价格结构。

## 9. 仓位是8月5日就能发现的问题

用户报告成本：

```text
E = 21.525
```

### 若以 20.60 作为结构失效参考

```text
stop distance ≈ 4.297%
```

按仓库当前计划风险：

```text
0.5% planned loss -> 理论仓位约 11.64% short-strategy NAV
1.0% hard ceiling -> 理论仓位约 23.27% short-strategy NAV
```

若同一 NAV 分母下真的使用 50% 仓位：

```text
计划损失约 2.15% NAV
```

尚未计入跳空 / 滑点。

### 若给到 20.00 更宽失效位

```text
stop distance ≈ 7.085%
0.5% risk -> 理论仓位约 7.06%
1.0% risk -> 理论仓位约 14.11%
50% 同分母仓位 -> 计划损失约 3.54%
```

用户所说“50%”的准确 NAV 分母未独立核验，因此这里只做条件诊断。

## 10. 8 月 5 日收盘时，如果已经人工成交怎么办

A 股 T+1 下，当天新买普通 A 股不能自由当日反向卖出。

因此如果仓位已经在 8 月 5 日形成：

```text
当日：无法用同日卖出修正
下一可执行交易日：
- 禁止因下跌补仓
- 先检查仓位是否突破风险/资本 Cap
- 重新定义事前失效位
- 只有正向确认才允许增加风险
```

如果 50% 确实以当前系统的同一短中期 NAV 为分母，则当前风险规则会优先要求降低风险，而不是等待市场先证明会跌。

## 11. 对抗审查结果

```text
Look-ahead errors in frozen file: 0
2026-08-05 financing PIT leak: corrected
Uncalibrated path probabilities: removed
Score-as-probability error: rejected
65–74 immediate-entry interpretation: corrected to WATCH
Support/resistance deterministic prediction: rejected
3–5d universal optimum claim: rejected
Risk-based sizing principle: retained
Exact risk percentages / 50-50 tranche: remain governance parameters
```

## 12. 理论依据

详细见：

`../../../research/short-mid-blind-replay-theoretical-audit-v1.md`

核心依据包括：

- Jegadeesh & Titman — 中期 momentum；
- Jegadeesh & Titman 1995 / 中国周频研究 — 短周期 reversal 对抗证据；
- Lo / Mamaysky / Wang — 技术形态具有条件信息但不是必然预测；
- Lee & Swaminathan — 成交量与 momentum / reversal 的条件关系；
- George & Hwang、Grinblatt & Han、Odean — 前高/参考价/处置效应相关理论；
- Kaminski & Lo — stop-loss 的效果依赖价格过程，不能宣称普遍提高收益；
- Markowitz / Kelly — 集中风险与 sizing 的理论方向；
- 中国技术规则 2019 与 2024 文献 — 结果存在分歧，必须控制 data snooping、成本和 out-of-sample。

## 13. Freeze rule

从本次 commit 起：

> **本文件禁止根据 8 月 6 日以后真实结果回写。**

真实路径的评价必须新建：

```text
2026-08-05-600699-blind-replay-reveal-YYYY-MM-DD.md
```

这样才能把“事前推理”和“事后结果”分开。
