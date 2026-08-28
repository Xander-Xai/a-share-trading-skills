# Official Disclosure Source Contract v0

> Status: `ACTIVE SOURCE-ADAPTER CONTRACT / LIVE TRANSPORT UNRESOLVED`
>
> Scope: Shanghai Stock Exchange and Shenzhen Stock Exchange listed-company disclosure ingestion.

## 1. Verified official source surfaces

Public official company-announcement surfaces verified on 2026-08-28:

```text
SSE company announcements:
https://www.sse.com.cn/assortment/stock/list/info/announcement/

SSE latest listed-company announcements:
https://www.sse.com.cn/disclosure/listedinfo/announcement/

SZSE listed-company announcements:
https://www.szse.cn/disclosure/notice/company/index.html
```

Official disclosure documents may be served from official subdomains such as:

```text
www.sse.com.cn
*.sse.com.cn
www.szse.cn
*.szse.cn
```

## 2. What is not verified

This repository has **not** verified a stable, documented public JSON/API contract for these announcement index pages.

Therefore v0 explicitly does not hard-code a reverse-engineered endpoint.

```text
official web surface exists
!= documented stable machine API exists
```

A future live transport may be added only after its acquisition mechanism, terms, timestamp semantics and failure behavior are documented and tested.

## 3. Current implementation

```text
src/data/official_disclosures.py
```

implements:

```text
OfficialDisclosureRow
OfficialDisclosureTransport protocol
StaticOfficialDisclosureTransport
OfficialDisclosureAdapter
SSE adapter builder
SZSE adapter builder
```

The adapter is real normalization code, but the live network transport is intentionally unresolved.

## 4. Timestamp rule

Announcement index surfaces may expose only a calendar date rather than a precise publication timestamp.

The system must not turn:

```text
2026-08-28
```

into an invented:

```text
2026-08-28 00:00:00
or
2026-08-28 15:00:00
```

Two explicit visibility bases exist:

### FIRST_OBSERVED

For forward collection:

```text
available_at = time our system first observed the official row
```

`published_at` may remain null.

This can be conservative but does not leak information backward.

### OFFICIAL_TIMESTAMP

For historical/event replay when a precise official publication timestamp is independently known:

```text
available_at = published_at
```

If exact `published_at` is unavailable, normalization fails with `TimestampResolutionError`.

## 5. Source tier vs permitted use

Official exchange disclosure evidence is:

```text
source_tier = TIER1
```

This does **not** automatically imply a production data license.

Default adapter metadata remains:

```text
permitted_use = UNRESOLVED_LICENSE
```

until actual website/vendor/exchange permitted-use terms for the intended production workflow are reviewed.

Tier describes evidence authority. `permitted_use` describes operational permission. They are separate axes.

## 6. Document-host validation

The adapter rejects document locators outside the configured official host family.

This reduces accidental normalization of scraped mirrors or third-party copies as Tier-1 evidence.

Host validation is provenance hygiene, not a cryptographic proof of document authenticity.

## 7. No content inference at the data layer

The source adapter normalizes index metadata only:

```text
security_id
announcement_id
title
category
document_url
period_end when known
published_at when exact
observed_at
```

It does not use an LLM to infer business impact, Surprise, Materiality, ERG state or long-term thesis implications.

Those belong to strategy/research layers after the disclosure is stored as canonical evidence.

## 8. Next promotion step

Before enabling a live official-disclosure transport:

```text
verify acquisition mechanism
freeze raw-response fixtures
verify timestamp meaning
verify pagination / query behavior
verify duplicate/revision behavior
verify rate/failure behavior
review permitted use
run PIT replay tests
```

Only then may the transport be considered for `INTERNAL_PRODUCTION` data snapshots.
