from datetime import UTC, datetime, time, timedelta
from unittest import TestCase

from hub.growhub.domain.remote_lighting import (
    LightState,
    ManualLightOverride,
    RemoteLightSchedule,
    resolve_light_state,
)


class RemoteLightScheduleTests(TestCase):
    def schedule(self, *, on: time = time(6), off: time = time(18)) -> RemoteLightSchedule:
        return RemoteLightSchedule(
            entity_id="switch.grow_light_1",
            on_time=on,
            off_time=off,
            weekdays=frozenset(range(7)),
        )

    def test_switches_on_inside_local_photoperiod(self) -> None:
        instant = datetime(2026, 8, 23, 12, tzinfo=UTC)
        self.assertEqual(LightState.ON, self.schedule().desired_at(instant))

    def test_switches_off_at_exact_end(self) -> None:
        instant = datetime(2026, 8, 23, 21, tzinfo=UTC)
        self.assertEqual(LightState.OFF, self.schedule().desired_at(instant))

    def test_supports_photoperiod_crossing_midnight(self) -> None:
        schedule = self.schedule(on=time(20), off=time(8))
        during = datetime(2026, 8, 24, 5, tzinfo=UTC)
        outside = datetime(2026, 8, 24, 15, tzinfo=UTC)
        self.assertEqual(LightState.ON, schedule.desired_at(during))
        self.assertEqual(LightState.OFF, schedule.desired_at(outside))

    def test_manual_override_expires_back_to_schedule(self) -> None:
        instant = datetime(2026, 8, 23, 12, tzinfo=UTC)
        override = ManualLightOverride(LightState.OFF, instant + timedelta(minutes=10))
        self.assertEqual(
            "manual_override", resolve_light_state(self.schedule(), instant, override).source
        )
        self.assertEqual(
            LightState.ON,
            resolve_light_state(
                self.schedule(), instant + timedelta(minutes=10), override
            ).state,
        )

    def test_disabled_schedule_is_off(self) -> None:
        schedule = RemoteLightSchedule(
            entity_id="switch.grow_light_1",
            on_time=time(6),
            off_time=time(18),
            weekdays=frozenset(range(7)),
            enabled=False,
        )
        self.assertEqual(
            LightState.OFF, schedule.desired_at(datetime(2026, 8, 23, 12, tzinfo=UTC))
        )

    def test_rejects_non_switch_entity_and_naive_time(self) -> None:
        with self.assertRaisesRegex(ValueError, "switch"):
            RemoteLightSchedule(
                entity_id="light.grow",
                on_time=time(6),
                off_time=time(18),
                weekdays=frozenset(range(7)),
            )
        with self.assertRaisesRegex(ValueError, "fuso"):
            self.schedule().desired_at(datetime(2026, 8, 23, 12))
