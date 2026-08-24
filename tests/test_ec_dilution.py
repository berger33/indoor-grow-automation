from datetime import UTC, datetime, timedelta
from unittest import TestCase

from hub.growhub.control.ec_dilution import (
    DilutionAction,
    DilutionState,
    ECDilutionController,
)


class ECDilutionControllerTests(TestCase):
    def setUp(self) -> None:
        self.now = datetime(2026, 8, 24, tzinfo=UTC)
        self.controller = ECDilutionController(
            target_ec_ms_cm=1.5,
            maximum_volume_l=50,
        )
        self.controller.start(now=self.now)

    def evaluate(self, ec, volume, seconds=0, **overrides):
        inputs = {"reading_valid": True, "reading_stable": True}
        inputs.update(overrides)
        return self.controller.evaluate(
            ec,
            volume,
            now=self.now + timedelta(seconds=seconds),
            **inputs,
        )

    def test_adds_water_only_while_ec_is_high_and_capacity_exists(self) -> None:
        self.assertEqual(DilutionAction.WATER_ON, self.evaluate(1.8, 30).action)
        complete = self.evaluate(1.5, 35, seconds=30)
        self.assertEqual(DilutionAction.WATER_OFF, complete.action)
        self.assertEqual(DilutionState.COMPLETE, complete.state)

    def test_stops_at_reserved_capacity_limit(self) -> None:
        decision = self.evaluate(1.8, 45)
        self.assertEqual(DilutionState.ALARM, decision.state)
        self.assertEqual("volume_limit", decision.reason)

    def test_stops_at_absolute_timeout(self) -> None:
        decision = self.evaluate(1.8, 30, seconds=480)
        self.assertEqual(DilutionState.ALARM, decision.state)
        self.assertEqual("timeout", decision.reason)

    def test_invalid_or_unstable_ec_never_leaves_water_on(self) -> None:
        decision = self.evaluate(1.8, 30, reading_stable=False)
        self.assertEqual(DilutionAction.WATER_OFF, decision.action)
        self.assertEqual(DilutionState.RUNNING, decision.state)

    def test_rejects_repeated_start_and_naive_time(self) -> None:
        with self.assertRaises(PermissionError):
            self.controller.start(now=self.now)
        with self.assertRaisesRegex(ValueError, "timezone"):
            ECDilutionController(
                target_ec_ms_cm=1.5, maximum_volume_l=50
            ).start(now=datetime(2026, 8, 24))
