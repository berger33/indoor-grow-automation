"""Intertravamentos e limites independentes para dosagem química."""

from __future__ import annotations

import math
from collections import deque
from dataclasses import dataclass
from datetime import datetime, timedelta
from enum import StrEnum


class PHChannel(StrEnum):
    UP = "ph_up"
    DOWN = "ph_down"


class PHDirectionInterlock:
    def __init__(self) -> None:
        self._active: PHChannel | None = None
        self._blocked = False

    @property
    def active(self) -> PHChannel | None:
        return self._active

    def request(self, channel: PHChannel) -> None:
        if self._blocked:
            raise PermissionError("intertravamento de pH está bloqueado")
        if self._active is not None and self._active is not channel:
            self._active = None
            self._blocked = True
            raise RuntimeError("pH up e pH down jamais podem operar juntos")
        self._active = channel

    def stop(self, channel: PHChannel) -> None:
        if self._active is channel:
            self._active = None

    def reset(self) -> None:
        if self._active is not None:
            raise PermissionError("desligue os canais de pH antes do rearme")
        self._blocked = False


@dataclass(frozen=True, slots=True)
class DoseLimits:
    per_event_ml: float
    per_hour_ml: float
    per_day_ml: float

    def __post_init__(self) -> None:
        values = (self.per_event_ml, self.per_hour_ml, self.per_day_ml)
        if any(not math.isfinite(value) or value <= 0 for value in values):
            raise ValueError("limites de dose devem ser finitos e positivos")
        if not self.per_event_ml <= self.per_hour_ml <= self.per_day_ml:
            raise ValueError("limites devem crescer de evento para hora e dia")


@dataclass(frozen=True, slots=True)
class DoseDecision:
    allowed: bool
    reason: str


class DoseBudget:
    def __init__(self, limits: DoseLimits) -> None:
        self._limits = limits
        self._events: deque[tuple[datetime, float]] = deque()

    def request(self, volume_ml: float, *, now: datetime) -> DoseDecision:
        if now.tzinfo is None or now.utcoffset() is None:
            raise ValueError("now deve conter timezone")
        if not math.isfinite(volume_ml) or volume_ml <= 0:
            raise ValueError("volume_ml deve ser finito e positivo")
        if self._events and now < self._events[-1][0]:
            raise ValueError("eventos de dose devem ser monotônicos")
        self._expire(now)
        if volume_ml > self._limits.per_event_ml:
            return DoseDecision(False, "event_limit")
        hour_total = sum(
            volume for at, volume in self._events if now - at < timedelta(hours=1)
        )
        if hour_total + volume_ml > self._limits.per_hour_ml:
            return DoseDecision(False, "hour_limit")
        day_total = sum(volume for _, volume in self._events)
        if day_total + volume_ml > self._limits.per_day_ml:
            return DoseDecision(False, "day_limit")
        self._events.append((now, volume_ml))
        return DoseDecision(True, "within_limits")

    def _expire(self, now: datetime) -> None:
        while self._events and now - self._events[0][0] >= timedelta(days=1):
            self._events.popleft()
