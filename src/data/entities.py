from __future__ import annotations

import math
import re
from dataclasses import asdict, dataclass
from datetime import date
from typing import Any, ClassVar, Mapping


_SECURITY_ID_RE = re.compile(r"^\d{6}$")


def _require_text(value: str, field_name: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{field_name} is required")
    return value.strip()


def _validate_security_id(value: str) -> None:
    if not _SECURITY_ID_RE.match(str(value)):
        raise ValueError(f"security_id must be six numeric digits: {value!r}")


def _validate_date(value: str | None, field_name: str, *, required: bool = False) -> None:
    if value is None:
        if required:
            raise ValueError(f"{field_name} is required")
        return
    try:
        date.fromisoformat(value)
    except Exception as exc:
        raise ValueError(f"{field_name} must be YYYY-MM-DD") from exc


def _finite(value: float | int | None, field_name: str, *, allow_none: bool = False) -> None:
    if value is None:
        if allow_none:
            return
        raise ValueError(f"{field_name} is required")
    if not isinstance(value, (int, float)) or isinstance(value, bool) or not math.isfinite(float(value)):
        raise ValueError(f"{field_name} must be a finite number")


def _validate_date_order(start: str, end: str | None, start_name: str, end_name: str) -> None:
    _validate_date(start, start_name, required=True)
    _validate_date(end, end_name)
    if end is not None and date.fromisoformat(end) < date.fromisoformat(start):
        raise ValueError(f"{end_name} cannot precede {start_name}")


class EntityMixin:
    entity_type: ClassVar[str]

    def validate(self) -> None:
        raise NotImplementedError

    def record_id(self) -> str:
        raise NotImplementedError

    def to_payload(self) -> dict[str, Any]:
        self.validate()
        return asdict(self)


@dataclass(frozen=True)
class SecurityMaster(EntityMixin):
    entity_type: ClassVar[str] = "SECURITY_MASTER"

    security_id: str
    exchange: str
    name: str
    security_type: str = "A_SHARE"
    board: str | None = None
    listing_date: str | None = None
    delisting_date: str | None = None
    currency: str = "CNY"

    def validate(self) -> None:
        _validate_security_id(self.security_id)
        _require_text(self.exchange, "exchange")
        _require_text(self.name, "name")
        _require_text(self.security_type, "security_type")
        _require_text(self.currency, "currency")
        _validate_date(self.listing_date, "listing_date")
        _validate_date(self.delisting_date, "delisting_date")
        if self.listing_date and self.delisting_date:
            if date.fromisoformat(self.delisting_date) < date.fromisoformat(self.listing_date):
                raise ValueError("delisting_date cannot precede listing_date")

    def record_id(self) -> str:
        self.validate()
        return f"SECURITY_MASTER:{self.security_id}"


@dataclass(frozen=True)
class DailyBar(EntityMixin):
    entity_type: ClassVar[str] = "DAILY_BAR"

    security_id: str
    trade_date: str
    open: float
    high: float
    low: float
    close: float
    prev_close: float | None
    volume: float
    turnover: float
    currency: str = "CNY"
    price_basis: str = "UNADJUSTED"
    suspended: bool = False

    def validate(self) -> None:
        _validate_security_id(self.security_id)
        _validate_date(self.trade_date, "trade_date", required=True)
        for name in ("open", "high", "low", "close"):
            _finite(getattr(self, name), name)
            if getattr(self, name) <= 0:
                raise ValueError(f"{name} must be > 0")
        _finite(self.prev_close, "prev_close", allow_none=True)
        if self.prev_close is not None and self.prev_close <= 0:
            raise ValueError("prev_close must be > 0 when present")
        _finite(self.volume, "volume")
        _finite(self.turnover, "turnover")
        if self.volume < 0 or self.turnover < 0:
            raise ValueError("volume/turnover cannot be negative")
        if self.high < max(self.open, self.close, self.low):
            raise ValueError("high must be >= open/close/low")
        if self.low > min(self.open, self.close, self.high):
            raise ValueError("low must be <= open/close/high")
        if self.price_basis != "UNADJUSTED":
            raise ValueError("canonical DAILY_BAR must store UNADJUSTED prices")

    def record_id(self) -> str:
        self.validate()
        return f"DAILY_BAR:{self.security_id}:{self.trade_date}"


@dataclass(frozen=True)
class Disclosure(EntityMixin):
    entity_type: ClassVar[str] = "DISCLOSURE"

    security_id: str
    disclosure_id: str
    title: str
    category: str
    source_locator: str
    period_end: str | None = None

    def validate(self) -> None:
        _validate_security_id(self.security_id)
        _require_text(self.disclosure_id, "disclosure_id")
        _require_text(self.title, "title")
        _require_text(self.category, "category")
        _require_text(self.source_locator, "source_locator")
        _validate_date(self.period_end, "period_end")

    def record_id(self) -> str:
        self.validate()
        return f"DISCLOSURE:{self.security_id}:{self.disclosure_id}"


@dataclass(frozen=True)
class FinancialStatement(EntityMixin):
    entity_type: ClassVar[str] = "FINANCIAL_STATEMENT"

    security_id: str
    period_end: str
    report_type: str
    statement_scope: str
    metrics: Mapping[str, float | int | None]
    currency: str = "CNY"
    unit_scale: float = 1.0
    audit_status: str | None = None

    def validate(self) -> None:
        _validate_security_id(self.security_id)
        _validate_date(self.period_end, "period_end", required=True)
        _require_text(self.report_type, "report_type")
        _require_text(self.statement_scope, "statement_scope")
        _require_text(self.currency, "currency")
        _finite(self.unit_scale, "unit_scale")
        if self.unit_scale <= 0:
            raise ValueError("unit_scale must be > 0")
        if not self.metrics:
            raise ValueError("metrics cannot be empty")
        for key, value in self.metrics.items():
            _require_text(str(key), "metric_name")
            _finite(value, f"metrics[{key}]", allow_none=True)

    def record_id(self) -> str:
        self.validate()
        return f"FINANCIAL_STATEMENT:{self.security_id}:{self.period_end}:{self.report_type}:{self.statement_scope}"

    def to_payload(self) -> dict[str, Any]:
        self.validate()
        payload = asdict(self)
        payload["metrics"] = dict(self.metrics)
        return payload


@dataclass(frozen=True)
class CompanyGuidance(EntityMixin):
    entity_type: ClassVar[str] = "GUIDANCE"

    security_id: str
    guidance_id: str
    fiscal_period: str
    metric: str
    lower: float | None = None
    upper: float | None = None
    point_estimate: float | None = None
    unit: str = "CNY"

    def validate(self) -> None:
        _validate_security_id(self.security_id)
        _require_text(self.guidance_id, "guidance_id")
        _require_text(self.fiscal_period, "fiscal_period")
        _require_text(self.metric, "metric")
        _require_text(self.unit, "unit")
        for name in ("lower", "upper", "point_estimate"):
            _finite(getattr(self, name), name, allow_none=True)
        if self.lower is None and self.upper is None and self.point_estimate is None:
            raise ValueError("guidance requires lower/upper or point_estimate")
        if self.lower is not None and self.upper is not None and self.lower > self.upper:
            raise ValueError("lower cannot exceed upper")

    def record_id(self) -> str:
        self.validate()
        return f"GUIDANCE:{self.security_id}:{self.guidance_id}:{self.metric}"


@dataclass(frozen=True)
class CorporateAction(EntityMixin):
    entity_type: ClassVar[str] = "CORPORATE_ACTION"

    security_id: str
    action_id: str
    action_type: str
    announcement_date: str
    record_date: str | None = None
    ex_date: str | None = None
    pay_date: str | None = None
    cash_per_share: float | None = None
    ratio: float | None = None
    currency: str = "CNY"

    def validate(self) -> None:
        _validate_security_id(self.security_id)
        _require_text(self.action_id, "action_id")
        _require_text(self.action_type, "action_type")
        _validate_date(self.announcement_date, "announcement_date", required=True)
        for name in ("record_date", "ex_date", "pay_date"):
            _validate_date(getattr(self, name), name)
        _finite(self.cash_per_share, "cash_per_share", allow_none=True)
        _finite(self.ratio, "ratio", allow_none=True)
        if self.cash_per_share is not None and self.cash_per_share < 0:
            raise ValueError("cash_per_share cannot be negative")
        if self.ratio is not None and self.ratio < 0:
            raise ValueError("ratio cannot be negative")

    def record_id(self) -> str:
        self.validate()
        return f"CORPORATE_ACTION:{self.security_id}:{self.action_id}"


@dataclass(frozen=True)
class IndexMembership(EntityMixin):
    entity_type: ClassVar[str] = "INDEX_MEMBERSHIP"

    security_id: str
    index_id: str
    effective_from: str
    effective_to: str | None = None
    weight: float | None = None

    def validate(self) -> None:
        _validate_security_id(self.security_id)
        _require_text(self.index_id, "index_id")
        _validate_date_order(self.effective_from, self.effective_to, "effective_from", "effective_to")
        _finite(self.weight, "weight", allow_none=True)
        if self.weight is not None and not 0 <= self.weight <= 1:
            raise ValueError("weight must be between 0 and 1")

    def record_id(self) -> str:
        self.validate()
        return f"INDEX_MEMBERSHIP:{self.index_id}:{self.security_id}:{self.effective_from}"


@dataclass(frozen=True)
class IndustryMembership(EntityMixin):
    entity_type: ClassVar[str] = "INDUSTRY_CLASSIFICATION"

    security_id: str
    taxonomy: str
    level: str
    industry_code: str
    industry_name: str
    effective_from: str
    effective_to: str | None = None

    def validate(self) -> None:
        _validate_security_id(self.security_id)
        _require_text(self.taxonomy, "taxonomy")
        _require_text(self.level, "level")
        _require_text(self.industry_code, "industry_code")
        _require_text(self.industry_name, "industry_name")
        _validate_date_order(self.effective_from, self.effective_to, "effective_from", "effective_to")

    def record_id(self) -> str:
        self.validate()
        return (
            f"INDUSTRY_CLASSIFICATION:{self.taxonomy}:{self.level}:"
            f"{self.security_id}:{self.effective_from}"
        )


@dataclass(frozen=True)
class ConsensusExpectation(EntityMixin):
    entity_type: ClassVar[str] = "CONSENSUS_EXPECTATION"

    security_id: str
    fiscal_period: str
    metric: str
    value: float
    unit: str
    baseline_type: str = "SELL_SIDE_CONSENSUS"
    coverage_count: int | None = None
    dispersion: float | None = None

    def validate(self) -> None:
        _validate_security_id(self.security_id)
        _require_text(self.fiscal_period, "fiscal_period")
        _require_text(self.metric, "metric")
        _require_text(self.unit, "unit")
        _require_text(self.baseline_type, "baseline_type")
        _finite(self.value, "value")
        _finite(self.dispersion, "dispersion", allow_none=True)
        if self.coverage_count is not None:
            if not isinstance(self.coverage_count, int) or isinstance(self.coverage_count, bool):
                raise ValueError("coverage_count must be an integer")
            if self.coverage_count < 0:
                raise ValueError("coverage_count cannot be negative")
        if self.dispersion is not None and self.dispersion < 0:
            raise ValueError("dispersion cannot be negative")

    def record_id(self) -> str:
        self.validate()
        return (
            f"CONSENSUS_EXPECTATION:{self.security_id}:"
            f"{self.fiscal_period}:{self.metric}:{self.baseline_type}"
        )
