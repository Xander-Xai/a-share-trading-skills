# A-share Short/Mid Daily Monitor — 2026-08-29

- as_of: `2026-08-29T00:04:22.554854+08:00`
- strategy_id: `a_share_short_mid`
- sleeve: `short_mid`
- runtime_mode: `SHORT_MID_MONITOR_ONLY`
- trading_day_status: `MARKET_CLOSED`
- spot_provider: `NOT_REQUESTED`
- sentiment_score: `None`
- regime: `DATA_INSUFFICIENT`
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
  "valid_stock_count": null,
  "advance_count": null,
  "decline_count": null,
  "flat_count": null,
  "limit_up_count": null,
  "limit_down_count": null,
  "broken_limit_count": null,
  "strong_count": null,
  "weak_count": null,
  "median_return_pct": null,
  "total_turnover": null,
  "turnover_20d_median": null
}
```

## Candidate monitor states

| Code | Name | Price | Day % | Vs baseline % | Snapshot | Pre-action |
|---|---|---:|---:|---:|---|---|
| 601600 | 中国铝业 |  |  |  |  | NO_ACTION_DATA_MISSING |
| 002602 | 世纪华通 |  |  |  |  | NO_ACTION_DATA_MISSING |
| 600096 | 云天化 |  |  |  |  | NO_ACTION_DATA_MISSING |
| 600392 | 盛和资源 |  |  |  |  | NO_ACTION_DATA_MISSING |
| 600415 | 小商品城 |  |  |  |  | NO_ACTION_DATA_MISSING |
| 601808 | 中海油服 |  |  |  |  | NO_ACTION_DATA_MISSING |
| 002831 | 裕同科技 |  |  |  |  | NO_ACTION_DATA_MISSING |
| 002273 | 水晶光电 |  |  |  |  | NO_ACTION_DATA_MISSING |

## Provider / configuration errors

- none

> `pre_action` belongs only to `short_mid`. `AUTO_ORDER=false`; no report row is an executable order and no state may mutate the long sleeve.
