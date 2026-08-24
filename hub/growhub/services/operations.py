"""Estado operacional validado usado pela API e pelo painel."""

from __future__ import annotations

import math
import uuid
from dataclasses import dataclass, field
from datetime import datetime, time
from enum import StrEnum

from ..domain.sensors import IDENTIFIER, ReadingQuality, SensorReading


class StationHealth(StrEnum):
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    FAILED = "failed"


@dataclass(frozen=True, slots=True)
class StationDefinition:
    station_id: str
    name: str
    timezone: str = "America/Sao_Paulo"

    def __post_init__(self) -> None:
        if IDENTIFIER.fullmatch(self.station_id) is None or not self.name.strip():
            raise ValueError("estação inválida")


@dataclass(frozen=True, slots=True)
class SensorDefinition:
    station_id: str
    sensor_id: str
    label: str
    maximum_age_seconds: int

    def __post_init__(self) -> None:
        if IDENTIFIER.fullmatch(self.station_id) is None or IDENTIFIER.fullmatch(self.sensor_id) is None:
            raise ValueError("sensor inválido")
        if not self.label.strip() or not 5 <= self.maximum_age_seconds <= 86_400:
            raise ValueError("configuração de sensor inválida")


@dataclass(frozen=True, slots=True)
class Setpoints:
    ph: float
    ec_ms_cm: float
    air_temperature_c: float
    humidity_percent: float
    vpd_kpa: float

    def __post_init__(self) -> None:
        values = (self.ph, self.ec_ms_cm, self.air_temperature_c, self.humidity_percent, self.vpd_kpa)
        if not all(math.isfinite(value) for value in values):
            raise ValueError("setpoints devem ser finitos")
        if not 4.0 <= self.ph <= 8.0:
            raise ValueError("setpoint de pH fora da faixa segura")
        if not 0.0 <= self.ec_ms_cm <= 5.0:
            raise ValueError("setpoint de EC fora da faixa segura")
        if not 10.0 <= self.air_temperature_c <= 40.0:
            raise ValueError("setpoint de temperatura fora da faixa segura")
        if not 20.0 <= self.humidity_percent <= 85.0:
            raise ValueError("setpoint de umidade fora da faixa segura")
        if not 0.2 <= self.vpd_kpa <= 2.5:
            raise ValueError("setpoint de VPD fora da faixa segura")


@dataclass(frozen=True, slots=True)
class RecipeStep:
    channel: int
    volume_ml: float
    order: int

    def __post_init__(self) -> None:
        if not 1 <= self.channel <= 6 or not 0 < self.volume_ml <= 500 or not 1 <= self.order <= 6:
            raise ValueError("etapa de receita inválida")


@dataclass(frozen=True, slots=True)
class Recipe:
    recipe_id: str
    name: str
    batch_liters: float
    target_ph: float
    target_ec_ms_cm: float
    steps: tuple[RecipeStep, ...]

    def __post_init__(self) -> None:
        if IDENTIFIER.fullmatch(self.recipe_id) is None or not self.name.strip():
            raise ValueError("receita inválida")
        if not 1 <= self.batch_liters <= 50 or not 4 <= self.target_ph <= 8 or not 0 <= self.target_ec_ms_cm <= 5:
            raise ValueError("alvos de receita inválidos")
        if not 1 <= len(self.steps) <= 6:
            raise ValueError("receita deve conter entre uma e seis etapas")
        channels = [step.channel for step in self.steps]
        orders = [step.order for step in self.steps]
        if len(channels) != len(set(channels)) or sorted(orders) != list(range(1, len(orders) + 1)):
            raise ValueError("canais e ordem da receita devem ser únicos e contíguos")


@dataclass(frozen=True, slots=True)
class IrrigationWindow:
    window_id: str
    start_time: time
    duration_seconds: int
    weekdays: frozenset[int]
    enabled: bool = True

    def __post_init__(self) -> None:
        if IDENTIFIER.fullmatch(self.window_id) is None:
            raise ValueError("identificador de irrigação inválido")
        if not 30 <= self.duration_seconds <= 600:
            raise ValueError("duração de irrigação fora da faixa")
        if not self.weekdays or not self.weekdays <= set(range(7)):
            raise ValueError("dias de irrigação inválidos")


@dataclass(slots=True)
class AlarmRecord:
    alarm_id: str
    station_id: str
    code: str
    severity: str
    cause: str
    procedure: str
    raised_at: datetime
    latched: bool = True
    acknowledged_at: datetime | None = None
    acknowledged_by: str | None = None


@dataclass(frozen=True, slots=True)
class AuditRecord:
    audit_id: str
    user_id: str
    station_id: str
    action: str
    target: str
    status: str
    occurred_at: datetime
    details: dict[str, object] = field(default_factory=dict)


class InMemoryOperations:
    """Implementação determinística; o adaptador SQL mantém o mesmo contrato."""

    def __init__(self) -> None:
        self.stations: dict[str, StationDefinition] = {}
        self.sensors: dict[tuple[str, str], SensorDefinition] = {}
        self.readings: dict[tuple[str, str], SensorReading] = {}
        self.history: dict[tuple[str, str], list[SensorReading]] = {}
        self.setpoints: dict[str, Setpoints] = {}
        self.recipes: dict[str, dict[str, Recipe]] = {}
        self.irrigation: dict[str, tuple[IrrigationWindow, ...]] = {}
        self.alarms: dict[str, AlarmRecord] = {}
        self.audit: list[AuditRecord] = []

    def record_reading(self, reading: SensorReading, *, maximum_samples: int = 2_880) -> None:
        """Atualiza a leitura corrente e mantém até 24 h a 30 s por padrão."""

        key = (reading.station_id, reading.sensor_id)
        if key not in self.sensors:
            raise KeyError("sensor não cadastrado")
        if not 10 <= maximum_samples <= 100_000:
            raise ValueError("limite de histórico inválido")
        self.readings[key] = reading
        samples = self.history.setdefault(key, [])
        samples.append(reading)
        if len(samples) > maximum_samples:
            del samples[:-maximum_samples]

    def history_views(
        self,
        station_id: str,
        sensor_ids: frozenset[str],
        *,
        since: datetime,
    ) -> list[dict[str, object]]:
        result: list[dict[str, object]] = []
        for (owner, sensor_id), samples in sorted(self.history.items()):
            if owner != station_id or (sensor_ids and sensor_id not in sensor_ids):
                continue
            for reading in samples:
                if reading.observed_at >= since:
                    result.append(
                        {
                            "sensorId": sensor_id,
                            "kind": reading.kind.value,
                            "value": reading.value,
                            "unit": reading.unit.value,
                            "quality": reading.quality.value,
                            "observedAt": reading.observed_at.isoformat(),
                        }
                    )
        return sorted(result, key=lambda item: str(item["observedAt"]))

    def station_health(self, station_id: str, *, now: datetime) -> StationHealth:
        definitions = [value for key, value in self.sensors.items() if key[0] == station_id]
        if not definitions:
            return StationHealth.FAILED
        degraded = False
        for definition in definitions:
            reading = self.readings.get((station_id, definition.sensor_id))
            if reading is None or reading.quality not in (ReadingQuality.VALID, ReadingQuality.STALE):
                return StationHealth.FAILED
            if reading.quality is ReadingQuality.STALE or (now - reading.observed_at).total_seconds() > definition.maximum_age_seconds:
                degraded = True
        return StationHealth.DEGRADED if degraded else StationHealth.HEALTHY

    def sensor_views(self, station_id: str, *, now: datetime) -> list[dict[str, object]]:
        result = []
        for (owner, sensor_id), definition in sorted(self.sensors.items()):
            if owner != station_id:
                continue
            reading = self.readings.get((station_id, sensor_id))
            age = (now - reading.observed_at).total_seconds() if reading else None
            health = "failed" if reading is None or reading.quality not in (ReadingQuality.VALID, ReadingQuality.STALE) else "degraded" if reading.quality is ReadingQuality.STALE or age > definition.maximum_age_seconds else "healthy"
            result.append({
                "sensorId": sensor_id,
                "label": definition.label,
                "value": reading.value if reading else None,
                "unit": reading.unit.value if reading else None,
                "quality": reading.quality.value if reading else "missing",
                "ageSeconds": age,
                "maximumAgeSeconds": definition.maximum_age_seconds,
                "health": health,
                "errorCode": reading.error_code if reading else "sensor_missing",
            })
        return result

    def save_irrigation(self, station_id: str, windows: tuple[IrrigationWindow, ...]) -> None:
        if len(windows) > 5:
            raise ValueError("são permitidas no máximo cinco irrigações")
        self.irrigation[station_id] = windows

    def record_audit(self, user_id: str, station_id: str, action: str, target: str, status: str, now: datetime, **details: object) -> AuditRecord:
        record = AuditRecord(str(uuid.uuid4()), user_id, station_id, action, target, status, now, details)
        self.audit.append(record)
        return record

    def acknowledge_alarm(self, alarm_id: str, user_id: str, now: datetime) -> AlarmRecord:
        alarm = self.alarms[alarm_id]
        alarm.acknowledged_at = now
        alarm.acknowledged_by = user_id
        return alarm
