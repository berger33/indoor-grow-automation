"""Executa reconciliação periódica das tomadas com backoff limitado."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Protocol

from ..domain.remote_lighting import ManualLightOverride, RemoteLightSchedule
from .remote_lighting import LightingReconciler, ReconciliationResult, SwitchClient


class LightingStore(Protocol):
    def load(
        self,
    ) -> tuple[tuple[RemoteLightSchedule, ...], dict[str, ManualLightOverride]]: ...

    def save(
        self,
        schedules: tuple[RemoteLightSchedule, ...],
        overrides: dict[str, ManualLightOverride],
    ) -> None: ...


@dataclass(frozen=True, slots=True)
class LightingLoopSnapshot:
    attempted: bool
    next_due_at: datetime
    consecutive_failures: int
    results: tuple[ReconciliationResult, ...] = ()
    error: str | None = None


class LightingReconciliationLoop:
    def __init__(
        self,
        client: SwitchClient,
        store: LightingStore,
        *,
        normal_interval: timedelta = timedelta(seconds=30),
        initial_backoff: timedelta = timedelta(seconds=5),
        maximum_backoff: timedelta = timedelta(minutes=5),
    ) -> None:
        if not timedelta(seconds=5) <= normal_interval <= timedelta(minutes=10):
            raise ValueError("intervalo normal inválido")
        if not timedelta(seconds=1) <= initial_backoff <= maximum_backoff:
            raise ValueError("backoff inicial inválido")
        if maximum_backoff > timedelta(hours=1):
            raise ValueError("backoff máximo inválido")
        self._client = client
        self._store = store
        self._normal_interval = normal_interval
        self._initial_backoff = initial_backoff
        self._maximum_backoff = maximum_backoff
        self._next_due_at: datetime | None = None
        self._last_now: datetime | None = None
        self._failures = 0
        self._last_results: tuple[ReconciliationResult, ...] = ()

    def run_once(self, *, now: datetime) -> LightingLoopSnapshot:
        self._validate_monotonic(now)
        if self._next_due_at is not None and now < self._next_due_at:
            return LightingLoopSnapshot(
                attempted=False,
                next_due_at=self._next_due_at,
                consecutive_failures=self._failures,
                results=self._last_results,
            )
        schedules, overrides = self._store.load()
        active_overrides = {
            entity_id: override
            for entity_id, override in overrides.items()
            if now < override.expires_at
        }
        if active_overrides != overrides:
            self._store.save(schedules, active_overrides)
        try:
            results = LightingReconciler(self._client, schedules).reconcile(
                now=now,
                overrides=active_overrides,
            )
        except (ConnectionError, TimeoutError, ValueError):
            self._failures += 1
            delay_seconds = self._initial_backoff.total_seconds() * 2 ** (
                self._failures - 1
            )
            delay = min(timedelta(seconds=delay_seconds), self._maximum_backoff)
            self._next_due_at = now + delay
            return LightingLoopSnapshot(
                attempted=True,
                next_due_at=self._next_due_at,
                consecutive_failures=self._failures,
                results=self._last_results,
                error="home_assistant_unavailable",
            )
        self._failures = 0
        self._last_results = results
        self._next_due_at = now + self._normal_interval
        return LightingLoopSnapshot(
            attempted=True,
            next_due_at=self._next_due_at,
            consecutive_failures=0,
            results=results,
        )

    def _validate_monotonic(self, value: datetime) -> None:
        if value.tzinfo is None or value.utcoffset() is None:
            raise ValueError("now deve conter timezone")
        if self._last_now is not None and value < self._last_now:
            raise ValueError("execuções da reconciliação devem ser monotônicas")
        self._last_now = value
