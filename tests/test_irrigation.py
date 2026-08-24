from datetime import UTC, datetime, time, timedelta
from unittest import TestCase

from hub.growhub.control.irrigation import (
    IrrigationAction,
    IrrigationEvent,
    IrrigationSchedule,
    IrrigationScheduler,
)


class IrrigationSchedulerTests(TestCase):
    def setUp(self) -> None:
        self.scheduler = IrrigationScheduler(
            IrrigationSchedule(
                (
                    IrrigationEvent("feed_1", time(8), timedelta(minutes=5)),
                    IrrigationEvent("feed_2", time(20), timedelta(minutes=2)),
                )
            )
        )

    def evaluate(self, hour, minute=0, **overrides):
        inputs = {
            "alarm_active": False,
            "level_ok": True,
            "level_reading_fresh": True,
        }
        inputs.update(overrides)
        return self.scheduler.evaluate(
            now=datetime(2026, 8, 24, hour, minute, tzinfo=UTC),
            **inputs,
        )

    def test_starts_and_stops_enabled_event_once(self) -> None:
        started = self.evaluate(11)  # 08:00 America/Sao_Paulo
        self.assertEqual(IrrigationAction.ON, started.action)
        self.assertEqual("feed_1", started.event_id)
        self.assertEqual(IrrigationAction.ON, self.evaluate(11, 4).action)
        complete = self.evaluate(11, 5)
        self.assertEqual(IrrigationAction.OFF, complete.action)
        self.assertEqual("event_complete", complete.reason)
        self.assertEqual("no_event_due", self.evaluate(11, 6).reason)

    def test_resumes_only_remaining_window_after_restart(self) -> None:
        late = self.evaluate(11, 3)
        self.assertEqual(IrrigationAction.ON, late.action)
        self.assertEqual(2, int((late.ends_at - datetime(2026, 8, 24, 11, 3, tzinfo=UTC)).total_seconds() / 60))

    def test_alarm_low_level_and_stale_reading_inhibit_pump(self) -> None:
        self.assertEqual(
            "alarm_active", self.evaluate(11, alarm_active=True).reason
        )
        self.assertEqual(
            "insufficient_level", self.evaluate(12, level_ok=False).reason
        )
        self.assertEqual(
            "stale_level", self.evaluate(13, level_reading_fresh=False).reason
        )

    def test_rejects_more_than_five_or_overlapping_events(self) -> None:
        with self.assertRaisesRegex(ValueError, "cinco"):
            IrrigationSchedule(
                tuple(
                    IrrigationEvent(str(index), time(index), timedelta(minutes=1))
                    for index in range(6)
                )
            )
        with self.assertRaisesRegex(ValueError, "sobrepostos"):
            IrrigationSchedule(
                (
                    IrrigationEvent("one", time(8), timedelta(minutes=5)),
                    IrrigationEvent("two", time(8, 4), timedelta(minutes=5)),
                )
            )
