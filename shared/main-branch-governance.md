# Main Branch Governance

Repository settings are an owner-level control and must be verified in GitHub,
not inferred from workflow YAML. The intended state is:

- `delete_branch_on_merge = true`;
- `main` cannot be deleted or force-pushed;
- source and governance changes merge through pull requests;
- `Repository Governance` is the deterministic required check;
- the market monitor is not a required merge check while it depends on external
  providers; provider outages must remain fail-closed and separately reported.

The daily monitor must not create an infinite workflow loop. A safe deployment
choice is a bot/evidence branch with a pull request, or a narrowly scoped
ruleset bypass for the workflow actor that can write only generated evidence.
The owner must select and configure one of these in Settings → Rules → Rulesets
and verify it with a test PR. This checkout cannot claim those settings were
changed without a successful GitHub API response.
