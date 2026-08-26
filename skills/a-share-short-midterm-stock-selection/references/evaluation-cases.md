# Evaluation Cases v4

Use these cases to test whether the Skill follows the intended process rather than merely producing plausible stock commentary.

## Eval 1 — Universe lock
Input: user supplies 20 A-share stocks and asks for the best 5; an outside famous stock looks stronger.
Pass: final names all come from the supplied 20 unless expansion is explicitly authorized.

## Eval 2 — Concept-only hot stock
Input: stock surges on a hot theme but official disclosure shows negligible related revenue/orders.
Pass: concept authenticity is low and the stock is rejected or materially penalized.

## Eval 3 — Profit growth with weak cash flow
Input: net profit +80%, revenue +5%, OCF sharply negative, receivables/inventory rise.
Pass: fundamental score is not near maximum and accounting-quality risk is explained.

## Eval 4 — Great company, terrible entry
Input: leader with strong earnings but price rose 20% in four sessions and is far above MA5.
Pass: quality pool may retain it; current status is wait/pullback rather than forced buy.

## Eval 5 — Hidden factor concentration
Input: miner, smelter and equipment supplier all depend primarily on copper.
Pass: shared factor is recognized and actual portfolio respects factor limits.

## Eval 6 — Binary earnings event
Input: stock scores 82 but reports earnings tomorrow.
Pass: event isolated or size reduced unless gap risk is explicitly accepted.

## Eval 7 — Vendor flow conflict
Input: vendor shows “main force inflow”, price closes weak on high volume and sector underperforms.
Pass: vendor flow does not override price/sector evidence.

## Eval 8 — Exact quota conflict
Input: user demands 36 names; only 31 pass hard gates.
Pass: return 31 and explain why quota is not forced.

## Eval 9 — Position sizing at Operating Target
Input: strategy NAV 100,000; risk 0.5%; entry 25; invalidation 24.
Expected: allowed loss 500; risk/share 1; theoretical size 500 shares before other caps.
Pass: size derives from risk, not conviction.

## Eval 10 — Hard Ceiling override
Input: proposed trade risks 1.2% of strategy NAV; score 88.
Pass: resize/reject because 1% per-trade hard ceiling overrides score.

## Eval 11 — Aggregate heat
Input: open initial risk 1.7%; new normal trade adds 0.5%.
Pass: normal operation reduces/skips because 2% is Operating Target; any exception remains <=3% Hard Ceiling and is documented.

## Eval 12 — Drawdown circuit breaker
Input: strategy down 6.3% from high-water mark; new stock scores 84.
Pass: no new position because 6% circuit breaker overrides stock score.

## Eval 13 — Time stop
Input: open 5 sessions, flat price, fading volume, weakening sector, hard stop not hit.
Pass: reduction/exit considered.

## Eval 14 — Post-earnings refresh
Input: historical pool stock publishes materially worse interim report.
Pass: historical inclusion does not protect it from rescore/removal.

## Eval 15 — Retired 3/4/4 tranche rule
Input: strategy capital 300,000; valid setup.
Pass: default is still 50/50; 50/30/20 only with genuine three-stage confirmation; child orders are execution slicing.

## Eval 16 — Losing first tranche
Input: first 50% entered, stock weakens, no positive confirmation.
Pass: second tranche is not used to lower average cost; stop/time-stop logic applies.

## Eval 17 — Profit-zone hierarchy
Input: tech stock +7%, initial stop distance 8%, only +0.875R, trend constructive.
Pass: +6%–10% observation zone does not force profit-taking; R/structure wins.

## Eval 18 — Policy precedence
Input: lower-level reference suggests position exceeding shared policy.
Pass: shared policy overrides and conflict is flagged.

## Eval 19 — Dynamic long/short allocation
Input: stock-dedicated capital 1,000,000; legacy note says short capital can be 30%.
Pass: legacy 30% ignored; `Final Short Cap = min(Size, Risk, Edge)`.

## Eval 20 — No-trade condition
Input: all candidates have poor R/R, unresolved event risk or execution failure.
Pass: return `no trade today` and keep unused capacity as cash.

## Eval 21 — Industry taxonomy consistency
Input: Shenwan Level-1 and concept/theme boards appear in different sources.
Pass: one formal taxonomy is declared; concept boards are not mixed into Level-1 count.

## Eval 22 — Core pool misses available industry
Input: locked universe covers 12 industries, core pool 8, four uncovered have in-universe names.
Pass: report both counts, identify `uncovered_but_available`, choose at most one qualified supplement per industry, do not silently promote to core quality.

## Eval 23 — Industry absent from universe
Input: taxonomy industry has zero in-universe stocks; famous outside leader exists.
Pass: mark `absent_from_universe`; no outside addition without explicit authorization.

## Eval 24 — Weak filler
Input: uncovered industry has one in-universe stock with unresolved governance/accounting hard veto.
Pass: leave uncovered; coverage never overrides eligibility.

## Eval 25 — Stale industry label
Input: company changed business/classification after restructuring.
Pass: use current declared taxonomy and record ambiguity/reclassification note.

## Eval 26 — Coverage ≠ diversification
Input: whitelist spans 20 industries but several names share AI-capex/commodity factor.
Pass: coverage reported accurately; actual portfolio still obeys factor limits.

## Eval 27 — Final Short Cap is a ceiling, not a target
Input:
- Size Cap 20%
- Risk Cap 15%
- Edge Cap 10%
- current short exposure 6%
- no valid setups today
Pass:
- `Final Short Cap = 10%`;
- no trade is created to reach 10%;
- remaining capacity stays cash.

## Eval 28 — Drift band cannot break a Cap
Input:
- Final Short Cap = 15%
- short exposure rises to 17% because positions appreciate
- a legacy note says ±5pp drift is acceptable
Pass:
- the ±5pp note cannot authorize 17%;
- exposure enters rebalance/profit-transfer review because Cap has priority.

## Eval 29 — Lower Short Cap does not force Long buying
Input:
- strategic table shows 80% long / 20% short
- Edge Cap reduces Final Short Cap to 10%
- no long-term candidate currently passes valuation Gate
Pass:
- do not force the other 10% into long stocks;
- retain it as pending cash until a qualified opportunity exists.

## Eval 30 — Paper capital vs standardized NAV
Input:
- reporting NAV starts at 100.00
- Paper model must buy an A-share whose board lot costs RMB 4,000
Pass:
- use `paper_capital_rmb` for shares/lot/fees/risk;
- use `reporting_nav` only for normalized performance;
- never treat 100 NAV points as RMB100 execution capital.

## Eval 31 — Broker timeout / duplicate-order protection
Input:
- order submission times out after broker may have accepted it
Pass:
- query/reconcile broker state first;
- do not blindly retry;
- duplicate order protection/idempotency remains active.

## Eval 32 — Historical 36 vs 43 whitelist
Input:
- intermediate 36-stock file and later 43-stock same-day case both exist
Pass:
- identify 36 as intermediate historical snapshot;
- identify 43 as later/final same-day forward-validation baseline;
- neither is treated as a current executable whitelist.
