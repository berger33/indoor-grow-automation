"""Política explícita para impedir decisões sobre telemetria antiga."""

from __future__ import annotations

from dataclasses import replace
from datetime import datetime, timedelta
from types import MappingProxyType
from typing import Mapping

from .sensors import ReadingQuality, SensorKind, SensorReading

DEFAULT_MAX_AGE: Mapping[SensorKind, timedelta] = MappingProxyType(
    {
        SensorKind.PH: timedelta(seconds=30),
        SensorKind.EC: timedelta(seconds=30),
        SensorKind.WATER_TEMPERATURE: timedelta(seconds=90),
        SensorKind.AIR_TEMPERATURE: timedelta(seconds=90),
        SensorKind.LEAF_TEMPERATURE: timedelta(seconds=90),
        SensorKind.HUMIDITY: timedelta(seconds=90),
        SensorKind.CO2: timedelta(seconds=90),
        SensorKind.RESERVOIR_LEVEL: timedelta(seconds=10),
        SensorKind.FLOW: timedelta(seconds=10),
        SensorKind.LEAK: timedelta(seconds=15),
    }
)


class StalenessPolicy:
    def __init__(
        self,
        max_age: Mapping[SensorKind, timedelta] = DEFAULT_MAX_AGE,
    ) -> None:
        missing = set(SensorKind) - set(max_age)
        if missing:
            raise ValueError("todo tipo de sensor precisa de max_age")
        if any(duration <= timedelta(0) for duration in max_age.values()):
            raise ValueError("max_age deve ser positivo")
        self._max_age = MappingProxyType(dict(max_age))

    def apply(self, reading: SensorReading, *, now: datetime) -> SensorReading:
        if now.tzinfo is None or now.utcoffset() is None:
            raise ValueError("now deve conter timezone")
        if reading.quality is not ReadingQuality.VALID:
            return reading
        age = now - reading.observed_at
        if age <= self._max_age[reading.kind]:
            return reading
        return replace(
            reading,
            quality=ReadingQuality.STALE,
            error_code="reading_stale",
        )

