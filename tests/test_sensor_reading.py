from datetime import UTC, datetime
from unittest import TestCase

from hub.growhub.domain.sensors import (
    ReadingQuality,
    SensorKind,
    SensorReading,
    Unit,
)


class SensorReadingTests(TestCase):
    def make_reading(self, **changes: object) -> SensorReading:
        values = {
            "station_id": "tent_a",
            "sensor_id": "ph_main",
            "kind": SensorKind.PH,
            "value": 6.1,
            "unit": Unit.PH,
            "observed_at": datetime(2026, 8, 22, tzinfo=UTC),
        }
        values.update(changes)
        return SensorReading(**values)  # type: ignore[arg-type]

    def test_constructs_valid_reading(self) -> None:
        reading = self.make_reading()
        self.assertEqual(ReadingQuality.VALID, reading.quality)

    def test_rejects_naive_timestamp(self) -> None:
        with self.assertRaisesRegex(ValueError, "timezone"):
            self.make_reading(observed_at=datetime(2026, 8, 22))

    def test_rejects_non_finite_value(self) -> None:
        with self.assertRaisesRegex(ValueError, "finito"):
            self.make_reading(value=float("nan"))

    def test_rejects_wrong_unit(self) -> None:
        with self.assertRaisesRegex(ValueError, "incompatível"):
            self.make_reading(unit=Unit.CELSIUS)

    def test_rejects_invalid_identifier(self) -> None:
        with self.assertRaisesRegex(ValueError, "sensor_id"):
            self.make_reading(sensor_id="pH principal")

    def test_rejects_error_on_valid_reading(self) -> None:
        with self.assertRaisesRegex(ValueError, "válida"):
            self.make_reading(error_code="timeout")

    def test_accepts_structured_failure(self) -> None:
        reading = self.make_reading(
            quality=ReadingQuality.TIMEOUT,
            error_code="atlas_timeout",
        )
        self.assertEqual("atlas_timeout", reading.error_code)

