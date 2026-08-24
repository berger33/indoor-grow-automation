"""Gateway MQTT TLS entre os nós ESP32, PostgreSQL e a API local."""

from __future__ import annotations

import asyncio
import ssl
from dataclasses import dataclass
from datetime import UTC, datetime, timedelta
from pathlib import Path
from typing import Protocol

import paho.mqtt.client as mqtt

from ..contracts.alarms import AlarmEnvelope
from ..contracts.commands import AckStatus, CommandAcknowledgement, CommandEnvelope
from ..contracts.telemetry import TelemetryEnvelope
from ..contracts.topics import MqttTopic, TopicDirection, command_topic
from .operations import AlarmRecord, InMemoryOperations
from .realtime import RealtimeBuffer


class MqttUnavailable(RuntimeError):
    """Indica que um comando não foi publicado e não pode ser presumido em fila."""


class TelemetryRepository(Protocol):
    def save(self, envelope: TelemetryEnvelope, *, received_at: datetime) -> bool: ...


@dataclass(frozen=True, slots=True)
class MqttConnectionSettings:
    host: str
    port: int
    ca_cert: Path
    client_cert: Path
    client_key: Path
    client_id: str = "grow-hub"
    keepalive_seconds: int = 30

    def __post_init__(self) -> None:
        if not self.host.strip() or not 1 <= self.port <= 65_535:
            raise ValueError("endereço do broker MQTT inválido")
        if not self.client_id.strip() or not 10 <= self.keepalive_seconds <= 300:
            raise ValueError("identidade ou keepalive MQTT inválido")


@dataclass(frozen=True, slots=True)
class PendingCommand:
    envelope: CommandEnvelope
    audit_id: str


COMMAND_ROUTES = {
    "start_batch": ("fertigation", "batch"),
    "stop_batch": ("fertigation", "batch"),
    "start_irrigation": ("fertigation", "irrigation"),
    "stop_irrigation": ("fertigation", "irrigation"),
    "safe_stop": ("safety", "emergency"),
}


class MqttGateway:
    """Publica comandos somente conectado e processa mensagens estritas da árvore v1."""

    def __init__(
        self,
        settings: MqttConnectionSettings,
        operations: InMemoryOperations,
        telemetry: TelemetryRepository,
        realtime: RealtimeBuffer,
        *,
        sensor_nodes: dict[tuple[str, str], str] | None = None,
        client: mqtt.Client | None = None,
        clock=lambda: datetime.now(UTC),
    ) -> None:
        self.settings = settings
        self.operations = operations
        self.telemetry = telemetry
        self.realtime = realtime
        self.sensor_nodes = dict(sensor_nodes or {})
        self.clock = clock
        self._client = client or self._secure_client(settings)
        self._loop: asyncio.AbstractEventLoop | None = None
        self._pending: dict[str, PendingCommand] = {}
        sequences = (
            int(record.details.get("sequence", -1))
            for record in operations.audit
            if isinstance(record.details.get("sequence"), int)
        )
        self._last_sequence = max(sequences, default=-1)
        self.last_error: str | None = "mqtt_not_started"
        self._client.on_connect = self._on_connect
        self._client.on_disconnect = self._on_disconnect
        self._client.on_message = self._on_message
        self._client.reconnect_delay_set(min_delay=1, max_delay=30)

    @staticmethod
    def _secure_client(settings: MqttConnectionSettings) -> mqtt.Client:
        missing = [str(path) for path in (settings.ca_cert, settings.client_cert, settings.client_key) if not path.is_file()]
        if missing:
            raise RuntimeError(f"certificado MQTT obrigatório ausente: {', '.join(missing)}")
        client = mqtt.Client(
            callback_api_version=mqtt.CallbackAPIVersion.VERSION2,
            client_id=settings.client_id,
            protocol=mqtt.MQTTv5,
        )
        client.tls_set(
            ca_certs=str(settings.ca_cert),
            certfile=str(settings.client_cert),
            keyfile=str(settings.client_key),
            tls_version=ssl.PROTOCOL_TLS_CLIENT,
        )
        client.tls_insecure_set(False)
        return client

    @property
    def connected(self) -> bool:
        return bool(self._client.is_connected())

    def health(self) -> dict[str, object]:
        return {
            "status": "connected" if self.connected else "disconnected",
            "pendingCommands": len(self._pending),
            "lastError": self.last_error,
        }

    def start(self, loop: asyncio.AbstractEventLoop) -> None:
        self._loop = loop
        self._client.connect_async(
            self.settings.host,
            self.settings.port,
            keepalive=self.settings.keepalive_seconds,
        )
        self._client.loop_start()

    def stop(self) -> None:
        self._client.disconnect()
        self._client.loop_stop()
        self._loop = None

    def dispatch(
        self,
        *,
        audit_id: str,
        station_id: str,
        action: str,
        target: str,
        now: datetime,
    ) -> CommandEnvelope:
        if not self.connected:
            raise MqttUnavailable("broker MQTT desconectado; comando não foi enviado")
        try:
            node_id, function = COMMAND_ROUTES[action]
        except KeyError as exc:
            raise ValueError("ação sem rota MQTT aprovada") from exc
        epoch_sequence = int(now.timestamp() * 1_000_000)
        sequence = max(self._last_sequence + 1, epoch_sequence)
        envelope = CommandEnvelope(
            command_id=audit_id,
            station_id=station_id,
            node_id=node_id,
            function=function,
            action=action,
            sequence=sequence,
            issued_at=now,
            expires_at=now + timedelta(seconds=15),
            parameters={"target": target},
        )
        result = self._client.publish(
            command_topic(station_id, node_id, function),
            envelope.to_json(),
            qos=1,
            retain=False,
        )
        result_code = result.rc if hasattr(result, "rc") else result[0]
        if result_code != mqtt.MQTT_ERR_SUCCESS:
            self.last_error = f"mqtt_publish_rc_{result_code}"
            raise MqttUnavailable("broker recusou a publicação; comando não foi enviado")
        self._last_sequence = sequence
        self._pending[envelope.command_id] = PendingCommand(envelope, audit_id)
        self.operations.update_audit_status(
            audit_id,
            "sent",
            now=now,
            commandId=envelope.command_id,
            sequence=sequence,
            nodeId=node_id,
            function=function,
            expiresAt=envelope.expires_at.isoformat(),
        )
        return envelope

    def handle_message(self, topic_value: str, payload: str | bytes, *, received_at: datetime) -> bool:
        topic = MqttTopic.parse(topic_value)
        if topic.direction is TopicDirection.TELEMETRY:
            return self._handle_telemetry(topic, payload, received_at)
        if topic.direction is TopicDirection.ALARM:
            return self._handle_alarm(topic, payload)
        if topic.direction is TopicDirection.ACK:
            return self._handle_ack(topic, payload)
        raise ValueError("direção MQTT não consumida pelo hub")

    def _handle_telemetry(self, topic: MqttTopic, payload: str | bytes, received_at: datetime) -> bool:
        envelope = TelemetryEnvelope.from_json(payload)
        reading = envelope.reading
        if reading.station_id != topic.station_id or reading.sensor_id != topic.function:
            raise ValueError("tópico e envelope de telemetria divergem")
        if (reading.station_id, reading.sensor_id) not in self.operations.sensors:
            raise ValueError("sensor MQTT não cadastrado")
        expected_node = self.sensor_nodes.get((reading.station_id, reading.sensor_id))
        if expected_node is not None and expected_node != topic.node_id:
            raise ValueError("nó MQTT não é proprietário do sensor")
        inserted = self.telemetry.save(envelope, received_at=received_at)
        if not inserted:
            return False
        self.operations.record_reading(reading)
        self._emit(
            "sensor.updated",
            reading.station_id,
            reading.observed_at,
            {
                "sensorId": reading.sensor_id,
                "value": reading.value,
                "unit": reading.unit.value,
                "quality": reading.quality.value,
            },
        )
        return True

    def _handle_alarm(self, topic: MqttTopic, payload: str | bytes) -> bool:
        envelope = AlarmEnvelope.from_json(payload)
        if envelope.station_id != topic.station_id or envelope.code != topic.function:
            raise ValueError("tópico e envelope de alarme divergem")
        inserted = self.operations.save_alarm(
            AlarmRecord(
                envelope.alarm_id,
                envelope.station_id,
                envelope.code,
                envelope.severity.value,
                envelope.cause,
                envelope.procedure,
                envelope.raised_at,
                envelope.latched,
            )
        )
        if inserted:
            self._emit(
                "alarm.raised",
                envelope.station_id,
                envelope.raised_at,
                {"alarmId": envelope.alarm_id, "code": envelope.code, "severity": envelope.severity.value},
            )
        return inserted

    def _handle_ack(self, topic: MqttTopic, payload: str | bytes) -> bool:
        acknowledgement = CommandAcknowledgement.from_json(payload)
        pending = self._pending.get(acknowledgement.command_id)
        if pending is None:
            return False
        command = pending.envelope
        if (
            acknowledgement.sequence != command.sequence
            or topic.station_id != command.station_id
            or topic.node_id != command.node_id
            or topic.function != command.function
        ):
            raise ValueError("ACK/NACK não corresponde ao comando pendente")
        del self._pending[acknowledgement.command_id]
        status = acknowledgement.status.value
        record = self.operations.update_audit_status(
            pending.audit_id,
            status,
            now=acknowledgement.handled_at,
            reason=acknowledgement.reason,
        )
        self._update_batch(record.action, record.station_id, record.audit_id, acknowledgement)
        self._emit(
            "command.acknowledged",
            record.station_id,
            acknowledgement.handled_at,
            {"auditId": record.audit_id, "status": status, "reason": acknowledgement.reason},
        )
        return True

    def _update_batch(
        self,
        action: str,
        station_id: str,
        audit_id: str,
        acknowledgement: CommandAcknowledgement,
    ) -> None:
        accepted = acknowledgement.status is AckStatus.ACK
        if action == "start_batch" and audit_id in self.operations.batch_runs:
            run = self.operations.batch_runs[audit_id]
            run.status = "running" if accepted else "failed"
            run.current_step = "firmware_ack" if accepted else "nack"
            run.failure_code = None if accepted else acknowledgement.reason
            run.finished_at = None if accepted else acknowledgement.handled_at
            self.operations.save_batch_run(run)
        elif action == "stop_batch":
            for run in self.operations.batch_runs.values():
                if run.station_id != station_id or run.status != "stop_queued":
                    continue
                run.status = "stopped" if accepted else "stop_rejected"
                run.current_step = "stopped" if accepted else "nack"
                run.failure_code = None if accepted else acknowledgement.reason
                run.finished_at = acknowledgement.handled_at if accepted else None
                self.operations.save_batch_run(run)

    def _emit(self, kind: str, station_id: str, occurred_at: datetime, payload: dict[str, object]) -> None:
        if self._loop is not None and self._loop.is_running():
            asyncio.run_coroutine_threadsafe(
                self.realtime.publish(kind, station_id, occurred_at, payload),
                self._loop,
            )

    def _on_connect(self, client, _userdata, _flags, reason_code, _properties) -> None:
        failed = reason_code.is_failure if hasattr(reason_code, "is_failure") else int(reason_code) != 0
        if failed:
            self.last_error = f"mqtt_connect_{reason_code}"
            return
        self.last_error = None
        client.subscribe(
            [
                ("grow/v1/+/+/telemetry/+", 1),
                ("grow/v1/+/+/alarm/+", 1),
                ("grow/v1/+/+/ack/+", 1),
            ]
        )

    def _on_disconnect(self, _client, _userdata, _flags, reason_code, _properties) -> None:
        self.last_error = f"mqtt_disconnected_{reason_code}"

    def _on_message(self, _client, _userdata, message) -> None:
        try:
            self.handle_message(message.topic, message.payload, received_at=self.clock())
        except (KeyError, ValueError) as exc:
            self.last_error = f"mqtt_message_rejected:{exc}"
