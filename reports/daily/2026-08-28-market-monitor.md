# A-share Daily Monitor — 2026-08-28

- as_of: `2026-08-28T02:24:42.442547+08:00`
- runtime_mode: `MONITOR_ONLY`
- trading_day_status: `TRADING_DAY`
- spot_provider: `SINA_FALLBACK`
- sentiment_score: `73.26`
- regime: `RISK_ON`
- crowding_flag: `False`
- data_confidence: `LOW`

## Governance references

```json
{
  "capital_policy": "shared/capital-allocation-and-entry-policy.md",
  "automation_governance": "shared/automation-execution-governance.md",
  "research_model_governance": "shared/research-model-governance.md",
  "short_mid_skill": "skills/a-share-short-midterm-stock-selection/SKILL.md",
  "sentiment_model": "skills/a-share-short-midterm-stock-selection/references/a-share-sentiment-regime-index.md"
}
```

## Market metrics

```json
{
  "valid_stock_count": 5549,
  "advance_count": 3393,
  "decline_count": 1944,
  "flat_count": 212,
  "limit_up_count": 77,
  "limit_down_count": 3,
  "broken_limit_count": 17,
  "strong_count": 503,
  "weak_count": 40,
  "median_return_pct": 0.527,
  "total_turnover": 2140562927883.0,
  "turnover_20d_median": null
}
```

## Candidate monitor states

| Code | Name | Price | Day % | Vs baseline % | Snapshot | Pre-action |
|---|---|---:|---:|---:|---|---|
| 601179 | 中国西电 | 12.98 | 0.00 | 0.00 | priority_scan | REFRESH_FULL_GATES |
| 600875 | 东方电气 | 25.95 | 0.74 | 0.74 | priority_scan | REFRESH_FULL_GATES |
| 600392 | 盛和资源 | 23.23 | 3.38 | 3.38 | wait_technical_confirmation | REFRESH_SETUP |
| 601958 | 金钼股份 | 23.39 | 1.48 | 1.48 | wait_technical_confirmation | REFRESH_SETUP |
| 000960 | 锡业股份 | 36.12 | 1.55 | 1.55 | wait_technical_confirmation | REFRESH_SETUP |
| 601600 | 中国铝业 | 9.65 | 0.63 | 0.63 | priority_scan | REFRESH_FULL_GATES |
| 600362 | 江西铜业 | 49.20 | 1.30 | 1.30 | downgrade_or_risk_watch | RISK_REVIEW |
| 601899 | 紫金矿业 | 34.57 | 0.29 | 0.29 | priority_scan | REFRESH_FULL_GATES |
| 603236 | 移远通信 | 56.62 | 4.33 | 3.43 | wait_technical_confirmation | REFRESH_SETUP |
| 600487 | 亨通光电 | 71.30 | 9.98 | 9.98 | wait_technical_confirmation | WAIT_NO_CHASE |
| 600522 | 中天科技 | 36.08 | 7.99 | 7.99 | wait_technical_confirmation | WAIT_NO_CHASE |
| 603296 | 华勤技术 | 78.49 | 1.68 | 1.68 | priority_scan | REFRESH_FULL_GATES |
| 600584 | 长电科技 | 76.54 | 3.97 | 3.97 | wait_technical_confirmation | REFRESH_SETUP |
| 002475 | 立讯精密 | 57.18 | 0.12 | 0.12 | downgrade_or_risk_watch | RISK_REVIEW |
| 601138 | 工业富联 | 63.86 | 5.43 | 5.43 | priority_scan | WAIT_NO_CHASE |
| 002430 | 杭氧股份 | 24.65 | 2.15 | 2.15 | wait_technical_confirmation | REFRESH_SETUP |
| 002080 | 中材科技 | 52.48 | 5.09 | 5.09 | wait_technical_confirmation | WAIT_NO_CHASE |
| 600176 | 中国巨石 | 42.64 | 7.95 | 7.95 | priority_scan | WAIT_NO_CHASE |
| 600160 | 巨化股份 | 39.54 | 3.64 | 3.64 | priority_scan | REFRESH_FULL_GATES |
| 603806 | 福斯特 | 15.34 | 1.72 | 1.72 | wait_technical_confirmation | REFRESH_SETUP |
| 002979 | 雷赛智能 | 56.20 | 1.65 | 1.65 | wait_technical_confirmation | REFRESH_SETUP |
| 002050 | 三花智控 | 36.82 | 1.88 | 1.88 | event_isolation | EVENT_REVIEW |
| 002602 | 世纪华通 | 13.92 | -0.21 | -0.22 | wait_technical_confirmation | REFRESH_SETUP |
| 000100 | TCL科技 | 4.97 | 1.22 | 1.22 | wait_technical_confirmation | REFRESH_SETUP |
| 000725 | 京东方A | 5.94 | 3.85 | 3.85 | wait_technical_confirmation | REFRESH_SETUP |
| 002736 | 国信证券 | 10.24 | 0.59 | 0.59 | priority_scan | REFRESH_FULL_GATES |
| 600741 | 华域汽车 | 15.32 | -0.65 | -0.65 | wait_technical_confirmation | REFRESH_SETUP |
| 600690 | 海尔智家 | 21.12 | -0.14 | -0.14 | event_isolation | EVENT_REVIEW |
| 600415 | 小商品城 | 12.28 | -0.24 | -0.24 | wait_technical_confirmation | REFRESH_SETUP |
| 000651 | 格力电器 | 39.27 | -0.78 | -5.56 | downgrade_or_risk_watch | RISK_REVIEW |
| 000858 | 五粮液 | 71.12 | -1.08 | -1.08 | wait_technical_confirmation | REFRESH_SETUP |
| 002273 | 水晶光电 | 26.81 | 2.96 | 2.96 | wait_technical_confirmation | REFRESH_SETUP |
| 600196 | 复星医药 | 22.89 | 0.13 | 0.13 | wait_technical_confirmation | REFRESH_SETUP |
| 600096 | 云天化 | 30.95 | 2.38 | 2.38 | wait_technical_confirmation | REFRESH_SETUP |
| 000967 | 盈峰环境 | 8.63 | 2.62 | 2.62 | downgrade_or_risk_watch | RISK_REVIEW |
| 601808 | 中海油服 | 12.58 | 1.95 | 1.94 | downgrade_or_risk_watch | RISK_REVIEW |
| 000977 | 浪潮信息 | 78.27 | 6.07 | 6.07 | event_isolation | EVENT_REVIEW |
| 002414 | 高德红外 | 12.95 | 0.94 | 0.94 | downgrade_or_risk_watch | RISK_REVIEW |
| 603162 | 海通发展 | 11.96 | 0.17 | 0.17 | downgrade_or_risk_watch | RISK_REVIEW |
| 600236 | 桂冠电力 | 9.92 | 0.81 | 0.81 | priority_scan | REFRESH_FULL_GATES |
| 002831 | 裕同科技 | 26.83 | 0.45 | 0.45 | event_isolation | EVENT_REVIEW |
| 002041 | 登海种业 | 11.23 | 4.17 | 4.17 | downgrade_or_risk_watch | RISK_REVIEW |
| 600549 | 厦门钨业 | 54.80 | 4.14 | 4.14 | downgrade_or_risk_watch | RISK_REVIEW |

## Provider errors

- stock_zh_a_spot_em: ConnectionError: ('Connection aborted.', RemoteDisconnected('Remote end closed connection without response'))

> `pre_action` is research/monitor output only. `AUTO_ORDER=false`; no report row is an executable order.
