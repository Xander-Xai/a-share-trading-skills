# ERG Validation Checklist

Before an ERG record can move from `CANDIDATE` to `CONFIRMED`, verify:

- [ ] `as_of` is explicit.
- [ ] `information_timestamp` is known or conservatively bounded.
- [ ] `first_tradable_timestamp` respects publication timing and A-share execution constraints.
- [ ] expectation baseline type is declared.
- [ ] expectation confidence is declared.
- [ ] surprise is not inferred from headline YoY growth alone.
- [ ] economic transmission path is documented.
- [ ] pre-event pricing has been checked.
- [ ] post-event reaction is measured against at least a broad benchmark and, when practical, sector/peer benchmarks.
- [ ] volume/turnover is used as participation evidence, not proof of institutional buying.
- [ ] research state and position state are separate.
- [ ] strategy type is declared before entry.
- [ ] execution gate passes.
- [ ] planned invalidation exists before entry.
- [ ] expected reward/risk is acceptable under the current strategy rules.
- [ ] shared risk budget and factor-cluster limits pass.
- [ ] event-gap risk is explicitly reviewed.
- [ ] missing data is recorded as unresolved rather than guessed.

For model promotion also verify:

- [ ] trial ledger includes losing/neutral variants.
- [ ] nearby parameter stability has been reviewed.
- [ ] final test/forward period was not repeatedly tuned against.
- [ ] DSR/PBO/reality-check status is disclosed when applicable.
- [ ] ablation results show which ERG components add value after cost.
