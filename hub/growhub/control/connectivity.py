"""Heartbeat do hub e política segura quando a rede desaparece."""

from __future__ import annotations

from datetime import datetime, timedelta
from enum import StrEnum

from .state_machine import ControlState


class HubLinkState(StrEnum):
    ONLINE = "online"
    DEGRADED = "degraded"
    LOST = "lost"


class HubLossAction(StrEnum):
    REJECT_REMOTE_COMMANDS = "reject_remote_commands"
    TRIP_LOCAL_CONTROL = "trip_local_control"


class HubHeartbeatMonitor:
    def __init__(self, *, degraded_after: timedelta, lost_after: timedelta) -> None:
        if not timedelta(seconds=1) <= degraded_after < lost_after <= timedelta(minutes=10):
            raise ValueError("janelas de heartbeat inválidas")
        self._degraded_after = degraded_after
        self._lost_after = lost_after
        self._last_seen: datetime | None = None
        self._last_sequence = -1

    def observe(self, sequence: int, *, now: datetime) -> None:
        self._validate_time(now)
        if isinstance(sequence, bool) or not isinstance(sequence, int) or sequence < 0:
            raise ValueError("sequence deve ser inteiro não negativo")
        if sequence <= self._last_sequence:
            raise ValueError("heartbeat repetido ou fora de ordem")
        if self._last_seen is not None and now < self._last_seen:
            raise ValueError("heartbeat deve ser monotônico")
        self._last_sequence = sequence
        self._last_seen = now

    def state(self, *, now: datetime) -> HubLinkState:
        self._validate_time(now)
        if self._last_seen is None:
            return HubLinkState.LOST
        if now < self._last_seen:
            raise ValueError("now não pode anteceder heartbeat")
        age = now - self._last_seen
        if age >= self._lost_after:
            return HubLinkState.LOST
        if age >= self._degraded_after:
            return HubLinkState.DEGRADED
        return HubLinkState.ONLINE

    def loss_action(self, control_state: ControlState) -> HubLossAction:
        if control_state in {
            ControlState.MANUAL,
            ControlState.BATCH,
            ControlState.IRRIGATING,
            ControlState.MAINTENANCE,
        }:
            return HubLossAction.TRIP_LOCAL_CONTROL
        return HubLossAction.REJECT_REMOTE_COMMANDS

    @staticmethod
    def _validate_time(value: datetime) -> None:
        if value.tzinfo is None or value.utcoffset() is None:
            raise ValueError("timestamp deve conter timezone")
