"""Modelo conservador para temperatura foliar via MLX90614."""

from __future__ import annotations

import math
from dataclasses import dataclass

from ..domain.faults import SensorFaultCode


@dataclass(frozen=True, slots=True)
class MLX90614Result:
    leaf_temperature_c: float | None
    fault: SensorFaultCode | None = None


def decode_leaf_temperature(
    raw_object_c: float | None,
    *,
    offset_c: float = 0.0,
) -> MLX90614Result:
    if not -10.0 <= offset_c <= 10.0:
        raise ValueError("offset_c deve estar entre -10 e 10")
    if raw_object_c is None:
        return MLX90614Result(None, SensorFaultCode.TIMEOUT)
    value = float(raw_object_c)
    if not math.isfinite(value) or not -20.0 <= value <= 100.0:
        return MLX90614Result(value, SensorFaultCode.OUT_OF_RANGE)
    adjusted = value + offset_c
    if not -20.0 <= adjusted <= 100.0:
        return MLX90614Result(adjusted, SensorFaultCode.OUT_OF_RANGE)
    return MLX90614Result(adjusted)
