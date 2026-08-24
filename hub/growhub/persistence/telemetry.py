"""Repositório idempotente de telemetria e política de retenção."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import UTC, datetime, timedelta

from sqlalchemy import delete, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session, sessionmaker

from ..contracts.telemetry import TelemetryEnvelope
from ..domain.sensors import SensorReading
from .models import SensorRow, StationRow, TelemetryRow


@dataclass(frozen=True, slots=True)
class TelemetryCapacityPlan:
    sensor_count: int = 16
    sample_interval_seconds: int = 30
    primary_bytes_per_sample: int = 220
    provisioned_bytes_per_sample: float = 549.7

    def __post_init__(self) -> None:
        if not 1 <= self.sensor_count <= 512:
            raise ValueError("quantidade de sensores inválida")
        if not 1 <= self.sample_interval_seconds <= 86_400:
            raise ValueError("intervalo de amostragem inválido")
        if self.primary_bytes_per_sample <= 0 or self.provisioned_bytes_per_sample < self.primary_bytes_per_sample:
            raise ValueError("estimativa de bytes inválida")

    @property
    def records_per_year(self) -> int:
        return int(365 * 86_400 / self.sample_interval_seconds * self.sensor_count)

    @property
    def primary_gib_per_year(self) -> float:
        return self.records_per_year * self.primary_bytes_per_sample / 1024**3

    @property
    def provisioned_gib_per_year(self) -> float:
        return self.records_per_year * self.provisioned_bytes_per_sample / 1024**3


class SqlTelemetryRepository:
    def __init__(self, sessions: sessionmaker[Session]) -> None:
        self._sessions = sessions

    def add_station(self, station_id: str, name: str, timezone: str, *, now: datetime) -> None:
        with self._sessions.begin() as session:
            session.add(StationRow(station_id=station_id, name=name, timezone=timezone, created_at=now))

    def add_sensor(
        self,
        station_id: str,
        sensor_id: str,
        node_id: str,
        kind: str,
        unit: str,
        maximum_age_seconds: int,
    ) -> None:
        with self._sessions.begin() as session:
            session.add(
                SensorRow(
                    station_id=station_id,
                    sensor_id=sensor_id,
                    node_id=node_id,
                    kind=kind,
                    unit=unit,
                    maximum_age_seconds=maximum_age_seconds,
                )
            )

    def save(self, envelope: TelemetryEnvelope, *, received_at: datetime) -> bool:
        reading = envelope.reading
        row = TelemetryRow(
            message_id=envelope.message_id,
            station_id=reading.station_id,
            sensor_id=reading.sensor_id,
            sequence=envelope.sequence,
            kind=reading.kind.value,
            value=reading.value,
            unit=reading.unit.value,
            quality=reading.quality.value,
            error_code=reading.error_code,
            observed_at=reading.observed_at,
            received_at=received_at,
        )
        try:
            with self._sessions.begin() as session:
                session.add(row)
        except IntegrityError:
            return False
        return True

    def latest(self, station_id: str) -> tuple[SensorReading, ...]:
        with self._sessions() as session:
            rows = session.scalars(
                select(TelemetryRow)
                .where(TelemetryRow.station_id == station_id)
                .order_by(TelemetryRow.sensor_id, TelemetryRow.observed_at.desc())
            ).all()
        latest: dict[str, TelemetryRow] = {}
        for row in rows:
            latest.setdefault(row.sensor_id, row)
        from ..domain.sensors import ReadingQuality, SensorKind, Unit

        return tuple(
            SensorReading(
                station_id=row.station_id,
                sensor_id=row.sensor_id,
                kind=SensorKind(row.kind),
                value=row.value,
                unit=Unit(row.unit),
                observed_at=(
                    row.observed_at
                    if row.observed_at.tzinfo is not None
                    else row.observed_at.replace(tzinfo=UTC)
                ),
                quality=ReadingQuality(row.quality),
                error_code=row.error_code,
            )
            for row in latest.values()
        )

    def purge_raw(self, *, now: datetime, keep_for: timedelta) -> int:
        if keep_for < timedelta(days=1):
            raise ValueError("retenção bruta mínima é de um dia")
        with self._sessions.begin() as session:
            result = session.execute(delete(TelemetryRow).where(TelemetryRow.observed_at < now - keep_for))
            return int(result.rowcount or 0)
