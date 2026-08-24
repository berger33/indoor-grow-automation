"""Diagnóstico consolidado de qualidade e idade de leituras."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from enum import StrEnum

from .sensors import ReadingQuality, SensorReading
from .staleness import StalenessPolicy


class DiagnosticState(StrEnum):
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    FAILED = "failed"


@dataclass(frozen=True, slots=True)
class ReadingDiagnostic:
    sensor_id: str
    state: DiagnosticState
    quality: ReadingQuality
    age_seconds: float
    reason: str


def diagnose_reading(
    reading: SensorReading,
    *,
    now: datetime,
    staleness: StalenessPolicy | None = None,
) -> ReadingDiagnostic:
    if now.tzinfo is None or now.utcoffset() is None:
        raise ValueError("now deve conter timezone")
    if now < reading.observed_at:
        raise ValueError("now não pode anteceder observed_at")
    effective = (staleness or StalenessPolicy()).apply(reading, now=now)
    if effective.quality is ReadingQuality.VALID:
        state = DiagnosticState.HEALTHY
        reason = "reading_valid"
    elif effective.quality in {ReadingQuality.STALE, ReadingQuality.UNCALIBRATED}:
        state = DiagnosticState.DEGRADED
        reason = effective.error_code or effective.quality.value
    else:
        state = DiagnosticState.FAILED
        reason = effective.error_code or effective.quality.value
    return ReadingDiagnostic(
        sensor_id=effective.sensor_id,
        state=state,
        quality=effective.quality,
        age_seconds=(now - effective.observed_at).total_seconds(),
        reason=reason,
    )
