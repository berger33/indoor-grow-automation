"""Mistura periódica condicionada ao volume seguro do reservatório."""

from __future__ import annotations

import math
from dataclasses import dataclass
from datetime import datetime, timedelta
from enum import StrEnum


class MixingAction(StrEnum):
    ON = "on"
    OFF = "off"


@dataclass(frozen=True, slots=True)
class MixingDecision:
    action: MixingAction
    reason: str


class PeriodicMixingController:
    def __init__(
        self,
        *,
        minimum_volume_l: float = 10,
        run_time: timedelta = timedelta(minutes=5),
        cycle_interval: timedelta = timedelta(minutes=20),
    ) -> None:
        if not math.isfinite(minimum_volume_l) or minimum_volume_l < 0:
            raise ValueError("volume mínimo inválido")
        if not timedelta(seconds=10) <= run_time < cycle_interval <= timedelta(hours=6):
            raise ValueError("tempos de mistura inválidos")
        self._minimum_volume_l = minimum_volume_l
        self._run_time = run_time
        self._cycle_interval = cycle_interval
        self._last_started_at: datetime | None = None
        self._last_now: datetime | None = None
        self._running = False

    def evaluate(
        self,
        current_volume_l: float,
        *,
        now: datetime,
        safe_to_operate: bool = True,
    ) -> MixingDecision:
        self._validate_time(now)
        if self._last_now is not None and now < self._last_now:
            raise ValueError("avaliações de mistura devem ser monotônicas")
        self._last_now = now
        if not math.isfinite(current_volume_l) or current_volume_l < 0:
            raise ValueError("volume atual inválido")
        if not safe_to_operate:
            self._running = False
            return MixingDecision(MixingAction.OFF, "safety_interlock")
        if current_volume_l <= self._minimum_volume_l:
            self._running = False
            return MixingDecision(MixingAction.OFF, "insufficient_volume")
        if self._running:
            if now - self._last_started_at < self._run_time:  # type: ignore[operator]
                return MixingDecision(MixingAction.ON, "active_cycle")
            self._running = False
            return MixingDecision(MixingAction.OFF, "run_time_complete")
        if (
            self._last_started_at is None
            or now - self._last_started_at >= self._cycle_interval
        ):
            self._last_started_at = now
            self._running = True
            return MixingDecision(MixingAction.ON, "cycle_due")
        return MixingDecision(MixingAction.OFF, "waiting_next_cycle")

    @staticmethod
    def _validate_time(value: datetime) -> None:
        if value.tzinfo is None or value.utcoffset() is None:
            raise ValueError("now deve conter timezone")
