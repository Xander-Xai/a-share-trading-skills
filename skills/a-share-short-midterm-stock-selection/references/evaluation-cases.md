# Evaluation Cases v3

Use these cases to test whether the skill follows the intended process rather than merely producing plausible stock commentary.

## Eval 1 — Universe lock

Input: user supplies 20 A-share stocks and asks for the best 5; an outside famous stock looks stronger.

Pass: final names all come from the supplied 20 and the answer states the universe is locked.

## Eval 2 — Concept-only hot stock

Input: one stock surges on a robot/AI/new-energy theme but official disclosure shows negligible related revenue and no material orders.

Pass: concept authenticity is low and the stock is rejected or materially penalized.

## Eval 3 — Profit growth with weak cash flow

Input: net profit +80%, revenue +5%, OCF turns sharply negative, receivables/inventory rise.

Pass: fundamental score is not near maximum and accounting-quality risk is explained.

## Eval 4 — Great company, terrible entry

Input: industry leader with strong earnings, but price rose 20% in four sessions and is far above MA5.

Pass: quality pool may retain the company but status is `wait for pullback` or equivalent.

## Eval 5 — Hidden factor concentration

Input: copper miner, smelter and copper equipment supplier all rank highly.

Pass: shared copper factor is recognized and actual portfolio respects factor limits.

## Eval 6 — Binary earnings event

Input: stock scores 82 but reports earnings tomorrow.

Pass: event is isolated or size reduced unless gap risk is explicitly accepted.

## Eval 7 — Vendor flow conflict

Input: vendor shows large “main force inflow”, but price closes weak on high volume and sector underperforms.

Pass: vendor flow does not override price/sector evidence.

## Eval 8 — Exact quota conflict

Input: user demands 36 stocks but only 31 pass hard gates.

Pass: return 31 and explain why the quota is not forced.

## Eval 9 — Position sizing at Operating Target

Input:

- strategy NAV RMB 100,000
- operating target risk 0.5%
- entry RMB 25
- invalidation RMB 24

Expected:

```text
allowed loss = 500
risk/share = 1
size before other caps = 500 shares
```

Pass: position is derived from risk, not conviction.

## Eval 10 — Hard Ceiling override

Input:

- a proposed trade would risk 1.2% of strategy NAV
- setup score is 88

Pass: trade is resized or rejected because 1% per-trade hard ceiling overrides the stock score.

## Eval 11 — Aggregate heat

Input:

- existing open initial risk = 1.7%
- new trade at normal 0.5% risk would make 2.2%

Pass: under normal operation, reduce or skip the new trade because 2% is the Operating Target.

If an explicit validated-Edge exception is considered, total heat must still remain <=3% Hard Ceiling and the reason must be documented.

## Eval 12 — Portfolio drawdown circuit breaker

Input: strategy is down 6.3% from high-water mark and a new stock scores 84.

Pass: no new position is opened because the 6% circuit breaker overrides stock score.

## Eval 13 — Time stop

Input: position has been open 5 sessions, price is flat, volume fades, sector leadership weakens, hard stop not hit.

Pass: reduction/exit is considered on opportunity-cost and thesis-deterioration grounds.

## Eval 14 — Post-earnings refresh

Input: a historical core-pool stock publishes a new interim report with material deterioration.

Pass: historical snapshot does not protect it from full rescore/removal.

## Eval 15 — Retired 3/4/4 tranche rule

Input:

- strategy capital RMB 300,000
- candidate triggers a valid setup

Pass:

- default strategy entry is still 50/50, not automatically four tranches because account size is above RMB 100,000;
- if a three-stage confirmation design is explicitly justified, 50/30/20 is allowed;
- any further order splitting is labeled execution slicing, not strategy tranches.

## Eval 16 — Losing first tranche

Input:

- first 50% tranche entered
- stock immediately weakens and no positive confirmation appears

Pass:

- second tranche is not used to lower average cost;
- invalidation/time-stop logic is followed.

## Eval 17 — Profit-zone hierarchy

Input:

- technology stock is +7%
- initial stop distance was 8%
- trade is only +0.875R and trend remains constructive

Pass:

- the historical +6%–10% observation zone does not force profit-taking;
- R multiple and structure take priority.

## Eval 18 — Policy precedence

Input:

- a lower-level reference suggests a position size that exceeds the current shared-policy limit

Pass:

- shared policy overrides the reference;
- answer flags the conflict and uses the stricter rule.

## Eval 19 — Dynamic long/short allocation

Input:

- stock-dedicated capital RMB 1,000,000
- a legacy note says short-term capital can be 30%

Pass:

- the legacy 30% rule is ignored;
- allocation is derived from current `Size Cap / Risk Cap / Edge Cap` in shared policy.

## Eval 20 — No-trade condition

Input: all candidates either have poor Reward/Risk, unresolved event risk or fail execution constraints.

Pass: return `no trade today` rather than forcing activity.

## Eval 21 — Industry taxonomy consistency

Input:

- user asks how many industries exist in a locked universe;
- some data source exposes Shenwan Level 1 industries while another exposes Eastmoney concept/theme boards.

Pass:

- one formal taxonomy is declared and used consistently;
- concept/theme boards are not mixed into the Level-1 industry count;
- classification date/version is stated.

## Eval 22 — Core pool misses an available industry

Input:

- locked universe contains stocks from 12 Shenwan Level-1 industries;
- quality-first core pool covers 8;
- one of the four uncovered industries contains three in-universe candidates.

Pass:

- report universe coverage = 12 and core coverage = 8;
- identify the four `uncovered_but_available` industries;
- compare only the in-universe candidates for each missing industry;
- select at most one default qualified representative per industry;
- label it as a coverage supplement rather than silently upgrading it to core quality.

## Eval 23 — Taxonomy industry absent from user universe

Input:

- current taxonomy contains an industry with zero stocks in the user's locked universe;
- a famous outside-universe leader exists.

Pass:

- classify the industry as `absent_from_universe`;
- do not add the famous outside stock unless the user explicitly authorizes expansion;
- do not claim 100% taxonomy coverage.

## Eval 24 — Weak filler must not be forced

Input:

- an uncovered-but-available industry has only one in-universe stock;
- that stock has unresolved accounting/governance risk and fails a hard gate.

Pass:

- leave the industry uncovered;
- explain that coverage does not override eligibility;
- do not award any score premium for being the only representative.

## Eval 25 — Stale historical industry label

Input:

- a company was historically associated with real estate;
- after restructuring/current classification it is now electronics and current filings support the new business mix.

Pass:

- count it under the current declared taxonomy classification;
- do not use the historical label to fill a real-estate gap;
- record the reclassification/ambiguity note when relevant.

## Eval 26 — Coverage does not equal portfolio diversification

Input:

- research whitelist covers 20 formal industries;
- several top-ranked names across different industries share the same commodity or AI-capex factor.

Pass:

- formal industry coverage is reported accurately;
- actual portfolio construction still obeys same-factor limits;
- the answer does not recommend holding one stock from every covered industry.
