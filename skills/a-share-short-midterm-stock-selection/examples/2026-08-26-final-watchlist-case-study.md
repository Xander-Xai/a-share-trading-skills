# 2026-08-26 Final Short/Mid-term Watchlist Case Study

> Status: historical forward-validation example
>
> Analysis timestamp: **2026-08-26 21:11 China Standard Time (UTC+8)**
>
> This document freezes the research state at the decision timestamp. It must **not** be rewritten later using future earnings or future price action. Future observations should be appended as dated follow-up records.

## 1. Why this example exists

This case is the first full end-to-end example for the short/mid-term skill:

```text
357-stock user-supplied universe
→ Universe Lock
→ deduplication
→ leader / concept-authenticity / fundamental filtering
→ industry-coverage audit
→ factor-concentration review
→ current-market validation
→ 43-stock final research whitelist
→ forward paper/live validation
```

The goal is not to prove that the 43 names will rise. The goal is to verify whether the **process** has positive expectancy when executed prospectively.

## 2. Universe integrity

- Original unique user-supplied universe: **357 A-share stocks**.
- Final watchlist: **43 unique stocks**.
- Outside-universe additions: **0**.
- Duplicate codes in final watchlist: **0**.
- The screenshot close is a **baseline observation**, not an assumed entry price.

Machine-readable baseline:

- `2026-08-26-final-watchlist.json`

## 3. Market regime at the freeze point

2026-08-26 market close:

- Shanghai Composite: **3912.52, +0.59%**
- Shenzhen Component: **13841.33, +0.69%**
- ChiNext: **3414.88, +0.51%**
- broad-market turnover: roughly **RMB 1.82 trillion**, lower than the previous session
- non-bank financials and non-ferrous metals were among the strongest Level-1 industries
- industrial metals were especially strong; Jiangxi Copper closed limit-up

Interpretation for this skill:

> **Neutral to mild Risk-On, but with fast rotation and non-expanding turnover.**

This is not a blanket “buy breakouts” environment. Late-stage chasing and same-factor concentration require additional penalties.

Market sources:

- https://finance.eastmoney.com/a/202608263854700034.html
- https://finance.eastmoney.com/a/202608263854638630.html
- https://fund.eastmoney.com/a/202608263854495011.html

## 4. Current structure of the 43-stock whitelist

### A. Priority scan

These names had the best combination of business quality, current fundamental evidence and research priority at the freeze point. They still require a valid setup before any trade.

| Code | Name | Close | Day | Why still priority |
|---|---|---:|---:|---|
| 601179 | 中国西电 | 12.98 | +1.25% | 输变电装备核心标的；真实电网资本开支逻辑。 |
| 600875 | 东方电气 | 25.76 | +0.63% | 发电设备龙头；设备订单和产业地位真实。 |
| 601600 | 中国铝业 | 9.59 | +2.35% | 铝产业链龙头；资源周期核心赛马候选。 |
| 601899 | 紫金矿业 | 34.47 | +2.35% | 全球金铜矿业龙头；盈利和商品因子同时验证。 |
| 603296 | 华勤技术 | 77.19 | +2.92% | 智能硬件 ODM 头部；增长真实但仍审查扣非与负债。 |
| 601138 | 工业富联 | 60.57 | +0.70% | AI服务器/云基础设施业绩已进入收入、利润、扣非和现金流。 |
| 600176 | 中国巨石 | 39.50 | -0.73% | 营收、净利、扣非、OCF同步改善，财务质量较完整。 |
| 600160 | 巨化股份 | 38.15 | +0.61% | 制冷剂/氟化工龙头；产业壁垒和利润兑现。 |
| 002736 | 国信证券 | 10.18 | +3.04% | 头部券商代表；当日板块共振，但避免高潮追涨。 |
| 600236 | 桂冠电力 | 9.84 | -0.51% | H1收入、利润、扣非和OCF同步增长，水电基本面完整。 |

Representative current fundamental validation:

- Industrial Fulian 2026 H1: revenue RMB 557.861bn (+54.63%), attributable profit RMB 23.740bn (+95.99%), adjusted profit +96.99%, OCF +425.32%.
  - https://finance.eastmoney.com/a/202608113838132181.html
- China Jushi 2026 H1: revenue +22.50%, attributable profit +73.87%, adjusted profit +70.93%, OCF +68.23%.
  - https://finance.eastmoney.com/a/202608203847783893.html
- Guiguan Power 2026 H1: revenue +37.59%, attributable profit +48.09%, adjusted profit +49.70%, OCF +30.81%.
  - https://finance.eastmoney.com/a/202607303827039920.html

### B. Wait for technical / capital confirmation

These names remain qualified research candidates, but the current decision is **not an entry**.

| Code | Name | Close | Day | Main reason to wait |
|---|---|---:|---:|---|
| 600392 | 盛和资源 | 22.47 | +0.67% | 稀土因子有效，但资源组拥挤。 |
| 601958 | 金钼股份 | 23.05 | +4.44% | 行业地位强；当日涨幅后需检查延伸度。 |
| 000960 | 锡业股份 | 35.57 | +1.92% | 资源龙头；需与其他商品股内部赛马。 |
| 603236 | 移远通信 | 54.74 | -3.37% | 业务增长真实，但现金流与趋势需要同时修复。 |
| 600487 | 亨通光电 | 64.83 | +0.36% | 光通信/海缆龙头；等待结构确认。 |
| 600522 | 中天科技 | 33.41 | -1.42% | 通信、电力、海洋装备支撑；等待相对强度。 |
| 600584 | 长电科技 | 73.62 | -0.58% | 封测龙头；业绩兑现后等待价格确认。 |
| 002430 | 杭氧股份 | 24.13 | +3.92% | 空分/工业气体龙头；避免追涨。 |
| 002080 | 中材科技 | 49.94 | +1.92% | 多细分龙头，但现金流历史波动需扣分。 |
| 603806 | 福斯特 | 15.08 | -1.89% | 利润修复强于收入，继续确认景气持续性。 |
| 002979 | 雷赛智能 | 55.29 | -0.20% | 真实运动控制业务，不能靠“机器人”标签加分。 |
| 002602 | 世纪华通 | 13.95 | -0.78% | 游戏主营兑现，等待趋势与资金。 |
| 000100 | TCL科技 | 4.91 | 0.00% | 面板周期；与京东方视为同因子。 |
| 000725 | 京东方A | 5.72 | -0.35% | 显示龙头；与TCL科技不宜同时重仓。 |
| 600741 | 华域汽车 | 15.42 | +0.39% | 汽车零部件综合龙头；偏质量型候选。 |
| 600415 | 小商品城 | 12.31 | +1.15% | 平台稀缺，但仍需检查现金流和拥挤。 |
| 000858 | 五粮液 | 71.90 | +0.53% | 高端白酒龙头；偏消费/防守因子。 |
| 002273 | 水晶光电 | 26.04 | +2.64% | 光学元件头部；确认突破质量再交易。 |
| 600196 | 复星医药 | 22.86 | -0.70% | 综合医药平台；重点看扣非和现金流。 |
| 600096 | 云天化 | 30.23 | +1.51% | 磷化工/化肥周期逻辑；不是高成长逻辑。 |

### C. Event isolation

These stocks remain in the research whitelist, but the system must not turn pre-event expectations into reported facts.

| Code | Name | Close | Day | Event handling |
|---|---|---:|---:|---|
| 002050 | 三花智控 | 36.14 | +0.53% | 报告/重大事件窗口后重新承保。 |
| 600690 | 海尔智家 | 21.15 | -0.38% | 等待报告落地后刷新基本面和事件分。 |
| 000977 | 浪潮信息 | 73.79 | -0.43% | H1业绩预告很强，但正式中报临近，高预期下禁止提前当成确定性利好。 |
| 002831 | 裕同科技 | 26.71 | +6.29% | 事件窗口叠加当日大涨，等待重新定价。 |

Inspur Information had forecast H1 attributable profit of roughly RMB 2.6–3.1bn, up 226%–288%, but the final report had not yet been published at the freeze timestamp. Therefore the correct state is **event isolation**, not “fundamental score confirmed.”

- https://finance.eastmoney.com/a/202607083797162975.html
- https://emweb.securities.eastmoney.com/PC_HSF10/CompanyBigNews/Index?code=SZ000977&color=w&type=web

### D. Downgrade / risk watch

These stocks are not necessarily bad companies. They are retained because they may become valid later, but current information or entry quality requires a lower priority.

| Code | Name | Close | Day | Main risk / reason for downgrade |
|---|---|---:|---:|---|
| 600362 | 江西铜业 | 48.57 | +10.01% | 公司质量强，但涨停后追高惩罚显著。 |
| 002475 | 立讯精密 | 57.11 | +4.10% | H1营收+40.16%，但扣非仅+6.47%，OCF为-24.46亿元。 |
| 000651 | 格力电器 | 41.58 | -0.10% | 晚间新中报：H1营收-8.15%，归母-7.87%，必须降级重评。 |
| 000967 | 盈峰环境 | 8.41 | +2.94% | 行业地位强，但现金流质量是硬监控项。 |
| 601808 | 中海油服 | 12.34 | -0.72% | 海上油服龙头，但当前增长弹性与行业相对强度一般。 |
| 002414 | 高德红外 | 12.83 | -2.88% | 真实军工交付，但高增含低基数/恢复性因素且波动高。 |
| 603162 | 海通发展 | 11.94 | -0.17% | 航运高弹性、高周期；盈利不可线性外推。 |
| 002041 | 登海种业 | 10.78 | -3.84% | 种业细分龙头，但短期相对强度偏弱。 |
| 600549 | 厦门钨业 | 52.62 | +0.44% | 钨龙头，但现金流风险与资源因子拥挤降低当前优先级。 |

Current validation examples:

- Luxshare Precision H1 revenue +40.16%, attributable profit +18.04%, adjusted profit +6.47%, OCF -RMB 2.446bn.
  - https://finance.eastmoney.com/a/202608243851540162.html
- Gree Electric H1 revenue RMB 89.398bn (-8.15%), attributable profit RMB 13.278bn (-7.87%). This report was published after market close on 2026-08-26, so it is valid for the 21:11 freeze point but not for an earlier intraday decision.
  - https://www.nbd.com.cn/articles/2026-08-26/4559084.html

## 5. Factor-concentration attack

The biggest structural risk in the 43-stock whitelist is **not poor company quality**. It is factor concentration.

### Resource / commodity cluster

- 盛和资源
- 金钼股份
- 锡业股份
- 中国铝业
- 江西铜业
- 紫金矿业
- 厦门钨业

Seven stocks do not equal seven independent bets. They share sensitivity to commodity prices, dollar/liquidity conditions and resource-sector risk appetite.

**Research whitelist:** all may remain.

**Actual portfolio:** normally no more than two positions sharing the dominant commodity factor.

### AI / electronics / communications capex cluster

A second concentration exists across:

- 工业富联
- 浪潮信息
- 华勤技术
- 长电科技
- 立讯精密
- 亨通光电
- 中天科技
- 移远通信
- 水晶光电

The formal industries differ, but several positions can still lose together if AI/datacenter/electronics capex expectations reverse.

## 6. Industry coverage interpretation

This 43-stock set is a **quality-first whitelist**, not a forced full-industry portfolio.

The prior industry-coverage audit showed that the 357-stock locked universe covered more Level-1 industries than this final 43-stock set. Missing categories are allowed when the best in-universe representative does not deserve a place in the higher-quality whitelist.

Therefore:

```text
industry coverage = research completeness diagnostic
not
industry coverage = score bonus / mandatory holding
```

## 7. Forward-validation protocol

The baseline close must never be silently converted into a paper entry.

For every future trade:

1. run a fresh score at decision time;
2. record the exact trigger;
3. define invalidation before entry;
4. calculate risk-based position size;
5. record paper or live fill separately;
6. obey T+1, price limits, slippage and gap risk;
7. record exit reason and actual fill;
8. calculate realized R, MFE, MAE and rule adherence;
9. preserve the original thesis and source timestamps;
10. never rewrite an old decision using later information.

Recommended forward record sequence:

```text
2026-08-26 baseline snapshot
→ daily score snapshots
→ paper-trade intent
→ simulated fill
→ holding-state updates
→ simulated exit
→ post-trade review
→ manual-live trade, if promotion gate passes
```

## 8. What would falsify this selection process?

The example should be considered evidence **against** the current process if forward results show persistent patterns such as:

- leader/fundamental filters do not improve expectancy;
- high-scoring names systematically underperform lower-scoring names;
- chase penalties do not reduce adverse excursion;
- event isolation has no value or systematically misses superior Reward/Risk;
- factor limits reduce returns without improving drawdown or tail risk;
- paper results disappear in live execution after fees/slippage;
- most profits come from a few outliers while median trade expectancy is weak;
- results depend on discretionary overrides that cannot be reproduced.

Do not change the rules after a handful of trades. Accumulate enough forward samples first.

## 9. Baseline conclusion

At the freeze point, the 43-stock set is suitable as a **formal short/mid-term research whitelist**.

It is **not** suitable as a 43-position portfolio.

The execution funnel remains:

```text
43-stock whitelist
→ daily refresh and score
→ ~8–10 watch names
→ 3–5 executable candidates
→ 0–3 actual new entries
```

No trade is a valid output when all setups fail entry, event, factor or risk gates.
