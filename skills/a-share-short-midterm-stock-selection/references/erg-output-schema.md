# ERG Output Schema v1

This is the minimum structured contract for Shadow research records using the Expectation–Reaction Gate.

```yaml
as_of: null
stock_code: null
stock_name: null
information_timestamp: null
first_tradable_timestamp: null
source_tier: null

expectation:
  baseline_type: NONE
  confidence: LOW
  center: null
  low: null
  high: null
  dispersion: null
  coverage_count: null

surprise:
  direction: UNRESOLVED
  evidence: []
  quarter_acceleration: null

materiality:
  state: UNRESOLVED
  transmission_path: null

prepricing:
  state: UNRESOLVED
  pre_event_AR_1: null
  pre_event_AR_5: null
  pre_event_AR_20: null
  pre_event_RVOL: null

reaction:
  state: UNRESOLVED
  overnight_AR: null
  post_event_AR_1: null
  post_event_AR_3: null
  post_event_AR_5: null
  relative_strength_vs_broad: null
  relative_strength_vs_sector: null
  relative_strength_vs_peer: null
  post_event_RVOL: null

research_state: WATCH
research_state_reason: null
strategy_type: null
position_state: FLAT
entry_trigger: null
invalidation: null
planned_RR: null
risk_budget_status: null
```

Rules:

- Missing data remains `null/UNRESOLVED`.
- `CONFIRMED` requires a documented reason; it is not inferred from a numerical score alone.
- `position_state` cannot move to `ENTRY` if shared risk/execution gates fail.
- `strategy_type` is locked for the life of the trade thesis unless the original record is closed and re-underwritten.
