"""Persistência local atômica para agendas e overrides de tomadas."""

from __future__ import annotations

import json
import os
from datetime import datetime, time
from pathlib import Path

from ..domain.remote_lighting import (
    LightState,
    ManualLightOverride,
    RemoteLightSchedule,
)

SCHEMA_VERSION = 1


class FileLightingStore:
    """Bootstrap durável; o adaptador PostgreSQL reutilizará o mesmo contrato."""

    def __init__(self, path: Path) -> None:
        if not path.name:
            raise ValueError("caminho de persistência inválido")
        self._path = path

    def save(
        self,
        schedules: tuple[RemoteLightSchedule, ...],
        overrides: dict[str, ManualLightOverride],
    ) -> None:
        ids = [schedule.entity_id for schedule in schedules]
        if not schedules or len(ids) != len(set(ids)):
            raise ValueError("agendas devem ser não vazias e únicas")
        unknown = set(overrides) - set(ids)
        if unknown:
            raise ValueError(f"override de tomada desconhecida: {sorted(unknown)}")
        payload = {
            "schema_version": SCHEMA_VERSION,
            "schedules": [self._schedule_to_dict(item) for item in schedules],
            "overrides": {
                entity_id: {
                    "state": override.state.value,
                    "expires_at": override.expires_at.isoformat(),
                }
                for entity_id, override in sorted(overrides.items())
            },
        }
        self._path.parent.mkdir(parents=True, exist_ok=True)
        temporary = self._path.with_name(f".{self._path.name}.tmp")
        temporary.write_text(
            json.dumps(payload, ensure_ascii=False, sort_keys=True, separators=(",", ":")),
            encoding="utf-8",
        )
        os.replace(temporary, self._path)

    def load(
        self,
    ) -> tuple[tuple[RemoteLightSchedule, ...], dict[str, ManualLightOverride]]:
        try:
            payload = json.loads(self._path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as exc:
            raise ValueError("persistência de tomadas ausente ou inválida") from exc
        if not isinstance(payload, dict) or payload.get("schema_version") != SCHEMA_VERSION:
            raise ValueError("schema de persistência de tomadas incompatível")
        raw_schedules = payload.get("schedules")
        raw_overrides = payload.get("overrides")
        if not isinstance(raw_schedules, list) or not isinstance(raw_overrides, dict):
            raise ValueError("estrutura de persistência de tomadas inválida")
        try:
            schedules = tuple(self._schedule_from_dict(item) for item in raw_schedules)
            overrides = {
                entity_id: ManualLightOverride(
                    state=LightState(item["state"]),
                    expires_at=datetime.fromisoformat(item["expires_at"]),
                )
                for entity_id, item in raw_overrides.items()
            }
        except (KeyError, TypeError, ValueError) as exc:
            raise ValueError("dados persistidos de tomadas inválidos") from exc
        ids = [schedule.entity_id for schedule in schedules]
        if not schedules or len(ids) != len(set(ids)) or set(overrides) - set(ids):
            raise ValueError("agendas persistidas inconsistentes")
        return schedules, overrides

    @staticmethod
    def _schedule_to_dict(schedule: RemoteLightSchedule) -> dict[str, object]:
        return {
            "entity_id": schedule.entity_id,
            "on_time": schedule.on_time.isoformat(),
            "off_time": schedule.off_time.isoformat(),
            "weekdays": sorted(schedule.weekdays),
            "timezone": schedule.timezone,
            "enabled": schedule.enabled,
        }

    @staticmethod
    def _schedule_from_dict(item: object) -> RemoteLightSchedule:
        if not isinstance(item, dict):
            raise ValueError("agenda persistida inválida")
        return RemoteLightSchedule(
            entity_id=item["entity_id"],
            on_time=time.fromisoformat(item["on_time"]),
            off_time=time.fromisoformat(item["off_time"]),
            weekdays=frozenset(item["weekdays"]),
            timezone=item["timezone"],
            enabled=item["enabled"],
        )
