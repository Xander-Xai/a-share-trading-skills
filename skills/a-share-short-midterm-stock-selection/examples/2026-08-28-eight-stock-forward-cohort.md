# 2026-08-28 Eight-stock ERG Forward Cohort

> Status: `FROZEN FORWARD BASELINE`
>
> Decision timestamp: `2026-08-28T18:10:00+08:00`
>
> Universe source: user-supplied eight-stock watchlist/screenshot.
>
> Purpose: first immutable case cohort for Champion vs Causal Challenger/ERG validation. Later outcomes must be appended; the baseline below must not be rewritten with hindsight.

## 1. Locked universe and closing references

| Code | Name | 2026-08-28 reference close | Day return |
|---|---|---:|---:|
| 002831 | 裕同科技 | 26.40 | -1.60% |
| 600096 | 云天化 | 31.58 | +2.04% |
| 601600 | 中国铝业 | 9.82 | +1.76% |
| 600415 | 小商品城 | 12.46 | +1.47% |
| 601808 | 中海油服 | 12.85 | +2.15% |
| 002602 | 世纪华通 | 13.97 | +0.36% |
| 600392 | 盛和资源 | 22.93 | -1.29% |
| 002273 | 水晶光电 | 26.12 | -2.57% |

These prices are frozen decision/reference inputs, not future fill prices.

## 2. Regime snapshot

```text
market_regime = ROTATIONAL_NEUTRAL
```

Interpretation used for this cohort:

- avoid automatic chase after short bursts;
- require explicit execution geometry;
- retain no-trade as a valid outcome;
- keep Champion and ERG decisions separate.

## 3. Frozen model outputs

Exact Champion point scores are intentionally not fabricated where capital-participation fields were incomplete. Score ranges/statuses are preserved as the actual research output at this timestamp.

| Priority | Stock | Champion range/status | ERG research state | Confirmation basis | Position state | Strategy type |
|---:|---|---|---|---|---|---|
| 1 | 中国铝业 | ~80 / high-priority research | CONFIRMED | MULTI_EVIDENCE | FLAT | EVENT_MOMENTUM |
| 2 | 世纪华通 | 75–79 / trigger candidate | CANDIDATE | EVENT_REACTION | FLAT | EVENT_MOMENTUM |
| 3 | 云天化 | 75–79 / trigger candidate | CONFIRMED | TREND_STRUCTURE | FLAT | TREND |
| 4* | 盛和资源 | 75–79 / event candidate | CANDIDATE | — (pending EVENT_REACTION) | FLAT | EVENT_MOMENTUM |
| 5 | 小商品城 | 65–74 / watch-trigger | CANDIDATE | MULTI_EVIDENCE | FLAT | EVENT_MOMENTUM |
| 6 | 中海油服 | 65–74 / watch-trigger | CONFIRMED | TREND_STRUCTURE | FLAT | TREND |
| 7 | 裕同科技 | ~60–67 / watch | WATCH | MULTI_EVIDENCE | FLAT | EVENT_MOMENTUM |
| 8 | 水晶光电 | <65 / no new position | INVALIDATED | EVENT_REACTION | FLAT | EVENT_MOMENTUM |

`*` 盛和资源 is isolated from ordinary ordinal comparison until the first tradable post-report reaction is observed. Its `confirmation_basis` is not populated because the research state is still `CANDIDATE`; the pending basis is `EVENT_REACTION`.

## 4. Frozen execution plans

These are Setup / Confirmation / Thesis Invalidation references, not deterministic support/resistance claims.

| Stock | Setup | Confirmation | Thesis invalidation | Frozen action |
|---|---|---|---|---|
| 中国铝业 | 9.55–9.70 | 9.90–10.00 hold/reclaim | ~9.30 structural failure | WAIT_FOR_SETUP |
| 世纪华通 | 13.65–13.80 | 14.20–14.30 breakout/hold | ~13.45 | WAIT_FOR_CONFIRMATION |
| 云天化 | 30.80–31.10 | 31.80–32.00 hold | <30.20 warning; ~29.70 strong invalidation | DO_NOT_CHASE |
| 盛和资源 | unresolved until reaction | observe 23.35–23.50 only as prior structure | recalc after reaction | EVENT_REACTION_PENDING |
| 小商品城 | 12.15–12.30 | 12.75–12.85 | ~11.75 | WAIT_FOR_CONFIRMATION |
| 中海油服 | 12.55–12.70 | 12.95–13.05 | ~12.20 | WAIT_FOR_RETEST_OR_CONFIRMATION |
| 裕同科技 | none | >27.70 only with new quantified evidence | none frozen | NO_NEW_POSITION |
| 水晶光电 | none | reclaim 27.30–28.00 + RS/participation | re-underwrite after repair | NO_NEW_POSITION |

## 5. Event/PIT lock: 盛和资源

At this cohort timestamp the formal H1 report had become public after the normal 15:00 close, around `2026-08-28T16:23:00+08:00` in the research snapshot.

Frozen rule:

```text
2026-08-28 close return (-1.29%)
!= post-H1-report reaction
```

The information timestamp was later than the current 15:05–15:30 post-close fixed-price trading window. Therefore same-day reaction is unavailable. The event must be anchored to the next valid exchange session, while the exact executable timestamp remains subject to the session-aware execution contract and broker/account resolution.

Frozen session fields:

```text
exchange = SSE
post_close_eligible = true
same_day_post_close_window_status = CLOSED_BEFORE_INFORMATION
session_type = NEXT_SESSION
first_exchange_tradable_timestamp = null
first_broker_executable_timestamp = null
first_tradable_timestamp = null
resolution_status = OUTSIDE_SESSION
```

Do not later rewrite the 2026-08-28 close as evidence that the market accepted or rejected that H1 report.

## 6. First outcome windows

Append outcomes at:

```text
+1 trading day
+3 trading days
+5 trading days
+10 trading days
+20 trading days
```

For each stock preserve:

```text
forward raw return
benchmark/sector excess return
MFE
MAE
state transitions
trigger hit timestamp
invalidation hit timestamp
simulated realized R when applicable
```

## 7. Disagreement cases to track

Priority disagreement cases for this cohort:

### 中海油服

```text
Champion: watch/trigger tier
Challenger: CONFIRMED / TREND_STRUCTURE
```

Question: does trend-state confirmation add useful discrimination when headline fundamental growth is limited?

### 盛和资源

```text
headline H1 growth: large
ERG: CANDIDATE / reaction pending
```

Question: does PIT + preannouncement/expectation + reaction gating reduce event-chasing false positives without excessive opportunity cost?

### 水晶光电

```text
fundamental eligibility: passes
ERG active thesis: INVALIDATED
```

Question: does negative event reaction prevent a failed event trade from being relabeled as a cheaper entry?

## 8. Immutability rule

The following fields are frozen and may never be edited because of later outcomes:

```text
universe
as_of
reference prices
Champion status/range
research_state
position_state
strategy_type
confirmation_basis
setup/confirmation/invalidation plan
PIT interpretation
```

Corrections to factual transcription errors must be logged separately with reason and timestamp.

## 9. What this cohort can and cannot establish

This cohort can test:

- workflow wiring;
- state semantics;
- PIT/session handling;
- disagreement logging;
- no-trade/opportunity-cost accounting.

This cohort alone cannot establish:

- stable alpha;
- optimal thresholds;
- Champion promotion;
- event-family robustness;
- regime robustness.

Those require larger frozen forward/historical point-in-time samples under the repository Promotion protocol.