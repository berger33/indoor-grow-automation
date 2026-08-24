from datetime import UTC, datetime, timedelta
from unittest import TestCase

from hub.growhub.control.dosing import PHChannel
from hub.growhub.control.ph_control import PHAction, PHControlConfig, PHStepController


class PHStepControllerTests(TestCase):
    def setUp(self) -> None:
        self.now = datetime(2026, 8, 24, tzinfo=UTC)
        self.controller = PHStepController(
            PHControlConfig(target=6.0, dose_ml=1, settling_time=timedelta(minutes=5))
        )

    def evaluate(self, ph, **overrides):
        inputs = {
            "now": self.now,
            "reading_fresh": True,
            "mixing": True,
            "level_ok": True,
        }
        inputs.update(overrides)
        return self.controller.evaluate(ph, **inputs)

    def test_doses_correct_direction_at_deadband_boundaries(self) -> None:
        high = self.evaluate(6.1)
        self.assertEqual(PHAction.DOSE_DOWN, high.action)
        self.assertEqual(PHChannel.DOWN, high.channel)
        self.assertEqual(1, high.volume_ml)

        another = PHStepController(PHControlConfig(target=6.0, dose_ml=1))
        low = another.evaluate(
            5.9,
            now=self.now,
            reading_fresh=True,
            mixing=True,
            level_ok=True,
        )
        self.assertEqual(PHAction.DOSE_UP, low.action)

    def test_waits_for_mixing_and_valid_level_and_reading(self) -> None:
        self.assertEqual("mixing_required", self.evaluate(6.2, mixing=False).reason)
        later = self.now + timedelta(minutes=1)
        self.assertEqual(
            "insufficient_level", self.evaluate(6.2, now=later, level_ok=False).reason
        )
        self.assertEqual(
            "invalid_or_stale_reading",
            self.evaluate(6.2, now=later + timedelta(minutes=1), reading_fresh=False).reason,
        )

    def test_enforces_evaluation_and_settling_intervals(self) -> None:
        self.evaluate(6.2)
        self.assertEqual(
            "settling", self.evaluate(6.2, now=self.now + timedelta(minutes=4)).reason
        )
        self.assertEqual(
            PHAction.DOSE_DOWN,
            self.evaluate(6.2, now=self.now + timedelta(minutes=5)).action,
        )

    def test_holds_inside_deadband(self) -> None:
        decision = self.evaluate(6.05)
        self.assertEqual(PHAction.HOLD, decision.action)
        self.assertEqual("inside_deadband", decision.reason)

    def test_rejects_unsafe_configuration_and_naive_time(self) -> None:
        with self.assertRaises(ValueError):
            PHControlConfig(target=7, dose_ml=1)
        with self.assertRaisesRegex(ValueError, "timezone"):
            self.controller.evaluate(
                6,
                now=datetime(2026, 8, 24),
                reading_fresh=True,
                mixing=True,
                level_ok=True,
            )
