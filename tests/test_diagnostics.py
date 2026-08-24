from datetime import UTC, datetime, timedelta
from unittest import TestCase

from hub.growhub.domain.diagnostics import DiagnosticState, diagnose_reading
from hub.growhub.domain.faults import SensorFaultCode, mark_sensor_fault
from hub.growhub.domain.sensors import SensorKind, SensorReading, Unit


class ReadingDiagnosticTests(TestCase):
    def reading(self) -> SensorReading:
        return SensorReading(
            station_id="grow-01",
            sensor_id="ph-01",
            kind=SensorKind.PH,
            value=6.0,
            unit=Unit.PH,
            observed_at=datetime(2026, 8, 24, tzinfo=UTC),
        )

    def test_reports_healthy_reading_and_exact_age(self) -> None:
        result = diagnose_reading(
            self.reading(),
            now=datetime(2026, 8, 24, tzinfo=UTC) + timedelta(seconds=12),
        )
        self.assertEqual(DiagnosticState.HEALTHY, result.state)
        self.assertEqual(12.0, result.age_seconds)

    def test_marks_stale_reading_as_degraded(self) -> None:
        result = diagnose_reading(
            self.reading(),
            now=datetime(2026, 8, 24, tzinfo=UTC) + timedelta(seconds=31),
        )
        self.assertEqual(DiagnosticState.DEGRADED, result.state)
        self.assertEqual("reading_stale", result.reason)

    def test_reports_transport_fault_as_failed(self) -> None:
        result = diagnose_reading(
            mark_sensor_fault(self.reading(), SensorFaultCode.TIMEOUT),
            now=datetime(2026, 8, 24, tzinfo=UTC),
        )
        self.assertEqual(DiagnosticState.FAILED, result.state)
        self.assertEqual("sensor_timeout", result.reason)

    def test_rejects_naive_or_retrograde_reference_time(self) -> None:
        with self.assertRaisesRegex(ValueError, "timezone"):
            diagnose_reading(self.reading(), now=datetime(2026, 8, 24))
        with self.assertRaisesRegex(ValueError, "anteceder"):
            diagnose_reading(
                self.reading(),
                now=datetime(2026, 8, 23, tzinfo=UTC),
            )
