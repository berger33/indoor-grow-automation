"""Watchdog local e motivo estável para o próximo registro de boot."""

from __future__ import annotations

from datetime import datetime, timedelta
from enum import StrEnum


class ResetReason(StrEnum):
    POWER_ON = "power_on"
    WATCHDOG = "watchdog"
    BROWNOUT = "brownout"
    SOFTWARE = "software"
    UNKNOWN = "unknown"


class LocalWatchdog:
    def __init__(self, *, timeout: timedelta) -> None:
        if not timedelta(milliseconds=100) <= timeout <= timedelta(minutes=5):
            raise ValueError("timeout deve estar entre 100 ms e 5 min")
        self._timeout = timeout
        self._last_feed: datetime | None = None
        self._tripped = False

    @property
    def tripped(self) -> bool:
        return self._tripped

    @property
    def reset_reason(self) -> ResetReason | None:
        return ResetReason.WATCHDOG if self._tripped else None

    def feed(self, *, now: datetime) -> None:
        self._validate_time(now)
        if self._tripped:
            raise PermissionError("watchdog disparado exige reinicialização")
        if self._last_feed is not None and now < self._last_feed:
            raise ValueError("alimentação do watchdog deve ser monotônica")
        self._last_feed = now

    def healthy(self, *, now: datetime) -> bool:
        self._validate_time(now)
        if self._tripped:
            return False
        if self._last_feed is None:
            return False
        if now < self._last_feed:
            raise ValueError("now não pode anteceder a última alimentação")
        if now - self._last_feed >= self._timeout:
            self._tripped = True
            return False
        return True

    @staticmethod
    def _validate_time(value: datetime) -> None:
        if value.tzinfo is None or value.utcoffset() is None:
            raise ValueError("timestamp deve conter timezone")
