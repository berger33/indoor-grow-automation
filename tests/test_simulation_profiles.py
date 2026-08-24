from datetime import UTC, datetime
from unittest import TestCase

from hub.growhub.domain.sensors import EXPECTED_UNIT, ReadingQuality, SensorKind
from hub.growhub.simulation.profiles import NOMINAL_VALUES, nominal_station_profile


class NominalStationProfileTests(TestCase):
    def test_covers_every_supported_sensor_kind(self) -> None:
        profile = nominal_station_profile()
        self.assertEqual(set(SensorKind), set(profile))
        self.assertEqual(set(SensorKind), set(NOMINAL_VALUES))

    def test_emits_valid_reading_with_canonical_unit(self) -> None:
        started = datetime(2026, 8, 24, tzinfo=UTC)
        for kind, simulator in nominal_station_profile("rack-01").items():
            with self.subTest(kind=kind):
                reading = simulator.next_reading(started_at=started)
                self.assertEqual("rack-01", reading.station_id)
                self.assertEqual(EXPECTED_UNIT[kind], reading.unit)
                self.assertEqual(ReadingQuality.VALID, reading.quality)
