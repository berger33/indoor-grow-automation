import json
from datetime import UTC, datetime
from unittest import TestCase

from hub.growhub.contracts.telemetry import TelemetryEnvelope
from hub.growhub.domain.sensors import SensorKind, SensorReading, Unit


class TelemetryContractTests(TestCase):
    def envelope(self) -> TelemetryEnvelope:
        observed = datetime(2026, 8, 22, 12, 0, tzinfo=UTC)
        return TelemetryEnvelope(
            message_id="4f1557f8-cc22-4b72-8168-d0a4d68f51b5",
            sequence=42,
            sent_at=observed,
            reading=SensorReading(
                station_id="tent_a",
                sensor_id="water_temp_main",
                kind=SensorKind.WATER_TEMPERATURE,
                value=22.75,
                unit=Unit.CELSIUS,
                observed_at=observed,
            ),
        )

    def mutate(self, callback) -> str:  # type: ignore[no-untyped-def]
        data = self.envelope().to_dict()
        callback(data)
        return json.dumps(data)

    def test_round_trip_preserves_envelope(self) -> None:
        original = self.envelope()
        self.assertEqual(original, TelemetryEnvelope.from_json(original.to_json()))

    def test_serialization_is_compact_and_unicode(self) -> None:
        payload = self.envelope().to_json()
        self.assertNotIn(" ", payload)
        self.assertIn("°C", payload)

    def test_rejects_unknown_schema_version(self) -> None:
        payload = self.mutate(lambda data: data.update(schema_version=2))
        with self.assertRaisesRegex(ValueError, "schema_version"):
            TelemetryEnvelope.from_json(payload)

    def test_rejects_missing_field(self) -> None:
        payload = self.mutate(lambda data: data.pop("message_id"))
        with self.assertRaisesRegex(ValueError, "ausentes"):
            TelemetryEnvelope.from_json(payload)

    def test_rejects_extra_field(self) -> None:
        payload = self.mutate(lambda data: data.update(untrusted="command"))
        with self.assertRaisesRegex(ValueError, "extras"):
            TelemetryEnvelope.from_json(payload)

    def test_rejects_boolean_as_numeric_value(self) -> None:
        def change(data: dict) -> None:
            data["reading"]["value"] = True

        with self.assertRaisesRegex(ValueError, "deve ser número"):
            TelemetryEnvelope.from_json(self.mutate(change))

    def test_rejects_negative_sequence(self) -> None:
        payload = self.mutate(lambda data: data.update(sequence=-1))
        with self.assertRaisesRegex(ValueError, "não negativo"):
            TelemetryEnvelope.from_json(payload)

    def test_rejects_non_object_json(self) -> None:
        with self.assertRaisesRegex(ValueError, "objeto JSON"):
            TelemetryEnvelope.from_json("[]")

    def test_rejects_invalid_json(self) -> None:
        with self.assertRaisesRegex(ValueError, "JSON"):
            TelemetryEnvelope.from_json("{")

