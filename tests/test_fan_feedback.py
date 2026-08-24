from datetime import UTC, datetime, timedelta
from unittest import TestCase

from hub.growhub.control.fan_feedback import FanFeedbackMonitor, FanFeedbackState


class FanFeedbackMonitorTests(TestCase):
    def setUp(self) -> None:
        self.now = datetime(2026, 8, 24, tzinfo=UTC)
        self.monitor = FanFeedbackMonitor()

    def test_confirms_current_after_startup_grace(self) -> None:
        self.monitor.command(True, now=self.now)
        self.assertEqual(
            FanFeedbackState.TRANSITIONING,
            self.monitor.observe(False, now=self.now + timedelta(seconds=4)),
        )
        self.assertEqual(
            FanFeedbackState.ON_CONFIRMED,
            self.monitor.observe(True, now=self.now + timedelta(seconds=5)),
        )

    def test_latches_missing_current_after_two_confirmations(self) -> None:
        self.monitor.command(True, now=self.now)
        self.assertEqual(
            FanFeedbackState.TRANSITIONING,
            self.monitor.observe(False, now=self.now + timedelta(seconds=5)),
        )
        self.assertEqual(
            FanFeedbackState.FAULT_NO_FEEDBACK,
            self.monitor.observe(False, now=self.now + timedelta(seconds=6)),
        )
        with self.assertRaises(PermissionError):
            self.monitor.command(True, now=self.now + timedelta(seconds=7))

    def test_detects_stuck_on_and_requires_safe_reset(self) -> None:
        self.monitor.command(False, now=self.now)
        self.monitor.observe(True, now=self.now + timedelta(seconds=5))
        fault = self.monitor.observe(True, now=self.now + timedelta(seconds=6))
        self.assertEqual(FanFeedbackState.FAULT_STUCK_ON, fault)
        with self.assertRaises(PermissionError):
            self.monitor.reset(current_present=True)
        self.monitor.reset(current_present=False)

    def test_repeated_command_does_not_extend_feedback_deadline(self) -> None:
        self.monitor.command(True, now=self.now)
        self.monitor.command(True, now=self.now + timedelta(seconds=4))
        self.monitor.observe(False, now=self.now + timedelta(seconds=5))
        fault = self.monitor.observe(False, now=self.now + timedelta(seconds=6))
        self.assertEqual(FanFeedbackState.FAULT_NO_FEEDBACK, fault)
