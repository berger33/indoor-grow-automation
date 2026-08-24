"""Supervisor local que converte riscos físicos em corte retido."""

from __future__ import annotations

from ..domain.leak import LeakLatch
from .state_machine import ControlEvent, ControlState, LocalControlStateMachine


class LocalSafetySupervisor:
    def __init__(
        self,
        state_machine: LocalControlStateMachine,
        *,
        leak_latch: LeakLatch | None = None,
    ) -> None:
        self._machine = state_machine
        self._leak = leak_latch or LeakLatch()

    @property
    def outputs_permitted(self) -> bool:
        return self._machine.state in {
            ControlState.MANUAL,
            ControlState.BATCH,
            ControlState.IRRIGATING,
            ControlState.MAINTENANCE,
        }

    def update_leak(self, wet: bool) -> bool:
        latched = self._leak.update(wet)
        if latched and self._machine.state is not ControlState.ALARM:
            self._machine.dispatch(ControlEvent.TRIP, reason="leak_detected")
        return latched

    def reset_leak_alarm(self) -> bool:
        if self._machine.alarm_reason != "leak_detected":
            return False
        if not self._leak.reset():
            return False
        self._machine.dispatch(ControlEvent.RESET, alarm_clear=True)
        return True
