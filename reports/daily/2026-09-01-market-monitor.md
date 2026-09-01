# A-share Short/Mid Daily Monitor — 2026-09-01

- as_of: `2026-09-01T20:44:41.203342+08:00`
- strategy_id: `a_share_short_mid`
- sleeve: `short_mid`
- runtime_mode: `SHORT_MID_MONITOR_ONLY`
- trading_day_status: `TRADING_DAY`
- spot_provider: `SINA_FALLBACK`
- sentiment_score: `70.75`
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
  "valid_stock_count": 5552,
  "advance_count": 3387,
  "decline_count": 2039,
  "flat_count": 126,
  "limit_up_count": 83,
  "limit_down_count": 0,
  "broken_limit_count": 6,
  "strong_count": 260,
  "weak_count": 170,
  "median_return_pct": 0.5735,
  "total_turnover": 2051576536965.0,
  "turnover_20d_median": null
}
```

## Candidate monitor states

| Code | Name | Price | Day % | Vs baseline % | Snapshot | Pre-action |
|---|---|---:|---:|---:|---|---|
| 601600 | 中国铝业 | 9.79 | 0.20 | -0.31 | priority_scan | REFRESH_FULL_GATES |
| 002602 | 世纪华通 | 13.85 | -2.05 | -0.86 | wait_technical_confirmation | REFRESH_SETUP |
| 600096 | 云天化 | 31.96 | 1.65 | 1.20 | wait_technical_confirmation | REFRESH_SETUP |
| 600392 | 盛和资源 | 22.75 | -2.19 | -0.78 | event_isolation | EVENT_REVIEW |
| 600415 | 小商品城 | 12.96 | 3.85 | 4.01 | wait_technical_confirmation | REFRESH_SETUP |
| 601808 | 中海油服 | 12.91 | 0.15 | 0.47 | wait_technical_confirmation | REFRESH_SETUP |
| 002831 | 裕同科技 | 26.31 | -1.75 | -0.34 | watch_only | RISK_REVIEW |
| 002273 | 水晶光电 | 26.00 | -2.66 | -0.46 | no_new_position | NO_NEW_ENTRY |

## Provider / configuration errors

- stock_zh_a_spot_em: ConnectionError: ('Connection aborted.', RemoteDisconnected('Remote end closed connection without response'))

> `pre_action` belongs only to `short_mid`. `AUTO_ORDER=false`; no report row is an executable order and no state may mutate the long sleeve.
