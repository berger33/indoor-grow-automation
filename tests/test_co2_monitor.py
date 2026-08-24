from datetime import UTC, datetime, timedelta
from unittest import TestCase

from hub.growhub.domain.co2 import CO2Monitor, CO2Status
from hub.growhub.domain.sensors import (
    ReadingQuality,
    SensorKind,
    SensorReading,
    Unit,
)


class CO2MonitorTests(TestCase):
    def setUp(self) -> None:
        self.now = datetime(2026, 8, 24, 12, tzinfo=UTC)
        self.monitor = CO2Monitor()

    def reading(self, value: float, **overrides) -> SensorReading:
        values = {
            "station_id": "grow-01",
            "sensor_id": "co2_tent",
            "kind": SensorKind.CO2,
            "value": value,
            "unit": Unit.PPM,
            "observed_at": self.now,
        }
        values.update(overrides)
        return SensorReading(**values)

    def test_classifies_normal_warning_and_critical_without_command(self) -> None:
        self.assertEqual(CO2Status.NORMAL, self.monitor.assess(self.reading(800), now=self.now).status)
        warning = self.monitor.assess(self.reading(1_200), now=self.now)
        self.assertEqual(CO2Status.WARNING, warning.status)
        self.assertIn("somente", warning.explanation)
        critical = self.monitor.assess(self.reading(2_100), now=self.now)
        self.assertEqual(CO2Status.CRITICAL, critical.status)
        self.assertIn("não injeta", critical.explanation)
        self.assertFalse(hasattr(self.monitor, "command_injection"))

    def test_missing_invalid_and_stale_readings_are_unavailable(self) -> None:
        self.assertEqual(CO2Status.UNAVAILABLE, self.monitor.assess(None, now=self.now).status)
        invalid = self.reading(
            0,
            quality=ReadingQuality.TIMEOUT,
            error_code="sensor_timeout",
        )
        self.assertEqual("co2_invalid", self.monitor.assess(invalid, now=self.now).alarm_code)
        stale = self.reading(700, observed_at=self.now - timedelta(minutes=3))
        self.assertEqual("co2_stale", self.monitor.assess(stale, now=self.now).alarm_code)
