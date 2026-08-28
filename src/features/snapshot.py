from __future__ import annotations

import hashlib
import json
import math
import os
import tempfile
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any, Iterable, Mapping

from src.core.strategy_boundary import StrategyContext


FEATURE_SNAPSHOT_SCHEMA_VERSION = "1.0"
VALID_FEATURE_STATUS = {"AVAILABLE", "MISSING", "UNRESOLVED"}


def _canonical_json(value: Any) -> str:
    return json.dumps(
        value,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
        allow_nan=False,
    )


def _sha256_text(content: str) -> str:
    return hashlib.sha256(content.encode("utf-8")).hexdigest()


def _parse_aware(value: str, field_name: str) -> datetime:
    parsed = datetime.fromisoformat(value)
    if parsed.tzinfo is None or parsed.utcoffset() is None:
        raise ValueError(f"{field_name} must be timezone-aware ISO-8601")
    return parsed


def _require_text(value: str, field_name: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{field_name} is required")
    return value.strip()


def _validate_scalar(value: Any) -> None:
    if isinstance(value, bool):
        return
    if isinstance(value, int):
        return
    if isinstance(value, float):
        if not math.isfinite(value):
            raise ValueError("feature value must be finite")
        return
    if isinstance(value, str):
        return
    raise ValueError("feature value must be a bool/int/float/string scalar")


def _atomic_write_text(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, tmp_name = tempfile.mkstemp(prefix=f".{path.name}.", dir=str(path.parent))
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as handle:
            handle.write(content)
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(tmp_name, path)
    finally:
        if os.path.exists(tmp_name):
            os.unlink(tmp_name)


@dataclass(frozen=True)
class FeatureValue:
    name: str
    status: str
    value: bool | int | float | str | None = None
    unit: str | None = None
    source_record_ids: tuple[str, ...] = ()
    calculation_id: str | None = None

    def validate(self) -> None:
        _require_text(self.name, "feature name")
        if self.status not in VALID_FEATURE_STATUS:
            raise ValueError(f"invalid feature status: {self.status}")

        if self.status == "AVAILABLE":
            if self.value is None:
                raise ValueError("AVAILABLE feature requires a value")
            _validate_scalar(self.value)
            if not self.source_record_ids and not self.calculation_id:
                raise ValueError(
                    "AVAILABLE feature requires source_record_ids or calculation_id"
                )
        else:
            if self.value is not None:
                raise ValueError(f"{self.status} feature must not carry a value")

        if self.unit is not None:
            _require_text(self.unit, "feature unit")
        if self.calculation_id is not None:
            _require_text(self.calculation_id, "calculation_id")

        seen: set[str] = set()
        for record_id in self.source_record_ids:
            clean = _require_text(record_id, "source_record_id")
            if clean in seen:
                raise ValueError(f"duplicate source_record_id: {clean}")
            seen.add(clean)

    def to_dict(self) -> dict[str, Any]:
        self.validate()
        return {
            "name": self.name,
            "status": self.status,
            "value": self.value,
            "unit": self.unit,
            "source_record_ids": sorted(self.source_record_ids),
            "calculation_id": self.calculation_id,
        }

    @classmethod
    def from_dict(cls, row: Mapping[str, Any]) -> "FeatureValue":
        feature = cls(
            name=str(row["name"]),
            status=str(row["status"]),
            value=row.get("value"),
            unit=row.get("unit"),
            source_record_ids=tuple(row.get("source_record_ids") or ()),
            calculation_id=row.get("calculation_id"),
        )
        feature.validate()
        return feature


@dataclass(frozen=True)
class FeatureSnapshot:
    feature_snapshot_id: str
    strategy_id: str
    sleeve: str
    as_of: str
    data_snapshot_id: str
    feature_set_version: str
    implementation_version: str
    config_version: str
    features: tuple[FeatureValue, ...]

    def validate(self) -> None:
        StrategyContext(strategy_id=self.strategy_id, sleeve=self.sleeve).validate()
        _parse_aware(self.as_of, "as_of")
        for field_name, value in (
            ("feature_snapshot_id", self.feature_snapshot_id),
            ("data_snapshot_id", self.data_snapshot_id),
            ("feature_set_version", self.feature_set_version),
            ("implementation_version", self.implementation_version),
            ("config_version", self.config_version),
        ):
            _require_text(value, field_name)

        names: set[str] = set()
        for feature in self.features:
            feature.validate()
            if feature.name in names:
                raise ValueError(f"duplicate feature name: {feature.name}")
            names.add(feature.name)

    def identity_payload(self) -> dict[str, Any]:
        self.validate()
        return {
            "schema_version": FEATURE_SNAPSHOT_SCHEMA_VERSION,
            "strategy_id": self.strategy_id,
            "sleeve": self.sleeve,
            "as_of": self.as_of,
            "data_snapshot_id": self.data_snapshot_id,
            "feature_set_version": self.feature_set_version,
            "implementation_version": self.implementation_version,
            "config_version": self.config_version,
            "features": [
                feature.to_dict()
                for feature in sorted(self.features, key=lambda item: item.name)
            ],
        }

    def to_dict(self) -> dict[str, Any]:
        return {**self.identity_payload(), "feature_snapshot_id": self.feature_snapshot_id}

    def feature_map(self) -> dict[str, FeatureValue]:
        self.validate()
        return {feature.name: feature for feature in self.features}

    @classmethod
    def build(
        cls,
        *,
        strategy_id: str,
        sleeve: str,
        as_of: str,
        data_snapshot_id: str,
        feature_set_version: str,
        implementation_version: str,
        config_version: str,
        features: Iterable[FeatureValue],
    ) -> "FeatureSnapshot":
        ordered = tuple(sorted(tuple(features), key=lambda item: item.name))
        provisional = cls(
            feature_snapshot_id="pending",
            strategy_id=strategy_id,
            sleeve=sleeve,
            as_of=as_of,
            data_snapshot_id=data_snapshot_id,
            feature_set_version=feature_set_version,
            implementation_version=implementation_version,
            config_version=config_version,
            features=ordered,
        )
        identity = provisional.identity_payload()
        snapshot_id = _sha256_text(_canonical_json(identity))
        snapshot = cls(
            feature_snapshot_id=snapshot_id,
            strategy_id=strategy_id,
            sleeve=sleeve,
            as_of=as_of,
            data_snapshot_id=data_snapshot_id,
            feature_set_version=feature_set_version,
            implementation_version=implementation_version,
            config_version=config_version,
            features=ordered,
        )
        snapshot.validate()
        return snapshot

    @classmethod
    def from_dict(cls, row: Mapping[str, Any]) -> "FeatureSnapshot":
        if row.get("schema_version") != FEATURE_SNAPSHOT_SCHEMA_VERSION:
            raise ValueError("unsupported feature snapshot schema")
        snapshot = cls(
            feature_snapshot_id=str(row["feature_snapshot_id"]),
            strategy_id=str(row["strategy_id"]),
            sleeve=str(row["sleeve"]),
            as_of=str(row["as_of"]),
            data_snapshot_id=str(row["data_snapshot_id"]),
            feature_set_version=str(row["feature_set_version"]),
            implementation_version=str(row["implementation_version"]),
            config_version=str(row["config_version"]),
            features=tuple(
                FeatureValue.from_dict(item) for item in row.get("features", [])
            ),
        )
        snapshot.validate()
        expected_id = _sha256_text(_canonical_json(snapshot.identity_payload()))
        if expected_id != snapshot.feature_snapshot_id:
            raise ValueError("feature snapshot content does not match feature_snapshot_id")
        return snapshot


class FeatureSnapshotStore:
    """Immutable local reference store for deterministic feature snapshots."""

    def __init__(self, root: str | Path):
        self.root = Path(root)
        self.snapshots_dir = self.root / "feature_snapshots"

    def save(self, snapshot: FeatureSnapshot) -> FeatureSnapshot:
        snapshot.validate()
        path = self.snapshots_dir / f"{snapshot.feature_snapshot_id}.json"
        content = json.dumps(snapshot.to_dict(), ensure_ascii=False, indent=2) + "\n"
        if path.exists():
            existing = self.load(snapshot.feature_snapshot_id)
            if existing.to_dict() != snapshot.to_dict():
                raise ValueError("feature snapshot identity conflict")
        else:
            _atomic_write_text(path, content)
        return self.load(snapshot.feature_snapshot_id)

    def load(self, feature_snapshot_id: str) -> FeatureSnapshot:
        _require_text(feature_snapshot_id, "feature_snapshot_id")
        path = self.snapshots_dir / f"{feature_snapshot_id}.json"
        if not path.exists():
            raise FileNotFoundError(path)
        row = json.loads(path.read_text(encoding="utf-8"))
        return FeatureSnapshot.from_dict(row)
