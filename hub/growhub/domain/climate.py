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


class ExhaustReason(StrEnum):
    HOLD = "hold"
    TEMPERATURE_HIGH = "temperature_high"
    HUMIDITY_HIGH = "humidity_high"
    ABSOLUTE_LIMIT = "absolute_limit"
    SENSOR_FAILSAFE = "sensor_failsafe"
    CONTROLLER_FAILSAFE = "controller_failsafe"
    BELOW_LOW_THRESHOLD = "below_low_threshold"


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


@dataclass(frozen=True, slots=True)
class ExhaustPolicy:
    temperature_target_c: float
    humidity_target_percent: float
    absolute_temperature_c: float
    absolute_humidity_percent: float
    low_level: int = 1
    high_level: int = 7
    emergency_level: int = 10
    fail_safe_level: int = 7
    temperature_high_delta_c: float = 2.0
    temperature_low_delta_c: float = 1.0
    humidity_high_delta_percent: float = 5.0

    def __post_init__(self) -> None:
        numeric = (
            self.temperature_target_c,
            self.humidity_target_percent,
            self.absolute_temperature_c,
            self.absolute_humidity_percent,
            self.temperature_high_delta_c,
            self.temperature_low_delta_c,
            self.humidity_high_delta_percent,
        )
        if any(not math.isfinite(value) for value in numeric):
            raise ValueError("parâmetros climáticos devem ser finitos")
        if not 0 <= self.humidity_target_percent < self.absolute_humidity_percent <= 100:
            raise ValueError("limites de umidade incoerentes")
        if self.absolute_temperature_c <= self.temperature_target_c:
            raise ValueError("limite absoluto deve superar alvo de temperatura")
        if any(value <= 0 for value in (
            self.temperature_high_delta_c,
            self.temperature_low_delta_c,
            self.humidity_high_delta_percent,
        )):
            raise ValueError("deltas devem ser positivos")
        if any(not 0 <= level <= 10 for level in (
            self.low_level,
            self.high_level,
            self.emergency_level,
            self.fail_safe_level,
        )):
            raise ValueError("níveis do exaustor devem estar entre 0 e 10")
        if not self.low_level <= self.high_level <= self.emergency_level:
            raise ValueError("níveis do exaustor fora de ordem")
        if self.fail_safe_level == 0:
            raise ValueError("fail-safe do exaustor não pode ser zero")


@dataclass(frozen=True, slots=True)
class ExhaustDecision:
    level: int
    reason: ExhaustReason


def select_exhaust_level(
    policy: ExhaustPolicy,
    *,
    temperature_c: tuple[float, float] | None,
    humidity_percent: tuple[float, float] | None,
    current_level: int,
    sensors_agree: bool,
    controller_online: bool,
) -> ExhaustDecision:
    """Replica os degraus do original, mas nunca usa zero como fail-safe."""
    if not 0 <= current_level <= 10:
        raise ValueError("current_level deve estar entre 0 e 10")
    if not controller_online:
        return ExhaustDecision(policy.fail_safe_level, ExhaustReason.CONTROLLER_FAILSAFE)
    if temperature_c is None or humidity_percent is None or not sensors_agree:
        return ExhaustDecision(policy.fail_safe_level, ExhaustReason.SENSOR_FAILSAFE)
    values = (*temperature_c, *humidity_percent)
    if any(not math.isfinite(value) for value in values):
        return ExhaustDecision(policy.fail_safe_level, ExhaustReason.SENSOR_FAILSAFE)
    if any(value >= policy.absolute_temperature_c for value in temperature_c) or any(
        value >= policy.absolute_humidity_percent for value in humidity_percent
    ):
        return ExhaustDecision(policy.emergency_level, ExhaustReason.ABSOLUTE_LIMIT)
    if all(
        value >= policy.temperature_target_c + policy.temperature_high_delta_c
        for value in temperature_c
    ):
        return ExhaustDecision(policy.high_level, ExhaustReason.TEMPERATURE_HIGH)
    if all(
        value >= policy.humidity_target_percent + policy.humidity_high_delta_percent
        for value in humidity_percent
    ):
        return ExhaustDecision(policy.high_level, ExhaustReason.HUMIDITY_HIGH)
    if all(
        value <= policy.temperature_target_c - policy.temperature_low_delta_c
        for value in temperature_c
    ) and all(value <= policy.humidity_target_percent for value in humidity_percent):
        return ExhaustDecision(policy.low_level, ExhaustReason.BELOW_LOW_THRESHOLD)
    return ExhaustDecision(current_level, ExhaustReason.HOLD)


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
