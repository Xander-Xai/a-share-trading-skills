# ERG Output Schema v1.2

This is the minimum structured contract for Shadow research records using the Expectation–Reaction Gate.

```yaml
as_of: null
stock_code: null
stock_name: null
exchange: null
board: null
information_timestamp: null
source_tier: null

execution_session:
  session_rule_version: null
  session_type: UNRESOLVED
  post_close_eligible: null
  suspension_state_at_1500: null
  broker_post_close_support: null
  first_exchange_tradable_timestamp: null
  first_broker_executable_timestamp: null
  first_tradable_timestamp: null
  resolution_status: UNRESOLVED

benchmark_contract:
  version: null
  contract_frozen_at: null
  primary_benchmark: null
  secondary_benchmark: null
  sector_benchmark: null
  peer_basket_rule: null
  peer_basket_members_as_of: []
  benchmark_selection_rule: null
  benchmark_fallback_rule: null
  pit_status: UNRESOLVED

reaction_window_contract:
  version: null
  contract_frozen_at: null
  event_family: null
  reaction_anchor: null
  primary_reaction_window: UNRESOLVED_RESEARCH
  secondary_reaction_windows: []
  window_selection_method: null
  session_treatment: null

expectation:
  baseline_type: NONE
  confidence: LOW
  center: null
  low: null
  high: null
  dispersion: null
  coverage_count: null
  coverage_flag: null

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
  abnormal_return_primary: null
  abnormal_return_sector: null
  abnormal_return_peer: null
  benchmark_sensitivity: UNRESOLVED
  window_sensitivity: UNRESOLVED
  post_event_RVOL: null

research_state: WATCH
research_state_reason: null
confirmation_basis: null
strategy_type: null
position_state: FLAT
entry_trigger: null
invalidation: null
planned_RR: null
risk_budget_status: null
```

Allowed `confirmation_basis` values:

```text
EVENT_REACTION
TREND_STRUCTURE
REGIME_RELATIVE_STRENGTH
MEAN_REVERSION_SETUP
MULTI_EVIDENCE
OTHER_EXPERIMENTAL
```

Allowed `benchmark_sensitivity` labels:

```text
BENCHMARK_STABLE
BENCHMARK_SENSITIVE
INSUFFICIENT_DATA
UNRESOLVED
```

Allowed `window_sensitivity` labels:

```text
WINDOW_STABLE
WINDOW_SENSITIVE
INSUFFICIENT_DATA
UNRESOLVED
```

Rules:

- Missing data remains `null/UNRESOLVED`.
- `CONFIRMED` requires a documented reason and `confirmation_basis`; it is not inferred from a numerical score alone.
- `position_state` cannot move to `ENTRY` if shared risk/execution gates fail.
- `strategy_type` is locked for the life of the trade thesis unless the original record is closed and re-underwritten.
- Event timing must be resolved with `session-aware-execution-calendar.md`; an after-15:00 disclosure is not automatically mapped to the next trading day.
- If exchange/broker/session state is unresolved, `first_tradable_timestamp` remains unresolved and no executable event trade is generated.
- Event abnormal-return interpretation follows `benchmark-and-reaction-window-contract.md`.
- A future event cohort must freeze the benchmark and primary reaction-window contracts before outcome observation.
- If a legacy frozen cohort predates the contract, do not retrofit the contract and relabel post-hoc analysis as original forward evidence.
- Low/none expectation coverage cannot be presented as a verified beat/miss without an explicit alternate expectation baseline.