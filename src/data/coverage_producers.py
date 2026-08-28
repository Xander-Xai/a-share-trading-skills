from __future__ import annotations

from datetime import date
from typing import Iterable

from src.core.pit_store import StoredPITRecord
from src.data.coverage import CoverageResolver, DatasetCoverage
from src.data.entities import DailyBar
from src.data.trading_calendar import TradingSession


class TradingCalendarCoverageProducer:
    """Reconcile DAILY_BAR dates against a PIT-visible exchange calendar.

    This producer does not trust calendar rows by presence alone. Before it can
    emit `CONFIRMED_COMPLETE` for a security's DAILY_BAR history, the input record
    set must itself contain a confirmed `TRADING_SESSION` coverage assertion for
    the requested exchange/date range using an accepted enumeration method.
    """

    ACCEPTED_CALENDAR_METHODS = {"EXCHANGE_CALENDAR_ENUMERATION"}

    def __init__(self, resolver: CoverageResolver | None = None):
        self.resolver = resolver or CoverageResolver()

    def evaluate(
        self,
        records: Iterable[StoredPITRecord],
        *,
        security_id: str,
        exchange: str,
        start_date: str,
        end_date: str,
        coverage_id: str,
    ) -> DatasetCoverage:
        start = date.fromisoformat(start_date)
        end = date.fromisoformat(end_date)
        if end < start:
            raise ValueError("end_date cannot precede start_date")

        materialized = tuple(records)
        calendar_resolution = self.resolver.resolve(
            materialized,
            dataset_family="TRADING_SESSION",
            requested_start=start_date,
            requested_end=end_date,
            exchange=exchange,
            accepted_methods=set(self.ACCEPTED_CALENDAR_METHODS),
        )

        bars = self._bars(materialized, security_id=security_id, exchange=exchange)
        observed_dates = {
            bar.trade_date
            for bar in bars
            if start <= date.fromisoformat(bar.trade_date) <= end
        }

        if not calendar_resolution.confirmed:
            return DatasetCoverage(
                coverage_id=coverage_id,
                dataset_family="DAILY_BAR",
                scope_type="SECURITY",
                security_id=security_id,
                exchange=exchange,
                start_date=start_date,
                end_date=end_date,
                completeness_status="UNRESOLVED",
                verification_method="TRADING_CALENDAR_RECONCILED",
                expected_count=None,
                observed_count=len(observed_dates),
                note=(
                    "calendar coverage unresolved: "
                    f"{calendar_resolution.reason}; "
                    f"calendar_method={calendar_resolution.verification_method or 'NONE'}"
                ),
            )

        sessions = self._sessions(materialized, exchange=exchange)
        expected_dates = {
            session.trade_date
            for session in sessions
            if session.is_open
            and start <= date.fromisoformat(session.trade_date) <= end
        }
        calendar_dates = {
            session.trade_date
            for session in sessions
            if start <= date.fromisoformat(session.trade_date) <= end
        }

        # Calendar coverage says the range is complete, so there must be a
        # canonical session row (open or closed) for every date represented by
        # the authoritative enumeration contract. We do not fabricate dates here;
        # any discrepancy is handled upstream when the calendar coverage assertion
        # is created.
        unexpected_bar_dates = observed_dates - expected_dates
        missing_bar_dates = expected_dates - observed_dates

        status = (
            "CONFIRMED_COMPLETE"
            if not unexpected_bar_dates and not missing_bar_dates
            else "PARTIAL"
        )
        note_parts = [
            f"calendar_assertion={calendar_resolution.assertion_ref or 'NONE'}",
            f"calendar_rows_in_range={len(calendar_dates)}",
        ]
        if missing_bar_dates:
            note_parts.append(f"missing_open_sessions={','.join(sorted(missing_bar_dates))}")
        if unexpected_bar_dates:
            note_parts.append(f"bars_on_non_open_dates={','.join(sorted(unexpected_bar_dates))}")

        coverage = DatasetCoverage(
            coverage_id=coverage_id,
            dataset_family="DAILY_BAR",
            scope_type="SECURITY",
            security_id=security_id,
            exchange=exchange,
            start_date=start_date,
            end_date=end_date,
            completeness_status=status,
            verification_method="TRADING_CALENDAR_RECONCILED",
            expected_count=len(expected_dates),
            observed_count=len(observed_dates),
            note="; ".join(note_parts),
        )
        coverage.validate()
        return coverage

    @staticmethod
    def _bars(
        records: Iterable[StoredPITRecord],
        *,
        security_id: str,
        exchange: str,
    ) -> list[DailyBar]:
        rows: list[DailyBar] = []
        seen: set[str] = set()
        for record in records:
            if record.metadata.entity_type != "DAILY_BAR":
                continue
            if record.metadata.security_id != security_id:
                continue
            if record.metadata.exchange and record.metadata.exchange != exchange:
                continue
            bar = DailyBar(**record.payload)
            bar.validate()
            if bar.security_id != security_id:
                raise ValueError("DAILY_BAR payload security_id disagrees with metadata")
            if bar.trade_date in seen:
                raise ValueError(f"duplicate DAILY_BAR trade_date: {bar.trade_date}")
            seen.add(bar.trade_date)
            rows.append(bar)
        return rows

    @staticmethod
    def _sessions(
        records: Iterable[StoredPITRecord],
        *,
        exchange: str,
    ) -> list[TradingSession]:
        rows: list[TradingSession] = []
        seen: set[str] = set()
        for record in records:
            if record.metadata.entity_type != "TRADING_SESSION":
                continue
            session = TradingSession(**record.payload)
            session.validate()
            if session.exchange != exchange:
                continue
            if session.trade_date in seen:
                raise ValueError(f"duplicate TRADING_SESSION trade_date: {session.trade_date}")
            seen.add(session.trade_date)
            rows.append(session)
        return rows
