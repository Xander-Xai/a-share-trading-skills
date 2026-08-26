# Industry Coverage Audit

## Purpose

This module answers a different question from ordinary stock ranking:

> Does the locked user universe, and the selected core pool derived from it, cover the industries that actually exist inside that universe? If not, which in-universe leader is the best representative of each uncovered industry?

Industry coverage is a **research-completeness diagnostic**, not a mandate to force diversification or fill quotas.

A weak company must never be promoted merely because its industry is missing from the core pool.

## 1. Taxonomy standard

Default to a single, explicit primary industry taxonomy for the entire audit.

For A-share work, use the **current Shenwan (申万) 2021 industry classification at Level 1** unless the user requests another taxonomy.

Authoritative source priority:

1. Shenwan Hongyuan Research current industry-classification download/index pages;
2. current constituent/classification data from a reliable structured market-data source that explicitly implements Shenwan Level 1;
3. company disclosures for current principal-business reality when classification is ambiguous because of restructuring or business transformation.

Relevant Shenwan sources:

- Current industry classification download center: https://www.swsresearch.com/institute_sw/allIndex/downloadCenter/industryType
- 2021 revision comparison document: https://wxweb.swsresearch.com/swsreport/2021_08/328340.pdf

Do not mix Shenwan Level 1, Eastmoney thematic boards, CSRC industry, Wind theme tags, and broker concepts in one coverage count.

Record:

```text
industry_taxonomy = Shenwan 2021 Level 1
classification_as_of = YYYY-MM-DD
```

The number and membership of industries are point-in-time data. Re-check the current taxonomy instead of permanently hard-coding a count.

## 2. Map every in-universe stock once

For every unique stock code in the locked universe, assign exactly one **primary Level-1 industry** for coverage counting.

Required fields:

- code
- name
- source provenance
- primary_sw1_industry
- classification_source
- classification_as_of
- classification_confidence: High / Medium / Low
- ambiguity_note, if any

A stock may have multiple economic factors or concepts, but it must contribute to only one Level-1 industry count.

## 3. Handle reclassification and transformed businesses

Historical labels can become stale after restructuring, asset injection, divestiture or major business transformation.

When current classification and historical reputation conflict:

1. use the current official/current taxonomy for the formal Level-1 coverage count;
2. verify the company's current principal businesses in recent official filings;
3. document material ambiguity;
4. do not use an old label merely to make the coverage table look complete.

A historical property company that is now classified as electronics, for example, must not be used to fill a real-estate coverage gap unless current evidence supports that classification.

## 4. Compute four different coverage numbers

Never report only one vague statement such as “covered 20 industries.” Compute these separately:

### A. Taxonomy total

`taxonomy_total`

Number of Level-1 industries in the chosen taxonomy at the stated point in time.

### B. Locked-universe coverage

`universe_industries = unique(primary_sw1_industry in locked universe)`

`universe_coverage_count = len(universe_industries)`

This answers:

> How many industries are actually represented by the user's supplied stocks?

### C. Core-pool coverage

`core_industries = unique(primary_sw1_industry in selected core-quality pool)`

`core_coverage_count = len(core_industries)`

This answers:

> How much of the user's available industry breadth did the quality-first core selection retain?

Useful diagnostic:

`core_coverage_ratio = core_coverage_count / universe_coverage_count`

### D. Missing-industry sets

Compute two distinct gaps:

`uncovered_but_available = universe_industries - core_industries`

These industries exist in the locked universe but have no core-pool representative.

`absent_from_universe = taxonomy_industries - universe_industries`

These industries do not exist in the supplied universe at all.

Do not search outside the locked universe to fill `absent_from_universe` unless the user explicitly authorizes expansion.

## 5. Quality pool and coverage-supplement pool are different

Maintain two layers:

### Core quality pool

Selected only because the stocks rank highly on business quality, leader authenticity, fundamentals, tradability and current setup quality.

### Coverage supplement pool

Contains the best in-universe representative for an industry that is present in the locked universe but absent from the core quality pool.

Coverage supplements are not automatically equal-quality or equal-priority to core names.

Every supplement must retain a label such as:

- `coverage supplement — high quality`
- `coverage supplement — watch only`
- `coverage supplement — event isolated`
- `coverage supplement — weak current fundamentals`

The final research whitelist can be:

`core quality pool + qualified coverage supplements`

but the executable portfolio still follows normal score, timing, factor, heat and position limits.

## 6. Selecting a representative for an uncovered industry

For each industry in `uncovered_but_available`:

1. collect only stocks from that industry that already exist in the locked universe;
2. run the normal hard eligibility gates;
3. rank remaining candidates using the same evidence standards as the core process;
4. select at most one default representative unless the user explicitly requests multiple names per industry.

Preferred representative hierarchy:

1. true national/global industry leader with healthy fundamentals;
2. true sub-sector leader with healthy fundamentals;
3. high-quality second-tier company with clearly superior current data;
4. if none pass hard gates, leave the industry **uncovered**.

Do not choose a representative merely because it is the largest market-cap stock in that industry.

## 7. Coverage-representative checklist

A proposed supplement must pass:

### Leader authenticity

Require measurable evidence such as:

- market share/ranking
- production/capacity
- revenue/profit scale
- customer/channel position
- technical/resource/brand moat

### Concept authenticity

Remove hot-theme wording and ask whether the underlying business still justifies selection.

### Fundamental quality

Check at minimum:

- revenue
- attributable profit
- adjusted profit
- operating cash flow or sector substitute
- receivables/inventory/balance-sheet risks

### Current tradability

For short/mid-term use, also check:

- liquidity
- trend and relative strength
- entry extension
- upcoming binary events
- realistic Reward/Risk

A company can qualify as the industry's research representative while still receiving status `wait`, `event isolation`, or `avoid for now`.

## 8. Coverage must not override portfolio factor control

Industry coverage is a research-universe property, not a command to hold one stock from every industry.

Examples:

- several different Level-1 industries may still share the same commodity or AI-capex factor;
- a 40–50 stock research whitelist may cover most industries while the actual portfolio still holds only 0–5 stocks;
- same-industry and same-factor limits remain binding.

Never convert “28 industries represented in the whitelist” into “hold 28 stocks.”

## 9. Coverage audit output

When the user asks for industry coverage, report:

### Coverage summary

- raw stock records
- unique stock codes
- taxonomy and classification date
- taxonomy total industries
- locked-universe industries
- core-pool industries
- core coverage ratio
- uncovered-but-available industries
- absent-from-universe industries

### Gap table

For each `uncovered_but_available` industry:

- industry
- all in-universe candidates considered, or at least candidate count
- chosen representative
- code
- leader evidence
- latest fundamental quality note
- short/mid-term status
- main risk
- confidence

### No-forcing statement

Explicitly state:

- whether any industry was left uncovered because no in-universe candidate passed the gates;
- whether any taxonomy industry was absent from the universe and therefore intentionally not filled.

## 10. Adversarial coverage review

Before finalizing the coverage result, attack it with these questions:

1. Did we use one taxonomy consistently?
2. Did we count one stock in multiple industries?
3. Did any stale historical classification fill a gap incorrectly?
4. Did any outside-universe stock enter the supplement pool?
5. Did we force a weak company merely to achieve 100% coverage?
6. Is the chosen representative truly the best available in-universe candidate?
7. Are we confusing industry diversification with economic-factor diversification?
8. Are coverage supplements being mislabeled as equal-priority core names?
9. Did event risk or accounting weakness get hidden because the stock was needed for coverage?

If any answer reveals an error, correct the mapping/selection and recompute the coverage metrics.

## 11. Design principle

The desired architecture is:

```text
locked universe
→ current Level-1 industry mapping
→ universe coverage audit
→ quality-first core selection
→ core coverage audit
→ identify uncovered-but-available industries
→ select best qualified in-universe representative per gap
→ label supplements separately
→ adversarial coverage review
→ research whitelist
→ ordinary daily scoring and execution funnel
```

**Coverage is diagnostic. Quality and risk remain the gatekeepers.**