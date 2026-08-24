from datetime import UTC, datetime, timedelta
from unittest import TestCase

from hub.growhub.control.actuators import ActuatorTimeoutGuard


class ActuatorTimeoutGuardTests(TestCase):
    def setUp(self) -> None:
        self.now = datetime(2026, 8, 24, tzinfo=UTC)
        self.guard = ActuatorTimeoutGuard(maximum_on=timedelta(seconds=10))

    def test_cuts_output_at_absolute_deadline(self) -> None:
        self.guard.start(now=self.now)
        self.assertTrue(self.guard.evaluate(now=self.now + timedelta(seconds=9)))
        self.assertFalse(self.guard.evaluate(now=self.now + timedelta(seconds=10)))
        self.assertTrue(self.guard.timed_out)
        self.assertFalse(self.guard.commanded_on)

    def test_repeated_start_does_not_extend_deadline(self) -> None:
        self.guard.start(now=self.now)
        self.guard.start(now=self.now + timedelta(seconds=9))
        self.assertFalse(self.guard.evaluate(now=self.now + timedelta(seconds=10)))

    def test_timeout_requires_explicit_reset(self) -> None:
        self.guard.start(now=self.now)
        self.guard.evaluate(now=self.now + timedelta(seconds=10))
        with self.assertRaises(PermissionError):
            self.guard.start(now=self.now + timedelta(seconds=11))
        self.guard.reset()
        self.guard.start(now=self.now + timedelta(seconds=11))
        self.assertTrue(self.guard.commanded_on)

    def test_rejects_invalid_duration_and_time(self) -> None:
        with self.assertRaises(ValueError):
            ActuatorTimeoutGuard(maximum_on=timedelta(0))
        with self.assertRaisesRegex(ValueError, "timezone"):
            self.guard.start(now=datetime(2026, 8, 24))
