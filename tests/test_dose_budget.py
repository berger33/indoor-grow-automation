from datetime import UTC, datetime, timedelta
from unittest import TestCase

from hub.growhub.control.dosing import DoseBudget, DoseLimits


class DoseBudgetTests(TestCase):
    def setUp(self) -> None:
        self.now = datetime(2026, 8, 24, tzinfo=UTC)
        self.budget = DoseBudget(DoseLimits(5, 10, 20))

    def test_accepts_request_inside_all_limits(self) -> None:
        decision = self.budget.request(4, now=self.now)
        self.assertTrue(decision.allowed)
        self.assertEqual("within_limits", decision.reason)

    def test_rejects_event_and_hour_limits_without_recording_denial(self) -> None:
        self.assertEqual("event_limit", self.budget.request(6, now=self.now).reason)
        self.assertTrue(self.budget.request(5, now=self.now).allowed)
        self.assertTrue(self.budget.request(5, now=self.now).allowed)
        denied = self.budget.request(1, now=self.now)
        self.assertFalse(denied.allowed)
        self.assertEqual("hour_limit", denied.reason)

    def test_hour_window_expires_but_day_limit_remains(self) -> None:
        self.budget.request(5, now=self.now)
        self.budget.request(5, now=self.now)
        later = self.now + timedelta(hours=1)
        self.assertTrue(self.budget.request(5, now=later).allowed)
        self.assertTrue(self.budget.request(5, now=later).allowed)
        self.assertEqual(
            "day_limit",
            self.budget.request(1, now=later + timedelta(hours=1)).reason,
        )

    def test_rejects_invalid_limits_volume_and_time(self) -> None:
        with self.assertRaises(ValueError):
            DoseLimits(10, 5, 20)
        with self.assertRaisesRegex(ValueError, "positivo"):
            self.budget.request(0, now=self.now)
        with self.assertRaisesRegex(ValueError, "timezone"):
            self.budget.request(1, now=datetime(2026, 8, 24))
