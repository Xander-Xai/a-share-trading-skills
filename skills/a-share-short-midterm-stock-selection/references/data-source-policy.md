# Data Source and Evidence Policy

## Purpose

This skill depends on fresh public information. Source quality and point-in-time validity are part of the investment process because stale, promotional, revised, or future information can turn a correct framework into a wrong decision.

## 1. Source hierarchy

Use the highest available tier for each claim.

### Tier 1 — authoritative primary sources

Preferred for hard facts:

- China Securities Regulatory Commission (CSRC)
- Shanghai Stock Exchange (SSE)
- Shenzhen Stock Exchange (SZSE)
- CNINFO / official exchange disclosure system
- listed-company official filings and investor-relations releases

Use Tier 1 for:

- financial reports
- earnings forecasts
- suspensions
- risk warnings
- regulatory actions
- major contracts
- shareholder changes
- buybacks/dividends
- restructuring
- official business descriptions

### Tier 2 — high-quality structured financial data

Use for:

- price history
- market capitalization
- valuation history
- margin-financing data
- turnover
- technical indicators

Cross-check material discrepancies with Tier 1 or another reliable data source.

### Tier 3 — reputable financial media / broker research

Use for:

- industry context
- product pricing
- supply-demand explanation
- consensus framing
- interviews

Do not use media wording as proof that a company is a “leader”.

### Tier 4 — social/community information

Use only for sentiment discovery or rumor detection.

Never use it as sole evidence for:

- earnings
- contracts
- policy
- revenue exposure
- market share
- regulatory status

## 2. Point-in-time rule

Every analysis must carry an explicit `as of` timestamp.

Only use information that was publicly available by that timestamp.

Forbidden:

- using a later earnings report to justify an earlier trade,
- using later price action to validate an earlier technical setup,
- using revised figures without noting that the revision occurred after the decision date,
- treating consensus estimates as already reported results.

If recreating a historical decision, use only contemporaneously available data.

## 3. Freshness rules

### Price and technical data

- Default: latest completed trading session.
- If user asks for intraday analysis: use current intraday data and state the timestamp.
- Never combine an old technical chart with a current fundamental conclusion without disclosing the mismatch.
- Adjust chart interpretation for ex-rights/ex-dividend or other mechanical price adjustments.

### Fundamentals

Priority:

1. latest official quarterly/interim/annual report
2. latest official earnings forecast/preannouncement if newer
3. previous official report for historical comparison

If a newer report is scheduled but not yet published, label it as an event risk; do not treat estimates as reported fact.

### Catalysts

Prefer catalysts:

- already officially disclosed
- currently occurring
- scheduled within the practical strategy horizon

A catalyst older than 30 days should be rechecked for progress and whether the market has already priced it in.

## 4. Evidence standards by claim type

### Code/name identity

Must match a reliable market/exchange source.

### Industry leader claim

Require at least two independent evidence categories, preferably including a primary source:

- market share/ranking
- production/capacity
- revenue/profit scale
- customer/channel position
- technology/resource moat

### Concept/theme claim

Prefer official company disclosure. Look for quantified evidence:

- revenue
- profit
- shipment
- orders
- capacity
- customers
- commercial product

If only narrative exposure exists, mark concept authenticity as weak.

### Fundamental quality

At minimum inspect:

- revenue
- attributable profit
- adjusted/non-recurring profit where available
- operating cash flow or sector-appropriate substitute
- balance-sheet quality

Do not cite profit growth alone.

### Capital flow

Commercial “main force” data is vendor-defined. Use it only with:

- price confirmation
- volume/turnover
- sector participation
- financing/institutional data where available

## 5. A-share market-rule awareness

Always check current SSE/SZSE rules when execution assumptions matter because market rules can change.

Authoritative references used when this skill was revised:

- SSE Trading Rules, 2026 revision, effective 2026-07-06:
  https://www.sse.com.cn/lawandrules/sselawsrules2025/stocks/exchange/c/c_20260424_10816482.shtml
- SZSE Trading Rules, 2026 revision, effective 2026-07-06:
  https://www.szse.cn/lawrules/rule/trade/current/t20260424_620190.html
- CSRC Listed Company Information Disclosure Measures:
  https://www.csrc.gov.cn/csrc/c106256/c1653948/content.shtml

Execution implications that must be checked rather than assumed:

- ordinary-share settlement / same-day round-trip eligibility
- daily price limits by board/security status
- suspension/resumption
- abnormal-volatility measures
- after-hours/closing mechanisms
- risk-warning status

A planned stop is not guaranteed to execute at the stop price.

## 6. Material-event monitoring

Explicitly search for recent or upcoming:

- large earnings changes
- major impairment
- major contracts
- litigation/arbitration
- investigation/penalty
- share pledge/freeze
- buyback
- restructuring
- control changes
- shareholder reduction
- lock-up expiry
- ex-rights/ex-dividend
- suspension/resumption
- significant policy impact

The absence of a media report is not proof that no event exists. Search official disclosures.

## 7. Data completeness label

Every final stock should receive one of:

- **Complete** — fresh official fundamentals + fresh price/technical data + current catalyst/event check
- **Partial** — one non-critical gap
- **Insufficient** — material missing/conflicting information

A stock with `Insufficient` data should not be an executable trade candidate.

## 8. Research trail

For every selected stock, keep:

- source title
- publisher/domain
- publication/disclosure date
- fact supported
- URL or source identifier
- whether the source is primary or secondary
- `as of` validity

For universe-locked tasks, also keep the screenshot/list provenance for code and name.

## 9. Conflict resolution

When sources conflict:

1. prefer later official disclosure that was available by the analysis timestamp
2. prefer audited/board-approved filing over media summary
3. distinguish company guidance/forecast from reported results
4. distinguish restated/revised data from originally reported data
5. state unresolved uncertainty rather than averaging incompatible numbers

## 10. No-hallucination rule

When a universe is locked, web research is for **validation and ranking**, not for expanding the candidate set.

If research discovers a superior outside-universe stock, do not insert it unless the user explicitly permits external alternatives.

## 11. Research basis

See `research-basis.md` for the regulatory, accounting-quality, position-sizing, quality-factor, momentum, and factor-concentration evidence used to justify the architecture of this skill.