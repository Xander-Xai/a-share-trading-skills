# Raw Evidence Archive Contract v1.1

> Status: `ACTIVE RAW LINEAGE CONTRACT`
>
> Scope: source adapters, public/vendor/exchange captures, replay evidence and future production-data ingestion.

## 1. First principle

Normalization is not enough for auditability.

A production research system should preserve the source observation from which a normalized record was derived:

```text
Raw Source Bytes
→ raw_snapshot_id
→ Canonical Entity / PIT Record
→ data_snapshot_id
→ Feature / Decision
```

This creates an evidence chain from decision back to source material.

## 2. Active implementation

```text
src/data/raw_archive.py
runtime/tests/test_raw_archive.py
```

The first backend is content-addressed and local:

```text
objects/<sha256-prefix>/<content_hash>
manifests/<raw_snapshot_id>.json
```

It is a reference implementation, not a final enterprise object store.

## 3. Content identity vs observation identity

Two different concepts are preserved.

### Content hash

```text
content_hash = SHA256(raw bytes)
```

The same bytes observed multiple times reuse the same content object.

### Raw snapshot ID

`raw_snapshot_id` includes observation context:

```text
source
locator
observed_at
content_hash
byte_length
content_type
permitted_use
source_tier
encoding
status_code
selected headers
```

Therefore the same bytes observed at different times may have:

```text
same content_hash
different raw_snapshot_id
```

This is intentional because observation time matters for Point-in-Time evidence.

## 4. Required observation metadata

Minimum fields:

```text
source
locator
observed_at
content_hash
byte_length
content_type
permitted_use
```

Optional:

```text
source_tier
encoding
status_code
headers
```

`observed_at` must be timezone-aware.

HTTP header names are canonicalized to lowercase before observation identity is computed so semantically equivalent header casing does not create different snapshots.

## 5. Immutable behavior

The archive must detect:

```text
manifest tampering
object tampering
missing object
hash mismatch
byte-length mismatch
```

A normalized source adapter should refer to the immutable raw observation through:

```text
PITMetadata.source_snapshot_id = raw_snapshot_id
```

when a raw archive capture exists.

## 6. Data-use metadata is preserved at capture time

Raw evidence itself carries:

```text
RESEARCH_ONLY
INTERNAL_PRODUCTION_ALLOWED
REDISTRIBUTION_ALLOWED
UNRESOLVED_LICENSE
```

Changing a permitted-use classification creates a different observation manifest identity; it does not silently rewrite an old manifest.

Legal/vendor review may later justify a new metadata observation or policy mapping, but historical evidence is not overwritten.

## 7. Security / privacy boundary

The raw archive is not credential storage.

It must not persist:

```text
broker passwords
API secrets
Authorization headers
Proxy-Authorization headers
Cookie / Set-Cookie headers
x-api-key / auth-token style headers
session cookies that authorize trades
identity documents
private account tokens
signed URLs containing access-token / signature / password style query parameters
```

The active reference implementation rejects common sensitive HTTP headers and common credential-bearing query parameter names.

Transport implementations must still perform source-specific secret scrubbing before passing evidence to the archive. The machine deny-list is a guardrail, not a complete data-loss-prevention system.

If a provider requires authenticated retrieval:

```text
credential
→ transport only

scrubbed locator + selected non-secret response metadata + raw evidence
→ archive
```

Never serialize request Authorization/Cookie material into an evidence manifest.

## 8. Source adapter rule

Preferred future live ingestion path:

```text
Fetch source
→ scrub credentials / request secrets
→ archive raw bytes + selected response metadata
→ raw_snapshot_id
→ parse/normalize
→ PITStore using source_snapshot_id = raw_snapshot_id
```

If parsing fails, raw evidence remains available for debugging/quarantine.

Only explicitly selected non-secret response headers should be archived. Do not dump an entire response-header map by default.

## 9. Current backend limitations

The v1 local backend does not provide:

```text
multi-writer locking
remote object storage
encryption-at-rest management
retention enforcement
distributed replication
large-scale lifecycle policies
full DLP / secret scanning
```

Those features should be added only when deployment requirements justify them.

The semantics of content hash, observation identity and normalized lineage must survive any backend migration.
