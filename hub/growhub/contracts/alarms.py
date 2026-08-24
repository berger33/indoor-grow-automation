"""Envelope MQTT v1 estrito para alarmes retidos pelo firmware."""

from __future__ import annotations

import json
import uuid
from dataclasses import dataclass
from datetime import datetime
from enum import StrEnum

from ..domain.sensors import IDENTIFIER


class AlarmSeverity(StrEnum):
    WARNING = "warning"
    CRITICAL = "critical"


@dataclass(frozen=True, slots=True)
class AlarmEnvelope:
    alarm_id: str
    station_id: str
    code: str
    severity: AlarmSeverity
    cause: str
    procedure: str
    raised_at: datetime
    latched: bool = True
    schema_version: int = 1

    def __post_init__(self) -> None:
        try:
            canonical = str(uuid.UUID(self.alarm_id))
        except (ValueError, AttributeError) as exc:
            raise ValueError("alarm_id deve ser UUID") from exc
        if canonical != self.alarm_id.lower():
            raise ValueError("alarm_id deve ser UUID canônico")
        if self.schema_version != 1:
            raise ValueError("schema de alarme não suportado")
        if IDENTIFIER.fullmatch(self.station_id) is None or IDENTIFIER.fullmatch(self.code) is None:
            raise ValueError("estação ou código de alarme inválido")
        if not isinstance(self.severity, AlarmSeverity):
            raise ValueError("severidade de alarme inválida")
        if not self.cause.strip() or len(self.cause) > 500:
            raise ValueError("causa de alarme inválida")
        if not self.procedure.strip() or len(self.procedure) > 1_000:
            raise ValueError("procedimento de alarme inválido")
        if self.raised_at.tzinfo is None or self.raised_at.utcoffset() is None:
            raise ValueError("raised_at deve conter timezone")
        if self.latched is not True:
            raise ValueError("alarmes MQTT devem ser retidos até reconhecimento")

    def to_json(self) -> str:
        return json.dumps(
            {
                "schema_version": self.schema_version,
                "alarm_id": self.alarm_id,
                "station_id": self.station_id,
                "code": self.code,
                "severity": self.severity.value,
                "cause": self.cause,
                "procedure": self.procedure,
                "raised_at": self.raised_at.isoformat(),
                "latched": self.latched,
            },
            ensure_ascii=False,
            separators=(",", ":"),
            sort_keys=True,
        )

    @classmethod
    def from_json(cls, payload: str | bytes) -> AlarmEnvelope:
        try:
            raw = json.loads(payload)
        except (json.JSONDecodeError, UnicodeDecodeError) as exc:
            raise ValueError("JSON de alarme inválido") from exc
        expected = {
            "schema_version",
            "alarm_id",
            "station_id",
            "code",
            "severity",
            "cause",
            "procedure",
            "raised_at",
            "latched",
        }
        if not isinstance(raw, dict) or set(raw) != expected:
            raise ValueError("estrutura de alarme inválida")
        try:
            raised_at = datetime.fromisoformat(raw["raised_at"].replace("Z", "+00:00"))
            severity = AlarmSeverity(raw["severity"])
        except (AttributeError, ValueError) as exc:
            raise ValueError("campos de alarme inválidos") from exc
        return cls(
            alarm_id=raw["alarm_id"],
            station_id=raw["station_id"],
            code=raw["code"],
            severity=severity,
            cause=raw["cause"],
            procedure=raw["procedure"],
            raised_at=raised_at,
            latched=raw["latched"],
            schema_version=raw["schema_version"],
        )
