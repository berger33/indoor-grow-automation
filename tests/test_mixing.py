from datetime import UTC, datetime, timedelta
from unittest import TestCase

from hub.growhub.control.mixing import MixingAction, PeriodicMixingController


class PeriodicMixingControllerTests(TestCase):
    def setUp(self) -> None:
        self.now = datetime(2026, 8, 24, tzinfo=UTC)
        self.controller = PeriodicMixingController()

    def evaluate(self, minutes, volume=20, safe=True):
        return self.controller.evaluate(
            volume,
            now=self.now + timedelta(minutes=minutes),
            safe_to_operate=safe,
        )

    def test_runs_five_minutes_every_twenty_minutes(self) -> None:
        self.assertEqual(MixingAction.ON, self.evaluate(0).action)
        self.assertEqual(MixingAction.ON, self.evaluate(4).action)
        self.assertEqual(MixingAction.OFF, self.evaluate(5).action)
        self.assertEqual(MixingAction.OFF, self.evaluate(19).action)
        self.assertEqual(MixingAction.ON, self.evaluate(20).action)

    def test_low_volume_and_interlock_stop_immediately(self) -> None:
        self.assertEqual(MixingAction.OFF, self.evaluate(0, volume=10).action)
        self.assertEqual(MixingAction.ON, self.evaluate(1, volume=20).action)
        self.assertEqual(MixingAction.OFF, self.evaluate(2, safe=False).action)

    def test_rejects_invalid_configuration_and_retrograde_time(self) -> None:
        with self.assertRaises(ValueError):
            PeriodicMixingController(
                run_time=timedelta(minutes=20),
                cycle_interval=timedelta(minutes=20),
            )
        self.evaluate(1)
        with self.assertRaisesRegex(ValueError, "monotônicas"):
            self.evaluate(0)
