"""Comandos MQTT v1 com ACK/NACK idempotente e proteção contra replay."""

from __future__ import annotations

import json
import uuid
from dataclasses import dataclass
from datetime import datetime
from enum import StrEnum
from typing import Callable, Mapping

from ..domain.sensors import IDENTIFIER

PARAMETER_TYPES = (str, int, float, bool)


def _aware(value: datetime, name: str) -> None:
    if value.tzinfo is None or value.utcoffset() is None:
        raise ValueError(f"{name} deve conter timezone")


class AckStatus(StrEnum):
    ACK = "ack"
    NACK = "nack"


@dataclass(frozen=True, slots=True)
class CommandEnvelope:
    command_id: str
    station_id: str
    node_id: str
    function: str
    action: str
    sequence: int
    issued_at: datetime
    expires_at: datetime
    parameters: Mapping[str, str | int | float | bool]
    schema_version: int = 1

    def __post_init__(self) -> None:
        try:
            canonical = str(uuid.UUID(self.command_id))
        except (ValueError, AttributeError) as exc:
            raise ValueError("command_id deve ser UUID") from exc
        if canonical != self.command_id.lower():
            raise ValueError("command_id deve ser UUID canônico")
        for name, value in (
            ("station_id", self.station_id),
            ("node_id", self.node_id),
            ("function", self.function),
            ("action", self.action),
        ):
            if IDENTIFIER.fullmatch(value) is None:
                raise ValueError(f"{name} inválido")
        if self.schema_version != 1:
            raise ValueError("schema de comando não suportado")
        if isinstance(self.sequence, bool) or not isinstance(self.sequence, int) or self.sequence < 0:
            raise ValueError("sequence deve ser inteiro não negativo")
        _aware(self.issued_at, "issued_at")
        _aware(self.expires_at, "expires_at")
        if self.expires_at <= self.issued_at:
            raise ValueError("expires_at deve ser posterior a issued_at")
        for key, value in self.parameters.items():
            if IDENTIFIER.fullmatch(key) is None or not isinstance(value, PARAMETER_TYPES):
                raise ValueError("parâmetro de comando inválido")

    def to_json(self) -> str:
        return json.dumps(
            {
                "schema_version": 1,
                "command_id": self.command_id,
                "station_id": self.station_id,
                "node_id": self.node_id,
                "function": self.function,
                "action": self.action,
                "sequence": self.sequence,
                "issued_at": self.issued_at.isoformat(),
                "expires_at": self.expires_at.isoformat(),
                "parameters": dict(self.parameters),
            },
            ensure_ascii=False,
            separators=(",", ":"),
            sort_keys=True,
        )

    @classmethod
    def from_json(cls, payload: str | bytes) -> CommandEnvelope:
        try:
            raw = json.loads(payload)
        except (json.JSONDecodeError, UnicodeDecodeError) as exc:
            raise ValueError("JSON de comando inválido") from exc
        expected = {
            "schema_version", "command_id", "station_id", "node_id", "function",
            "action", "sequence", "issued_at", "expires_at", "parameters",
        }
        if not isinstance(raw, dict) or set(raw) != expected or not isinstance(raw["parameters"], dict):
            raise ValueError("estrutura de comando inválida")
        try:
            issued_at = datetime.fromisoformat(raw["issued_at"].replace("Z", "+00:00"))
            expires_at = datetime.fromisoformat(raw["expires_at"].replace("Z", "+00:00"))
        except (AttributeError, ValueError) as exc:
            raise ValueError("timestamp de comando inválido") from exc
        return cls(**{**raw, "issued_at": issued_at, "expires_at": expires_at})


@dataclass(frozen=True, slots=True)
class CommandAcknowledgement:
    command_id: str
    sequence: int
    status: AckStatus
    reason: str
    handled_at: datetime

    def __post_init__(self) -> None:
        try:
            canonical = str(uuid.UUID(self.command_id))
        except (ValueError, AttributeError) as exc:
            raise ValueError("command_id de ACK/NACK deve ser UUID") from exc
        if canonical != self.command_id.lower():
            raise ValueError("command_id de ACK/NACK deve ser UUID canônico")
        if isinstance(self.sequence, bool) or not isinstance(self.sequence, int) or self.sequence < 0:
            raise ValueError("sequence de ACK/NACK deve ser inteiro não negativo")
        if not isinstance(self.status, AckStatus):
            raise ValueError("status de ACK/NACK inválido")
        _aware(self.handled_at, "handled_at")
        if IDENTIFIER.fullmatch(self.reason) is None:
            raise ValueError("reason de ACK/NACK inválido")

    def to_json(self) -> str:
        return json.dumps(
            {
                "schema_version": 1,
                "command_id": self.command_id,
                "sequence": self.sequence,
                "status": self.status.value,
                "reason": self.reason,
                "handled_at": self.handled_at.isoformat(),
            },
            ensure_ascii=False,
            separators=(",", ":"),
            sort_keys=True,
        )

    @classmethod
    def from_json(cls, payload: str | bytes) -> CommandAcknowledgement:
        try:
            raw = json.loads(payload)
        except (json.JSONDecodeError, UnicodeDecodeError) as exc:
            raise ValueError("JSON de ACK/NACK inválido") from exc
        expected = {
            "schema_version",
            "command_id",
            "sequence",
            "status",
            "reason",
            "handled_at",
        }
        if not isinstance(raw, dict) or set(raw) != expected or raw["schema_version"] != 1:
            raise ValueError("estrutura de ACK/NACK inválida")
        try:
            handled_at = datetime.fromisoformat(raw["handled_at"].replace("Z", "+00:00"))
            ack_status = AckStatus(raw["status"])
        except (AttributeError, ValueError) as exc:
            raise ValueError("campos de ACK/NACK inválidos") from exc
        return cls(
            command_id=raw["command_id"],
            sequence=raw["sequence"],
            status=ack_status,
            reason=raw["reason"],
            handled_at=handled_at,
        )


class IdempotentCommandProcessor:
    """Executa cada UUID uma vez e rejeita sequência repetida ou expirada."""

    def __init__(self) -> None:
        self._last_sequence: dict[tuple[str, str], int] = {}
        self._responses: dict[str, CommandAcknowledgement] = {}

    def process(
        self,
        command: CommandEnvelope,
        *,
        now: datetime,
        execute: Callable[[CommandEnvelope], tuple[bool, str]],
    ) -> CommandAcknowledgement:
        _aware(now, "now")
        cached = self._responses.get(command.command_id)
        if cached is not None:
            return cached
        key = (command.station_id, command.node_id)
        last_sequence = self._last_sequence.get(key, -1)
        if command.sequence <= last_sequence:
            return self._remember(command, now, AckStatus.NACK, "sequence_replayed")
        self._last_sequence[key] = command.sequence
        if now > command.expires_at:
            return self._remember(command, now, AckStatus.NACK, "command_expired")
        if command.issued_at > now:
            return self._remember(command, now, AckStatus.NACK, "issued_in_future")
        accepted, reason = execute(command)
        return self._remember(
            command,
            now,
            AckStatus.ACK if accepted else AckStatus.NACK,
            reason,
        )

    def _remember(
        self,
        command: CommandEnvelope,
        now: datetime,
        status: AckStatus,
        reason: str,
    ) -> CommandAcknowledgement:
        response = CommandAcknowledgement(
            command_id=command.command_id,
            sequence=command.sequence,
            status=status,
            reason=reason,
            handled_at=now,
        )
        self._responses[command.command_id] = response
        return response
