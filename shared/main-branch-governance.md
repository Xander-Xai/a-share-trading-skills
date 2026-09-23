# Main Branch Governance

Repository settings are an owner-level control and must be verified in GitHub,
not inferred from workflow YAML. The intended state is:

- `delete_branch_on_merge = true`;
- `main` cannot be deleted or force-pushed;
- source and governance changes merge through pull requests;
- solo-maintainer policy requires zero approvals, the `governance` check, resolved conversations, administrator enforcement, and no bypass actors;
- `Repository Governance` is the deterministic required check;
- the market monitor is not a required merge check while it depends on external
  providers; provider outages must remain fail-closed and separately reported.

The Daily Monitor uses a deterministic `automation/public-market-evidence`
branch and one PR at a time. Its isolated publisher job can write only
`runtime/state/market_history.csv`, creates or updates the PR, and relies on
normal protected-main checks. The monitor/test job has read-only permissions.
No workflow bypass actor is configured or required. The workflow never pushes
directly to `main`.
