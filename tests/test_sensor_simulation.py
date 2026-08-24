from datetime import UTC, datetime, timedelta
from unittest import TestCase

from hub.growhub.domain.sensors import SensorKind, Unit
from hub.growhub.simulation.sensors import SequenceSensorSimulator, SimulationFrame


class SequenceSensorSimulatorTests(TestCase):
    def simulator(self) -> SequenceSensorSimulator:
        return SequenceSensorSimulator(
            station_id="grow-01",
            sensor_id="ph-01",
            kind=SensorKind.PH,
            unit=Unit.PH,
            frames=(
                SimulationFrame(6.0),
                SimulationFrame(6.1, timedelta(seconds=5)),
            ),
        )

    def test_replays_values_and_timestamps_deterministically(self) -> None:
        started = datetime(2026, 8, 24, tzinfo=UTC)
        simulator = self.simulator()
        first = simulator.next_reading(started_at=started)
        second = simulator.next_reading(started_at=started)
        self.assertEqual((6.0, started), (first.value, first.observed_at))
        self.assertEqual((6.1, started + timedelta(seconds=5)), (second.value, second.observed_at))
        self.assertTrue(simulator.exhausted)

    def test_reset_restarts_sequence(self) -> None:
        started = datetime(2026, 8, 24, tzinfo=UTC)
        simulator = self.simulator()
        simulator.next_reading(started_at=started)
        simulator.reset()
        self.assertEqual(6.0, simulator.next_reading(started_at=started).value)

    def test_rejects_empty_negative_or_naive_scenario(self) -> None:
        with self.assertRaisesRegex(ValueError, "ao menos um"):
            SequenceSensorSimulator(
                station_id="grow-01",
                sensor_id="ph-01",
                kind=SensorKind.PH,
                unit=Unit.PH,
                frames=(),
            )
        with self.assertRaisesRegex(ValueError, "negativo"):
            SimulationFrame(6.0, timedelta(seconds=-1))
        with self.assertRaisesRegex(ValueError, "timezone"):
            self.simulator().next_reading(started_at=datetime(2026, 8, 24))

    def test_stops_after_last_frame(self) -> None:
        simulator = self.simulator()
        started = datetime(2026, 8, 24, tzinfo=UTC)
        simulator.next_reading(started_at=started)
        simulator.next_reading(started_at=started)
        with self.assertRaises(StopIteration):
            simulator.next_reading(started_at=started)
