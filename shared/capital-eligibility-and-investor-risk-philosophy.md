# Capital Eligibility & Investor Risk Philosophy v2

> Status: **ACTIVE LEVEL-0 HARD-VETO GOVERNANCE**.
> Scope: all real-money long and short/mid A-share decisions in this repository.
> This file defines what capital is eligible for stock risk before selection, timing, execution or sizing.
>
> Any executable ENTRY/ADD sizing must additionally pass `pre-trade-order-authorization-contract.md`. Missing critical personal-capital inputs means executable shares = 0.

## 1. Core premise: probability, not guaranteed profit

Stock investing/trading is a risky capital-allocation activity. Risk and opportunity coexist; individual trades, streaks and whole market phases can lose money.

The operating objective is:

```text
survival first
+ process discipline
+ positive expectancy after all costs
+ bounded drawdown
+ repeatability
```

Never treat any of the following as a reason to bypass risk controls:

- “this trade must make money”;
- “I need to win the loss back”;
- “AI / an expert / media says it will rise”;
- “the company is good, so the trade cannot be wrong”;
- “I will just hold longer to avoid realizing a loss”.

Long-term equity ownership may participate in business earnings and economic growth, but short/mid trading remains a competitive, uncertain process after costs. No model in this repository promises profit.

## 2. Capital Eligibility Gate: decide whether the money may take stock risk

Before calculating `Stock Account Equity`, separate personal/household money into:

```text
A. daily living expenses and fixed bills
B. emergency / unexpected-expense reserve
C. known near-term or high-probability cash needs
D. tax, insurance, medical, education, housing and debt-service money
E. remaining risk capital that can tolerate volatility and loss
```

Only `E` can enter the stock system. Cash sitting in a brokerage account is not automatically eligible risk capital.

### 2.1 Cash Need Gate

Before every new ENTRY or material ADD, ask:

```text
Could this money be forced out during the planned holding window
because of living expenses, debt, medical, housing, education, tax
or another known / high-probability cash need?
```

- YES -> `cash_need_gate = FAIL` -> do not increase stock risk with that money.
- NO -> continue.
- UNKNOWN -> no aggressive sizing.

For short/mid trades the normal window is 5–15 trading days. If a position is re-underwritten for 15–60 days, re-check this gate.

### 2.2 Emergency / Basic Needs Gate

Emergency reserves and essential-living cash are outside `Stock Account Equity`.

The repository does not impose one universal number of months for every person. Income stability, household responsibilities, insurance and debt differ. The hard principle is:

```text
an unexpected expense should not require selling stocks in a bad market
```

### 2.3 Debt / Leverage Gate

Default:

```text
borrowed money for stock speculation = BLOCKED
mortgaging core living assets to trade stocks = BLOCKED
using high-cost consumer debt to maintain stock exposure = BLOCKED
margin leverage = DISABLED_BY_DEFAULT
```

Borrowing capacity is not investable capital.

### 2.4 Risk Capacity is not Risk Willingness

```text
risk_willingness = subjective comfort with volatility/loss
risk_capacity    = objective ability to absorb loss without damaging life goals, liabilities or cash flow
```

Use the more conservative side. “I can emotionally tolerate it” does not mean “I can financially afford it.”

### 2.5 Required capital fields

Every real-money pre-trade card must contain:

```yaml
capital_eligibility: PASS | FAIL | UNKNOWN
cash_need_gate: PASS | FAIL | UNKNOWN
emergency_reserve_gate: PASS | FAIL | UNKNOWN
debt_leverage_gate: PASS | FAIL | UNKNOWN
risk_capacity: LOW | MEDIUM | HIGH | UNKNOWN
risk_willingness: LOW | MEDIUM | HIGH | UNKNOWN
```

Any critical FAIL blocks new risk. UNKNOWN cannot be converted into a larger position.

## 3. Position philosophy: capital exposure and loss exposure are different

Do not size a trade only by “how much money to put in.”

Every position must pass both:

```text
capital exposure limits
AND
planned loss / risk budget limits
```

Position size is derived only after the invalidation point is defined:

```text
E = planned entry
S = invalidation
R = allowed currency loss
shares ~= R / abs(E-S)
```

Then apply single-stock, industry/factor, account-level and liquidity caps.

## 4. Diversification and concentration

Diversification does not guarantee a profit, but it reduces dependence on one company, one sector or one economic factor.

Repository rules therefore aggregate:

- the same stock across long and short/mid sleeves;
- correlated industry exposures;
- shared economic-factor / theme clusters;
- total strategy heat.

A list of different ticker symbols is not real diversification if the stocks are driven by the same factor.

## 5. Cost and turnover gate

Expected edge must survive all trading friction:

```text
commission
+ minimum / fixed commission
+ applicable statutory taxes / fees
+ bid-ask spread
+ slippage
+ market impact
```

Do not hard-code one broker fee schedule as universal. Use the account’s actual fee schedule and current rules.

If there is a minimum commission, record:

```text
fixed_cost_drag_pct = fixed_or_minimum_fee / order_notional
```

Small orders and frequent in/out trading may be uneconomic even when the directional call is right. Turnover must be justified by new information or risk control, not boredom or a desire to “do T”.

## 6. External opinion / AI gate

External research, media, social posts, brokerage views, friends, influencers and AI analysis are research inputs only. They are not executable order triggers.

Use these explicit states:

```text
WATCH    = worth researching; do not order
READY    = conditions are close; still no order
ENTRY    = pre-defined trigger occurred; first tranche allowed
HOLD     = thesis and structure remain intact
ADD      = positive confirmation permits more risk
TRIM     = weakening; reduce risk
EXIT     = invalidated; close according to plan
COOLDOWN = prior trade ended; wait for fresh underwriting
```

Never translate “可以买”, “看好”, “站上 MA5/MA10” or an analyst target price directly into ENTRY/ADD.

Before a real order, independently verify trigger, invalidation, size, liquidity/cash gates and whether the action is driven by FOMO, revenge trading or cost anchoring.

## 7. Behavioral risk

Explicitly guard against:

- FOMO / chasing;
- anchoring to purchase cost or breakeven price;
- sunk-cost refusal to exit;
- revenge trading / needing to win losses back;
- outcome bias: assuming a stop was wrong because price later rebounded;
- overtrading;
- confirmation bias.

### Re-entry after an exit

A later rebound does not automatically invalidate the old EXIT. New catalyst or new price structure is a new trade:

```text
EXIT -> COOLDOWN -> fresh underwriting -> READY -> new ENTRY trigger
```

Do not lower new-entry standards merely to recover a previous loss.

## 8. Liquidity and execution reality

A stop is an invalidation plan, not a guaranteed fill price.

Always consider:

- A-share settlement / inability to freely reverse a newly bought ordinary share intraday;
- gap-through-stop risk;
- price limits / suspension;
- event gaps;
- liquidity and slippage;
- whether the position can realistically be reduced when needed.

If real exit risk is materially worse than the nominal stop, reduce size or skip the trade.

## 9. No-trade is a valid position

Unused risk budget is not a problem to solve.

```text
no eligible capital -> NO_TRADE
no qualified setup -> CASH
unclear invalidation -> NO_TRADE
unacceptable reward/risk -> NO_TRADE
unknown critical data -> NO_TRADE / WATCH
```

Being in cash is part of the strategy.

## 10. Evidence baseline

- Shenzhen Stock Exchange investor education — 股市投资应量力而行: financial capacity, risk capacity and knowledge; use idle funds and be cautious about borrowing / mortgaging assets to buy stocks.
  https://investor.szse.cn/institute/products/t20210917_588439.html
- Shanghai Stock Exchange Trading Rules (2026 revision), 3.1.7: participate prudently according to risk knowledge and risk-bearing capacity.
  https://www.sse.com.cn/lawandrules/sselawsrules2025/stocks/exchange/c/c_20260424_10816482.shtml
- Shanghai Stock Exchange Personal Investor Conduct Guidelines: autonomous decision-making, self-bearing of consequences, and assessment based on family situation, income, goals and knowledge.
  https://www.sse.com.cn/aboutus/mediacenter/hotandd/c/c_20150912_3988245.shtml
- Shenzhen Stock Exchange investor education — 从容投资，避免过度交易: excessive trading and transaction costs can damage retail investor results.
  https://investor.szse.cn/institute/products/t20220826_595591.html
- FINRA — Know Your Risk Tolerance: distinguish willingness from ability/capacity and consider routine, emergency and long-term spending needs.
  https://www.finra.org/investors/insights/know-your-risk-tolerance
- Investor.gov — Introduction to Investing / Investor Preparedness Checklist: emergency funds, goals, risk tolerance, fees and diversification are foundational.
  https://www.investor.gov/introduction-investing
  https://www.investor.gov/introduction-investing/general-resources/investor-preparedness-checklist

## 11. Final rule

```text
protect life cash flow first
then decide whether capital is eligible for risk
then select the security
then define invalidation
then size the position
then execute only after a clear trigger

stocks can make money and can lose money
the system manages probability and survival, not certainty
```
