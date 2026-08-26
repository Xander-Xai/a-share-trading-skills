# Evaluation Cases

Use these cases to test whether the skill is following the intended process rather than merely producing plausible stock commentary.

## Eval 1 — Universe lock

Input:

- User supplies 20 A-share stocks and asks for the best 5.
- A famous outside stock looks much stronger.

Pass criteria:

- Final 5 all come from the supplied 20.
- Outside stock is not inserted.
- Answer states universe is locked.

Fail criteria:

- Any outside ticker appears as a selected name.

## Eval 2 — Concept-only hot stock

Input:

- One stock is up sharply on a robot/AI/new-energy theme.
- Official disclosure shows negligible related revenue and no material orders.

Pass criteria:

- Concept authenticity score is low.
- Theme does not create leader status.
- Stock is rejected or materially penalized despite price strength.

## Eval 3 — Profit growth with weak cash flow

Input:

- Net profit +80%.
- Revenue +5%.
- Operating cash flow turns sharply negative.
- Receivables/inventory rise materially.

Pass criteria:

- Fundamental score is not near maximum.
- Accounting-quality risk is explained.
- Stock may remain on watchlist but is not treated as unquestioned quality.

## Eval 4 — Great company, terrible entry

Input:

- Industry leader with strong earnings.
- Stock has risen 20% in four sessions and is far above MA5.

Pass criteria:

- Company may remain in quality pool.
- Current status is `wait for pullback` or equivalent.
- Chase/extension penalty is applied.

## Eval 5 — Same factor hidden by different industries

Input:

- Copper miner, copper smelter, and copper equipment supplier all rank highly.

Pass criteria:

- Factor correlation is recognized.
- Actual portfolio does not hold more than two if copper is the dominant shared driver.

## Eval 6 — Binary earnings event

Input:

- Stock scores 82 but reports earnings tomorrow.

Pass criteria:

- Event is explicitly identified.
- Stock is isolated or position size reduced unless user explicitly accepts gap risk.
- Unknown earnings are not written as known facts.

## Eval 7 — Vendor capital-flow conflict

Input:

- Vendor says large “main force inflow”.
- Price closes weak on high volume and sector underperforms.

Pass criteria:

- Capital score is reduced.
- Vendor flow is not used as a standalone bullish signal.

## Eval 8 — Exact quota conflict

Input:

- User demands 36 stocks.
- Only 31 pass hard gates.

Pass criteria:

- Return 31 qualified names and explain why the quota is not forced.

Fail criteria:

- Add five weak names simply to reach 36.

## Eval 9 — Position sizing

Input:

- Strategy capital RMB 100,000.
- Max trade risk 0.5%.
- Entry RMB 25, invalidation RMB 24.

Expected reasoning:

- max loss RMB 500
- loss per share RMB 1
- theoretical size 500 shares before other capital limits

Pass criteria:

- position is derived from risk, not arbitrary conviction percentage.

## Eval 10 — Portfolio drawdown circuit breaker

Input:

- strategy is down 6.3% from high-water mark
- a new stock scores 84

Pass criteria:

- no new position is opened because the 6% circuit breaker overrides stock score.

## Eval 11 — Time stop

Input:

- position has been open 5 sessions
- price is flat, volume fades, sector leadership weakens
- hard stop not hit

Pass criteria:

- reduction/exit is considered on opportunity-cost and thesis-deterioration grounds.

## Eval 12 — Post-earnings refresh

Input:

- a historical core-pool stock publishes a new interim report with material deterioration

Pass criteria:

- historical inclusion is not treated as permanent.
- stock is fully rescored and can be removed.
