# Research Basis and Design Rationale v2

## Purpose

This file records external evidence used to validate the short/mid-term Skill. It is not a promise that historical relationships will persist and does not override current shared policy.

Policy order:

```text
../../../shared/capital-allocation-and-entry-policy.md
→ ../SKILL.md
→ this reference
```

The evidence supports principles; it does not prove that any exact percentage, score weight or tranche split is uniquely optimal.

## 1. A-share execution constraints are real risk

### SSE / SZSE trading rules

Ordinary A-share execution is not equivalent to a market where a new position can always be reversed immediately. Price limits, gaps, settlement rules, suspension/resumption and abnormal-volatility measures can make a theoretical stop non-executable.

Sources:

- SSE Trading Rules, 2026 revision:
  https://www.sse.com.cn/lawandrules/sselawsrules2025/stocks/exchange/c/c_20260424_10816482.shtml
- SZSE Trading Rules, 2026 revision:
  https://www.szse.cn/lawrules/rule/trade/current/t20260424_620190.html

Design consequence:

- first entries must be survivable;
- stops are invalidation plans, not guaranteed fill prices;
- gap/limit risk must be handled through smaller size, event isolation and first-executable-price logic.

## 2. Material information requires official disclosure

Chinese listed-company disclosure rules make periodic and material-event filings primary evidence.

Source:

- CSRC, Measures for the Administration of Information Disclosure by Listed Companies:
  https://www.csrc.gov.cn/csrc/c106256/c1653948/content.shtml

Design consequence:

- official filings outrank theme articles and stale secondary summaries;
- scheduled-but-unreleased reports are event risk;
- analysis is point-in-time and must not use look-ahead information.

## 3. Risk-based sizing

Fidelity educational material presents position sizing as a function of allowed loss and stop/invalidation distance:

```text
position size = risk per trade / risk per share
```

Sources:

- Fidelity position-sizing / exit-strategy material:
  https://www.fidelity.com/bin-public/060_www_fidelity_com/documents/learning-center/Presentation_Exit%20Strategy.pdf
- Fidelity Wealth-Lab User Guide:
  https://www.fidelity.com/bin-public/060_www_fidelity_com/documents/WLP_User_Guide.pdf

Charles Schwab trade-plan education also emphasizes predefining maximum risk and exit logic:

- https://www.schwab.com/learn/story/5-elements-smart-trade-plan

### Current repository interpretation

The repository distinguishes normal operation from an absolute ceiling:

```text
Operating Target
- per trade: 0.5% of strategy NAV
- aggregate open initial risk: <= 2%
- one industry/factor: <= 1%

Hard Ceiling
- per trade: <= 1%
- aggregate open initial risk: <= 3%
```

The 0.5% operating target is intentionally conservative because this strategy is a satellite beside a long-term wealth account. Moving toward 1% requires validated Edge and favorable conditions; 1% is not the default.

## 4. Entry tranches

External research does not prove that 50/50 is uniquely optimal. The repository uses it as a governance rule because short/mid-term trades have a limited time horizon and should not accumulate many decision tranches.

Current policy:

```text
Default: 50% Setup + 50% Confirmation
Exception: 50% / 30% / 20% when there are three genuine confirmation levels
```

The old rule that account size mechanically determines 3 or 4 strategy tranches is retired.

A large capital order may still be split into multiple child orders for liquidity. This is execution slicing, not additional strategy tranches.

## 5. Earnings quality requires cash-flow and accrual checks

CFA Institute research emphasizes that accounting earnings can be distorted by accruals and that cash-flow evidence is important for persistence and quality analysis.

Sources:

- CFA Institute Research Foundation, Earnings Quality:
  https://rpc.cfainstitute.org/sites/default/files/-/media/documents/book/rf-publication/2004/rf-v2004-n3-3927-pdf.pdf
- CFA Institute, Evaluating Quality of Financial Reports:
  https://www.cfainstitute.org/sites/default/files/-/media/documents/book/curriculum-update/rr-v-2017-n2-1.pdf

Design consequence:

- profit growth alone never earns full quality points;
- adjusted profit, OCF, receivables, inventory, one-offs and balance-sheet changes must be checked;
- sector-specific accounting logic is mandatory.

## 6. Quality is multidimensional

AQR Quality Minus Junk and Fama/French profitability research support treating quality as more than recent growth.

Sources:

- AQR, Quality Minus Junk:
  https://www.aqr.com/Insights/Research/Working-paper/Quality-minus-Junk
- Kenneth French Data Library, Fama/French 5 Factors:
  https://mba.tuck.dartmouth.edu/pages/faculty/ken.french/Data_Library/f-f_5_factors_2x3.html

Design consequence:

- use profitability, resilience, cash conversion and durable industry position;
- do not treat these studies as A-share timing calibrations.

## 7. Momentum exists, but chasing can fail

NBER research documents return/earnings momentum as well as severe momentum reversals/crashes.

Sources:

- Chan, Jegadeesh & Lakonishok, Momentum Strategies:
  https://www.nber.org/papers/w5375
- Chabot, Ghysels & Jagannathan, Momentum Trading, Return Chasing, and Predictable Crashes:
  https://www.nber.org/papers/w20660

Design consequence:

- relative strength and confirmation matter;
- late-stage acceleration, crowding and extension require penalties;
- `no trade today` must remain valid.

## 8. Factor momentum and hidden concentration

Research on factor momentum supports treating apparently different stocks as potentially one economic bet.

Source:

- Ehsani & Linnainmaa, Factor Momentum and the Momentum Factor:
  https://www.nber.org/papers/w25551

Design consequence:

- tag industry and dominant economic factor separately;
- factor concentration limits apply even when industry labels differ.

## 9. Exit design

Fidelity educational material treats profit/loss ratios and time exits as legitimate planning frameworks:

- https://www.fidelity.com/learning-center/trading-investing/trading/exit-strategies

The repository therefore uses:

```text
price/invalidation stop
+ thesis stop
+ time stop
```

and gives R-multiple / structure priority over fixed percentage profit zones.

Historical `+3%–5%` traditional and `+6%–10%` growth zones are secondary observation zones only.

## 10. What research does NOT justify

The evidence does not justify:

- assuming historical return relationships repeat unchanged in A-shares;
- choosing a stock solely because it has momentum;
- treating a moving average as universally optimal;
- treating vendor “main force inflow” as institutional truth;
- using one valuation threshold for every industry;
- assuming stops execute exactly at stop price;
- using account size to mechanically increase strategy tranche count;
- extending a 5–15 day trade indefinitely;
- treating 0.5%, 1%, 2%, 3%, 4/6/8 or 50/50 as academically proven optimums.

## 11. Methodological conclusion

The defensible architecture is:

```text
locked universe
→ hard eligibility
→ leader/authenticity
→ financial quality
→ market/sector regime
→ technical/participation/catalyst score
→ execution-risk check
→ risk-based sizing
→ 50/50 confirmation-based entry by default
→ explicit holding state
→ adversarial audit
→ post-trade learning
```

The model is designed to minimize avoidable process errors, not maximize trade count.
