"""Rotas operacionais autenticadas e canal em tempo real retomável."""

from __future__ import annotations

import uuid
from collections.abc import Callable
from datetime import UTC, datetime, timedelta, time
from typing import Annotated, Literal

from fastapi import APIRouter, Cookie, Depends, HTTPException, Query, Response, WebSocket, WebSocketDisconnect, status
from pydantic import BaseModel, ConfigDict, Field

from ..services.calibration import evaluate_calibration
from ..services.mqtt_gateway import MqttGateway, MqttUnavailable
from ..services.operations import BatchRunRecord, CalibrationRecord, InMemoryOperations, IrrigationWindow, Recipe, RecipeStep, Setpoints
from ..services.realtime import RealtimeBuffer
from ..services.security import AuthService, UserAccount, UserRole


class LoginPayload(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
    user_id: str = Field(alias="userId")
    password: str


class UserPayload(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
    user_id: str = Field(alias="userId")
    display_name: str = Field(alias="displayName")
    role: Literal["viewer", "operator", "admin"]
    password: str


class SetpointsPayload(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
    ph: float
    ec_ms_cm: float = Field(alias="ecMsCm")
    air_temperature_c: float = Field(alias="airTemperatureC")
    humidity_percent: float = Field(alias="humidityPercent")
    vpd_kpa: float = Field(alias="vpdKpa")


class RecipeStepPayload(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
    channel: int
    volume_ml: float = Field(alias="volumeMl")
    order: int


class RecipePayload(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
    recipe_id: str = Field(alias="recipeId")
    name: str
    batch_liters: float = Field(alias="batchLiters")
    target_ph: float = Field(alias="targetPh")
    target_ec_ms_cm: float = Field(alias="targetEcMsCm")
    steps: tuple[RecipeStepPayload, ...]


class IrrigationWindowPayload(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
    window_id: str = Field(alias="windowId")
    start_time: time = Field(alias="startTime")
    duration_seconds: int = Field(alias="durationSeconds")
    weekdays: frozenset[int]
    enabled: bool = True


class CommandPayload(BaseModel):
    action: Literal[
        "start_batch",
        "stop_batch",
        "start_irrigation",
        "stop_irrigation",
        "safe_stop",
    ]
    target: str


class CalibrationPayload(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
    device_id: str = Field(alias="deviceId")
    kind: Literal["mass", "pump", "ph", "ec"]
    measurements: dict[str, object]


def _setpoints_payload(value: Setpoints) -> dict[str, float]:
    return {
        "ph": value.ph,
        "ecMsCm": value.ec_ms_cm,
        "airTemperatureC": value.air_temperature_c,
        "humidityPercent": value.humidity_percent,
        "vpdKpa": value.vpd_kpa,
    }


def create_operations_router(
    operations: InMemoryOperations,
    auth: AuthService,
    realtime: RealtimeBuffer,
    *,
    clock: Callable[[], datetime] = lambda: datetime.now(UTC),
    dispatcher: MqttGateway | None = None,
) -> APIRouter:
    router = APIRouter(prefix="/api/v1")

    def require_role(minimum: UserRole):
        def dependency(growhub_session: Annotated[str | None, Cookie()] = None) -> UserAccount:
            account = auth.verify(growhub_session or "", now=clock())
            if account is None:
                raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="sessão inválida ou expirada")
            if account.role < minimum:
                raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="perfil sem permissão")
            return account

        return dependency

    viewer = require_role(UserRole.VIEWER)
    operator = require_role(UserRole.OPERATOR)
    admin = require_role(UserRole.ADMIN)

    @router.post("/auth/login")
    def login(payload: LoginPayload, response: Response) -> dict[str, str]:
        account = auth.authenticate(payload.user_id, payload.password)
        if account is None:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="credenciais inválidas")
        response.set_cookie(
            "growhub_session",
            auth.issue(account, now=clock()),
            max_age=28_800,
            httponly=True,
            secure=True,
            samesite="strict",
            path="/",
        )
        return {"userId": account.user_id, "displayName": account.display_name, "role": account.role.name.lower()}

    @router.post("/auth/logout", status_code=204)
    def logout(response: Response) -> None:
        response.delete_cookie("growhub_session", path="/", secure=True, httponly=True, samesite="strict")

    @router.post("/users", status_code=201)
    def create_user(payload: UserPayload, account: UserAccount = Depends(admin)) -> dict[str, str]:
        try:
            created = auth.add_user(payload.user_id, payload.display_name, UserRole[payload.role.upper()], payload.password)
        except ValueError as exc:
            raise HTTPException(status_code=400, detail=str(exc)) from exc
        audit_station = next(iter(operations.stations), "system")
        operations.record_audit(account.user_id, audit_station, "create_user", created.user_id, "applied", clock(), role=payload.role)
        return {"userId": created.user_id, "displayName": created.display_name, "role": created.role.name.lower()}

    @router.get("/stations")
    def stations(_: UserAccount = Depends(viewer)) -> dict[str, object]:
        now = clock()
        return {
            "stations": [
                {
                    "stationId": station.station_id,
                    "name": station.name,
                    "timezone": station.timezone,
                    "health": operations.station_health(station.station_id, now=now).value,
                }
                for station in sorted(operations.stations.values(), key=lambda item: item.station_id)
            ]
        }

    @router.get("/stations/{station_id}/sensors")
    def sensors(station_id: str, _: UserAccount = Depends(viewer)) -> dict[str, object]:
        if station_id not in operations.stations:
            raise HTTPException(status_code=404, detail="estação não encontrada")
        return {"stationId": station_id, "sensors": operations.sensor_views(station_id, now=clock())}

    @router.get("/stations/{station_id}/history")
    def history(
        station_id: str,
        _: UserAccount = Depends(viewer),
        sensor_ids: Annotated[list[str] | None, Query(alias="sensorId")] = None,
        hours: Annotated[int, Query(ge=1, le=720)] = 24,
    ) -> dict[str, object]:
        if station_id not in operations.stations:
            raise HTTPException(status_code=404, detail="estação não encontrada")
        samples = operations.history_views(station_id, frozenset(sensor_ids or ()), since=clock() - timedelta(hours=hours))
        return {"stationId": station_id, "samples": samples}

    @router.get("/stations/{station_id}/setpoints")
    def get_setpoints(station_id: str, _: UserAccount = Depends(viewer)) -> dict[str, float]:
        try:
            return _setpoints_payload(operations.setpoints[station_id])
        except KeyError as exc:
            raise HTTPException(status_code=404, detail="setpoints não configurados") from exc

    @router.put("/stations/{station_id}/setpoints")
    async def put_setpoints(station_id: str, payload: SetpointsPayload, account: UserAccount = Depends(operator)) -> dict[str, float]:
        if station_id not in operations.stations:
            raise HTTPException(status_code=404, detail="estação não encontrada")
        try:
            value = Setpoints(**payload.model_dump())
        except ValueError as exc:
            raise HTTPException(status_code=400, detail=str(exc)) from exc
        operations.save_setpoints(station_id, value, user_id=account.user_id, now=clock())
        operations.record_audit(account.user_id, station_id, "update_setpoints", station_id, "applied", clock())
        await realtime.publish("configuration.updated", station_id, clock(), {"resource": "setpoints"})
        return _setpoints_payload(value)

    @router.get("/stations/{station_id}/recipes")
    def recipes(station_id: str, _: UserAccount = Depends(viewer)) -> dict[str, object]:
        values = operations.recipes.get(station_id, {}).values()
        return {"recipes": [
            {
                "recipeId": value.recipe_id,
                "name": value.name,
                "batchLiters": value.batch_liters,
                "targetPh": value.target_ph,
                "targetEcMsCm": value.target_ec_ms_cm,
                "steps": [{"channel": step.channel, "volumeMl": step.volume_ml, "order": step.order} for step in value.steps],
            }
            for value in sorted(values, key=lambda item: item.recipe_id)
        ]}

    @router.post("/stations/{station_id}/recipes", status_code=201)
    def save_recipe(station_id: str, payload: RecipePayload, account: UserAccount = Depends(operator)) -> dict[str, str]:
        if station_id not in operations.stations:
            raise HTTPException(status_code=404, detail="estação não encontrada")
        try:
            recipe = Recipe(
                payload.recipe_id,
                payload.name,
                payload.batch_liters,
                payload.target_ph,
                payload.target_ec_ms_cm,
                tuple(RecipeStep(**step.model_dump()) for step in payload.steps),
            )
        except ValueError as exc:
            raise HTTPException(status_code=400, detail=str(exc)) from exc
        operations.save_recipe(station_id, recipe, user_id=account.user_id, now=clock())
        operations.record_audit(account.user_id, station_id, "save_recipe", recipe.recipe_id, "applied", clock())
        return {"recipeId": recipe.recipe_id, "status": "saved"}

    @router.get("/stations/{station_id}/irrigation-schedules")
    def get_irrigation(station_id: str, _: UserAccount = Depends(viewer)) -> dict[str, object]:
        return {"windows": [
            {
                "windowId": item.window_id,
                "startTime": item.start_time.isoformat(timespec="minutes"),
                "durationSeconds": item.duration_seconds,
                "weekdays": sorted(item.weekdays),
                "enabled": item.enabled,
            }
            for item in operations.irrigation.get(station_id, ())
        ]}

    @router.put("/stations/{station_id}/irrigation-schedules")
    def put_irrigation(station_id: str, payload: tuple[IrrigationWindowPayload, ...], account: UserAccount = Depends(operator)) -> dict[str, int]:
        if station_id not in operations.stations:
            raise HTTPException(status_code=404, detail="estação não encontrada")
        try:
            windows = tuple(IrrigationWindow(**item.model_dump()) for item in payload)
            operations.save_irrigation(station_id, windows)
        except ValueError as exc:
            raise HTTPException(status_code=400, detail=str(exc)) from exc
        operations.record_audit(account.user_id, station_id, "save_irrigation", station_id, "applied", clock(), windows=len(windows))
        return {"saved": len(windows)}

    @router.get("/stations/{station_id}/alarms")
    def alarms(station_id: str, _: UserAccount = Depends(viewer)) -> dict[str, object]:
        return {"alarms": [
            {
                "alarmId": alarm.alarm_id,
                "code": alarm.code,
                "severity": alarm.severity,
                "cause": alarm.cause,
                "procedure": alarm.procedure,
                "raisedAt": alarm.raised_at.isoformat(),
                "latched": alarm.latched,
                "acknowledgedAt": alarm.acknowledged_at.isoformat() if alarm.acknowledged_at else None,
                "acknowledgedBy": alarm.acknowledged_by,
            }
            for alarm in sorted(operations.alarms.values(), key=lambda item: item.raised_at, reverse=True)
            if alarm.station_id == station_id
        ]}

    @router.post("/alarms/{alarm_id}/ack")
    def acknowledge_alarm(alarm_id: str, account: UserAccount = Depends(operator)) -> dict[str, str]:
        try:
            alarm = operations.acknowledge_alarm(alarm_id, account.user_id, clock())
        except KeyError as exc:
            raise HTTPException(status_code=404, detail="alarme não encontrado") from exc
        operations.record_audit(account.user_id, alarm.station_id, "ack_alarm", alarm_id, "applied", clock())
        return {"alarmId": alarm_id, "status": "acknowledged"}

    @router.post("/stations/{station_id}/commands", status_code=202)
    async def command(station_id: str, payload: CommandPayload, account: UserAccount = Depends(operator)) -> dict[str, str]:
        if station_id not in operations.stations:
            raise HTTPException(status_code=404, detail="estação não encontrada")
        if payload.action == "start_batch":
            if payload.target not in operations.recipes.get(station_id, {}):
                raise HTTPException(status_code=400, detail="receita não encontrada")
            active = any(run.station_id == station_id and run.status in {"queued", "running"} for run in operations.batch_runs.values())
            if active:
                raise HTTPException(status_code=409, detail="já existe uma batelada ativa")
        now = clock()
        audit = operations.record_audit(account.user_id, station_id, payload.action, payload.target, "queued", now)
        if payload.action == "start_batch":
            operations.save_batch_run(BatchRunRecord(audit.audit_id, station_id, payload.target, "queued", "awaiting_ack", 0, now))
        elif payload.action == "stop_batch":
            for run in operations.batch_runs.values():
                if run.station_id == station_id and run.status in {"queued", "running"}:
                    run.status = "stop_queued"
                    operations.save_batch_run(run)
        transport_status = "queued"
        if dispatcher is not None:
            try:
                dispatcher.dispatch(
                    audit_id=audit.audit_id,
                    station_id=station_id,
                    action=payload.action,
                    target=payload.target,
                    now=now,
                )
            except MqttUnavailable as exc:
                operations.update_audit_status(audit.audit_id, "transport_unavailable", now=now, reason=str(exc))
                if payload.action == "start_batch":
                    run = operations.batch_runs[audit.audit_id]
                    run.status = "failed"
                    run.current_step = "transport_unavailable"
                    run.failure_code = "mqtt_unavailable"
                    run.finished_at = now
                    operations.save_batch_run(run)
                elif payload.action == "stop_batch":
                    for run in operations.batch_runs.values():
                        if run.station_id == station_id and run.status == "stop_queued":
                            run.status = "stop_rejected"
                            run.current_step = "transport_unavailable"
                            run.failure_code = "mqtt_unavailable"
                            operations.save_batch_run(run)
                await realtime.publish("command.rejected", station_id, now, {"auditId": audit.audit_id, "reason": "mqtt_unavailable"})
                raise HTTPException(status_code=503, detail=str(exc)) from exc
            transport_status = "sent"
        await realtime.publish("command.queued", station_id, now, {"auditId": audit.audit_id, "action": payload.action, "target": payload.target, "transportStatus": transport_status})
        return {"auditId": audit.audit_id, "status": transport_status, "explanation": "aguardando ACK/NACK do firmware"}

    @router.get("/stations/{station_id}/batch-runs")
    def batch_runs(station_id: str, _: UserAccount = Depends(viewer)) -> dict[str, object]:
        return {"runs": [
            {
                "batchId": run.batch_id,
                "recipeId": run.recipe_id,
                "status": run.status,
                "currentStep": run.current_step,
                "progressPercent": run.progress_percent,
                "startedAt": run.started_at.isoformat(),
                "finishedAt": run.finished_at.isoformat() if run.finished_at else None,
                "failureCode": run.failure_code,
            }
            for run in sorted(operations.batch_runs.values(), key=lambda item: item.started_at, reverse=True)
            if run.station_id == station_id
        ]}

    @router.get("/stations/{station_id}/calibrations")
    def calibrations(station_id: str, _: UserAccount = Depends(viewer)) -> dict[str, object]:
        return {"calibrations": [
            {
                "calibrationId": item.calibration_id,
                "deviceId": item.device_id,
                "kind": item.kind,
                "coefficients": item.coefficients,
                "status": item.status,
                "calibratedAt": item.calibrated_at.isoformat(),
                "calibratedBy": item.calibrated_by,
            }
            for item in reversed(operations.calibrations)
            if item.station_id == station_id
        ]}

    @router.post("/stations/{station_id}/calibrations", status_code=201)
    async def calibrate(station_id: str, payload: CalibrationPayload, account: UserAccount = Depends(operator)) -> dict[str, object]:
        if station_id not in operations.stations:
            raise HTTPException(status_code=404, detail="estação não encontrada")
        try:
            result = evaluate_calibration(payload.kind, payload.measurements, device_id=payload.device_id, now=clock())
        except ValueError as exc:
            raise HTTPException(status_code=400, detail=str(exc)) from exc
        record = CalibrationRecord(str(uuid.uuid4()), station_id, payload.device_id, payload.kind, result.coefficients, result.status, clock(), account.user_id)
        operations.save_calibration(record)
        operations.record_audit(account.user_id, station_id, "calibration_record", payload.device_id, result.status, clock(), kind=payload.kind)
        await realtime.publish("calibration.updated", station_id, clock(), {"calibrationId": record.calibration_id, "status": result.status})
        return {"calibrationId": record.calibration_id, "status": result.status, "coefficients": result.coefficients, "explanation": result.explanation}

    @router.get("/audit")
    def audit(_: UserAccount = Depends(admin)) -> dict[str, object]:
        return {"records": [
            {
                "auditId": item.audit_id,
                "userId": item.user_id,
                "stationId": item.station_id,
                "action": item.action,
                "target": item.target,
                "status": item.status,
                "occurredAt": item.occurred_at.isoformat(),
                "details": item.details,
            }
            for item in operations.audit
        ]}

    @router.websocket("/realtime")
    async def websocket(websocket: WebSocket, last_event_id: int = 0) -> None:
        account = auth.verify(websocket.cookies.get("growhub_session", ""), now=clock())
        if account is None:
            await websocket.close(code=4401, reason="sessão inválida")
            return
        await websocket.accept()
        for event in realtime.after(last_event_id):
            await websocket.send_json(event.as_dict())
        queue = realtime.subscribe()
        try:
            while True:
                await websocket.send_json((await queue.get()).as_dict())
        except WebSocketDisconnect:
            pass
        finally:
            realtime.unsubscribe(queue)

    return router
