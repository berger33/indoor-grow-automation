from datetime import UTC, datetime, timedelta
from unittest import TestCase

from hub.growhub.control.exhaust import (
    ExhaustAction,
    ExhaustConfig,
    OnOffExhaustController,
)


class OnOffExhaustControllerTests(TestCase):
    def setUp(self) -> None:
        self.now = datetime(2026, 8, 24, tzinfo=UTC)
        self.controller = OnOffExhaustController(
            ExhaustConfig(target_temperature_c=24)
        )

    def evaluate(self, temperatures, seconds=0, humidity=60, vpd=1.0):
        return self.controller.evaluate(
            temperatures,
            humidity_percent=humidity,
            vpd_kpa=vpd,
            now=self.now + timedelta(seconds=seconds),
        )

    def test_turns_on_when_both_sensors_are_hot_and_off_when_cool(self) -> None:
        hot = self.evaluate((26, 27))
        self.assertEqual(ExhaustAction.ON, hot.action)
        self.assertEqual("both_sensors_hot", hot.reason)
        self.assertEqual(
            "minimum_cycle_time", self.evaluate((22, 22), seconds=20).reason
        )
        self.assertEqual(ExhaustAction.OFF, self.evaluate((23, 23), seconds=30).action)

    def test_low_vpd_and_absolute_limits_force_ventilation(self) -> None:
        self.assertEqual(ExhaustAction.ON, self.evaluate((24, 24), vpd=0.5).action)
        other = OnOffExhaustController(ExhaustConfig(target_temperature_c=24))
        decision = other.evaluate(
            (36, 24), humidity_percent=60, vpd_kpa=1, now=self.now
        )
        self.assertEqual("absolute_temperature_high", decision.reason)

    def test_single_sensor_uses_degraded_policy(self) -> None:
        hot = self.evaluate((25, None))
        self.assertTrue(hot.degraded)
        self.assertEqual(ExhaustAction.ON, hot.action)
        held = self.evaluate((23, None), seconds=30)
        self.assertTrue(held.degraded)
        self.assertEqual("single_sensor_hold", held.reason)

    def test_no_valid_temperature_fails_to_fan_on(self) -> None:
        decision = self.evaluate((None, None))
        self.assertEqual(ExhaustAction.ON, decision.action)
        self.assertEqual("no_valid_temperature", decision.reason)

    def test_current_exhaust_is_never_treated_as_pwm(self) -> None:
        self.assertEqual({ExhaustAction.ON, ExhaustAction.OFF}, set(ExhaustAction))
