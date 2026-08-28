# Official Disclosure Adapter v0 — Research / Implementation Status

> Status: `NORMALIZATION IMPLEMENTED / LIVE TRANSPORT UNRESOLVED`
>
> Date: 2026-08-28

## Verified public source surfaces

SSE:

```text
https://www.sse.com.cn/assortment/stock/list/info/announcement/
https://www.sse.com.cn/disclosure/listedinfo/announcement/
```

SZSE:

```text
https://www.szse.cn/disclosure/notice/company/index.html
```

These are official exchange disclosure surfaces.

## Research finding

The current research did not establish a stable documented public JSON/API contract for these dynamic announcement listings.

Therefore the implementation deliberately stops at:

```text
verified official index row/capture
→ Source Transport interface
→ official disclosure normalization
→ PITStore
```

and does not hard-code a reverse-engineered private endpoint.

## Implemented safety properties

```text
official-host allowlist
no fabricated intra-day publication timestamp
FIRST_OBSERVED forward-safe visibility mode
OFFICIAL_TIMESTAMP strict historical/event mode
Tier-1 evidence classification
UNRESOLVED_LICENSE default permitted-use state
strategy visibility for long/short_mid shared facts
PIT revision/record lineage through existing store
```

## Why FIRST_OBSERVED exists

If the exchange listing exposes only:

```text
2026-08-28
```

we cannot infer whether the announcement was visible at 08:00, 12:00, 15:10 or 18:00.

For forward collection the system can instead preserve:

```text
observed_at = first time our collector actually saw it
```

and set:

```text
available_at = observed_at
```

This may delay the modeled availability, but it cannot create look-ahead by moving information earlier.

For historical event research requiring exact reaction timing, a precise official timestamp must be independently established or the record remains non-promotable for that use.

## Not yet implemented

```text
live SSE announcement index transport
live SZSE announcement index transport
pagination / query-state transport contract
rate-limit/retry behavior
raw HTML/JSON response archive
PDF/content downloader
announcement content extraction
revision/correction detection from live source
```

## Next gate

A live transport should not be promoted until:

```text
acquisition mechanism verified
raw fixture captured
timestamp semantics verified
pagination verified
duplicate/revision behavior verified
failure modes tested
permitted-use reviewed
```

This keeps the production-data path conservative while allowing the normalization layer to progress.
