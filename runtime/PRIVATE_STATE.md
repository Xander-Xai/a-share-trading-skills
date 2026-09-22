# Private Runtime State

Personal portfolio data, transaction history, cash-needs answers, risk-capacity answers, broker/account information and frozen pre-trade authorizations are **runtime-private data**, not repository source code.

Do not commit real personal financial records to this repository.

Use local/private paths such as:

```text
runtime/private/portfolio_instances.json
runtime/pretrade_authorizations/<decision_id>.json
runtime/state/private/
reports/private/
```

These paths are ignored by `.gitignore`.

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
