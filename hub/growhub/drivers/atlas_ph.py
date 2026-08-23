"""Parser seguro de leituras do circuito Atlas EZO-pH."""

from __future__ import annotations

import math
from dataclasses import dataclass

from ..domain.faults import SensorFaultCode
from .atlas_ezo import status_fault


@dataclass(frozen=True, slots=True)
class AtlasPHResult:
    ph: float | None
    fault: SensorFaultCode | None = None


def decode_ph(status: int | None, payload: str | None) -> AtlasPHResult:
    fault = status_fault(status)
    if fault is not None:
        return AtlasPHResult(None, fault)
    try:
        value = float(payload) if payload is not None else math.nan
    except ValueError:
        return AtlasPHResult(None, SensorFaultCode.PROTOCOL_ERROR)
    if not math.isfinite(value) or not 0.0 <= value <= 14.0:
        return AtlasPHResult(value, SensorFaultCode.OUT_OF_RANGE)
    return AtlasPHResult(value)
