# Core Pool Snapshot — 2026-08-26

> Status: **intermediate historical snapshot**.
>
> This 36-stock pool was produced earlier in the 2026-08-26 research workflow. It is **not** the final same-day forward-validation whitelist.
>
> The later/final 2026-08-26 research artifact contains 43 stocks and is stored at:
>
> - `../examples/2026-08-26-final-watchlist-case-study.md`
> - `../examples/2026-08-26-final-watchlist.json`
>
> Both artifacts are historical Level-4 evidence records. The 43-stock example supersedes this file only as the **later same-day research state**; neither overrides current policy, current market data or a fresh Skill run.

## Scope

This is the 36-stock shortlist produced from the user's five screenshot batches during an intermediate stage on 2026-08-26.

Important:

- The five batches contained 357 raw stock records before any cross-batch deduplication step.
- The 36 names below are unique by stock code.
- Every name below came from the user-supplied screenshot universe.
- This is a historical **research/watchlist snapshot**, not a permanent buy list.
- Do not interpret `36` versus the later `43` as a contradiction: additional industry-coverage and final-market validation steps produced the later 43-stock whitelist.
- For forward validation from the final 2026-08-26 state, use the 43-stock example files above.
- Revalidate after earnings, major announcements, abnormal price moves, or market-regime changes.

## 36-stock intermediate pool

| # | Code | Name | Source batch | Primary role |
|---:|---|---|---:|---|
| 1 | 601899 | 紫金矿业 | 5 | 金铜资源龙头 |
| 2 | 600362 | 江西铜业 | 5 | 铜产业链龙头 |
| 3 | 601600 | 中国铝业 | 5 | 铝产业链龙头 |
| 4 | 000960 | 锡业股份 | 5 | 锡资源龙头 |
| 5 | 601958 | 金钼股份 | 5 | 钼产业龙头 |
| 6 | 600392 | 盛和资源 | 5 | 稀土产业头部 |
| 7 | 601088 | 中国神华 | 1 | 煤电运一体化龙头 |
| 8 | 600875 | 东方电气 | 5 | 发电设备龙头 |
| 9 | 601179 | 中国西电 | 4 | 输变电装备龙头 |
| 10 | 002430 | 杭氧股份 | 3 | 空分设备/工业气体龙头 |
| 11 | 601138 | 工业富联 | 4 | AI服务器/制造平台龙头 |
| 12 | 002475 | 立讯精密 | 5 | 消费电子/汽车电子平台龙头 |
| 13 | 600584 | 长电科技 | 5 | 半导体封测龙头 |
| 14 | 603296 | 华勤技术 | 5 | 智能硬件ODM头部 |
| 15 | 600522 | 中天科技 | 5 | 通信/电力/海洋装备龙头 |
| 16 | 600487 | 亨通光电 | 4 | 光通信/海缆龙头 |
| 17 | 603236 | 移远通信 | 2 | 物联网模组龙头 |
| 18 | 000725 | 京东方A | 5 | 显示面板龙头 |
| 19 | 000100 | TCL科技 | 5 | 半导体显示龙头 |
| 20 | 002602 | 世纪华通 | 3 | 游戏行业头部 |
| 21 | 002050 | 三花智控 | 4 | 热管理/控制部件龙头 |
| 22 | 002979 | 雷赛智能 | 5 | 运动控制细分龙头 |
| 23 | 603806 | 福斯特 | 4 | 光伏封装材料龙头 |
| 24 | 600160 | 巨化股份 | 2 | 制冷剂/氟化工龙头 |
| 25 | 600176 | 中国巨石 | 5 | 玻纤龙头 |
| 26 | 002080 | 中材科技 | 3 | 复合材料多细分龙头 |
| 27 | 600096 | 云天化 | 4 | 磷矿磷肥一体化龙头 |
| 28 | 600196 | 复星医药 | 1 | 综合医药平台头部 |
| 29 | 002273 | 水晶光电 | 3 | 光学元器件头部 |
| 30 | 000858 | 五粮液 | 5 | 高端白酒龙头 |
| 31 | 000651 | 格力电器 | 4 | 空调龙头 |
| 32 | 600415 | 小商品城 | 5 | 义乌商贸平台龙头 |
| 33 | 600690 | 海尔智家 | 5 | 全球家电龙头 |
| 34 | 600741 | 华域汽车 | 3 | 汽车零部件综合龙头 |
| 35 | 002736 | 国信证券 | 4 | 头部券商 |
| 36 | 600549 | 厦门钨业 | 4 | 钨/稀土/电池材料龙头 |

## Portfolio-correlation warning

This list intentionally contains multiple candidates from broad themes so they can compete internally. They are **not** intended to be held together automatically.

Examples:

- 紫金矿业 / 江西铜业 / 中国铝业 / 锡业股份 / 金钼股份 / 盛和资源 / 厦门钨业 share varying degrees of commodity-cycle risk.
- 工业富联 / 立讯精密 / 长电科技 / 华勤技术 / 中天科技 / 亨通光电 / 水晶光电 share varying degrees of technology-capex/electronics-cycle risk.
- 京东方A and TCL科技 should normally compete for the same display-sector slot rather than both being treated as independent diversification.

Apply current shared-policy and Skill same-factor limits before opening positions.

## Revalidation rule

This file must not be used as an executable current shortlist without a fresh run.

Refresh when any of the following occurs:

- new quarterly/interim/annual report;
- earnings forecast or major guidance change;
- material regulatory/governance event;
- major contract/restructuring event;
- large commodity/product-price regime change;
- stock becomes technically extended or breaks its trend;
- broad market regime changes;
- shared policy / Skill version changes.

A stock can remain a good company while being removed from the executable trading list.
