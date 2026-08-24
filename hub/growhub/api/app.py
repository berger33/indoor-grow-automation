"""API FastAPI e hospedagem opcional do painel compilado."""

from __future__ import annotations

import asyncio
from contextlib import asynccontextmanager, suppress
from datetime import UTC, datetime, time
from pathlib import Path
from typing import AsyncIterator, Callable, Literal

from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, ConfigDict, Field

from ..domain.remote_lighting import LightState
from ..services.lighting_application import (
    LightingApplicationService,
    RemoteLightView,
)
from ..services.operations import InMemoryOperations
from ..services.realtime import RealtimeBuffer
from ..services.security import AuthService, UserRole
from .operations_router import create_operations_router


class SchedulePayload(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    on_time: time = Field(alias="onTime")
    off_time: time = Field(alias="offTime")
    weekdays: frozenset[int]
    timezone: str = "America/Sao_Paulo"
    enabled: bool = True


class OverridePayload(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    state: Literal["on", "off"] | None
    duration_minutes: int = Field(default=30, alias="durationMinutes", ge=1, le=1_440)


def _channel_payload(channel: RemoteLightView) -> dict[str, object]:
    return {
        "entityId": channel.entity_id,
        "label": channel.label,
        "desired": channel.desired.value,
        "observed": channel.observed.value if channel.observed is not None else None,
        "status": channel.status,
        "source": channel.source,
        "schedule": {
            "onTime": channel.schedule.on_time.isoformat(timespec="minutes"),
            "offTime": channel.schedule.off_time.isoformat(timespec="minutes"),
            "weekdays": sorted(channel.schedule.weekdays),
            "timezone": channel.schedule.timezone,
            "enabled": channel.schedule.enabled,
        },
        "override": (
            {
                "state": channel.override.state.value,
                "expiresAt": channel.override.expires_at.isoformat(),
            }
            if channel.override is not None
            else None
        ),
        "explanation": channel.explanation,
    }


def create_app(
    service: LightingApplicationService,
    *,
    web_dist: Path | None = None,
    operations: InMemoryOperations | None = None,
    auth: AuthService | None = None,
    realtime: RealtimeBuffer | None = None,
    operations_clock: Callable[[], datetime] | None = None,
) -> FastAPI:
    @asynccontextmanager
    async def lifespan(_: FastAPI) -> AsyncIterator[None]:
        stop = asyncio.Event()

        async def reconcile_forever() -> None:
            while not stop.is_set():
                await asyncio.to_thread(service.reconcile_once)
                try:
                    await asyncio.wait_for(stop.wait(), timeout=1)
                except TimeoutError:
                    pass

        task = (
            asyncio.create_task(reconcile_forever())
            if service.can_reconcile
            else None
        )
        try:
            yield
        finally:
            stop.set()
            if task is not None:
                task.cancel()
                with suppress(asyncio.CancelledError):
                    await task

    app = FastAPI(title="Grow Hub API", version="1.0", lifespan=lifespan)

    configured = (operations is not None, auth is not None, realtime is not None)
    if any(configured) and not all(configured):
        raise ValueError("operações, autenticação e tempo real devem ser configurados juntos")
    if operations is not None and auth is not None and realtime is not None:
        clock = operations_clock or (lambda: datetime.now(UTC))
        app.include_router(
            create_operations_router(
                operations,
                auth,
                realtime,
                clock=clock,
            )
        )

        @app.middleware("http")
        async def secure_lighting(request: Request, call_next):
            if request.url.path.startswith("/api/v1/lighting"):
                account = auth.verify(request.cookies.get("growhub_session", ""), now=clock())
                minimum = UserRole.VIEWER if request.method == "GET" else UserRole.OPERATOR
                if account is None:
                    return JSONResponse({"detail": "sessão inválida ou expirada"}, status_code=401)
                if account.role < minimum:
                    return JSONResponse({"detail": "perfil sem permissão"}, status_code=403)
            return await call_next(request)

    @app.get("/health")
    def health() -> dict[str, str]:
        return {"status": "ok"}

    @app.get("/api/v1/lighting")
    def get_lighting() -> dict[str, object]:
        try:
            view = service.view()
        except ValueError as exc:
            raise HTTPException(status_code=503, detail=str(exc)) from exc
        return {
            "channels": [_channel_payload(channel) for channel in view.channels],
            "reconciledAt": (
                view.reconciled_at.isoformat()
                if view.reconciled_at is not None
                else None
            ),
        }

    @app.put("/api/v1/lighting/{entity_id}/schedule")
    def put_schedule(entity_id: str, payload: SchedulePayload) -> dict[str, object]:
        try:
            channel = service.update_schedule(
                entity_id,
                on_time=payload.on_time,
                off_time=payload.off_time,
                weekdays=payload.weekdays,
                timezone=payload.timezone,
                enabled=payload.enabled,
            )
        except KeyError as exc:
            raise HTTPException(status_code=404, detail="tomada não configurada") from exc
        except ValueError as exc:
            raise HTTPException(status_code=400, detail=str(exc)) from exc
        return _channel_payload(channel)

    @app.post("/api/v1/lighting/{entity_id}/override")
    def post_override(entity_id: str, payload: OverridePayload) -> dict[str, object]:
        try:
            channel = service.set_override(
                entity_id,
                state=LightState(payload.state) if payload.state is not None else None,
                duration_minutes=payload.duration_minutes,
            )
        except KeyError as exc:
            raise HTTPException(status_code=404, detail="tomada não configurada") from exc
        except ValueError as exc:
            raise HTTPException(status_code=400, detail=str(exc)) from exc
        return _channel_payload(channel)

    if web_dist is not None and web_dist.is_dir():
        app.mount("/", StaticFiles(directory=web_dist, html=True), name="panel")
    return app
