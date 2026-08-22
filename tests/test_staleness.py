from datetime import UTC, datetime, timedelta
from unittest import TestCase

from hub.growhub.domain.sensors import (
    ReadingQuality,
    SensorKind,
    SensorReading,
    Unit,
)
from hub.growhub.domain.staleness import StalenessPolicy


NOW = datetime(2026, 8, 22, 12, 0, tzinfo=UTC)


def ph_reading(age: timedelta, quality: ReadingQuality = ReadingQuality.VALID) -> SensorReading:
    return SensorReading(
        station_id="tent_a",
        sensor_id="ph_main",
        kind=SensorKind.PH,
        value=6.0,
        unit=Unit.PH,
        observed_at=NOW - age,
        quality=quality,
        error_code=None if quality is ReadingQuality.VALID else "atlas_timeout",
    )


class StalenessPolicyTests(TestCase):
    def setUp(self) -> None:
        self.policy = StalenessPolicy()

    def test_preserves_fresh_reading(self) -> None:
        reading = ph_reading(timedelta(seconds=10))
        self.assertIs(reading, self.policy.apply(reading, now=NOW))

    def test_accepts_exact_maximum_age(self) -> None:
        result = self.policy.apply(ph_reading(timedelta(seconds=30)), now=NOW)
        self.assertEqual(ReadingQuality.VALID, result.quality)

    def test_marks_reading_older_than_limit(self) -> None:
        result = self.policy.apply(ph_reading(timedelta(seconds=31)), now=NOW)
        self.assertEqual(ReadingQuality.STALE, result.quality)
        self.assertEqual("reading_stale", result.error_code)

    def test_preserves_prior_failure(self) -> None:
        reading = ph_reading(timedelta(minutes=5), ReadingQuality.TIMEOUT)
        self.assertIs(reading, self.policy.apply(reading, now=NOW))

    def test_rejects_naive_reference_time(self) -> None:
        with self.assertRaisesRegex(ValueError, "timezone"):
            self.policy.apply(ph_reading(timedelta()), now=datetime(2026, 8, 22))

