"""Drenagem por boia com espera, timeout e pós-tempo controlados."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta
from enum import StrEnum


class DrainState(StrEnum):
    IDLE = "idle"
    CONFIRM_DELAY = "confirm_delay"
    PUMPING = "pumping"
    POST_RUN = "post_run"
    ALARM = "alarm"


class DrainAction(StrEnum):
    PUMP_ON = "pump_on"
    PUMP_OFF = "pump_off"


@dataclass(frozen=True, slots=True)
class DrainDecision:
    state: DrainState
    action: DrainAction
    reason: str


class DrainController:
    def __init__(
        self,
        *,
        confirmation_delay: timedelta = timedelta(seconds=30),
        maximum_pump_time: timedelta = timedelta(minutes=8),
        post_run_time: timedelta = timedelta(minutes=1),
    ) -> None:
        if not timedelta(seconds=1) <= confirmation_delay <= timedelta(minutes=5):
            raise ValueError("espera de confirmação inválida")
        if not timedelta(seconds=10) <= maximum_pump_time <= timedelta(minutes=30):
            raise ValueError("timeout de drenagem inválido")
        if not timedelta(seconds=1) <= post_run_time <= timedelta(minutes=5):
            raise ValueError("pós-tempo inválido")
        self._confirmation_delay = confirmation_delay
        self._maximum_pump_time = maximum_pump_time
        self._post_run_time = post_run_time
        self._state = DrainState.IDLE
        self._state_started_at: datetime | None = None
        self._pump_started_at: datetime | None = None
        self._last_now: datetime | None = None

    @property
    def state(self) -> DrainState:
        return self._state

    def evaluate(
        self,
        basin_full: bool,
        *,
        now: datetime,
        safe_to_operate: bool = True,
    ) -> DrainDecision:
        self._validate_monotonic(now)
        if self._state is DrainState.ALARM:
            return DrainDecision(self._state, DrainAction.PUMP_OFF, "latched_alarm")
        if not safe_to_operate:
            self._state = DrainState.ALARM
            return DrainDecision(self._state, DrainAction.PUMP_OFF, "safety_interlock")
        if self._state is DrainState.IDLE:
            if not basin_full:
                return DrainDecision(self._state, DrainAction.PUMP_OFF, "basin_empty")
            self._state = DrainState.CONFIRM_DELAY
            self._state_started_at = now
            return DrainDecision(self._state, DrainAction.PUMP_OFF, "full_detected")
        if self._state is DrainState.CONFIRM_DELAY:
            if not basin_full:
                self._state = DrainState.IDLE
                return DrainDecision(self._state, DrainAction.PUMP_OFF, "full_cleared")
            if now - self._state_started_at < self._confirmation_delay:  # type: ignore[operator]
                return DrainDecision(self._state, DrainAction.PUMP_OFF, "confirming_full")
            self._state = DrainState.PUMPING
            self._pump_started_at = now
            return DrainDecision(self._state, DrainAction.PUMP_ON, "drain_started")
        if self._pump_started_at is not None and now - self._pump_started_at >= self._maximum_pump_time:
            self._state = DrainState.ALARM
            return DrainDecision(self._state, DrainAction.PUMP_OFF, "drain_timeout")
        if self._state is DrainState.PUMPING:
            if basin_full:
                return DrainDecision(self._state, DrainAction.PUMP_ON, "draining")
            self._state = DrainState.POST_RUN
            self._state_started_at = now
            return DrainDecision(self._state, DrainAction.PUMP_ON, "float_released")
        if basin_full:
            self._state = DrainState.PUMPING
            return DrainDecision(self._state, DrainAction.PUMP_ON, "basin_refilled")
        if now - self._state_started_at < self._post_run_time:  # type: ignore[operator]
            return DrainDecision(self._state, DrainAction.PUMP_ON, "post_run")
        self._state = DrainState.IDLE
        self._state_started_at = None
        self._pump_started_at = None
        return DrainDecision(self._state, DrainAction.PUMP_OFF, "drain_complete")

    def reset_alarm(self, *, basin_empty_confirmed: bool) -> None:
        if self._state is not DrainState.ALARM:
            return
        if not basin_empty_confirmed:
            raise PermissionError("boia ainda indica bacia cheia")
        self._state = DrainState.IDLE
        self._state_started_at = None
        self._pump_started_at = None

    def _validate_monotonic(self, value: datetime) -> None:
        if value.tzinfo is None or value.utcoffset() is None:
            raise ValueError("now deve conter timezone")
        if self._last_now is not None and value < self._last_now:
            raise ValueError("avaliações de dreno devem ser monotônicas")
        self._last_now = value
