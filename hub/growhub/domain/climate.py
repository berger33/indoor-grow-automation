"""Cálculos e diagnósticos do subsistema climático."""

from __future__ import annotations

import math
from dataclasses import dataclass
from enum import StrEnum

from .sensors import ReadingQuality, SensorKind, SensorReading


class AgreementStatus(StrEnum):
    CONSISTENT = "consistent"
    DIVERGENT = "divergent"
    UNAVAILABLE = "unavailable"


@dataclass(frozen=True, slots=True)
class AgreementResult:
    status: AgreementStatus
    absolute_delta: float | None


def assess_sensor_agreement(
    first: SensorReading,
    second: SensorReading,
    *,
    maximum_delta: float,
) -> AgreementResult:
    if not math.isfinite(maximum_delta) or maximum_delta <= 0:
        raise ValueError("maximum_delta deve ser positivo e finito")
    if first.kind is not second.kind:
        raise ValueError("sensores comparados devem ter o mesmo tipo")
    if first.station_id != second.station_id:
        raise ValueError("sensores comparados devem pertencer à mesma estação")
    if first.quality is not ReadingQuality.VALID or second.quality is not ReadingQuality.VALID:
        return AgreementResult(AgreementStatus.UNAVAILABLE, None)
    delta = abs(first.value - second.value)
    status = (
        AgreementStatus.CONSISTENT
        if delta <= maximum_delta
        else AgreementStatus.DIVERGENT
    )
    return AgreementResult(status, delta)


@dataclass(frozen=True, slots=True)
class VPDResult:
    kilopascals: float
    condensation_risk: bool


def _saturation_vapor_pressure(temperature_c: float) -> float:
    return 0.6108 * math.exp((17.27 * temperature_c) / (temperature_c + 237.3))


def calculate_leaf_vpd(
    *,
    air_temperature_c: float,
    leaf_temperature_c: float,
    relative_humidity_percent: float,
) -> VPDResult:
    """Calcula VPD foliar preservando valor negativo como alerta de condensação."""
    for name, value in (
        ("air_temperature_c", air_temperature_c),
        ("leaf_temperature_c", leaf_temperature_c),
        ("relative_humidity_percent", relative_humidity_percent),
    ):
        if not math.isfinite(value):
            raise ValueError(f"{name} deve ser finito")
    if not -20.0 <= air_temperature_c <= 80.0:
        raise ValueError("temperatura do ar fora da faixa")
    if not -20.0 <= leaf_temperature_c <= 100.0:
        raise ValueError("temperatura foliar fora da faixa")
    if not 0.0 <= relative_humidity_percent <= 100.0:
        raise ValueError("umidade relativa fora da faixa")
    leaf_svp = _saturation_vapor_pressure(leaf_temperature_c)
    air_vapor_pressure = _saturation_vapor_pressure(air_temperature_c) * (
        relative_humidity_percent / 100.0
    )
    vpd = leaf_svp - air_vapor_pressure
    return VPDResult(vpd, vpd < 0.0)
