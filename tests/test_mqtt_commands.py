from datetime import UTC, datetime, timedelta
from unittest import TestCase
from uuid import uuid4

from hub.growhub.contracts.commands import (
    AckStatus,
    CommandAcknowledgement,
    CommandEnvelope,
    IdempotentCommandProcessor,
)


class MqttCommandTests(TestCase):
    def setUp(self) -> None:
        self.now = datetime(2026, 8, 24, 15, tzinfo=UTC)
        self.processor = IdempotentCommandProcessor()

    def command(self, sequence=1, **overrides) -> CommandEnvelope:
        values = {
            "command_id": str(uuid4()),
            "station_id": "grow-01",
            "node_id": "fertigation",
            "function": "mixer",
            "action": "start",
            "sequence": sequence,
            "issued_at": self.now,
            "expires_at": self.now + timedelta(seconds=30),
            "parameters": {"duration_ms": 5000},
        }
        values.update(overrides)
        return CommandEnvelope(**values)

    def test_round_trip_preserves_strict_command(self) -> None:
        command = self.command()
        self.assertEqual(command, CommandEnvelope.from_json(command.to_json()))
        with self.assertRaises(ValueError):
            CommandEnvelope.from_json(command.to_json()[:-1] + ',"extra":1}')

    def test_round_trip_preserves_strict_acknowledgement(self) -> None:
        acknowledgement = CommandAcknowledgement(
            command_id=self.command().command_id,
            sequence=4,
            status=AckStatus.ACK,
            reason="command_applied",
            handled_at=self.now,
        )
        self.assertEqual(
            acknowledgement,
            CommandAcknowledgement.from_json(acknowledgement.to_json()),
        )
        with self.assertRaises(ValueError):
            CommandAcknowledgement.from_json(
                acknowledgement.to_json()[:-1] + ',"extra":1}'
            )

    def test_duplicate_uuid_returns_same_ack_without_second_execution(self) -> None:
        calls = []
        command = self.command()

        def execute(value):
            calls.append(value.command_id)
            return True, "command_applied"

        first = self.processor.process(command, now=self.now, execute=execute)
        duplicate = self.processor.process(command, now=self.now + timedelta(seconds=1), execute=execute)
        self.assertIs(first, duplicate)
        self.assertEqual(AckStatus.ACK, first.status)
        self.assertEqual(1, len(calls))

    def test_replayed_sequence_and_expired_command_are_nacked(self) -> None:
        accepted = self.command(sequence=10)
        self.processor.process(accepted, now=self.now, execute=lambda _: (True, "command_applied"))
        replay = self.command(sequence=10)
        response = self.processor.process(replay, now=self.now, execute=lambda _: (True, "command_applied"))
        self.assertEqual((AckStatus.NACK, "sequence_replayed"), (response.status, response.reason))

        expired = self.command(
            sequence=11,
            issued_at=self.now - timedelta(minutes=2),
            expires_at=self.now - timedelta(minutes=1),
        )
        response = self.processor.process(expired, now=self.now, execute=lambda _: (True, "command_applied"))
        self.assertEqual("command_expired", response.reason)
