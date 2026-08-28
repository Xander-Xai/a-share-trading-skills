# ERG Promotion Criteria

ERG may be proposed for partial or full promotion only after the normal repository Promotion Gate passes.

Minimum evidence package:

```text
1. Point-in-time audit
2. Cost-aware Forward results
3. ERG ablation ladder
4. Regime breakdown
5. Event-type breakdown
6. MFE / MAE analysis
7. Rule-violation analysis
8. Parameter-stability review
9. Model-selection / trial-count disclosure
10. Complexity-benefit review
```

Promotion should answer separately:

- Does `Expectation/Surprise` add useful discrimination?
- Does `Materiality` remove narrative false positives?
- Does `Prepricing` reduce post-event chasing / reversal losses?
- Does `Reaction` improve timing or reduce false positives?
- Does research-state/position-state separation reduce rule violations?
- Does strategy-type lock reduce holding-inertia / thesis drift?

Allowed outcomes:

```text
PROMOTE_SELECTED_COMPONENTS
PROMOTE_FULL_ERG
KEEP_SHADOW
REMOVE_COMPONENT
REVISE_AND_RESTART
REJECT
```

A coherent narrative is not sufficient evidence for promotion.
