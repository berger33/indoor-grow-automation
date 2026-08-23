"""Taxonomia estável para falhas observadas na aquisição de sensores."""

from __future__ import annotations

from dataclasses import replace
from enum import StrEnum
from types import MappingProxyType
from typing import Mapping

from .sensors import ReadingQuality, SensorReading


class SensorFaultCode(StrEnum):
    TIMEOUT = "sensor_timeout"
    CRC_MISMATCH = "crc_mismatch"
    DISCONNECTED = "sensor_disconnected"
    CALIBRATION_REQUIRED = "calibration_required"
    SENSOR_NOT_READY = "sensor_not_ready"
    OUT_OF_RANGE = "out_of_sensor_range"
    PROTOCOL_ERROR = "sensor_protocol_error"


FAULT_QUALITY: Mapping[SensorFaultCode, ReadingQuality] = MappingProxyType(
    {
        SensorFaultCode.TIMEOUT: ReadingQuality.TIMEOUT,
        SensorFaultCode.CRC_MISMATCH: ReadingQuality.CRC_ERROR,
        SensorFaultCode.DISCONNECTED: ReadingQuality.DISCONNECTED,
        SensorFaultCode.CALIBRATION_REQUIRED: ReadingQuality.UNCALIBRATED,
        SensorFaultCode.SENSOR_NOT_READY: ReadingQuality.INVALID,
        SensorFaultCode.OUT_OF_RANGE: ReadingQuality.INVALID,
        SensorFaultCode.PROTOCOL_ERROR: ReadingQuality.INVALID,
    }
)


def mark_sensor_fault(
    reading: SensorReading,
    fault: SensorFaultCode,
) -> SensorReading:
    """Preserva valor/timestamp brutos e aplica uma falha canônica."""
    return replace(reading, quality=FAULT_QUALITY[fault], error_code=fault.value)
