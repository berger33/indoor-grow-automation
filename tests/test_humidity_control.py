from datetime import UTC, datetime, timedelta
from unittest import TestCase

from hub.growhub.control.humidity import (
    HumidifierAction,
    HumidityConfig,
    HumidityController,
)


class HumidityControllerTests(TestCase):
    def setUp(self) -> None:
        self.now = datetime(2026, 8, 24, tzinfo=UTC)
        self.controller = HumidityController(HumidityConfig(target_percent=60))

    def evaluate(self, humidity, seconds=0, **overrides):
        inputs = {
            "reading_valid": True,
            "water_level_ok": True,
            "leak_detected": False,
        }
        inputs.update(overrides)
        return self.controller.evaluate(
            humidity,
            now=self.now + timedelta(seconds=seconds),
            **inputs,
        )

    def test_uses_five_percent_hysteresis_and_anti_cycle(self) -> None:
        self.assertEqual(HumidifierAction.ON, self.evaluate(55).action)
        self.assertEqual("minimum_on_time", self.evaluate(66, seconds=20).reason)
        self.assertEqual(HumidifierAction.OFF, self.evaluate(66, seconds=30).action)
        self.assertEqual("minimum_off_time", self.evaluate(50, seconds=40).reason)
        self.assertEqual(HumidifierAction.ON, self.evaluate(50, seconds=60).action)

    def test_level_leak_and_invalid_reading_force_output_off(self) -> None:
        self.evaluate(50)
        self.assertEqual(
            "humidifier_level_low",
            self.evaluate(50, seconds=1, water_level_ok=False).reason,
        )
        self.assertEqual(
            "leak_detected",
            self.evaluate(50, seconds=2, leak_detected=True).reason,
        )
        self.assertEqual(
            "invalid_or_stale_reading",
            self.evaluate(50, seconds=3, reading_valid=False).reason,
        )

    def test_absolute_high_limit_overrides_minimum_on_time(self) -> None:
        self.evaluate(50)
        decision = self.evaluate(95, seconds=1)
        self.assertEqual(HumidifierAction.OFF, decision.action)
        self.assertEqual("absolute_humidity_high", decision.reason)

    def test_rejects_unsafe_target_and_naive_time(self) -> None:
        with self.assertRaises(ValueError):
            HumidityConfig(target_percent=95)
        with self.assertRaisesRegex(ValueError, "timezone"):
            self.controller.evaluate(
                60,
                now=datetime(2026, 8, 24),
                reading_valid=True,
                water_level_ok=True,
                leak_detected=False,
            )
