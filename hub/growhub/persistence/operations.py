"""Adaptador SQL do estado operacional usado pela API."""

from __future__ import annotations

from datetime import UTC, datetime, timedelta

from sqlalchemy import delete, select
from sqlalchemy.orm import Session, sessionmaker

from ..domain.sensors import ReadingQuality, SensorKind, SensorReading, Unit
from ..services.operations import (
    AlarmRecord,
    AuditRecord,
    BatchRunRecord,
    CalibrationRecord,
    InMemoryOperations,
    IrrigationWindow,
    Recipe,
    RecipeStep,
    SensorDefinition,
    Setpoints,
    StationDefinition,
)
from .models import (
    AlarmRow,
    BatchRunRow,
    CalibrationRow,
    CommandAuditRow,
    IrrigationScheduleRow,
    RecipeRow,
    RecipeStepRow,
    SensorRow,
    SetpointsRow,
    StationRow,
    TelemetryHourlyRow,
    TelemetryRow,
)


def _aware(value: datetime | None) -> datetime | None:
    if value is None or value.tzinfo is not None:
        return value
    return value.replace(tzinfo=UTC)


class SqlOperations(InMemoryOperations):
    def __init__(self, sessions: sessionmaker[Session]) -> None:
        super().__init__()
        self._sessions = sessions
        self._load()

    def _load(self) -> None:
        with self._sessions() as session:
            for row in session.scalars(select(StationRow)).all():
                self.stations[row.station_id] = StationDefinition(row.station_id, row.name, row.timezone)
            for row in session.scalars(select(SensorRow)).all():
                definition = SensorDefinition(row.station_id, row.sensor_id, row.sensor_id.replace("_", " ").title(), row.maximum_age_seconds)
                self.sensors[(row.station_id, row.sensor_id)] = definition
                latest = session.scalar(
                    select(TelemetryRow)
                    .where(TelemetryRow.station_id == row.station_id, TelemetryRow.sensor_id == row.sensor_id)
                    .order_by(TelemetryRow.observed_at.desc())
                    .limit(1)
                )
                if latest is not None:
                    observed_at = _aware(latest.observed_at)
                    assert observed_at is not None
                    self.readings[(row.station_id, row.sensor_id)] = SensorReading(
                        row.station_id, row.sensor_id, SensorKind(latest.kind), latest.value, Unit(latest.unit), observed_at, ReadingQuality(latest.quality), latest.error_code
                    )
            for row in session.scalars(select(SetpointsRow)).all():
                self.setpoints[row.station_id] = Setpoints(row.ph, row.ec_ms_cm, row.air_temperature_c, row.humidity_percent, row.vpd_kpa)
            recipe_rows = session.scalars(select(RecipeRow)).all()
            for row in recipe_rows:
                steps = tuple(
                    RecipeStep(step.channel, step.volume_ml, step.step_order)
                    for step in session.scalars(
                        select(RecipeStepRow)
                        .where(RecipeStepRow.station_id == row.station_id, RecipeStepRow.recipe_id == row.recipe_id)
                        .order_by(RecipeStepRow.step_order)
                    ).all()
                )
                self.recipes.setdefault(row.station_id, {})[row.recipe_id] = Recipe(row.recipe_id, row.name, row.batch_liters, row.target_ph, row.target_ec_ms_cm, steps)
            irrigation_by_station: dict[str, list[IrrigationWindow]] = {}
            for row in session.scalars(select(IrrigationScheduleRow).order_by(IrrigationScheduleRow.start_time)).all():
                irrigation_by_station.setdefault(row.station_id, []).append(
                    IrrigationWindow(row.window_id, datetime.strptime(row.start_time, "%H:%M").time(), row.duration_seconds, frozenset(row.weekdays), row.enabled)
                )
            self.irrigation = {station: tuple(values) for station, values in irrigation_by_station.items()}
            for row in session.scalars(select(AlarmRow)).all():
                raised_at = _aware(row.raised_at)
                assert raised_at is not None
                self.alarms[row.alarm_id] = AlarmRecord(row.alarm_id, row.station_id, row.code, row.severity, row.cause, row.procedure, raised_at, row.latched, _aware(row.acknowledged_at), row.acknowledged_by)
            for row in session.scalars(select(CommandAuditRow).order_by(CommandAuditRow.occurred_at.desc()).limit(1000)).all():
                occurred_at = _aware(row.occurred_at)
                assert occurred_at is not None
                self.audit.append(AuditRecord(row.audit_id, row.user_id, row.station_id, row.action, row.target, row.status, occurred_at, row.details))
            for row in session.scalars(select(CalibrationRow).order_by(CalibrationRow.calibrated_at)).all():
                calibrated_at = _aware(row.calibrated_at)
                assert calibrated_at is not None
                self.calibrations.append(CalibrationRecord(row.calibration_id, row.station_id, row.device_id, row.kind, row.coefficients, row.status, calibrated_at, row.calibrated_by))
            for row in session.scalars(select(BatchRunRow)).all():
                started_at = _aware(row.started_at)
                assert started_at is not None
                self.batch_runs[row.batch_id] = BatchRunRecord(row.batch_id, row.station_id, row.recipe_id, row.status, row.current_step, row.progress_percent, started_at, _aware(row.finished_at), row.failure_code)

    def bootstrap_station(self, station: StationDefinition, sensors: tuple[tuple[SensorDefinition, str, str, str], ...], *, now: datetime) -> None:
        if station.station_id in self.stations:
            return
        with self._sessions.begin() as session:
            session.add(StationRow(station_id=station.station_id, name=station.name, timezone=station.timezone, enabled=True, created_at=now))
            session.add_all(
                SensorRow(station_id=definition.station_id, sensor_id=definition.sensor_id, node_id=node_id, kind=kind, unit=unit, maximum_age_seconds=definition.maximum_age_seconds, enabled=True)
                for definition, node_id, kind, unit in sensors
            )
        self.stations[station.station_id] = station
        for definition, _, _, _ in sensors:
            self.sensors[(definition.station_id, definition.sensor_id)] = definition

    def history_views(self, station_id: str, sensor_ids: frozenset[str], *, since: datetime) -> list[dict[str, object]]:
        with self._sessions() as session:
            if datetime.now(UTC) - since > timedelta(days=2):
                query = select(TelemetryHourlyRow).where(TelemetryHourlyRow.station_id == station_id, TelemetryHourlyRow.bucket_at >= since)
                if sensor_ids:
                    query = query.where(TelemetryHourlyRow.sensor_id.in_(sensor_ids))
                rows = session.scalars(query.order_by(TelemetryHourlyRow.bucket_at).limit(20_000)).all()
                return [{"sensorId": row.sensor_id, "kind": row.kind, "value": row.average, "unit": row.unit, "quality": "valid", "observedAt": _aware(row.bucket_at).isoformat()} for row in rows]  # type: ignore[union-attr]
            query = select(TelemetryRow).where(TelemetryRow.station_id == station_id, TelemetryRow.observed_at >= since)
            if sensor_ids:
                query = query.where(TelemetryRow.sensor_id.in_(sensor_ids))
            rows = session.scalars(query.order_by(TelemetryRow.observed_at).limit(20_000)).all()
            return [{"sensorId": row.sensor_id, "kind": row.kind, "value": row.value, "unit": row.unit, "quality": row.quality, "observedAt": _aware(row.observed_at).isoformat()} for row in rows]  # type: ignore[union-attr]

    def save_setpoints(self, station_id: str, value: Setpoints, *, user_id: str, now: datetime) -> None:
        with self._sessions.begin() as session:
            row = session.get(SetpointsRow, station_id)
            if row is None:
                row = SetpointsRow(station_id=station_id, ph=value.ph, ec_ms_cm=value.ec_ms_cm, air_temperature_c=value.air_temperature_c, humidity_percent=value.humidity_percent, vpd_kpa=value.vpd_kpa, updated_at=now, updated_by=user_id)
                session.add(row)
            else:
                row.ph, row.ec_ms_cm, row.air_temperature_c = value.ph, value.ec_ms_cm, value.air_temperature_c
                row.humidity_percent, row.vpd_kpa, row.updated_at, row.updated_by = value.humidity_percent, value.vpd_kpa, now, user_id
        super().save_setpoints(station_id, value, user_id=user_id, now=now)

    def save_recipe(self, station_id: str, value: Recipe, *, user_id: str, now: datetime) -> None:
        with self._sessions.begin() as session:
            row = session.get(RecipeRow, (station_id, value.recipe_id))
            if row is None:
                row = RecipeRow(station_id=station_id, recipe_id=value.recipe_id, name=value.name, batch_liters=value.batch_liters, target_ph=value.target_ph, target_ec_ms_cm=value.target_ec_ms_cm, enabled=True, updated_at=now)
                session.add(row)
            else:
                row.name, row.batch_liters, row.target_ph, row.target_ec_ms_cm, row.updated_at = value.name, value.batch_liters, value.target_ph, value.target_ec_ms_cm, now
            session.execute(delete(RecipeStepRow).where(RecipeStepRow.station_id == station_id, RecipeStepRow.recipe_id == value.recipe_id))
            session.flush()
            session.add_all(RecipeStepRow(station_id=station_id, recipe_id=value.recipe_id, step_order=step.order, channel=step.channel, volume_ml=step.volume_ml) for step in value.steps)
        super().save_recipe(station_id, value, user_id=user_id, now=now)

    def save_irrigation(self, station_id: str, windows: tuple[IrrigationWindow, ...]) -> None:
        super().save_irrigation(station_id, windows)
        with self._sessions.begin() as session:
            session.execute(delete(IrrigationScheduleRow).where(IrrigationScheduleRow.station_id == station_id))
            session.add_all(IrrigationScheduleRow(station_id=station_id, window_id=item.window_id, start_time=item.start_time.isoformat(timespec="minutes"), duration_seconds=item.duration_seconds, weekdays=sorted(item.weekdays), enabled=item.enabled, updated_at=datetime.now(UTC)) for item in windows)

    def record_audit(self, user_id: str, station_id: str, action: str, target: str, status: str, now: datetime, **details: object) -> AuditRecord:
        record = super().record_audit(user_id, station_id, action, target, status, now, **details)
        with self._sessions.begin() as session:
            session.add(CommandAuditRow(audit_id=record.audit_id, user_id=user_id, station_id=station_id, action=action, target=target, status=status, occurred_at=now, details=details))
        return record

    def update_audit_status(self, audit_id: str, status: str, *, now: datetime, **details: object) -> AuditRecord:
        record = super().update_audit_status(audit_id, status, now=now, **details)
        with self._sessions.begin() as session:
            row = session.get(CommandAuditRow, audit_id)
            if row is None:
                raise KeyError("registro de auditoria não encontrado")
            row.status = record.status
            row.details = record.details
        return record

    def save_alarm(self, alarm: AlarmRecord) -> bool:
        if alarm.station_id not in self.stations:
            raise KeyError("estação do alarme não cadastrada")
        with self._sessions.begin() as session:
            if session.get(AlarmRow, alarm.alarm_id) is not None:
                return False
            session.add(
                AlarmRow(
                    alarm_id=alarm.alarm_id,
                    station_id=alarm.station_id,
                    code=alarm.code,
                    severity=alarm.severity,
                    cause=alarm.cause,
                    procedure=alarm.procedure,
                    raised_at=alarm.raised_at,
                    latched=alarm.latched,
                    acknowledged_at=alarm.acknowledged_at,
                    acknowledged_by=alarm.acknowledged_by,
                )
            )
        return super().save_alarm(alarm)

    def acknowledge_alarm(self, alarm_id: str, user_id: str, now: datetime) -> AlarmRecord:
        alarm = super().acknowledge_alarm(alarm_id, user_id, now)
        with self._sessions.begin() as session:
            row = session.get(AlarmRow, alarm_id)
            if row is not None:
                row.acknowledged_at, row.acknowledged_by = now, user_id
        return alarm

    def save_calibration(self, value: CalibrationRecord) -> None:
        with self._sessions.begin() as session:
            session.add(CalibrationRow(calibration_id=value.calibration_id, station_id=value.station_id, device_id=value.device_id, kind=value.kind, coefficients=value.coefficients, status=value.status, calibrated_at=value.calibrated_at, expires_at=None, calibrated_by=value.calibrated_by))
        super().save_calibration(value)

    def save_batch_run(self, value: BatchRunRecord) -> None:
        with self._sessions.begin() as session:
            row = session.get(BatchRunRow, value.batch_id)
            if row is None:
                session.add(BatchRunRow(batch_id=value.batch_id, station_id=value.station_id, recipe_id=value.recipe_id, status=value.status, current_step=value.current_step, progress_percent=value.progress_percent, started_at=value.started_at, finished_at=value.finished_at, failure_code=value.failure_code))
            else:
                row.status, row.current_step, row.progress_percent = value.status, value.current_step, value.progress_percent
                row.finished_at, row.failure_code = value.finished_at, value.failure_code
        super().save_batch_run(value)
