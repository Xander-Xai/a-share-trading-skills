# Repository Truth / Drift Audit — 2026-09-22

## Frozen remote snapshot

- Repository: `Xander-Xai/a-share-trading-skills`
- `origin/main`: `16c3a935f22236172282d2e4b86818316da57bf0`
- Open PR: #29, `audit/repository-governance-hardening-v2`, HEAD `88810c22c9ec4e46fd5c8816a836f56dbfb0257c`
- Open Issues: #25, #26, #27, #30, #31
- Protection: required `governance` check, one approving review, conversation resolution, admins enforced, force-push/deletion disabled.
- PR #28: closed, superseded.

## Branch inventory and disposition

Remote branches were re-enumerated after `fetch --all --prune`. The repository currently contains `main`, active PR branches, and historical branches. `security/history-rewrite-candidate` is content-identical to `main` and is stale. `audit/repository-governance-hardening` is the superseded PR #28 branch. Other merged-PR branches require per-head/content equivalence review before retirement; no historical branch is merged or rebased by this audit.

## Current policy / skill truth

- Capital eligibility `v2`
- Pre-trade authorization `v1.1`
- Capital allocation `v2.6`
- Automation / execution `v1.5`
- Research / model `v3.2`
- Canonical PIT data `v1.2`
- Short/Mid skill `1.7.3`
- Long skill `2.2.2`
- Multi-asset skill `1.1.1`

## Current versus historical documents

The dated research and roadmap documents remain historical evidence unless explicitly declared current. The current runtime and policy headers are the authoritative implementation references. A broader documentation/current-state convergence remains tracked by Issues #30 and #31 and is not silently declared complete here.

## PR #29 checks at snapshot

- Existing governance and monitor checks: successful at the frozen HEAD.
- Review decision: `REVIEW_REQUIRED`; no independent approval is present.
- Conversation resolution is required by branch protection.
- This branch adds fail-closed handling for JSON serialization `TypeError` and evaluates effective Git ignore semantics with `git check-ignore`.

## Privacy boundary

No personal financial values are recorded in this report. Private runtime prefixes are ignored and checked using effective Git behavior; tracked-tree enumeration is fail-closed. No history rewrite, force push, protected-main bypass, or restoration of personal data was performed.

## Remaining owner actions

- Independent eligible reviewer approval is required before PR #29 can merge (`MERGE_BLOCKED_BY_APPROVAL_SATISFIABILITY` if no eligible reviewer exists).
- Issues #25, #27, #30, and #31 remain open until their stated external, current-tip, integration, and drift gates are actually satisfied.
- Historical GitHub-managed pull refs require GitHub Support; they were not modified.
