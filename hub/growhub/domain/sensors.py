"""Tipos fundamentais para aquisição confiável de sensores."""

from __future__ import annotations

import math
import re
from dataclasses import dataclass
from datetime import UTC, datetime
from enum import StrEnum

IDENTIFIER = re.compile(r"^[a-z][a-z0-9_-]{0,63}$")


class SensorKind(StrEnum):
    PH = "ph"
    EC = "ec"
    WATER_TEMPERATURE = "water_temperature"
    AIR_TEMPERATURE = "air_temperature"
    LEAF_TEMPERATURE = "leaf_temperature"
    HUMIDITY = "humidity"
    CO2 = "co2"
    RESERVOIR_LEVEL = "reservoir_level"
    FLOW = "flow"
    LEAK = "leak"


class Unit(StrEnum):
    PH = "pH"
    MILLISIEMENS_PER_CM = "mS/cm"
    CELSIUS = "°C"
    PERCENT = "%"
    PPM = "ppm"
    LITER = "L"
    LITER_PER_MINUTE = "L/min"
    BOOLEAN = "bool"


class ReadingQuality(StrEnum):
    VALID = "valid"
    INVALID = "invalid"
    STALE = "stale"
    DISCONNECTED = "disconnected"
    TIMEOUT = "timeout"
    UNCALIBRATED = "uncalibrated"


EXPECTED_UNIT = {
    SensorKind.PH: Unit.PH,
    SensorKind.EC: Unit.MILLISIEMENS_PER_CM,
    SensorKind.WATER_TEMPERATURE: Unit.CELSIUS,
    SensorKind.AIR_TEMPERATURE: Unit.CELSIUS,
    SensorKind.LEAF_TEMPERATURE: Unit.CELSIUS,
    SensorKind.HUMIDITY: Unit.PERCENT,
    SensorKind.CO2: Unit.PPM,
    SensorKind.RESERVOIR_LEVEL: Unit.LITER,
    SensorKind.FLOW: Unit.LITER_PER_MINUTE,
    SensorKind.LEAK: Unit.BOOLEAN,
}


@dataclass(frozen=True, slots=True)
class SensorReading:
    station_id: str
    sensor_id: str
    kind: SensorKind
    value: float
    unit: Unit
    observed_at: datetime
    quality: ReadingQuality = ReadingQuality.VALID
    error_code: str | None = None

    def __post_init__(self) -> None:
        for field_name, identifier in (
            ("station_id", self.station_id),
            ("sensor_id", self.sensor_id),
        ):
            if not IDENTIFIER.fullmatch(identifier):
                raise ValueError(f"{field_name} inválido: {identifier!r}")
        if self.observed_at.tzinfo is None or self.observed_at.utcoffset() is None:
            raise ValueError("observed_at deve conter timezone")
        if not math.isfinite(self.value):
            raise ValueError("value deve ser finito")
        if EXPECTED_UNIT[self.kind] is not self.unit:
            raise ValueError(f"unidade {self.unit} incompatível com {self.kind}")
        if self.quality is ReadingQuality.VALID and self.error_code:
            raise ValueError("leitura válida não pode conter error_code")
        if self.error_code and not IDENTIFIER.fullmatch(self.error_code):
            raise ValueError("error_code deve ser um identificador estável")

    @classmethod
    def now(
        cls,
        *,
        station_id: str,
        sensor_id: str,
        kind: SensorKind,
        value: float,
        unit: Unit,
        quality: ReadingQuality = ReadingQuality.VALID,
        error_code: str | None = None,
    ) -> SensorReading:
        return cls(
            station_id=station_id,
            sensor_id=sensor_id,
            kind=kind,
            value=value,
            unit=unit,
            observed_at=datetime.now(UTC),
            quality=quality,
            error_code=error_code,
        )

