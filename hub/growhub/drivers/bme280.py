"""Modelo de leitura e compensação local do BME280."""

from __future__ import annotations

import math
from dataclasses import dataclass

from ..domain.faults import SensorFaultCode


@dataclass(frozen=True, slots=True)
class BME280Offsets:
    temperature_c: float = 0.0
    humidity_percent: float = 0.0

    def __post_init__(self) -> None:
        if not -10.0 <= self.temperature_c <= 10.0:
            raise ValueError("offset de temperatura fora do limite")
        if not -20.0 <= self.humidity_percent <= 20.0:
            raise ValueError("offset de umidade fora do limite")


@dataclass(frozen=True, slots=True)
class BME280Result:
    temperature_c: float | None
    humidity_percent: float | None
    fault: SensorFaultCode | None = None


def decode_environment(
    raw_temperature_c: float | None,
    raw_humidity_percent: float | None,
    offsets: BME280Offsets = BME280Offsets(),
) -> BME280Result:
    if raw_temperature_c is None or raw_humidity_percent is None:
        return BME280Result(None, None, SensorFaultCode.TIMEOUT)
    temperature = float(raw_temperature_c)
    humidity = float(raw_humidity_percent)
    if not math.isfinite(temperature) or not math.isfinite(humidity):
        return BME280Result(None, None, SensorFaultCode.OUT_OF_RANGE)
    if not -40.0 <= temperature <= 85.0 or not 0.0 <= humidity <= 100.0:
        return BME280Result(temperature, humidity, SensorFaultCode.OUT_OF_RANGE)
    adjusted_humidity = min(100.0, max(0.0, humidity + offsets.humidity_percent))
    return BME280Result(
        temperature + offsets.temperature_c,
        adjusted_humidity,
    )
