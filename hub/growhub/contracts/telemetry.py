"""Codec estrito do envelope MQTT de telemetria v1."""

from __future__ import annotations

import json
import uuid
from dataclasses import dataclass
from datetime import datetime
from typing import Any

from ..domain.sensors import ReadingQuality, SensorKind, SensorReading, Unit

SCHEMA_VERSION = 1
ENVELOPE_FIELDS = {
    "schema_version",
    "message_id",
    "station_id",
    "sequence",
    "sent_at",
    "reading",
}
READING_FIELDS = {
    "sensor_id",
    "kind",
    "value",
    "unit",
    "observed_at",
    "quality",
    "error_code",
}


def _timestamp(value: datetime) -> str:
    if value.tzinfo is None or value.utcoffset() is None:
        raise ValueError("timestamp deve conter timezone")
    return value.isoformat().replace("+00:00", "Z")


def _parse_timestamp(value: object, field: str) -> datetime:
    if not isinstance(value, str):
        raise ValueError(f"{field} deve ser string ISO-8601")
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError as exc:
        raise ValueError(f"{field} inválido") from exc
    if parsed.tzinfo is None or parsed.utcoffset() is None:
        raise ValueError(f"{field} deve conter timezone")
    return parsed


def _require_exact_fields(data: dict[str, Any], expected: set[str], name: str) -> None:
    missing = expected - set(data)
    extra = set(data) - expected
    if missing or extra:
        raise ValueError(
            f"campos inválidos em {name}: ausentes={sorted(missing)}, extras={sorted(extra)}"
        )


@dataclass(frozen=True, slots=True)
class TelemetryEnvelope:
    message_id: str
    sequence: int
    sent_at: datetime
    reading: SensorReading

    def __post_init__(self) -> None:
        try:
            parsed = uuid.UUID(self.message_id)
        except (ValueError, AttributeError) as exc:
            raise ValueError("message_id deve ser UUID") from exc
        if str(parsed) != self.message_id.lower():
            raise ValueError("message_id deve usar forma UUID canônica")
        if (
            isinstance(self.sequence, bool)
            or not isinstance(self.sequence, int)
            or self.sequence < 0
        ):
            raise ValueError("sequence deve ser inteiro não negativo")
        _timestamp(self.sent_at)

    def to_dict(self) -> dict[str, Any]:
        reading = self.reading
        return {
            "schema_version": SCHEMA_VERSION,
            "message_id": self.message_id,
            "station_id": reading.station_id,
            "sequence": self.sequence,
            "sent_at": _timestamp(self.sent_at),
            "reading": {
                "sensor_id": reading.sensor_id,
                "kind": reading.kind.value,
                "value": reading.value,
                "unit": reading.unit.value,
                "observed_at": _timestamp(reading.observed_at),
                "quality": reading.quality.value,
                "error_code": reading.error_code,
            },
        }

    def to_json(self) -> str:
        return json.dumps(self.to_dict(), separators=(",", ":"), ensure_ascii=False)

    @classmethod
    def from_json(cls, payload: str | bytes) -> TelemetryEnvelope:
        try:
            data = json.loads(payload)
        except (json.JSONDecodeError, UnicodeDecodeError) as exc:
            raise ValueError("JSON de telemetria inválido") from exc
        if not isinstance(data, dict):
            raise ValueError("envelope deve ser objeto JSON")
        _require_exact_fields(data, ENVELOPE_FIELDS, "envelope")
        if data["schema_version"] != SCHEMA_VERSION:
            raise ValueError("schema_version não suportada")
        if not isinstance(data["reading"], dict):
            raise ValueError("reading deve ser objeto")
        raw = data["reading"]
        _require_exact_fields(raw, READING_FIELDS, "reading")
        if isinstance(raw["value"], bool) or not isinstance(raw["value"], (int, float)):
            raise ValueError("reading.value deve ser número")
        reading = SensorReading(
            station_id=data["station_id"],
            sensor_id=raw["sensor_id"],
            kind=SensorKind(raw["kind"]),
            value=float(raw["value"]),
            unit=Unit(raw["unit"]),
            observed_at=_parse_timestamp(raw["observed_at"], "observed_at"),
            quality=ReadingQuality(raw["quality"]),
            error_code=raw["error_code"],
        )
        sequence = data["sequence"]
        if isinstance(sequence, bool) or not isinstance(sequence, int):
            raise ValueError("sequence deve ser inteiro")
        return cls(
            message_id=data["message_id"],
            sequence=sequence,
            sent_at=_parse_timestamp(data["sent_at"], "sent_at"),
            reading=reading,
        )
