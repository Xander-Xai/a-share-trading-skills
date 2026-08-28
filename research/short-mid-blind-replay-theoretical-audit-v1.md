# Short/Mid Blind-Replay Theoretical Audit v1

> Status: RESEARCH / GOVERNANCE SUPPORT. This document does **not** change the production Champion, scoring thresholds, capital caps, entry permissions, or automation permissions.
>
> Purpose: adversarially audit the reasoning used in a 2026-08-05 point-in-time replay of 600699 (均胜电子), separate research-supported principles from heuristics, and prevent hindsight or pseudo-theoretical language from entering money-risk decisions.

## 1. Governance classification

Every inference in a blind replay must be labeled as one of:

```text
FACT / PIT FACT
RESEARCH-SUPPORTED PRINCIPLE
EXECUTION / RISK PRINCIPLE
GOVERNANCE PARAMETER
ALPHA HYPOTHESIS / CHALLENGER ONLY
UNCALIBRATED JUDGMENT — PROHIBITED AS PRODUCTION PROBABILITY
```

The repository already has a partial theory base in `skills/a-share-short-midterm-stock-selection/references/research-basis.md`, but it did not previously make the 5–15-day continuation-vs-reversal conflict explicit enough. This audit fills that gap.

## 2. Adversarial result summary

| Reasoning component | Audit result | Production interpretation |
|---|---|---|
| Point-in-time / no future leakage | KEEP — strong | mandatory governance |
| Recent strength can contain information | KEEP CONDITIONALLY | not a guarantee; horizon dependent |
| Strong volume confirms bullish continuation | REWRITE | volume is conditional evidence, not monotonic bullish proof |
| Prior highs / local pivots matter | KEEP AS EXECUTION GEOMETRY | resistance/support are conditional reference levels, not deterministic forecasts |
| Breakout + follow-through improves confidence | KEEP AS HYPOTHESIS | requires A-share forward validation |
| 3–5 day follow-through review | KEEP AS GOVERNANCE / CHALLENGER PARAMETER | not academically established as optimal |
| 50/50 setup-confirmation tranche | KEEP AS GOVERNANCE PARAMETER | no claim of optimality |
| Stop / invalidation improves returns | REWRITE | stop is primarily risk control; return benefit is conditional |
| Purchase cost should determine exit | REJECT | cost anchoring is behaviorally dangerous; cost remains P&L/accounting information only |
| Position size must shrink when stop distance/risk rises | KEEP — strong risk logic | exact 0.5%/1% caps remain governance parameters |
| 50%/30%/20% scenario probabilities | REMOVE | uncalibrated; prohibited from frozen replay |
| Exact manual score around 70 is a probability | REJECT | score is ranking only; incomplete PIT inputs require confidence downgrade |

## 3. Momentum evidence is real, but the horizon mismatch matters

### Supporting evidence

- Jegadeesh & Titman (1993), *The Journal of Finance*: winner-minus-loser momentum was documented over roughly 3–12 month holding horizons.
  - https://doi.org/10.1111/j.1540-6261.1993.tb04702.x
- Lo, Mamaysky & Wang (2000), *The Journal of Finance*: several objectively defined technical patterns contained incremental conditional information in a large U.S. equity sample.
  - https://www.nber.org/papers/w7613
- George & Hwang (2004), *The Journal of Finance*: nearness to the 52-week high contained information related to momentum profits.
  - https://doi.org/10.1111/j.1540-6261.2004.00695.x

### Adversarial evidence

- Jegadeesh & Titman (1995), *Journal of Financial Intermediation*: short-horizon negative serial covariance / reversals can arise from market microstructure effects.
  - https://doi.org/10.1006/jfin.1995.1006
- Yu, Fung & Leung (2019), *International Review of Economics & Finance*: using weekly Chinese stock returns, significant weekly reversals were found across SSE, SZSE and GEM; results depend on formation/holding horizon.
  - https://doi.org/10.1016/j.iref.2019.03.006
- Chen et al. (2025), *Journal of Empirical Finance*: weekly reversal effects remain economically relevant and are stronger in certain retail/illiquidity states.
  - https://doi.org/10.1016/j.jempfin.2025.101608

### Repository conclusion

```text
Intermediate-horizon momentum evidence
!=
proof of 3–5 day or 5–15 day continuation.
```

Therefore the short/mid system must not convert a few strong days into a deterministic right-side forecast. It should create conditional paths and wait for new evidence.

## 4. Technical-analysis evidence in China is mixed, not a license to curve-fit

Two high-quality results point in different directions:

- Jiang, Tong & Song (2019), *International Review of Finance*: after data-snooping controls, some technical rules on Chinese aggregate market data retained timing / Sharpe improvements, including after transaction costs.
  - https://doi.org/10.1111/irfi.12161
- Chuang et al. (2024), *Pacific-Basin Finance Journal*: across 38,456 rules on SSEC/GEM and after multiple-testing correction, only a few rules survived in-sample; most attractive rules became negative out-of-sample after transaction costs, and none outperformed GEM.
  - https://doi.org/10.1016/j.pacfin.2024.102278
- Earlier Chinese-index evidence also found that apparent MA / trading-range-break profits could disappear after transaction costs and data-snooping adjustment.
  - https://doi.org/10.1016/j.physa.2015.07.032

Production consequence:

```text
technical state = conditional information / execution geometry
not = proven standalone alpha
```

This strengthens the repository's existing Statistical Promotion Guard and argues against adding many local thresholds after observing one memorable trade.

## 5. Volume-price confirmation must be conditional

Lee & Swaminathan (2000), *The Journal of Finance*, showed that past turnover helps explain the magnitude and persistence of momentum, but high-volume winners can also reverse faster over longer horizons.

- https://doi.org/10.1111/0022-1082.00280

Therefore:

```text
high volume + price progress
may strengthen a continuation hypothesis

high volume alone
is not bullish evidence

high volume + poor price progress / stagnation
may be exhaustion or distribution evidence
```

This supports the repository's `price_progress_per_RVOL` research direction but does not validate one fixed formula or threshold.

## 6. Prior highs, resistance and reference prices: usable, but only as geometry

Three evidence families support using old highs / traded-price zones as *conditional reference levels*:

1. George & Hwang (2004): distance to the 52-week high contains information related to momentum.
2. Odean (1998), *The Journal of Finance*: investors tend to realize gains more readily than losses; purchase/reference prices influence trading behavior.
   - https://doi.org/10.1111/0022-1082.00072
3. Grinblatt & Han (2005), *Journal of Financial Economics*: aggregate unrealized capital gains / reference prices can affect price dynamics and momentum.
   - https://doi.org/10.1016/j.jfineco.2004.10.006
4. Osler (2000/2003) found support/resistance levels and clustered orders could help predict trend interruptions in FX markets.
   - https://www.newyorkfed.org/research/epr/00v06n2/0007osle.html
   - https://www.newyorkfed.org/research/staff_reports/sr125.html

Cross-market caveat: FX microstructure is not A-share single-stock microstructure. Therefore local highs/lows may be used to define invalidation, reward/risk and retest geometry, but must **not** be assigned deterministic bounce/break probabilities without A-share calibration.

## 7. Breakout / follow-through logic: keep, but downgrade its epistemic status

The blind-replay reasoning used:

```text
break above pivot + price progress + participation
→ stronger state

failure to progress for several days
→ weaker state / review
```

The first part is consistent with conditional technical-pattern evidence, but there is no credible literature showing that **exactly 3–5 trading days** is an optimal universal A-share review window.

Therefore:

```text
3–5 day review = Governance Parameter / Challenger research variable
not = Research-proven law
```

Candidate test variables:

```text
MFE_3d / MFE_5d
RS_3d / RS_5d
RVOL
price_progress_per_RVOL
breakout_hold
retest_success
```

Required validation:

```text
same PIT universe
same execution assumptions
cost-aware outcomes
MFE / MAE
false-positive reduction
blocked-upside cost
regime segmentation
untouched forward cohort
```

## 8. Stop-loss / invalidation: risk control first, alpha second

Kaminski & Lo (2014), *Journal of Financial Markets*, derive an important conditional result:

- if prices are random walks, stop-loss rules reduce expected returns;
- if prices exhibit momentum, some stop-loss policies can add value by reducing losses.

Source:
- https://doi.org/10.1016/j.finmar.2013.07.001

Therefore the repository should never write:

```text
stop-loss automatically improves returns
```

The defensible statement is:

```text
predefined invalidation limits planned exposure to a falsified thesis;
its effect on expectancy must be tested under the actual signal process and A-share execution constraints.
```

This is why `price stop + thesis stop + time review` remains risk architecture, while exact stop buffers remain calibration parameters.

## 9. Cost anchoring and holding losers

Odean (1998) documented the disposition effect: investors held losing positions longer and realized winning positions more readily, and the behavior was not justified by subsequent performance in that sample.

China-specific evidence also documents disposition behavior among Chinese retail investors using brokerage-level data:

- Zhang et al. (2022), *International Review of Financial Analysis*.
  - https://doi.org/10.1016/j.irfa.2022.102205
- An & Wang et al. (2024), *The Journal of Finance*, find portfolio-level reference framing in both U.S. and Chinese archival/experimental settings.
  - https://doi.org/10.1111/jofi.13378

Production implication:

```text
purchase cost is valid accounting/P&L information
but must not be the sole reason to HOLD, ADD or wait for breakeven.
```

This does **not** mean every losing position should be sold. It means the thesis must be re-evaluated with current opportunity cost and risk, rather than using breakeven as a market target.

## 10. Position sizing and concentration

### Strong theoretical direction

- Markowitz (1952), *The Journal of Finance*, provides the foundational diversification / portfolio-risk framework.
  - https://doi.org/10.1111/j.1540-6261.1952.tb01525.x
- Kelly (1956) derives growth-optimal betting under known probabilities/odds.
  - https://doi.org/10.1002/j.1538-7305.1956.tb03809.x

These support two broad principles:

```text
1. concentration changes portfolio risk nonlinearly;
2. optimal size depends on edge and downside distribution, not conviction language alone.
```

### What they do NOT prove

They do not prove the repository's exact:

```text
0.5% planned loss
1% hard per-trade ceiling
20% single short/mid symbol guideline
50/50 setup-confirmation split
```

Those remain conservative governance parameters pending forward calibration.

Because real stock return probabilities are unknown and tails/gaps are material, **full Kelly is not an appropriate default interpretation** for this repository.

## 11. Momentum crashes and regime dependence

Daniel & Moskowitz (2016), *Journal of Financial Economics*, show momentum strategies can suffer rare, persistent crashes, especially around panic/rebound states.

- https://doi.org/10.1016/j.jfineco.2015.12.002

Therefore market regime belongs in the causal path. Risk-on does not mean every recent winner deserves more size; risk-off/panic recovery can change the sign and tail properties of momentum-like exposures.

## 12. Corrections to the 600699 blind replay

The adversarial audit requires these corrections before freezing the case:

### Correction A — remove uncalibrated scenario probabilities

Previously stated `50% / 30% / 20%` path probabilities were judgmental and not statistically estimated. They are removed. The frozen sample stores **conditional paths only**.

### Correction B — respect production score thresholds

A manual reconstructed score range around `68–74` is not a probability and is not a fully reproducible production score because several PIT inputs are incomplete.

Under current production thresholds:

```text
65–74 = WATCH / WAIT FOR CONFIRMATION
75–79 = trade candidate with trigger
```

Therefore a no-position production decision at the 2026-08-05 close would be `WATCH / WAIT`, not an immediate setup order.

### Correction C — financing data PIT leak

The prior retrospective sample incorrectly inserted **2026-08-05 financing activity** into the entry-day context. That information was published on 2026-08-06 and was not available at the 2026-08-05 close.

The last confirmed financing snapshot available before the 2026-08-05 close was published at 08:01 on 2026-08-05 and described **2026-08-04** activity:

```text
financing buy = RMB 67.0095m
financing repayment = RMB 63.3481m
net financing buy = RMB 3.6614m
financing balance = RMB 1.4385806bn
```

Source:
- https://finance.sina.com.cn/stock/aiassist/lr/2026-08-05/doc-inimffsp3699411.shtml

### Correction D — unknown intraday entry timestamp

The user's reported cost is 21.525 on 2026-08-05, but the exact execution timestamp is unknown. Therefore a replay timestamped `2026-08-05T15:00:00+08:00` evaluates the **close-state / next-session decision**, not the exact information set at the moment of purchase.

This limitation must remain explicit.

## 13. Frozen blind-replay logic after audit

At the 2026-08-05 close, using no post-close/future information:

```text
Observed:
- close 21.62, high 21.85, low 21.21
- recent recovery from 19.19 on 7/24
- broad market risk-on / high turnover
- intelligent-driving theme strong that day
- Q1: revenue down, profit / adjusted profit up, OCF positive, new lifecycle orders strong
- prior overhead zone around 23.45–24.05 from early July
- last financing snapshot (8/4) low/muted rather than strongly expanding
```

Defensible state:

```text
research state = constructive recovery, but not clean new-high breakout
production decision for a new position = WATCH / WAIT FOR CONFIRMATION
```

Conditional path map — **no numeric probabilities**:

```text
CONTINUATION:
close/reclaim above ~21.85–22.00
+ price progress
+ sector/participation confirmation
→ rerun score; only consider trade if production threshold/risk gate passes

NEUTRAL / NO FOLLOW-THROUGH:
~21.0–21.85 range
→ no add; observe 3–5d as a governance review window

FAILURE:
break of ~20.60 short setup pivot
→ weakening / re-underwrite

broader break near ~20.00
→ recovery thesis materially damaged / invalidation candidate
```

The levels are execution geometry derived only from prices already observed by 2026-08-05. They are **not** claimed as calibrated probability barriers.

## 14. Counterfactual sizing calculation

For user-reported entry cost `E = 21.525`:

### If structural invalidation = 20.60

```text
stop distance = 4.297%
0.5% planned-loss budget -> theoretical exposure ≈ 11.64% of short-strategy NAV
1.0% hard-loss budget -> theoretical exposure ≈ 23.27%
```

### If broader invalidation = 20.00

```text
stop distance = 7.085%
0.5% planned-loss budget -> theoretical exposure ≈ 7.06%
1.0% hard-loss budget -> theoretical exposure ≈ 14.11%
```

If the reported `50%` exposure used the same NAV denominator, planned loss to those invalidations would be approximately `2.15%` or `3.54%`, respectively, before gap/slippage. The user's denominator was not independently verified, so these are conditional diagnostics, not an assertion about the actual account NAV.

## 15. Promotion status

No production parameter is changed by this audit.

```text
PIT correction                           = ACTIVE factual correction
scenario numeric probabilities           = REMOVED
3–5d follow-through                      = CHALLENGER / calibration required
breakout/retest interpretation            = CONDITIONAL RESEARCH PRINCIPLE
risk-based sizing                         = ACTIVE governance principle
exact risk percentages / position caps    = GOVERNANCE PARAMETERS
Champion weights / thresholds             = UNCHANGED
```

## 16. Final standard

For money-risk decisions, the repository should prefer:

```text
conditional reasoning
+ explicit uncertainty
+ pre-outcome frozen rules
+ adversarial counterevidence
+ risk sizing before return stories
+ cost-aware / PIT forward validation
```

over confident narrative precision.
