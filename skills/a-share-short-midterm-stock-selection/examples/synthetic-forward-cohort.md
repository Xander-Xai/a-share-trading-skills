# Synthetic Forward-Validation Cohort Example

> `SYNTHETIC EXAMPLE / NOT REAL USER DATA`
>
> Classification: `SYNTHETIC`; no real ticker, selected watchlist, account, position, trade date or fill is represented.

## Frozen baseline

```text
cohort = CASE-SM-COHORT-001
status = SYNTHETIC_FIXTURE
production_effect = NONE
AUTO_ORDER = false
```

| Case | Research state | Position state | Evidence status | Permitted interpretation |
|---|---|---|---|---|
| CASE-SM-001 | CANDIDATE | FLAT | synthetic evidence complete | test schema and decision separation only |
| CASE-SM-002 | WATCH | FLAT | synthetic event timestamp unresolved | remain blocked pending a valid timestamp |
| CASE-SM-003 | INVALIDATED | FLAT | synthetic invalidation condition met | no new entry; do not infer performance |

These rows do not encode market forecasts, actual transactions or expected returns. The fixture exists to test immutable-baseline handling, evidence-state transitions, missing-data behavior and the separation of research status from position/action semantics.

Execution-side sample events such as `BUY` / `SELL` are not canonical position-state semantics. Canonical states remain defined by the governing contract; this fixture does not change their namespace.

## Validation rule

Future outcomes may be appended to a real private evidence store, but must not rewrite a frozen decision. Synthetic fixtures cannot establish Alpha or promote a model.
