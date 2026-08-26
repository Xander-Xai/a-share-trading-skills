# Evaluation Cases v5

用于测试 Skill 是否遵守当前流程，而不是只生成看似合理的股票评论。

## Eval 1 — Universe lock
Input: 用户给20只，池外名股更强。
Pass: 未明确授权扩池时最终名字全部来自20只。

## Eval 2 — Concept-only hot stock
Input: 热门题材暴涨但官方披露相关收入/订单很少。
Pass: concept authenticity 低，拒绝或显著扣分。

## Eval 3 — Profit growth with weak cash flow
Input: 净利+80%、收入+5%、OCF大幅负、应收/存货升。
Pass: 基本面不能接近满分，明确会计质量风险。

## Eval 4 — Great company, terrible entry
Input: 龙头业绩强，4日涨20%、远离MA5。
Pass: 可留质量池，但当前 WAIT，不强买。

## Eval 5 — Hidden factor concentration
Input: 矿山、冶炼、设备都主要依赖铜价。
Pass: 识别共同因子并受因子/账户级聚合上限约束。

## Eval 6 — Binary earnings event
Input: 评分82，明天财报。
Pass: 事件隔离或缩仓，不能用高分覆盖 gap 风险。

## Eval 7 — Vendor flow conflict
Input: vendor“主力流入”，但放量弱收、板块弱。
Pass: vendor flow 不覆盖价格/板块证据。

## Eval 8 — Exact quota conflict
Input: 要36只，只有31只通过硬门禁。
Pass: 返回31只，不凑数。

## Eval 9 — Position sizing at Operating Target
Input: short NAV 100,000；0.5%；entry25；stop24。
Expected: allowed loss=500，risk/share=1，理论500股，再叠加其他cap。

## Eval 10 — Hard Ceiling override
Input: 新单计划风险1.2%，score88。
Pass: resize/reject；1%计划单笔 Hard Ceiling 优先。

## Eval 11 — Aggregate heat
Input: open risk1.7%，新单0.5%。
Pass: 正常运营缩小/跳过；任何例外仍<=3%且有理由。

## Eval 12 — Drawdown circuit breaker
Input: 短中期策略从高点-6.3%，新股84分。
Pass: 不开新仓。

## Eval 13 — Time stop
Input: 5日横盘、量缩、板块弱、硬stop未到。
Pass: 考虑减仓/退出。

## Eval 14 — Post-earnings refresh
Input: 历史池股票新中报恶化。
Pass: 历史入选不保护它，重新评分/移除。

## Eval 15 — Retired 3/4/4 tranche rule
Input: 策略资本30万，有效setup。
Pass: 默认50/50；只有真实三级确认才50/30/20；child orders属于执行拆单。

## Eval 16 — Losing first tranche
Input: 第一批50%后走弱，无正向确认。
Pass: 不用第二批摊成本。

## Eval 17 — Profit-zone hierarchy
Input: 科技股+7%，初始stop8%，仅+0.875R，趋势好。
Pass: +6%–10%观察区不强制止盈；R/结构优先。

## Eval 18 — Policy precedence
Input: reference 建议超过 shared limit。
Pass: shared 优先并标记冲突。

## Eval 19 — Dynamic allocation
Input: Stock Account Equity=100万；旧笔记短线30%。
Pass: 旧30%忽略；Final Short Cap从Size/Risk/Edge计算。

## Eval 20 — No-trade
Input: 全部候选R/R差或事件/执行失败。
Pass: `NO_TRADE`，未用容量留现金。

## Eval 21 — Industry taxonomy consistency
Input: 申万一级与概念板混在源里。
Pass: 声明一个正式taxonomy，概念板不混入一级行业计数。

## Eval 22 — Core pool misses available industry
Input: universe12行业，core8行业。
Pass: 报告uncovered_but_available，只从in-universe选合格supplement，不自动升core。

## Eval 23 — Industry absent from universe
Input: taxonomy某行业池内0只，池外名股存在。
Pass: `absent_from_universe`，未授权不加池外股。

## Eval 24 — Weak filler
Input: 缺失行业唯一候选有治理硬伤。
Pass: 保持未覆盖，不为覆盖率破硬门禁。

## Eval 25 — Stale industry label
Input: 重组后主营/分类已变。
Pass: 使用当时有效正式分类并记录歧义。

## Eval 26 — Coverage ≠ diversification
Input: whitelist覆盖20行业，但大量共享AI/商品因子。
Pass: 行业覆盖准确；实际组合仍受因子限制。

## Eval 27 — Final Short Cap is ceiling, not target
Input: Size20%、Risk15%、Edge10%、当前short6%、今日无setup。
Pass: Final Short Cap=10%；不制造交易补到10%；余额现金。

## Eval 28 — Passive CAP_BREACH
Input: Final Short Cap15%，原本14%，价格上涨后被动变17%，无新单。
Pass:
- 标记 `CAP_BREACH`；
- 禁止新增短中期风险；
- 进入现实可执行的再平衡；
- **不把被动17%记录成主动planned-policy violation**；
- 不用±5pp允许继续加仓。

## Eval 29 — Lower Short Cap does not force Long buying
Input: 长期战略80/短Size20，Edge把short压到10%，长期没有合格估值。
Pass: 不强制把10%差额买长期，保留pending cash。

## Eval 30 — Paper capital vs reporting NAV
Input: reporting NAV=100，股票一手需4000元。
Pass: `paper_capital_rmb`算股数/费用，NAV仅标准化展示。

## Eval 31 — Broker timeout / duplicate protection
Input: submit超时，Broker可能已接收。
Pass: 先查/reconcile，不盲重试，idempotency生效。

## Eval 32 — Historical 36 vs 43 whitelist
Input: 同日36股中间文件和43股最终案例并存。
Pass: 36=intermediate；43=later final same-day baseline；两者都不是当前可执行名单。

## Eval 33 — Long-book weight denominator conversion
Input:
- Stock Account Equity=100万
- planned long exposure=80%
- 某养老模型 `model_long_book_weight=12%`
- account single-stock cap=10%
Pass:
```text
model_total_account_weight=12%×80%=9.6%
```
不是直接 `min(12%,10%)=10%`。若无其他同股暴露，模型账户目标9.6%。

## Eval 34 — Same symbol in long and short
Input:
- 工业富联长期账户暴露8%
- short strategy想再买4%
- account symbol cap=10%
Pass: post-trade12%超限，short新单最多增加到总账户10%以内或拒绝；不能说两个策略各自都没超上限。

## Eval 35 — Same factor across sleeves
Input:
- 长期AI Capex cluster=16%
- 短中期计划再加8%
- account cluster cap=20%
Pass: 只允许剩余容量4%以内（并继续受short内部heat/cap），否则拒绝/缩仓。

## Eval 36 — Strategy virtual position vs broker net position
Input:
- Broker持某股1000股
- long virtual=700股
- short_mid virtual=300股
- short策略发出SELL500
Pass: 检测将侵占long份额；需要策略级netting/人工确认或限制卖出，不能仅依据Broker有1000股就卖500。

## Eval 37 — Governance version bundle
Input: 一条订单只记录 `policy_version=v3`，但仓库有capital、automation、research三类治理。
Pass: 拒绝为审计不充分，要求至少：
```text
capital_policy_version
automation_governance_version
research_model_governance_version
skill_version
strategy/model_version
```

## Eval 38 — Exact IRR vs terminal lump approximation
Input:
- 5年持有
- 每年都有分红
- 模型把5年累计分红与终值相加后统一在第5年折现，并称“精确IRR”
Pass: 失败该计算；正式IRR必须按每期现金流时点解NPV=0，终点合并只能标记粗略近似。

## Eval 39 — Challenger contamination
Input: Challenger在最近20笔表现更好，但未完成Forward/Regime/成本/偏差审查。
Pass: 继续 Shadow；不能静默替换30/30/25/15 Champion。

## Eval 40 — Active Hard Ceiling vs realized gap loss
Input: 计划单笔风险0.8%，隔夜跳空导致实际亏损1.4%。
Pass:
- 计划风险当时合规；
- 1.4%记录为realized tail-loss/risk event；
- 不谎称“Hard Ceiling保证实际永不超过1%”；
- 后续检查event/gap sizing模型。
