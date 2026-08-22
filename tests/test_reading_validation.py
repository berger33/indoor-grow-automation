from datetime import UTC, datetime
from unittest import TestCase

from hub.growhub.domain.sensors import (
    ReadingQuality,
    SensorKind,
    SensorReading,
    Unit,
)
from hub.growhub.domain.validation import ReadingValidator


def humidity(value: float, quality: ReadingQuality = ReadingQuality.VALID) -> SensorReading:
    return SensorReading(
        station_id="tent_a",
        sensor_id="humidity_a",
        kind=SensorKind.HUMIDITY,
        value=value,
        unit=Unit.PERCENT,
        observed_at=datetime(2026, 8, 22, tzinfo=UTC),
        quality=quality,
        error_code=None if quality is ReadingQuality.VALID else "sensor_timeout",
    )


class ReadingValidatorTests(TestCase):
    def setUp(self) -> None:
        self.validator = ReadingValidator()

    def test_preserves_value_inside_range(self) -> None:
        reading = humidity(63.0)
        self.assertIs(reading, self.validator.validate(reading))

    def test_accepts_range_boundaries(self) -> None:
        self.assertEqual(ReadingQuality.VALID, self.validator.validate(humidity(0)).quality)
        self.assertEqual(ReadingQuality.VALID, self.validator.validate(humidity(100)).quality)

    def test_marks_out_of_range_without_discarding_raw_value(self) -> None:
        result = self.validator.validate(humidity(104.5))
        self.assertEqual(104.5, result.value)
        self.assertEqual(ReadingQuality.INVALID, result.quality)
        self.assertEqual("out_of_plausible_range", result.error_code)

    def test_does_not_overwrite_existing_failure(self) -> None:
        reading = humidity(104.5, ReadingQuality.TIMEOUT)
        self.assertIs(reading, self.validator.validate(reading))

