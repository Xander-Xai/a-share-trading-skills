# ERG Integration Map

This integration adds a Shadow-only expectation/reaction research layer to the existing A-share short/mid-term Challenger without replacing the current Champion.

## Added modules

- `expectation-reaction-gate.md` — operationalizes expectation baseline, surprise, economic materiality, prepricing and post-event reaction.
- `erg-forward-test-extension.md` — adds ERG-specific frozen fields, event breakdowns and ablation ladders to forward validation.
- `statistical-promotion-guard.md` — records model-selection trials and adds anti-data-snooping/statistical review requirements.
- `erg-adversarial-review-report.md` — adversarial review and current pass/fail conclusion.

## Intended architecture

```text
Universe / Point-in-Time Gate
→ Fundamental Eligibility
→ Expectation–Reaction Gate
→ Market / Sector Regime
→ Participation / Relative Strength
→ Research State
→ Execution Gate
→ Risk Budget
→ Position State
→ Portfolio Cluster Risk
→ MFE / MAE / Forward Learning
→ Statistical Promotion Guard
```

## Governance status

```text
Champion: unchanged
Causal Challenger: remains SHADOW ONLY
ERG: SHADOW ONLY
Production-order impact: none
```

The next valid step is frozen forward/ablation testing. No production promotion should occur merely because the framework appears more coherent.
