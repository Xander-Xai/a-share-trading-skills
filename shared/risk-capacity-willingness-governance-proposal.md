# Risk Capacity / Risk Willingness Governance Proposal

Status: `PROPOSED — BLOCKED_BY_GOVERNANCE_DECISION`

`LOW`, `MEDIUM`, and `HIGH` are currently Level-0 completeness and suitability
inputs only. They do **not** imply a percentage, RMB amount, or multiplier, and
the production risk budgets remain unchanged until this proposal is approved.

Before a quantitative mapping is adopted, governance must choose and approve:

1. whether capacity and willingness combine by `min`, a matrix, or a veto;
2. whether the mapping is a hard ceiling or an advisory sizing input;
3. the calibration dataset, review cadence, and breach/escalation policy; and
4. the versioned policy owner and rollback rule.

The test framework should verify deterministic mapping, missing/unknown fail
closed, monotonicity (higher risk tolerance cannot reduce the approved cap),
policy-version identity, and that existing 0.5%/1%/2%/3% governance values are
not changed by an unapproved mapping. Until then, `risk_capacity` and
`risk_willingness` remain required inputs for real-money ENTRY/ADD but have no
secret numerical interpretation.
