# A-share Short/Mid Daily Monitor — 2026-09-22

- as_of: `2026-09-22T12:12:27.802265+08:00`
- strategy_id: `a_share_short_mid`
- sleeve: `short_mid`
- runtime_mode: `SHORT_MID_MONITOR_ONLY`
- trading_day_status: `TRADING_DAY`
- spot_provider: `EASTMONEY_PRIMARY`
- sentiment_score: `69.79`
- regime: `RISK_ON`
- crowding_flag: `False`
- data_confidence: `LOW`

## Runtime universe

```json
{
  "runtime_universe_version": "2026-08-28-v1",
  "as_of": "2026-08-28T18:10:00+08:00",
  "source_type": "RUNTIME_CONFIG",
  "source_note": "Bootstrapped from the approved 2026-08-28 short/mid research set. This is runtime configuration, not a mutable rewrite of the frozen Forward cohort.",
  "path": "runtime/config/short_mid_universe.json",
  "status": "LOADED"
}
```

## Governance references

```json
{
  "capital_policy": "shared/capital-allocation-and-entry-policy.md",
  "automation_governance": "shared/automation-execution-governance.md",
  "research_model_governance": "shared/research-model-governance.md",
  "strategy_boundary": "shared/strategy-boundary-contract.md",
  "pit_data_contract": "shared/canonical-pit-data-contract.md",
  "short_mid_skill": "skills/a-share-short-midterm-stock-selection/SKILL.md",
  "sentiment_model": "skills/a-share-short-midterm-stock-selection/references/a-share-sentiment-regime-index.md"
}
```

## Market metrics

```json
{
  "valid_stock_count": 5554,
  "advance_count": 2883,
  "decline_count": 2475,
  "flat_count": 196,
  "limit_up_count": 57,
  "limit_down_count": 0,
  "broken_limit_count": 13,
  "strong_count": 218,
  "weak_count": 26,
  "median_return_pct": 0.1,
  "total_turnover": 1440692506110.4,
  "turnover_20d_median": null
}
```

## Candidate monitor states

| Code | Name | Price | Day % | Vs baseline % | Snapshot | Pre-action |
|---|---|---:|---:|---:|---|---|
| 601600 | 中国铝业 | 9.34 | 1.74 | -4.89 | priority_scan | REFRESH_FULL_GATES |
| 002602 | 世纪华通 | 14.56 | -0.34 | 4.22 | wait_technical_confirmation | REFRESH_SETUP |
| 600096 | 云天化 | 28.28 | 0.00 | -10.45 | wait_technical_confirmation | REFRESH_SETUP |
| 600392 | 盛和资源 | 22.23 | 0.14 | -3.05 | event_isolation | EVENT_REVIEW |
| 600415 | 小商品城 | 11.91 | -0.17 | -4.41 | wait_technical_confirmation | REFRESH_SETUP |
| 601808 | 中海油服 | 12.28 | -1.92 | -4.44 | wait_technical_confirmation | REFRESH_SETUP |
| 002831 | 裕同科技 | 28.71 | 1.41 | 8.75 | watch_only | RISK_REVIEW |
| 002273 | 水晶光电 | 26.01 | 1.56 | -0.42 | no_new_position | NO_NEW_ENTRY |

## Provider / configuration errors

- none

> `pre_action` belongs only to `short_mid`. `AUTO_ORDER=false`; no report row is an executable order and no state may mutate the long sleeve.
