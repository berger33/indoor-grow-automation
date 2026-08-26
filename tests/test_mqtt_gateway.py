from datetime import UTC, datetime, timedelta
from pathlib import Path
from types import SimpleNamespace
from unittest import TestCase
from uuid import uuid4

from hub.growhub.contracts.alarms import AlarmEnvelope, AlarmSeverity
from hub.growhub.contracts.commands import AckStatus, CommandAcknowledgement, CommandEnvelope
from hub.growhub.contracts.telemetry import TelemetryEnvelope
from hub.growhub.contracts.topics import acknowledgement_topic, telemetry_topic
from hub.growhub.domain.sensors import ReadingQuality, SensorKind, SensorReading, Unit
from hub.growhub.services.mqtt_gateway import MqttConnectionSettings, MqttGateway, MqttUnavailable
from hub.growhub.services.operations import InMemoryOperations, SensorDefinition, StationDefinition
from hub.growhub.services.realtime import RealtimeBuffer


NOW = datetime(2026, 8, 24, 12, tzinfo=UTC)


class FakeClient:
    def __init__(self) -> None:
        self.online = True
        self.published: list[tuple[str, str, int, bool]] = []
        self.subscriptions = []
        self.on_connect = None
        self.on_disconnect = None
        self.on_message = None

    def reconnect_delay_set(self, **_kwargs) -> None: pass
    def is_connected(self) -> bool: return self.online
    def publish(self, topic, payload, qos, retain):
        self.published.append((topic, payload, qos, retain))
        return SimpleNamespace(rc=0)
    def subscribe(self, topics): self.subscriptions = topics
    def connect_async(self, *_args, **_kwargs): return None
    def loop_start(self): return None
    def disconnect(self): self.online = False
    def loop_stop(self): return None


class FakeTelemetry:
    def __init__(self) -> None:
        self.ids: set[str] = set()
        self.envelopes: list[TelemetryEnvelope] = []

    def save(self, envelope: TelemetryEnvelope, *, received_at: datetime) -> bool:
        if envelope.message_id in self.ids:
            return False
        self.ids.add(envelope.message_id)
        self.envelopes.append(envelope)
        return True


class MqttGatewayTests(TestCase):
    def setUp(self) -> None:
        self.operations = InMemoryOperations()
        self.operations.stations["grow-01"] = StationDefinition("grow-01", "Estufa")
        self.operations.sensors[("grow-01", "ph_tank")] = SensorDefinition("grow-01", "ph_tank", "pH", 60)
        self.client = FakeClient()
        self.telemetry = FakeTelemetry()
        self.gateway = MqttGateway(
            MqttConnectionSettings("broker", 8883, Path("unused-ca"), Path("unused-cert"), Path("unused-key")),
            self.operations,
            self.telemetry,
            RealtimeBuffer(),
            sensor_nodes={("grow-01", "ph_tank"): "controller"},
            client=self.client,  # type: ignore[arg-type]
            clock=lambda: NOW,
        )

    def test_persists_valid_telemetry_once_and_checks_topic_owner(self) -> None:
        reading = SensorReading("grow-01", "ph_tank", SensorKind.PH, 5.8, Unit.PH, NOW, ReadingQuality.VALID)
        envelope = TelemetryEnvelope(str(uuid4()), 1, NOW, reading)
        topic = telemetry_topic("grow-01", "controller", "ph_tank")
        self.assertTrue(self.gateway.handle_message(topic, envelope.to_json(), received_at=NOW))
        self.assertFalse(self.gateway.handle_message(topic, envelope.to_json(), received_at=NOW))
        self.assertEqual(5.8, self.operations.readings[("grow-01", "ph_tank")].value)
        with self.assertRaises(ValueError):
            self.gateway.handle_message(telemetry_topic("grow-01", "legacy_node", "ph_tank"), envelope.to_json(), received_at=NOW)

    def test_publishes_command_and_accepts_only_matching_ack(self) -> None:
        audit = self.operations.record_audit("operator", "grow-01", "start_irrigation", "bed_a", "queued", NOW)
        command = self.gateway.dispatch(audit_id=audit.audit_id, station_id="grow-01", action="start_irrigation", target="bed_a", now=NOW)
        self.assertEqual(command, CommandEnvelope.from_json(self.client.published[0][1]))
        self.assertEqual((1, False), self.client.published[0][2:])
        acknowledgement = CommandAcknowledgement(command.command_id, command.sequence, AckStatus.ACK, "command_applied", NOW)
        topic = acknowledgement_topic("grow-01", "controller", "irrigation")
        self.assertTrue(self.gateway.handle_message(topic, acknowledgement.to_json(), received_at=NOW))
        self.assertFalse(self.gateway.handle_message(topic, acknowledgement.to_json(), received_at=NOW))
        self.assertEqual("ack", self.operations.audit[0].status)

    def test_disconnected_gateway_never_claims_command_was_queued(self) -> None:
        self.client.online = False
        audit = self.operations.record_audit("operator", "grow-01", "safe_stop", "station", "queued", NOW)
        with self.assertRaises(MqttUnavailable):
            self.gateway.dispatch(audit_id=audit.audit_id, station_id="grow-01", action="safe_stop", target="station", now=NOW)
        self.assertEqual([], self.client.published)

    def test_pending_command_expires_without_ack_and_is_not_replayed(self) -> None:
        audit = self.operations.record_audit("operator", "grow-01", "safe_stop", "station", "queued", NOW)
        command = self.gateway.dispatch(audit_id=audit.audit_id, station_id="grow-01", action="safe_stop", target="station", now=NOW)
        self.assertEqual(0, self.gateway.expire_pending(now=command.expires_at))
        self.assertEqual(1, self.gateway.expire_pending(now=command.expires_at + timedelta(microseconds=1)))
        self.assertEqual("timeout", self.operations.audit[0].status)
        self.assertEqual(0, self.gateway.health()["pendingCommands"])

    def test_persists_latched_alarm_idempotently(self) -> None:
        alarm = AlarmEnvelope(str(uuid4()), "grow-01", "leak_detected", AlarmSeverity.CRITICAL, "Água confirmada.", "Mantenha OFF e inspecione.", NOW)
        topic = "grow/v1/grow-01/controller/alarm/leak_detected"
        self.assertTrue(self.gateway.handle_message(topic, alarm.to_json(), received_at=NOW))
        self.assertFalse(self.gateway.handle_message(topic, alarm.to_json(), received_at=NOW))
        self.assertTrue(self.operations.alarms[alarm.alarm_id].latched)
