"""Reconcilia agenda desejada com o estado observado das tomadas Wi-Fi."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Protocol

from ..domain.remote_lighting import (
    LightState,
    ManualLightOverride,
    RemoteLightSchedule,
    resolve_light_state,
)
from ..integrations.home_assistant import SwitchObservation


class SwitchClient(Protocol):
    def read_switch(self, entity_id: str) -> SwitchObservation: ...

    def set_switch(self, entity_id: str, *, on: bool) -> SwitchObservation: ...


@dataclass(frozen=True, slots=True)
class ReconciliationResult:
    entity_id: str
    desired: LightState
    observed: LightState
    source: str
    command_sent: bool
    confirmed: bool


class LightingReconciler:
    def __init__(
        self,
        client: SwitchClient,
        schedules: tuple[RemoteLightSchedule, ...],
    ) -> None:
        ids = [schedule.entity_id for schedule in schedules]
        if not schedules:
            raise ValueError("ao menos uma tomada deve ser configurada")
        if len(ids) != len(set(ids)):
            raise ValueError("entity_id duplicada")
        self._client = client
        self._schedules = schedules

    def reconcile(
        self,
        *,
        now: datetime,
        overrides: dict[str, ManualLightOverride] | None = None,
    ) -> tuple[ReconciliationResult, ...]:
        if now.tzinfo is None or now.utcoffset() is None:
            raise ValueError("now deve conter timezone")
        override_map = overrides or {}
        unknown = set(override_map) - {item.entity_id for item in self._schedules}
        if unknown:
            raise ValueError(f"override de tomada desconhecida: {sorted(unknown)}")
        results = []
        for schedule in self._schedules:
            desired = resolve_light_state(
                schedule,
                now,
                override_map.get(schedule.entity_id),
            )
            first = self._client.read_switch(schedule.entity_id)
            observed = LightState.ON if first.is_on else LightState.OFF
            command_sent = observed is not desired.state
            if command_sent:
                confirmation = self._client.set_switch(
                    schedule.entity_id,
                    on=desired.state is LightState.ON,
                )
                observed = LightState.ON if confirmation.is_on else LightState.OFF
            results.append(
                ReconciliationResult(
                    entity_id=schedule.entity_id,
                    desired=desired.state,
                    observed=observed,
                    source=desired.source,
                    command_sent=command_sent,
                    confirmed=observed is desired.state,
                )
            )
        return tuple(results)
