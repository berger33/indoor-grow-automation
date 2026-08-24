"""Agenda lógica de tomadas Wi-Fi; nenhuma carga é acionada pelo ESP32."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, time, timedelta
from enum import StrEnum
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError


class LightState(StrEnum):
    OFF = "off"
    ON = "on"


@dataclass(frozen=True, slots=True)
class RemoteLightSchedule:
    entity_id: str
    on_time: time
    off_time: time
    weekdays: frozenset[int]
    timezone: str = "America/Sao_Paulo"
    enabled: bool = True

    def __post_init__(self) -> None:
        if not self.entity_id.startswith("switch.") or len(self.entity_id) < 8:
            raise ValueError("entity_id deve identificar uma entidade switch")
        if self.on_time == self.off_time:
            raise ValueError("on_time e off_time não podem ser iguais")
        if not self.weekdays or any(
            isinstance(day, bool) or not 0 <= day <= 6 for day in self.weekdays
        ):
            raise ValueError("weekdays deve conter dias entre 0 e 6")
        try:
            ZoneInfo(self.timezone)
        except ZoneInfoNotFoundError as exc:
            raise ValueError("timezone IANA inválido") from exc

    def desired_at(self, instant: datetime) -> LightState:
        if instant.tzinfo is None:
            raise ValueError("instant deve incluir fuso horário")
        if not self.enabled:
            return LightState.OFF
        local = instant.astimezone(ZoneInfo(self.timezone))
        local_time = local.timetz().replace(tzinfo=None)
        if self.on_time < self.off_time:
            active = (
                local.weekday() in self.weekdays
                and self.on_time <= local_time < self.off_time
            )
        elif local_time >= self.on_time:
            active = local.weekday() in self.weekdays
        elif local_time < self.off_time:
            previous_day = (local - timedelta(days=1)).weekday()
            active = previous_day in self.weekdays
        else:
            active = False
        return LightState.ON if active else LightState.OFF


@dataclass(frozen=True, slots=True)
class ManualLightOverride:
    state: LightState
    expires_at: datetime

    def __post_init__(self) -> None:
        if self.expires_at.tzinfo is None:
            raise ValueError("expires_at deve incluir fuso horário")


@dataclass(frozen=True, slots=True)
class DesiredLightState:
    state: LightState
    source: str


def resolve_light_state(
    schedule: RemoteLightSchedule,
    instant: datetime,
    override: ManualLightOverride | None = None,
) -> DesiredLightState:
    if instant.tzinfo is None:
        raise ValueError("instant deve incluir fuso horário")
    if override is not None and instant < override.expires_at:
        return DesiredLightState(override.state, "manual_override")
    return DesiredLightState(schedule.desired_at(instant), "schedule")
