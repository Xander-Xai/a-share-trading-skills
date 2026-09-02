# A-share Short/Mid Daily Monitor — 2026-09-02

- as_of: `2026-09-02T20:17:22.302703+08:00`
- strategy_id: `a_share_short_mid`
- sleeve: `short_mid`
- runtime_mode: `SHORT_MID_MONITOR_ONLY`
- trading_day_status: `TRADING_DAY`
- spot_provider: `SINA_FALLBACK`
- sentiment_score: `54.8`
- regime: `NEUTRAL`
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
  "valid_stock_count": 5553,
  "advance_count": 1541,
  "decline_count": 3900,
  "flat_count": 112,
  "limit_up_count": 52,
  "limit_down_count": 8,
  "broken_limit_count": 15,
  "strong_count": 164,
  "weak_count": 126,
  "median_return_pct": -0.943,
  "total_turnover": 1819769854257.0,
  "turnover_20d_median": null
}
```

## Candidate monitor states

| Code | Name | Price | Day % | Vs baseline % | Snapshot | Pre-action |
|---|---|---:|---:|---:|---|---|
| 601600 | 中国铝业 | 9.60 | -1.94 | -2.24 | priority_scan | REFRESH_FULL_GATES |
| 002602 | 世纪华通 | 14.03 | 1.30 | 0.43 | wait_technical_confirmation | REFRESH_SETUP |
| 600096 | 云天化 | 30.91 | -3.29 | -2.12 | wait_technical_confirmation | REFRESH_SETUP |
| 600392 | 盛和资源 | 21.97 | -3.43 | -4.19 | event_isolation | EVENT_REVIEW |
| 600415 | 小商品城 | 12.61 | -2.70 | 1.20 | wait_technical_confirmation | REFRESH_SETUP |
| 601808 | 中海油服 | 12.68 | -1.78 | -1.32 | wait_technical_confirmation | REFRESH_SETUP |
| 002831 | 裕同科技 | 26.58 | 1.03 | 0.68 | watch_only | RISK_REVIEW |
| 002273 | 水晶光电 | 25.69 | -1.19 | -1.65 | no_new_position | NO_NEW_ENTRY |

## Provider / configuration errors

- stock_zh_a_spot_em: ConnectionError: ('Connection aborted.', RemoteDisconnected('Remote end closed connection without response'))

> `pre_action` belongs only to `short_mid`. `AUTO_ORDER=false`; no report row is an executable order and no state may mutate the long sleeve.
