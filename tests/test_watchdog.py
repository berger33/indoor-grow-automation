from datetime import UTC, datetime, timedelta
from unittest import TestCase

from hub.growhub.control.watchdog import LocalWatchdog, ResetReason


class LocalWatchdogTests(TestCase):
    def setUp(self) -> None:
        self.now = datetime(2026, 8, 24, tzinfo=UTC)
        self.watchdog = LocalWatchdog(timeout=timedelta(seconds=5))

    def test_requires_first_feed_before_reporting_healthy(self) -> None:
        self.assertFalse(self.watchdog.healthy(now=self.now))
        self.watchdog.feed(now=self.now)
        self.assertTrue(self.watchdog.healthy(now=self.now + timedelta(seconds=4)))

    def test_trips_at_deadline_and_records_reset_reason(self) -> None:
        self.watchdog.feed(now=self.now)
        self.assertFalse(self.watchdog.healthy(now=self.now + timedelta(seconds=5)))
        self.assertTrue(self.watchdog.tripped)
        self.assertEqual(ResetReason.WATCHDOG, self.watchdog.reset_reason)

    def test_feed_never_revives_tripped_watchdog(self) -> None:
        self.watchdog.feed(now=self.now)
        self.watchdog.healthy(now=self.now + timedelta(seconds=5))
        with self.assertRaises(PermissionError):
            self.watchdog.feed(now=self.now + timedelta(seconds=6))

    def test_rejects_invalid_timeout_and_non_monotonic_time(self) -> None:
        with self.assertRaises(ValueError):
            LocalWatchdog(timeout=timedelta(milliseconds=99))
        self.watchdog.feed(now=self.now)
        with self.assertRaisesRegex(ValueError, "monotônica"):
            self.watchdog.feed(now=self.now - timedelta(seconds=1))
