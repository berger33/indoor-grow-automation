"""Decodificação compartilhada dos códigos de resposta Atlas EZO."""

from __future__ import annotations

from enum import IntEnum

from ..domain.faults import SensorFaultCode


class AtlasStatus(IntEnum):
    SUCCESS = 1
    SYNTAX_ERROR = 2
    PROCESSING = 254
    NO_DATA = 255


def status_fault(status: int | None) -> SensorFaultCode | None:
    if status is None:
        return SensorFaultCode.TIMEOUT
    try:
        parsed = AtlasStatus(status)
    except ValueError:
        return SensorFaultCode.PROTOCOL_ERROR
    return {
        AtlasStatus.SUCCESS: None,
        AtlasStatus.SYNTAX_ERROR: SensorFaultCode.PROTOCOL_ERROR,
        AtlasStatus.PROCESSING: SensorFaultCode.SENSOR_NOT_READY,
        AtlasStatus.NO_DATA: SensorFaultCode.DISCONNECTED,
    }[parsed]
