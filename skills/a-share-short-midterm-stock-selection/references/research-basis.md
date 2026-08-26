# Research Basis and Design Rationale

## Purpose

This file records the external evidence used to validate and refine the skill. It is not a promise that historical relationships will persist, and it is not a substitute for current A-share disclosures or market data.

The skill deliberately separates:

1. **A-share market rules and disclosure facts** — grounded in Chinese regulators/exchanges.
2. **Risk-management principles** — grounded in position-sizing and portfolio-risk practice.
3. **Accounting-quality principles** — grounded in financial-report analysis literature.
4. **Momentum/quality evidence** — used only as conceptual support, not as fixed A-share parameter calibration.

## 1. A-share execution constraints are real risk, not implementation detail

### SSE trading rules

The 2026 Shanghai Stock Exchange Trading Rules state that securities bought by investors generally cannot be sold before settlement unless the security is specifically eligible for same-day round-trip trading. This means ordinary A-share execution is not equivalent to a market where an entry can always be reversed intraday.

The same rules also define daily price-limit mechanisms for stocks and funds and were revised in 2026. Price-limit and settlement mechanics mean a theoretical stop price may not be executable during a gap or limit-down move.

Source:
- Shanghai Stock Exchange, *Trading Rules (2026 Revision)*, effective 2026-07-06
- https://www.sse.com.cn/lawandrules/sselawsrules2025/stocks/exchange/c/c_20260424_10816482.shtml

Design consequence:
- Entry-day risk must account for the inability to freely reverse a normal A-share position intraday.
- Stops are **invalidation plans**, not guaranteed fill prices.
- Gap and price-limit risk must be handled by smaller size, event isolation, and first-executable-price exit logic.

## 2. Material information must be verified through official disclosure

Chinese listed-company disclosure rules require periodic reports and disclosure of information that can materially influence investors' value judgments and investment decisions. Interim reports are therefore a core source, not an optional secondary input.

Source:
- China Securities Regulatory Commission, *Measures for the Administration of Information Disclosure by Listed Companies*
- https://www.csrc.gov.cn/csrc/c106256/c1653948/content.shtml

Design consequence:
- Official filings take precedence over theme articles, social posts, or stale annual data.
- A scheduled-but-unreleased report is an event risk, not a fact that can be filled with consensus estimates.
- Research must be point-in-time: only information available by the stated `as of` timestamp may be used in the decision.

## 3. Risk-based sizing is superior to arbitrary share counts

Fidelity's educational material presents position sizing as a function of maximum portfolio loss and the distance between entry and stop/invalidation level:

`position size = risk per trade / risk per share`

Sources:
- Fidelity Investments, *Exit Strategy / Position Sizing*
- https://www.fidelity.com/bin-public/060_www_fidelity_com/documents/learning-center/Presentation_Exit%20Strategy.pdf
- Fidelity Wealth-Lab User Guide, max-percent-risk position sizing
- https://www.fidelity.com/bin-public/060_www_fidelity_com/documents/WLP_User_Guide.pdf

Design consequence:
- The skill sizes positions from planned loss, not from conviction language.
- A wider invalidation distance requires a smaller position.
- The user's default 0.5% maximum planned loss per trade is intentionally stricter than common educational rules of thumb and should not be loosened without explicit review.

## 4. Earnings quality requires cash-flow and accrual checks

CFA Institute research emphasizes that reported earnings can be distorted by accruals and that cash flows are generally less dependent on accounting estimates. CFA material on financial-report quality also notes that unusually high accrual components can imply less persistent earnings.

Sources:
- CFA Institute Research Foundation, *Earnings Quality*
- https://rpc.cfainstitute.org/sites/default/files/-/media/documents/book/rf-publication/2004/rf-v2004-n3-3927-pdf.pdf
- CFA Institute, *Evaluating Quality of Financial Reports*
- https://www.cfainstitute.org/sites/default/files/-/media/documents/book/curriculum-update/rr-v-2017-n2-1.pdf

Design consequence:
- Profit growth never receives a full fundamental score without checking adjusted profit, operating cash flow, receivables/inventory, and one-off gains.
- Sector-specific accounting logic is mandatory; banks and brokers should not be evaluated using industrial operating-cash-flow rules mechanically.

## 5. Quality is multidimensional

AQR's Quality Minus Junk research defines quality through dimensions including profitability, growth, safety, and payout/management-related characteristics and documents a historical risk-adjusted return premium to high-quality firms across many markets.

Source:
- AQR, *Quality Minus Junk*
- https://www.aqr.com/Insights/Research/Working-paper/Quality-minus-Junk

Fama/French factor construction also explicitly uses operating profitability as a systematic return-related characteristic.

Source:
- Kenneth French Data Library, Fama/French 5 Factors
- https://mba.tuck.dartmouth.edu/pages/faculty/ken.french/Data_Library/f-f_5_factors_2x3.html

Design consequence:
- “Good fundamentals” means more than high recent profit growth.
- The skill looks for profitability quality, balance-sheet resilience, cash conversion, and durable industry position.
- These studies are not A-share timing models; they validate the use of business-quality gates rather than calibrating exact score weights.

## 6. Momentum exists, but chasing momentum can fail catastrophically

NBER research documents persistence in return and earnings momentum, consistent with markets sometimes reacting gradually to information. Other NBER work also documents rare but large momentum crashes.

Sources:
- Chan, Jegadeesh & Lakonishok, *Momentum Strategies*, NBER Working Paper 5375
- https://www.nber.org/papers/w5375
- Chabot, Ghysels & Jagannathan, *Momentum Trading, Return Chasing, and Predictable Crashes*, NBER Working Paper 20660
- https://www.nber.org/papers/w20660

Design consequence:
- Relative strength and price confirmation deserve weight.
- Momentum cannot be treated as “buy whatever already rose the most.”
- Extension, crowding, late-stage breakout, and market-regime penalties are necessary.
- The skill must permit `no trade today` when the only available setups are overextended.

## 7. Short-term momentum can be factor-driven

Research on factor momentum finds that individual-stock momentum can reflect persistence in broader factor returns.

Source:
- Ehsani & Linnainmaa, *Factor Momentum and the Momentum Factor*, NBER Working Paper 25551
- https://www.nber.org/papers/w25551

Design consequence:
- Sector/commodity/macro-factor tagging is mandatory.
- Several apparently different stocks may be one economic bet.
- Portfolio limits apply to shared economic drivers, not only exchange industry labels.

## 8. What the research does NOT justify

The evidence above does **not** justify:

- assuming historical returns repeat unchanged in A-shares,
- choosing a stock solely because it has momentum,
- treating any fixed moving average as universally optimal,
- treating a vendor's “main force inflow” as institutional truth,
- mechanically using one valuation threshold across sectors,
- assuming a stop order can always execute at the stop price,
- extending a 5–15 day trade indefinitely without a fresh decision.

## 9. Methodological conclusion

The most defensible architecture is therefore:

`locked universe -> hard eligibility -> leader/authenticity -> financial quality -> market/sector regime -> technical/participation/catalyst score -> execution-risk check -> risk-based sizing -> explicit holding state -> adversarial audit -> post-trade learning`

The model is designed to minimize avoidable process errors rather than maximize the number of trades.