from __future__ import annotations

import hashlib
import json
import math
from dataclasses import asdict, dataclass
from typing import Any, Iterable

from src.core.strategy_boundary import (
    SHORT_MID_SLEEVE,
    SHORT_MID_STRATEGY_ID,
    require_strategy_context,
)
from src.data.adjustments import AdjustmentSeries
from src.data.benchmarks import BenchmarkSeries


RELATIVE_PERFORMANCE_SCHEMA_VERSION = "1.0"
VALID_BENCHMARK_ROLES = {"PRIMARY", "SECTOR", "PEER", "OTHER_RESEARCH"}


def _require_text(value: str, field_name: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{field_name} is required")
    return value.strip()


def _canonical_json(value: Any) -> str:
    return json.dumps(
        value,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
        allow_nan=False,
    )


def _sha256(value: Any) -> str:
    return hashlib.sha256(_canonical_json(value).encode("utf-8")).hexdigest()


def _validate_windows(values: Iterable[int]) -> tuple[int, ...]:
    windows = tuple(values)
    if any(not isinstance(value, int) or isinstance(value, bool) or value <= 0 for value in windows):
        raise ValueError("diagnostic windows must be positive integers")
    if len(set(windows)) != len(windows):
        raise ValueError("diagnostic windows must be unique")
    return tuple(sorted(windows))


@dataclass(frozen=True)
class RelativePerformancePoint:
    trade_date: str
    stock_adjusted_close: float
    benchmark_close: float
    stock_return_1d: float | None
    benchmark_return_1d: float | None
    abnormal_return_1d: float | None

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class WindowPerformance:
    sessions: int
    start_date: str
    end_date: str
    stock_return: float
    benchmark_return: float
    excess_return: float
    cumulative_abnormal_return: float

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class RelativePerformanceSeries:
    relative_performance_id: str
    schema_version: str
    strategy_id: str
    sleeve: str
    security_id: str
    benchmark_id: str
    benchmark_role: str
    benchmark_selection_contract_id: str
    adjustment_series_id: str
    benchmark_series_id: str
    start_date: str
    end_date: str
    points: tuple[RelativePerformancePoint, ...]
    windows: tuple[WindowPerformance, ...]

    def identity_payload(self) -> dict[str, Any]:
        return {
            "schema_version": self.schema_version,
            "strategy_id": self.strategy_id,
            "sleeve": self.sleeve,
            "security_id": self.security_id,
            "benchmark_id": self.benchmark_id,
            "benchmark_role": self.benchmark_role,
            "benchmark_selection_contract_id": self.benchmark_selection_contract_id,
            "adjustment_series_id": self.adjustment_series_id,
            "benchmark_series_id": self.benchmark_series_id,
            "start_date": self.start_date,
            "end_date": self.end_date,
            "points": [point.to_dict() for point in self.points],
            "windows": [window.to_dict() for window in self.windows],
        }

    def validate(self) -> None:
        if self.schema_version != RELATIVE_PERFORMANCE_SCHEMA_VERSION:
            raise ValueError("unsupported relative-performance schema")
        require_strategy_context(
            strategy_id=self.strategy_id,
            sleeve=self.sleeve,
            expected_strategy_id=SHORT_MID_STRATEGY_ID,
            expected_sleeve=SHORT_MID_SLEEVE,
        )
        _require_text(self.security_id, "security_id")
        _require_text(self.benchmark_id, "benchmark_id")
        if self.benchmark_role not in VALID_BENCHMARK_ROLES:
            raise ValueError(f"invalid benchmark_role: {self.benchmark_role}")
        _require_text(self.benchmark_selection_contract_id, "benchmark_selection_contract_id")
        _require_text(self.adjustment_series_id, "adjustment_series_id")
        _require_text(self.benchmark_series_id, "benchmark_series_id")
        if len(self.points) < 2:
            raise ValueError("relative-performance series requires at least two aligned points")
        if self.start_date != self.points[0].trade_date:
            raise ValueError("start_date must equal first point date")
        if self.end_date != self.points[-1].trade_date:
            raise ValueError("end_date must equal last point date")
        if _sha256(self.identity_payload()) != self.relative_performance_id:
            raise ValueError("relative_performance_id does not match content")

    def to_dict(self) -> dict[str, Any]:
        return {**self.identity_payload(), "relative_performance_id": self.relative_performance_id}


class RelativePerformanceBuilder:
    """Compare one adjusted stock series with one already-selected benchmark.

    This builder is intentionally Short/Mid-only. It does not select a benchmark,
    infer an event reaction window, or change Champion/ERG state. Diagnostic
    windows must be supplied explicitly by the caller and therefore become part of
    the content-addressed output identity.
    """

    def build(
        self,
        stock: AdjustmentSeries,
        benchmark: BenchmarkSeries,
        *,
        benchmark_selection_contract_id: str,
        benchmark_role: str = "PRIMARY",
        diagnostic_windows: Iterable[int] = (),
        strategy_id: str = SHORT_MID_STRATEGY_ID,
        sleeve: str = SHORT_MID_SLEEVE,
    ) -> RelativePerformanceSeries:
        stock.validate()
        benchmark.validate()
        require_strategy_context(
            strategy_id=strategy_id,
            sleeve=sleeve,
            expected_strategy_id=SHORT_MID_STRATEGY_ID,
            expected_sleeve=SHORT_MID_SLEEVE,
        )
        contract_id = _require_text(
            benchmark_selection_contract_id,
            "benchmark_selection_contract_id",
        )
        if benchmark_role not in VALID_BENCHMARK_ROLES:
            raise ValueError(f"invalid benchmark_role: {benchmark_role}")
        windows = _validate_windows(diagnostic_windows)

        stock_dates = tuple(point.trade_date for point in stock.points)
        benchmark_dates = tuple(point.trade_date for point in benchmark.points)
        if stock_dates != benchmark_dates:
            missing_benchmark = sorted(set(stock_dates) - set(benchmark_dates))
            missing_stock = sorted(set(benchmark_dates) - set(stock_dates))
            raise ValueError(
                "stock and benchmark dates must align exactly; "
                f"missing_benchmark={missing_benchmark}; missing_stock={missing_stock}"
            )

        if windows and max(windows) > len(stock.points) - 1:
            raise ValueError(
                "insufficient aligned history for requested diagnostic window: "
                f"max_window={max(windows)}, available_return_sessions={len(stock.points) - 1}"
            )

        points: list[RelativePerformancePoint] = []
        previous_stock: float | None = None
        previous_benchmark: float | None = None
        daily_abnormal: list[float | None] = []
        for stock_point, benchmark_point in zip(stock.points, benchmark.points, strict=True):
            stock_close = float(stock_point.adjusted_close)
            benchmark_close = float(benchmark_point.close)
            if not math.isfinite(stock_close) or stock_close <= 0:
                raise ValueError(f"invalid adjusted stock close on {stock_point.trade_date}")
            if not math.isfinite(benchmark_close) or benchmark_close <= 0:
                raise ValueError(f"invalid benchmark close on {benchmark_point.trade_date}")

            if previous_stock is None:
                stock_return = None
                benchmark_return = None
                abnormal = None
            else:
                stock_return = (stock_close / previous_stock) - 1.0
                benchmark_return = (benchmark_close / previous_benchmark) - 1.0  # type: ignore[operator]
                abnormal = stock_return - benchmark_return
                for name, value in (
                    ("stock_return_1d", stock_return),
                    ("benchmark_return_1d", benchmark_return),
                    ("abnormal_return_1d", abnormal),
                ):
                    if not math.isfinite(value):
                        raise ValueError(f"non-finite {name} on {stock_point.trade_date}")
                if benchmark_point.return_1d is not None:
                    if abs(benchmark_point.return_1d - benchmark_return) > 1e-12:
                        raise ValueError(
                            f"benchmark return lineage mismatch on {stock_point.trade_date}"
                        )

            points.append(
                RelativePerformancePoint(
                    trade_date=stock_point.trade_date,
                    stock_adjusted_close=stock_close,
                    benchmark_close=benchmark_close,
                    stock_return_1d=stock_return,
                    benchmark_return_1d=benchmark_return,
                    abnormal_return_1d=abnormal,
                )
            )
            daily_abnormal.append(abnormal)
            previous_stock = stock_close
            previous_benchmark = benchmark_close

        window_rows: list[WindowPerformance] = []
        for sessions in windows:
            start_index = len(points) - 1 - sessions
            start_point = points[start_index]
            end_point = points[-1]
            stock_return = (end_point.stock_adjusted_close / start_point.stock_adjusted_close) - 1.0
            benchmark_return = (end_point.benchmark_close / start_point.benchmark_close) - 1.0
            excess_return = stock_return - benchmark_return
            abnormal_values = daily_abnormal[start_index + 1 :]
            if any(value is None for value in abnormal_values):
                raise AssertionError("window abnormal returns unexpectedly contain None")
            cumulative_abnormal = sum(float(value) for value in abnormal_values)
            window_rows.append(
                WindowPerformance(
                    sessions=sessions,
                    start_date=start_point.trade_date,
                    end_date=end_point.trade_date,
                    stock_return=stock_return,
                    benchmark_return=benchmark_return,
                    excess_return=excess_return,
                    cumulative_abnormal_return=cumulative_abnormal,
                )
            )

        provisional = RelativePerformanceSeries(
            relative_performance_id="pending",
            schema_version=RELATIVE_PERFORMANCE_SCHEMA_VERSION,
            strategy_id=strategy_id,
            sleeve=sleeve,
            security_id=stock.security_id,
            benchmark_id=benchmark.benchmark_id,
            benchmark_role=benchmark_role,
            benchmark_selection_contract_id=contract_id,
            adjustment_series_id=stock.adjustment_series_id,
            benchmark_series_id=benchmark.benchmark_series_id,
            start_date=points[0].trade_date,
            end_date=points[-1].trade_date,
            points=tuple(points),
            windows=tuple(window_rows),
        )
        result = RelativePerformanceSeries(
            relative_performance_id=_sha256(provisional.identity_payload()),
            schema_version=provisional.schema_version,
            strategy_id=provisional.strategy_id,
            sleeve=provisional.sleeve,
            security_id=provisional.security_id,
            benchmark_id=provisional.benchmark_id,
            benchmark_role=provisional.benchmark_role,
            benchmark_selection_contract_id=provisional.benchmark_selection_contract_id,
            adjustment_series_id=provisional.adjustment_series_id,
            benchmark_series_id=provisional.benchmark_series_id,
            start_date=provisional.start_date,
            end_date=provisional.end_date,
            points=provisional.points,
            windows=provisional.windows,
        )
        result.validate()
        return result
