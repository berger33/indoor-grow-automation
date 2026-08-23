from datetime import UTC, datetime
from unittest import TestCase

from hub.growhub.domain.climate import (
    AgreementStatus,
    assess_sensor_agreement,
    calculate_leaf_vpd,
)
from hub.growhub.domain.sensors import ReadingQuality, SensorKind, SensorReading, Unit


def air_temperature(sensor_id: str, value: float, *, valid: bool = True) -> SensorReading:
    return SensorReading(
        station_id="tent_a",
        sensor_id=sensor_id,
        kind=SensorKind.AIR_TEMPERATURE,
        value=value,
        unit=Unit.CELSIUS,
        observed_at=datetime(2026, 8, 23, tzinfo=UTC),
        quality=ReadingQuality.VALID if valid else ReadingQuality.TIMEOUT,
        error_code=None if valid else "sensor_timeout",
    )


class SensorAgreementTests(TestCase):
    def test_flags_climate_sensors_beyond_allowed_delta(self) -> None:
        result = assess_sensor_agreement(
            air_temperature("air_a", 24.0),
            air_temperature("air_b", 27.0),
            maximum_delta=1.5,
        )
        self.assertEqual(AgreementStatus.DIVERGENT, result.status)
        self.assertEqual(3.0, result.absolute_delta)

    def test_accepts_delta_at_threshold(self) -> None:
        result = assess_sensor_agreement(
            air_temperature("air_a", 24.0),
            air_temperature("air_b", 25.5),
            maximum_delta=1.5,
        )
        self.assertEqual(AgreementStatus.CONSISTENT, result.status)

    def test_reports_unavailable_when_either_reading_failed(self) -> None:
        result = assess_sensor_agreement(
            air_temperature("air_a", 24.0),
            air_temperature("air_b", 24.5, valid=False),
            maximum_delta=1.5,
        )
        self.assertEqual(AgreementStatus.UNAVAILABLE, result.status)

    def test_rejects_non_positive_threshold(self) -> None:
        with self.assertRaises(ValueError):
            assess_sensor_agreement(
                air_temperature("air_a", 24.0),
                air_temperature("air_b", 24.5),
                maximum_delta=0.0,
            )


class LeafVPDTests(TestCase):
    def test_calculates_vpd_from_air_leaf_and_humidity(self) -> None:
        result = calculate_leaf_vpd(
            air_temperature_c=25.0,
            leaf_temperature_c=24.0,
            relative_humidity_percent=60.0,
        )
        self.assertAlmostEqual(1.083, result.kilopascals, places=3)
        self.assertFalse(result.condensation_risk)

    def test_preserves_negative_vpd_as_condensation_warning(self) -> None:
        result = calculate_leaf_vpd(
            air_temperature_c=28.0,
            leaf_temperature_c=20.0,
            relative_humidity_percent=95.0,
        )
        self.assertLess(result.kilopascals, 0.0)
        self.assertTrue(result.condensation_risk)

    def test_rejects_impossible_humidity(self) -> None:
        with self.assertRaises(ValueError):
            calculate_leaf_vpd(
                air_temperature_c=25.0,
                leaf_temperature_c=24.0,
                relative_humidity_percent=101.0,
            )
