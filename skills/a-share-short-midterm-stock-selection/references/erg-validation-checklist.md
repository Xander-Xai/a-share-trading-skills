# ERG Validation Checklist v1.1

Before an ERG record can move from `CANDIDATE` to `CONFIRMED`, verify:

- [ ] `as_of` is explicit.
- [ ] `information_timestamp` is known or conservatively bounded.
- [ ] `first_tradable_timestamp` respects publication timing and A-share execution constraints.
- [ ] expectation baseline type is declared.
- [ ] expectation confidence is declared.
- [ ] expectation coverage is not overstated; `NONE/LOW` is not relabeled as verified surprise without an alternate documented baseline.
- [ ] surprise is not inferred from headline YoY growth alone.
- [ ] economic transmission path is documented.
- [ ] pre-event pricing has been checked.
- [ ] benchmark contract is frozen before outcome interpretation for new cohorts.
- [ ] primary benchmark selection rule is documented.
- [ ] sector/peer benchmark construction is point-in-time where used.
- [ ] reaction-window contract is frozen before outcome interpretation for new cohorts.
- [ ] primary reaction window is predeclared; D1/D3/D5 is not selected after inspecting outcomes.
- [ ] post-event reaction is measured under the frozen benchmark/window contract.
- [ ] benchmark sensitivity is disclosed if predeclared benchmarks disagree materially.
- [ ] window sensitivity is disclosed if interpretation depends on one narrow window.
- [ ] volume/turnover is used as participation evidence, not proof of institutional buying.
- [ ] research state and position state are separate.
- [ ] every `CONFIRMED` state has a `confirmation_basis`.
- [ ] strategy type is declared before entry.
- [ ] execution gate passes.
- [ ] planned invalidation exists before entry.
- [ ] planned R/R is treated as entry geometry / governance, not proof of positive expectancy.
- [ ] shared risk budget and factor-cluster limits pass.
- [ ] event-gap risk is explicitly reviewed.
- [ ] missing data is recorded as unresolved rather than guessed.
- [ ] human-language phrases such as "资金认可" or "位置不错" map to measurable machine fields.

For cohort / validation analysis also verify:

- [ ] agreement between related methods is not treated as independent model voting.
- [ ] decision robustness diagnostics are kept separate from return validation.
- [ ] rank/state stability, if reported, is labeled diagnostic rather than alpha evidence.
- [ ] no-trade opportunity cost is measured.
- [ ] false positives and false negatives are both reported when gate strictness is evaluated.
- [ ] actual-event and placebo samples use the same benchmark/window/session/cost contract.
- [ ] legacy frozen cohorts are not retrofitted and relabeled as pre-outcome evidence.

Validation maturity must be labeled explicitly:

```text
Level A = Integration / Case Validation
Level B = Historical Point-in-Time Research Validation
Level C = Untouched Forward Validation
```

An integration PASS does not imply alpha is proven.

For model promotion also verify:

- [ ] trial ledger includes losing/neutral variants.
- [ ] nearby parameter stability has been reviewed.
- [ ] final test/forward period was not repeatedly tuned against.
- [ ] DSR/PBO/reality-check status is disclosed when applicable.
- [ ] ablation results show which ERG components add value after cost.
- [ ] primary benchmark/window choices were frozen before the promotion cohort.
- [ ] blocked-opportunity cost is disclosed for stricter filters.
- [ ] promotion claim is based on cost-aware outcome evidence, not rank stability or narrative plausibility alone.
