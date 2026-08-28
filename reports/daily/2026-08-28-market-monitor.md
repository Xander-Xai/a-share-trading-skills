# A-share Short/Mid Daily Monitor — 2026-08-28

- as_of: `2026-08-28T22:03:01.478996+08:00`
- strategy_id: `a_share_short_mid`
- sleeve: `short_mid`
- runtime_mode: `SHORT_MID_MONITOR_ONLY`
- trading_day_status: `TRADING_DAY`
- spot_provider: `SINA_FALLBACK`
- sentiment_score: `66.96`
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
  "valid_stock_count": 5550,
  "advance_count": 3013,
  "decline_count": 2389,
  "flat_count": 148,
  "limit_up_count": 82,
  "limit_down_count": 1,
  "broken_limit_count": 16,
  "strong_count": 209,
  "weak_count": 138,
  "median_return_pct": 0.2225,
  "total_turnover": 2117306158992.0,
  "turnover_20d_median": null
}
```

## Candidate monitor states

| Code | Name | Price | Day % | Vs baseline % | Snapshot | Pre-action |
|---|---|---:|---:|---:|---|---|
| 601600 | 中国铝业 | 9.82 | 1.76 | 0.00 | priority_scan | REFRESH_FULL_GATES |
| 002602 | 世纪华通 | 13.97 | 0.36 | 0.00 | wait_technical_confirmation | REFRESH_SETUP |
| 600096 | 云天化 | 31.58 | 2.04 | 0.00 | wait_technical_confirmation | REFRESH_SETUP |
| 600392 | 盛和资源 | 22.93 | -1.29 | 0.00 | event_isolation | EVENT_REVIEW |
| 600415 | 小商品城 | 12.46 | 1.47 | 0.00 | wait_technical_confirmation | REFRESH_SETUP |
| 601808 | 中海油服 | 12.85 | 2.15 | 0.00 | wait_technical_confirmation | REFRESH_SETUP |
| 002831 | 裕同科技 | 26.40 | -1.60 | 0.00 | watch_only | RISK_REVIEW |
| 002273 | 水晶光电 | 26.12 | -2.57 | 0.00 | no_new_position | NO_NEW_ENTRY |

## Provider / configuration errors

- stock_zh_a_spot_em: ConnectionError: ('Connection aborted.', RemoteDisconnected('Remote end closed connection without response'))

> `pre_action` belongs only to `short_mid`. `AUTO_ORDER=false`; no report row is an executable order and no state may mutate the long sleeve.
