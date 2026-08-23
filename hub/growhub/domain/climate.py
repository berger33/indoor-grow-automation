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
