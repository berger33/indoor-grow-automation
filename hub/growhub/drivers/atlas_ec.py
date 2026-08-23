"""Parser seguro do primeiro campo de condutividade Atlas EZO-EC."""

from __future__ import annotations

import math
from dataclasses import dataclass

from ..domain.faults import SensorFaultCode
from .atlas_ezo import status_fault


@dataclass(frozen=True, slots=True)
class AtlasECResult:
    millisiemens_per_cm: float | None
    fault: SensorFaultCode | None = None


def decode_ec(status: int | None, payload: str | None) -> AtlasECResult:
    fault = status_fault(status)
    if fault is not None:
        return AtlasECResult(None, fault)
    first_field = payload.split(",", maxsplit=1)[0] if payload else ""
    try:
        microsiemens = float(first_field)
    except ValueError:
        return AtlasECResult(None, SensorFaultCode.PROTOCOL_ERROR)
    millisiemens = microsiemens / 1_000.0
    if not math.isfinite(millisiemens) or not 0.0 <= millisiemens <= 20.0:
        return AtlasECResult(millisiemens, SensorFaultCode.OUT_OF_RANGE)
    return AtlasECResult(millisiemens)
