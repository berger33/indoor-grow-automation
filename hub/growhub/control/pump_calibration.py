"""Curva calibrada que converte volume em tempo para cada dosadora."""

from __future__ import annotations

import math
from dataclasses import dataclass
from datetime import datetime


@dataclass(frozen=True, slots=True)
class CalibrationPoint:
    duration_s: float
    volume_ml: float

    def __post_init__(self) -> None:
        if (
            not math.isfinite(self.duration_s)
            or not math.isfinite(self.volume_ml)
            or self.duration_s <= 0
            or self.volume_ml <= 0
        ):
            raise ValueError("ponto de calibração deve ser finito e positivo")


@dataclass(frozen=True, slots=True)
class PumpCalibration:
    pump_id: str
    flow_ml_s: float
    supply_voltage_v: float
    calibrated_at: datetime
    maximum_relative_error: float

    @classmethod
    def fit(
        cls,
        pump_id: str,
        points: tuple[CalibrationPoint, ...],
        *,
        supply_voltage_v: float,
        calibrated_at: datetime,
        allowed_relative_error: float = 0.10,
    ) -> PumpCalibration:
        if not pump_id or pump_id.isspace():
            raise ValueError("pump_id é obrigatório")
        if len(points) < 3 or len({point.duration_s for point in points}) < 3:
            raise ValueError("calibração exige três durações distintas")
        if not math.isfinite(supply_voltage_v) or not 5 <= supply_voltage_v <= 24:
            raise ValueError("tensão de calibração deve estar entre 5 e 24 V")
        if calibrated_at.tzinfo is None or calibrated_at.utcoffset() is None:
            raise ValueError("calibrated_at deve conter timezone")
        if (
            not math.isfinite(allowed_relative_error)
            or not 0 < allowed_relative_error <= 0.50
        ):
            raise ValueError("erro permitido deve estar entre 0 e 50%")

        denominator = sum(point.duration_s**2 for point in points)
        flow_ml_s = sum(
            point.duration_s * point.volume_ml for point in points
        ) / denominator
        errors = tuple(
            abs(flow_ml_s * point.duration_s - point.volume_ml) / point.volume_ml
            for point in points
        )
        maximum_error = max(errors)
        if maximum_error > allowed_relative_error:
            raise ValueError("repetibilidade da bomba excede o limite")
        return cls(
            pump_id=pump_id,
            flow_ml_s=flow_ml_s,
            supply_voltage_v=supply_voltage_v,
            calibrated_at=calibrated_at,
            maximum_relative_error=maximum_error,
        )

    def duration_for(self, volume_ml: float, *, maximum_s: float = 60) -> float:
        if not math.isfinite(volume_ml) or volume_ml <= 0:
            raise ValueError("volume deve ser finito e positivo")
        if not math.isfinite(maximum_s) or maximum_s <= 0:
            raise ValueError("maximum_s deve ser finito e positivo")
        duration = volume_ml / self.flow_ml_s
        if duration > maximum_s:
            raise ValueError("volume excede o tempo máximo da bomba")
        return duration

    def volume_for(self, duration_s: float) -> float:
        if not math.isfinite(duration_s) or duration_s <= 0:
            raise ValueError("duração deve ser finita e positiva")
        return duration_s * self.flow_ml_s
