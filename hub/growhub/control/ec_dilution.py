"""Diluição controlada por EC com limite de volume e timeout absoluto."""

from __future__ import annotations

import math
from dataclasses import dataclass
from datetime import datetime, timedelta
from enum import StrEnum


class DilutionState(StrEnum):
    IDLE = "idle"
    RUNNING = "running"
    COMPLETE = "complete"
    ALARM = "alarm"


class DilutionAction(StrEnum):
    HOLD = "hold"
    WATER_ON = "water_on"
    WATER_OFF = "water_off"


@dataclass(frozen=True, slots=True)
class DilutionDecision:
    state: DilutionState
    action: DilutionAction
    reason: str


class ECDilutionController:
    def __init__(
        self,
        *,
        target_ec_ms_cm: float,
        maximum_volume_l: float,
        reserve_l: float = 5,
        timeout: timedelta = timedelta(minutes=8),
    ) -> None:
        values = (target_ec_ms_cm, maximum_volume_l, reserve_l)
        if any(not math.isfinite(value) for value in values):
            raise ValueError("configuração de diluição deve ser finita")
        if not 0.5 <= target_ec_ms_cm <= 2.5:
            raise ValueError("EC alvo deve estar entre 0,5 e 2,5 mS/cm")
        if maximum_volume_l <= reserve_l or reserve_l < 0:
            raise ValueError("volume máximo deve superar a reserva")
        if not timedelta(seconds=10) <= timeout <= timedelta(minutes=30):
            raise ValueError("timeout de diluição inválido")
        self._target = target_ec_ms_cm
        self._limit = maximum_volume_l - reserve_l
        self._timeout = timeout
        self._started_at: datetime | None = None
        self._last_now: datetime | None = None
        self._state = DilutionState.IDLE

    @property
    def state(self) -> DilutionState:
        return self._state

    def start(self, *, now: datetime) -> None:
        self._validate_time(now)
        if self._state is DilutionState.RUNNING:
            raise PermissionError("diluição já está em execução")
        self._started_at = now
        self._last_now = now
        self._state = DilutionState.RUNNING

    def evaluate(
        self,
        ec_ms_cm: float,
        current_volume_l: float,
        *,
        now: datetime,
        reading_valid: bool,
        reading_stable: bool,
    ) -> DilutionDecision:
        self._validate_monotonic(now)
        if self._state is DilutionState.IDLE or self._started_at is None:
            raise PermissionError("diluição não iniciada")
        if self._state is not DilutionState.RUNNING:
            return DilutionDecision(self._state, DilutionAction.HOLD, "terminal_state")
        if not math.isfinite(ec_ms_cm) or not 0 <= ec_ms_cm <= 20:
            raise ValueError("EC fora do envelope físico")
        if not math.isfinite(current_volume_l) or current_volume_l < 0:
            raise ValueError("volume atual inválido")
        if not reading_valid or not reading_stable:
            return DilutionDecision(
                self._state,
                DilutionAction.WATER_OFF,
                "ec_invalid_or_unstable",
            )
        if ec_ms_cm <= self._target:
            self._state = DilutionState.COMPLETE
            return DilutionDecision(self._state, DilutionAction.WATER_OFF, "target_reached")
        if current_volume_l >= self._limit:
            self._state = DilutionState.ALARM
            return DilutionDecision(self._state, DilutionAction.WATER_OFF, "volume_limit")
        if now - self._started_at >= self._timeout:
            self._state = DilutionState.ALARM
            return DilutionDecision(self._state, DilutionAction.WATER_OFF, "timeout")
        return DilutionDecision(
            self._state,
            DilutionAction.WATER_ON,
            "ec_above_target",
        )

    def _validate_monotonic(self, value: datetime) -> None:
        self._validate_time(value)
        if self._last_now is not None and value < self._last_now:
            raise ValueError("tempo da diluição deve ser monotônico")
        self._last_now = value

    @staticmethod
    def _validate_time(value: datetime) -> None:
        if value.tzinfo is None or value.utcoffset() is None:
            raise ValueError("timestamp deve conter timezone")
