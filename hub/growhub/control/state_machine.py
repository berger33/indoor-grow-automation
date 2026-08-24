"""Máquina de estados local com alarme retido e transições explícitas."""

from __future__ import annotations

import re
from enum import StrEnum

REASON = re.compile(r"^[a-z][a-z0-9_-]{0,63}$")


class ControlState(StrEnum):
    BOOT = "boot"
    IDLE = "idle"
    MANUAL = "manual"
    BATCH = "batch"
    ALARM = "alarm"


class ControlEvent(StrEnum):
    BOOT_COMPLETE = "boot_complete"
    START_MANUAL = "start_manual"
    START_BATCH = "start_batch"
    STOP = "stop"
    TRIP = "trip"
    RESET = "reset"


TRANSITIONS = {
    (ControlState.BOOT, ControlEvent.BOOT_COMPLETE): ControlState.IDLE,
    (ControlState.IDLE, ControlEvent.START_MANUAL): ControlState.MANUAL,
    (ControlState.IDLE, ControlEvent.START_BATCH): ControlState.BATCH,
    (ControlState.MANUAL, ControlEvent.STOP): ControlState.IDLE,
    (ControlState.BATCH, ControlEvent.STOP): ControlState.IDLE,
}


class LocalControlStateMachine:
    def __init__(self) -> None:
        self._state = ControlState.BOOT
        self._alarm_reason: str | None = None

    @property
    def state(self) -> ControlState:
        return self._state

    @property
    def alarm_reason(self) -> str | None:
        return self._alarm_reason

    def dispatch(
        self,
        event: ControlEvent,
        *,
        reason: str | None = None,
        alarm_clear: bool = False,
    ) -> ControlState:
        if event is ControlEvent.TRIP:
            if not reason or not REASON.fullmatch(reason):
                raise ValueError("trip exige motivo estável")
            self._state = ControlState.ALARM
            self._alarm_reason = reason
            return self._state
        if self._state is ControlState.ALARM:
            if event is not ControlEvent.RESET:
                return self._state
            if not alarm_clear:
                raise PermissionError("alarme físico ainda não foi liberado")
            self._state = ControlState.IDLE
            self._alarm_reason = None
            return self._state
        try:
            self._state = TRANSITIONS[(self._state, event)]
        except KeyError as exc:
            raise ValueError(
                f"transição inválida: {self._state.value}+{event.value}"
            ) from exc
        return self._state
