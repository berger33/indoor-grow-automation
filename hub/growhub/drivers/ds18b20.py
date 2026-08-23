"""Interpretação segura das respostas do termômetro DS18B20."""

from __future__ import annotations

import math
from dataclasses import dataclass

from ..domain.faults import SensorFaultCode


@dataclass(frozen=True, slots=True)
class DS18B20Result:
    celsius: float | None
    fault: SensorFaultCode | None = None

    @property
    def valid(self) -> bool:
        return self.fault is None


def decode_temperature(raw_celsius: float | None) -> DS18B20Result:
    if raw_celsius is None:
        return DS18B20Result(None, SensorFaultCode.TIMEOUT)
    value = float(raw_celsius)
    if not math.isfinite(value):
        return DS18B20Result(None, SensorFaultCode.OUT_OF_RANGE)
    if value == -127.0:
        return DS18B20Result(None, SensorFaultCode.DISCONNECTED)
    if value == 85.0:
        return DS18B20Result(None, SensorFaultCode.SENSOR_NOT_READY)
    if not -55.0 <= value <= 125.0:
        return DS18B20Result(value, SensorFaultCode.OUT_OF_RANGE)
    return DS18B20Result(value)
