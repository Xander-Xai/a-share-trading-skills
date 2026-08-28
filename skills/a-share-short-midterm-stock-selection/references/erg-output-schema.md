# ERG Output Schema v1.3

This is the minimum structured contract for Shadow research records using the Expectation-Reaction Gate.

v1.3 adds machine evidence/state lineage without changing Champion, Position State or execution authority.

```yaml
as_of: null
stock_code: null
stock_name: null
exchange: null
board: null
information_timestamp: null
source_tier: null

evidence_bundle_id: null
state_machine_version: null
shadow_decision_id: null

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

eligibility:
  status: UNRESOLVED
  reasons: []

expectation:
  baseline_type: NONE
  confidence: LOW
  center: null
  low: null
  high: null
  dispersion: null
  coverage_count: null
  coverage_flag: null
  fiscal_period: null
  metric: null
  unit: null
  verified_surprise_eligible: false
  evidence_refs: []

surprise:
  direction: UNRESOLVED
  verified: false
  metric: null
  actual: null
  expected_center: null
  delta: null
  delta_pct: null
  calculation_method: null
  classification_contract_id: null
  evidence: []
  evidence_refs: []
  quarter_acceleration: null

materiality:
  state: UNRESOLVED
  transmission_path: null
  assessment_contract_id: null
  impact_metrics: null
  evidence_refs: []

prepricing:
  state: UNRESOLVED
  event_measurement_id: null
  classification_contract_id: null
  pre_event_AR_1: null
  pre_event_AR_5: null
  pre_event_AR_20: null
  pre_event_RVOL: null

reaction:
  state: UNRESOLVED
  event_measurement_id: null
  classification_contract_id: null
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
research_state_reason_code: null
confirmation_basis: null
strategy_type: null
position_state: FLAT
entry_trigger: null
invalidation: null
planned_RR: null
risk_budget_status: null
executable: false
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

Machine-evidence rules:

- `evidence_bundle_id` is the content-addressed identity of the structured ERG evidence used by the state machine.
- `shadow_decision_id` is the content-addressed identity of the Shadow research-state output.
- `state_machine_version` must be explicit for machine-generated states.
- a `verified=true` surprise requires an eligible expectation baseline; `NONE`, `LOW` confidence or insufficient consensus coverage cannot be silently promoted into a verified beat/miss.
- resolved Materiality requires an auditable transmission path and assessment contract.
- resolved Prepricing/Reaction categories require explicit classification contracts; numerical thresholds are not inferred from this schema.
- Prepricing and Reaction should reference the same event measurement when both are derived from the same event window calculation.

General rules:

- Missing data remains `null/UNRESOLVED`.
- `CONFIRMED` requires a documented reason and `confirmation_basis`; it is not inferred from a numerical score alone.
- the initial machine ERG implementation may only emit `EVENT_REACTION` as its own confirmation basis; other bases belong to higher Challenger layers.
- `position_state` cannot move to `ENTRY` if shared risk/execution gates fail.
- the v0 ERG Shadow state machine itself always remains `position_state = FLAT` and `executable = false`.
- `strategy_type` is locked for the life of the trade thesis unless the original record is closed and re-underwritten.
- Event timing must be resolved with `session-aware-execution-calendar.md`; an after-15:00 disclosure is not automatically mapped to the next trading day.
- If exchange/broker/session state is unresolved, `first_tradable_timestamp` remains unresolved and no executable event trade is generated.
- Event abnormal-return interpretation follows `benchmark-and-reaction-window-contract.md`.
- A future event cohort must freeze the benchmark and primary reaction-window contracts before outcome observation.
- If a legacy frozen cohort predates the contract, do not retrofit the contract and relabel post-hoc analysis as original forward evidence.
- Low/none expectation coverage cannot be presented as a verified beat/miss without an explicit alternate expectation baseline.
- ERG remains `SHADOW ONLY` until repository Promotion governance is satisfied.
