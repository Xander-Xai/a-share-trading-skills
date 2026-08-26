# Adversarial Review Checklist

Use this after ranking and before finalizing any shortlist or holding decision.

The purpose is to actively search for reasons the answer may be wrong, rather than merely finding supporting evidence.

## A. Universe integrity attack

Ask:

- Did any selected stock come from outside the locked user universe?
- Was a ticker silently replaced by a similarly named company?
- Were duplicate codes counted twice under different names?
- Was a convertible bond, ETF, fund, or other non-stock instrument accidentally treated as a stock?

Failure response:

- remove the invalid name
- replace only from the locked universe
- rerun ranking and portfolio checks

## B. Point-in-time attack

Ask:

- Was any fact published after the stated `as of` timestamp?
- Was a later earnings report used to validate an earlier decision?
- Was later price action used as evidence that an entry setup was good?
- Was a consensus forecast silently converted into a reported result?

Any look-ahead leakage invalidates the affected score and requires rerun.

## C. Industry-taxonomy attack

When industry coverage is part of the task, ask:

- Was one formal taxonomy used consistently for every stock?
- Was the taxonomy version/current classification checked at the analysis timestamp?
- Were theme/concept boards mixed into Level-1 industry counts?
- Was one stock counted in multiple Level-1 industries?
- Did a stale historical classification survive after restructuring or business transformation?
- Does the current company principal business support any disputed mapping?

Failure response:

- remap the affected stocks,
- recompute universe/core coverage,
- rerun the missing-industry analysis.

## D. Industry-coverage attack

Distinguish these explicitly:

- `taxonomy_total`
- industries actually present in the locked universe
- industries represented in the core quality pool
- `uncovered_but_available`
- `absent_from_universe`

Then ask:

- Did any outside-universe stock enter merely to fill an absent industry?
- Was a weak stock promoted solely to make coverage reach 100%?
- Was the best in-universe representative actually compared with its same-industry peers?
- Are coverage supplements clearly labeled as supplements rather than equal-priority core names?
- Was an industry left uncovered when no in-universe candidate passed the normal hard gates?

Coverage is a research diagnostic, not a quota.

## E. “Fake leader” attack

For every company labeled leader, ask:

- What measurable evidence proves leadership?
- Is the claim about the company itself or only the industry/theme?
- Is the ranking current?
- Does the company actually make money from the business being cited?

If leadership relies mainly on promotional/media wording, remove the premium.

## F. Concept-rubbing attack

Assume the hot theme does not exist. Would the company still be selected?

Check:

- material revenue/profit contribution
- real product/order/customer evidence
- official company confirmation
- whether the theme is still pre-commercial

If the only thesis is narrative adjacency, reject it.

## G. Accounting attack

Try to falsify apparent growth.

Check:

- low-base effect
- non-recurring gains
- subsidy/fair-value/asset-sale contribution
- operating cash flow divergence
- receivables growth
- inventory growth
- impairment
- debt/interest burden

A large profit-growth percentage alone is insufficient.

## H. Cyclical-peak attack

For commodity/cyclical stocks ask:

- Is low PE caused by peak earnings?
- Are commodity prices already stretched?
- Are capacity additions likely to reverse margins?
- Is the stock late in the price cycle even if current earnings look excellent?

## I. Technical trap attack

Assume the chart is a bull trap.

Look for:

- breakout without volume
- volume spike without price progress
- repeated upper shadows
- failure near previous high
- late-stage acceleration
- large MA5/MA10 deviation
- sector already entering climax

If reward/risk is poor, status must be `wait` even when the company remains in the quality pool.

## J. A-share execution attack

Assume the planned stop cannot execute exactly where modeled.

Check:

- ordinary-share settlement / inability to freely reverse a new position intraday
- opening gap through stop
- limit-down or illiquidity
- suspension/resumption
- ex-rights/ex-dividend distortion
- abnormal-volatility measures

Ask what happens if the first executable exit is materially worse than the planned invalidation price.

If realistic execution loss breaches the account risk budget, reduce size or reject the trade.

## K. Event-gap attack

Ask what happens if tomorrow opens 5–10% against the position.

Check:

- earnings
- regulatory decision
- major shareholder sale
- lock-up expiry
- restructuring
- litigation
- commodity-policy shock

If a normal stop cannot protect against the event gap, position size or event exposure must be reduced explicitly.

## L. Capital-flow attack

Assume vendor “main force inflow” is wrong or noisy.

Would the thesis still hold using:

- volume
- turnover
- price response
- financing data
- institutional activity
- sector breadth?

If not, capital score is overstated.

## M. Correlation attack

Ignore industry labels and ask what would make several holdings lose money simultaneously.

Examples:

- same commodity price
- same AI capex cycle
- same consumer demand factor
- same market-turnover factor
- same policy theme

If more than two holdings share the dominant factor, rebuild the portfolio.

Industry coverage never overrides factor concentration rules.

## N. Opportunity-cost attack

For each selected name, identify the best excluded in-universe peer.

Ask:

- Is the selected name truly superior on current data?
- Is it only more familiar?
- Is the excluded peer cheaper, stronger, less crowded, or easier to execute?

For a coverage supplement, perform this comparison specifically against other in-universe stocks in the same uncovered industry.

Replace when the alternative clearly dominates.

## O. Holding-inertia attack

For any position held beyond the original 5–15 day horizon ask:

- Was the position explicitly re-underwritten?
- Is there a fresh score, thesis, stop and risk budget?
- Is the trader holding only because the position is underwater?

A short-term trade cannot become medium-term merely to avoid realizing a loss.

## P. No-trade attack

Ask:

- If no current setup has attractive reward/risk, is the system willing to return `no trade today`?
- Is an exact requested shortlist size causing weak names to be promoted?
- Is a desire to stay active overriding market-regime evidence?

The system must never create trades to satisfy an output quota.

## Q. Process-overfitting attack

When changing thresholds after recent trades ask:

- Is the sample large enough?
- Is the change driven by one memorable winner/loss?
- Does the rule improve expectancy across multiple setups/regimes or merely fit recent noise?

Prefer stable rules and explicit experiments over emotional parameter changes.

## R. Source attack

For each material claim ask:

- Is the source official when an official source exists?
- Is the date current and point-in-time valid?
- Is a forecast being presented as reported earnings?
- Are two sources repeating the same original rumor?
- For industry coverage, does the classification come from the declared formal taxonomy rather than a media/theme label?

Unresolved source conflict reduces confidence or blocks execution.

## S. Final pass/fail report

Before final answer report at least:

- outside-universe errors: 0 / corrected
- duplicate errors: 0 / corrected
- code-name mismatches: 0 / corrected
- look-ahead errors: 0 / corrected
- taxonomy-mapping errors: 0 / corrected
- stale-industry-classification errors: 0 / corrected
- taxonomy total industries: count, when relevant
- locked-universe industry count: count, when relevant
- core-pool industry count: count, when relevant
- uncovered-but-available industries: count/list, when relevant
- absent-from-universe industries: count/list, when relevant
- weak coverage fillers rejected: count
- concept-only names removed: count
- accounting-quality failures removed: count
- event-isolated names: count
- execution-risk failures removed: count
- excessive-factor clusters corrected: count
- insufficient-data names: count
- `no trade today` considered: yes/no

The answer is not complete until this review passes.