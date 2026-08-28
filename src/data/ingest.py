from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable

from src.core.pit_store import PITStore, StoredPITRecord
from src.data.adapters import NormalizedRecordCandidate, SourceAdapter


@dataclass(frozen=True)
class IngestResult:
    adapter_id: str
    received: int
    written_or_existing: int
    record_ids: tuple[str, ...]


def ingest_candidates(
    store: PITStore,
    candidates: Iterable[NormalizedRecordCandidate],
    *,
    adapter_id: str = "DIRECT",
) -> IngestResult:
    """Validate and append normalized candidates into the canonical PIT store.

    PITStore itself enforces immutable identity and revision lineage. This helper
    deliberately does not catch validation failures: bad source normalization is
    a data-contract failure and should fail closed rather than be silently skipped.
    """
    received = 0
    stored: list[StoredPITRecord] = []
    for candidate in candidates:
        received += 1
        candidate.validate()
        stored.append(store.append(candidate.metadata, candidate.payload))

    return IngestResult(
        adapter_id=adapter_id,
        received=received,
        written_or_existing=len(stored),
        record_ids=tuple(record.metadata.record_id for record in stored),
    )


def run_adapter(store: PITStore, adapter: SourceAdapter, *, as_of: str) -> IngestResult:
    return ingest_candidates(
        store,
        adapter.collect(as_of=as_of),
        adapter_id=adapter.adapter_id,
    )
