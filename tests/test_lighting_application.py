from datetime import UTC, datetime, time
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest import TestCase

from hub.growhub.domain.remote_lighting import LightState, RemoteLightSchedule
from hub.growhub.services.lighting_application import LightingApplicationService
from hub.growhub.services.lighting_store import FileLightingStore


class LightingApplicationServiceTests(TestCase):
    def setUp(self) -> None:
        self.temporary = TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.store = FileLightingStore(Path(self.temporary.name) / "lighting.json")
        self.schedule = RemoteLightSchedule(
            entity_id="switch.grow_light_1",
            on_time=time(18),
            off_time=time(6),
            weekdays=frozenset(range(7)),
        )
        self.store.save((self.schedule,), {})
        self.now = datetime(2026, 8, 24, 22, tzinfo=UTC)
        self.service = LightingApplicationService(self.store, clock=lambda: self.now)

    def test_view_never_invents_remote_confirmation(self) -> None:
        channel = self.service.view().channels[0]
        self.assertEqual("unavailable", channel.status)
        self.assertIsNone(channel.observed)

    def test_schedule_update_is_persisted(self) -> None:
        channel = self.service.update_schedule(
            self.schedule.entity_id,
            on_time=time(20),
            off_time=time(8),
            weekdays=frozenset({0, 1, 2, 3, 4}),
            timezone="America/Sao_Paulo",
            enabled=False,
        )
        self.assertFalse(channel.schedule.enabled)
        self.assertEqual(time(20), self.store.load()[0][0].on_time)

    def test_override_and_cancel_are_persisted(self) -> None:
        channel = self.service.set_override(
            self.schedule.entity_id,
            state=LightState.ON,
            duration_minutes=30,
        )
        self.assertEqual("manual_override", channel.source)
        self.assertEqual(LightState.ON, self.store.load()[1][self.schedule.entity_id].state)
        cancelled = self.service.set_override(
            self.schedule.entity_id,
            state=None,
            duration_minutes=30,
        )
        self.assertIsNone(cancelled.override)

    def test_unknown_entity_is_rejected(self) -> None:
        with self.assertRaises(KeyError):
            self.service.set_override(
                "switch.unknown", state=LightState.OFF, duration_minutes=30
            )
