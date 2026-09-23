# Private Runtime State

Personal portfolio data, transaction history, cash-needs answers, risk-capacity answers, broker/account information and frozen pre-trade authorizations are **runtime-private data**, not repository source code.

Do not commit real personal financial records to this repository.

Use local/private paths such as:

```text
runtime/private/portfolio_instances.json
runtime/private/short_mid_universe.json
runtime/private/sample_registry.json
runtime/state/private/sample_evidence/
runtime/pretrade_authorizations/<decision_id>.json
runtime/state/private/
reports/private/
reports/private/daily/
reports/private/sample_evidence/
```

These paths are ignored by `.gitignore`.

Legacy public-output locations `runtime/config/short_mid_universe.json`, `runtime/config/sample_registry.json`, `runtime/state/sample_evidence/`, and `reports/daily/` are also ignored and must not be repopulated with private case rows.

A sanitized schema example is available at:

`runtime/portfolio_instances.example.json`

## Allowed in Git

- schemas;
- synthetic examples clearly labeled synthetic;
- redacted process case studies with no personal holdings/cost basis/cash-needs details;
- aggregate research metrics that cannot reconstruct a person's account.

## Not allowed in Git

- real share counts and cost basis tied to a user;
- personal realized P&L;
- emergency-fund/cash-need answers;
- total financial assets or account balances;
- broker account identifiers;
- API credentials;
- private pre-trade authorization cards.

If private financial data was accidentally committed to a public repository, deleting the current file is only the first mitigation. Git history may still retain the content; history rewriting and cache/search remediation require a separate explicit operation.
