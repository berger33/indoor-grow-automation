"""Validação de plausibilidade sem esconder a amostra bruta."""

from __future__ import annotations

from dataclasses import dataclass, replace
from types import MappingProxyType
from typing import Mapping

from .sensors import ReadingQuality, SensorKind, SensorReading


@dataclass(frozen=True, slots=True)
class PlausibilityRange:
    minimum: float
    maximum: float

    def __post_init__(self) -> None:
        if self.minimum >= self.maximum:
            raise ValueError("minimum deve ser menor que maximum")

    def contains(self, value: float) -> bool:
        return self.minimum <= value <= self.maximum


DEFAULT_RANGES: Mapping[SensorKind, PlausibilityRange] = MappingProxyType(
    {
        SensorKind.PH: PlausibilityRange(0.0, 14.0),
        SensorKind.EC: PlausibilityRange(0.0, 20.0),
        SensorKind.WATER_TEMPERATURE: PlausibilityRange(0.0, 60.0),
        SensorKind.AIR_TEMPERATURE: PlausibilityRange(-20.0, 80.0),
        SensorKind.LEAF_TEMPERATURE: PlausibilityRange(-20.0, 100.0),
        SensorKind.HUMIDITY: PlausibilityRange(0.0, 100.0),
        SensorKind.CO2: PlausibilityRange(0.0, 10_000.0),
        SensorKind.RESERVOIR_LEVEL: PlausibilityRange(0.0, 10_000.0),
        SensorKind.MASS: PlausibilityRange(-5.0, 100.0),
        SensorKind.VPD: PlausibilityRange(-5.0, 10.0),
        SensorKind.FLOW: PlausibilityRange(0.0, 1_000.0),
        SensorKind.LEAK: PlausibilityRange(0.0, 1.0),
    }
)


class ReadingValidator:
    def __init__(
        self,
        ranges: Mapping[SensorKind, PlausibilityRange] = DEFAULT_RANGES,
    ) -> None:
        missing = set(SensorKind) - set(ranges)
        if missing:
            names = ", ".join(sorted(item.value for item in missing))
            raise ValueError(f"faixas ausentes: {names}")
        self._ranges = MappingProxyType(dict(ranges))

    def validate(self, reading: SensorReading) -> SensorReading:
        """Marca a qualidade; o valor bruto permanece disponível para auditoria."""
        if reading.quality is not ReadingQuality.VALID:
            return reading
        if self._ranges[reading.kind].contains(reading.value):
            return reading
        return replace(
            reading,
            quality=ReadingQuality.INVALID,
            error_code="out_of_plausible_range",
        )
