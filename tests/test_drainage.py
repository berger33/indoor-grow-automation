from datetime import UTC, datetime, timedelta
from unittest import TestCase

from hub.growhub.control.drainage import DrainAction, DrainController, DrainState


class DrainControllerTests(TestCase):
    def setUp(self) -> None:
        self.now = datetime(2026, 8, 24, tzinfo=UTC)
        self.controller = DrainController()

    def evaluate(self, seconds, full, safe=True):
        return self.controller.evaluate(
            full,
            now=self.now + timedelta(seconds=seconds),
            safe_to_operate=safe,
        )

    def test_waits_drains_and_runs_one_minute_after_float_release(self) -> None:
        self.assertEqual(DrainState.CONFIRM_DELAY, self.evaluate(0, True).state)
        self.assertEqual(DrainAction.PUMP_OFF, self.evaluate(29, True).action)
        self.assertEqual(DrainAction.PUMP_ON, self.evaluate(30, True).action)
        self.assertEqual(DrainState.POST_RUN, self.evaluate(60, False).state)
        self.assertEqual(DrainAction.PUMP_ON, self.evaluate(119, False).action)
        complete = self.evaluate(120, False)
        self.assertEqual(DrainAction.PUMP_OFF, complete.action)
        self.assertEqual(DrainState.IDLE, complete.state)

    def test_transient_full_signal_never_starts_pump(self) -> None:
        self.evaluate(0, True)
        decision = self.evaluate(10, False)
        self.assertEqual(DrainState.IDLE, decision.state)
        self.assertEqual(DrainAction.PUMP_OFF, decision.action)

    def test_latches_alarm_at_absolute_eight_minute_timeout(self) -> None:
        self.evaluate(0, True)
        self.evaluate(30, True)
        timeout = self.evaluate(510, True)
        self.assertEqual(DrainState.ALARM, timeout.state)
        self.assertEqual("drain_timeout", timeout.reason)
        self.assertEqual(DrainAction.PUMP_OFF, self.evaluate(511, False).action)

    def test_reset_requires_empty_basin_confirmation(self) -> None:
        self.evaluate(0, True, safe=False)
        with self.assertRaises(PermissionError):
            self.controller.reset_alarm(basin_empty_confirmed=False)
        self.controller.reset_alarm(basin_empty_confirmed=True)
        self.assertEqual(DrainState.IDLE, self.controller.state)
