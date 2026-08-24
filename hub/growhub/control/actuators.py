"""Guardas locais de tempo para atuadores energizados."""

from __future__ import annotations

from datetime import datetime, timedelta


class ActuatorTimeoutGuard:
    def __init__(self, *, maximum_on: timedelta) -> None:
        if not timedelta(milliseconds=1) <= maximum_on <= timedelta(hours=24):
            raise ValueError("maximum_on deve estar entre 1 ms e 24 h")
        self._maximum_on = maximum_on
        self._started_at: datetime | None = None
        self._timed_out = False

    @property
    def commanded_on(self) -> bool:
        return self._started_at is not None and not self._timed_out

    @property
    def timed_out(self) -> bool:
        return self._timed_out

    def start(self, *, now: datetime) -> None:
        self._validate_time(now)
        if self._timed_out:
            raise PermissionError("timeout retido exige rearme")
        if self._started_at is None:
            self._started_at = now

    def stop(self) -> None:
        self._started_at = None

    def evaluate(self, *, now: datetime) -> bool:
        self._validate_time(now)
        if self._started_at is None or self._timed_out:
            return False
        if now < self._started_at:
            raise ValueError("now não pode anteceder o acionamento")
        if now - self._started_at < self._maximum_on:
            return True
        self._started_at = None
        self._timed_out = True
        return False

    def reset(self) -> None:
        if self._started_at is not None:
            raise PermissionError("desligue o atuador antes do rearme")
        self._timed_out = False

    @staticmethod
    def _validate_time(value: datetime) -> None:
        if value.tzinfo is None or value.utcoffset() is None:
            raise ValueError("timestamp deve conter timezone")
