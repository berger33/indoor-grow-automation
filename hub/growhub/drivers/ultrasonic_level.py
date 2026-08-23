"""Estimativa filtrada de nível por distância ultrassônica."""

from __future__ import annotations

import math
from dataclasses import dataclass

from ..domain.faults import SensorFaultCode
from ..domain.filters import MedianFilter


@dataclass(frozen=True, slots=True)
class TankGeometry:
    full_distance_cm: float
    empty_distance_cm: float
    capacity_liters: float
    sensor_min_cm: float = 2.0
    sensor_max_cm: float = 400.0

    def __post_init__(self) -> None:
        values = (
            self.full_distance_cm,
            self.empty_distance_cm,
            self.capacity_liters,
            self.sensor_min_cm,
            self.sensor_max_cm,
        )
        if not all(math.isfinite(value) for value in values):
            raise ValueError("geometria deve conter valores finitos")
        if not self.sensor_min_cm <= self.full_distance_cm < self.empty_distance_cm:
            raise ValueError("distâncias de cheio/vazio inválidas")
        if self.empty_distance_cm > self.sensor_max_cm or self.capacity_liters <= 0:
            raise ValueError("geometria fora da zona útil do sensor")


@dataclass(frozen=True, slots=True)
class LevelResult:
    liters: float | None
    filtered_distance_cm: float | None
    fault: SensorFaultCode | None = None


class UltrasonicLevelEstimator:
    def __init__(self, geometry: TankGeometry, *, window_size: int = 5) -> None:
        self._geometry = geometry
        self._filter = MedianFilter(window_size)

    def update(self, distance_cm: float | None) -> LevelResult:
        if distance_cm is None:
            return LevelResult(None, None, SensorFaultCode.TIMEOUT)
        distance = float(distance_cm)
        if (
            not math.isfinite(distance)
            or distance < self._geometry.sensor_min_cm
            or distance > self._geometry.sensor_max_cm
        ):
            return LevelResult(None, distance, SensorFaultCode.OUT_OF_RANGE)
        filtered = self._filter.add(distance)
        span = self._geometry.empty_distance_cm - self._geometry.full_distance_cm
        fraction = (self._geometry.empty_distance_cm - filtered) / span
        liters = self._geometry.capacity_liters * min(1.0, max(0.0, fraction))
        return LevelResult(liters, filtered)
