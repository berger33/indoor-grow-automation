"""Caso de uso do painel para agenda e override das tomadas remotas."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import UTC, datetime, time, timedelta
from threading import Lock
from typing import Callable

from ..domain.remote_lighting import (
    LightState,
    ManualLightOverride,
    RemoteLightSchedule,
    resolve_light_state,
)
from .lighting_runtime import LightingReconciliationLoop, LightingStore, SwitchClient
from .remote_lighting import ReconciliationResult


@dataclass(frozen=True, slots=True)
class RemoteLightView:
    entity_id: str
    label: str
    desired: LightState
    observed: LightState | None
    status: str
    source: str
    schedule: RemoteLightSchedule
    override: ManualLightOverride | None
    explanation: str


@dataclass(frozen=True, slots=True)
class LightingView:
    channels: tuple[RemoteLightView, ...]
    reconciled_at: datetime | None


class LightingApplicationService:
    """Mantém a fronteira HTTP livre de detalhes do HA e da persistência."""

    def __init__(
        self,
        store: LightingStore,
        *,
        client: SwitchClient | None = None,
        clock: Callable[[], datetime] | None = None,
    ) -> None:
        self._store = store
        self._clock = clock or (lambda: datetime.now(UTC))
        self._loop = (
            LightingReconciliationLoop(client, store) if client is not None else None
        )
        self._latest: dict[str, ReconciliationResult] = {}
        self._reconciled_at: datetime | None = None
        self._lock = Lock()

    @property
    def can_reconcile(self) -> bool:
        return self._loop is not None

    def view(self) -> LightingView:
        with self._lock:
            return self._view_locked(self._clock())

    def update_schedule(
        self,
        entity_id: str,
        *,
        on_time: time,
        off_time: time,
        weekdays: frozenset[int],
        timezone: str,
        enabled: bool,
    ) -> RemoteLightView:
        with self._lock:
            schedules, overrides = self._store.load()
            if entity_id not in {item.entity_id for item in schedules}:
                raise KeyError(entity_id)
            replacement = RemoteLightSchedule(
                entity_id=entity_id,
                on_time=on_time,
                off_time=off_time,
                weekdays=weekdays,
                timezone=timezone,
                enabled=enabled,
            )
            updated = tuple(
                replacement if item.entity_id == entity_id else item
                for item in schedules
            )
            self._store.save(updated, overrides)
            return self._channel_locked(entity_id, self._clock(), updated, overrides)

    def set_override(
        self,
        entity_id: str,
        *,
        state: LightState | None,
        duration_minutes: int,
    ) -> RemoteLightView:
        if not 1 <= duration_minutes <= 1_440:
            raise ValueError("duração do override deve ficar entre 1 e 1440 minutos")
        with self._lock:
            now = self._clock()
            schedules, overrides = self._store.load()
            if entity_id not in {item.entity_id for item in schedules}:
                raise KeyError(entity_id)
            updated_overrides = dict(overrides)
            if state is None:
                updated_overrides.pop(entity_id, None)
            else:
                updated_overrides[entity_id] = ManualLightOverride(
                    state=state,
                    expires_at=now + timedelta(minutes=duration_minutes),
                )
            self._store.save(schedules, updated_overrides)
            return self._channel_locked(
                entity_id, now, schedules, updated_overrides
            )

    def reconcile_once(self) -> None:
        if self._loop is None:
            raise RuntimeError("cliente de tomadas não configurado")
        now = self._clock()
        with self._lock:
            snapshot = self._loop.run_once(now=now)
            if snapshot.attempted and snapshot.error is None:
                self._latest = {item.entity_id: item for item in snapshot.results}
                self._reconciled_at = now

    def _view_locked(self, now: datetime) -> LightingView:
        schedules, overrides = self._store.load()
        active = {
            entity_id: override
            for entity_id, override in overrides.items()
            if now < override.expires_at
        }
        if active != overrides:
            self._store.save(schedules, active)
        return LightingView(
            channels=tuple(
                self._channel_locked(item.entity_id, now, schedules, active)
                for item in schedules
            ),
            reconciled_at=self._reconciled_at,
        )

    def _channel_locked(
        self,
        entity_id: str,
        now: datetime,
        schedules: tuple[RemoteLightSchedule, ...],
        overrides: dict[str, ManualLightOverride],
    ) -> RemoteLightView:
        schedule = next(item for item in schedules if item.entity_id == entity_id)
        desired = resolve_light_state(schedule, now, overrides.get(entity_id))
        latest = self._latest.get(entity_id)
        observed = latest.observed if latest is not None else None
        if observed is None:
            status = "unavailable"
            explanation = "Aguardando confirmação do Home Assistant."
        elif observed is desired.state and latest is not None and latest.confirmed:
            status = "confirmed"
            explanation = "Estado confirmado pelo Home Assistant."
        else:
            status = "divergent"
            explanation = "Comando e estado observado ainda não coincidem."
        return RemoteLightView(
            entity_id=entity_id,
            label=entity_id.removeprefix("switch.").replace("_", " ").title(),
            desired=desired.state,
            observed=observed,
            status=status,
            source=desired.source,
            schedule=schedule,
            override=overrides.get(entity_id),
            explanation=explanation,
        )
