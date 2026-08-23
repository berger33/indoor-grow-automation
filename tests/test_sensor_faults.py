from datetime import UTC, datetime
from unittest import TestCase

from hub.growhub.domain.faults import SensorFaultCode, mark_sensor_fault
from hub.growhub.domain.sensors import ReadingQuality, SensorKind, SensorReading, Unit


class SensorFaultTests(TestCase):
    def setUp(self) -> None:
        self.reading = SensorReading(
            station_id="tent_a",
            sensor_id="water_temp_a",
            kind=SensorKind.WATER_TEMPERATURE,
            value=22.5,
            unit=Unit.CELSIUS,
            observed_at=datetime(2026, 8, 23, tzinfo=UTC),
        )

    def test_maps_every_fault_to_non_valid_quality(self) -> None:
        for fault in SensorFaultCode:
            with self.subTest(fault=fault):
                result = mark_sensor_fault(self.reading, fault)
                self.assertIsNot(ReadingQuality.VALID, result.quality)
                self.assertEqual(fault.value, result.error_code)

    def test_preserves_raw_measurement_for_diagnostics(self) -> None:
        result = mark_sensor_fault(self.reading, SensorFaultCode.CRC_MISMATCH)
        self.assertEqual(self.reading.value, result.value)
        self.assertEqual(self.reading.observed_at, result.observed_at)
        self.assertEqual(ReadingQuality.CRC_ERROR, result.quality)
