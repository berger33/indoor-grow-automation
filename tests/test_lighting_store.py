import json
from datetime import UTC, datetime, time, timedelta
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest import TestCase

from hub.growhub.domain.remote_lighting import (
    LightState,
    ManualLightOverride,
    RemoteLightSchedule,
)
from hub.growhub.services.lighting_store import FileLightingStore


class FileLightingStoreTests(TestCase):
    def setUp(self) -> None:
        self.temporary = TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.path = Path(self.temporary.name) / "lighting.json"
        self.store = FileLightingStore(self.path)
        self.schedule = RemoteLightSchedule(
            entity_id="switch.grow_light_1",
            on_time=time(20),
            off_time=time(8),
            weekdays=frozenset(range(7)),
        )

    def test_round_trip_preserves_schedule_and_override(self) -> None:
        expires = datetime(2026, 8, 24, tzinfo=UTC) + timedelta(minutes=30)
        override = ManualLightOverride(LightState.OFF, expires)
        self.store.save((self.schedule,), {self.schedule.entity_id: override})
        schedules, overrides = self.store.load()
        self.assertEqual((self.schedule,), schedules)
        self.assertEqual(override, overrides[self.schedule.entity_id])

    def test_write_is_atomic_and_contains_no_credentials(self) -> None:
        self.store.save((self.schedule,), {})
        self.assertFalse(self.path.with_name(".lighting.json.tmp").exists())
        payload = json.loads(self.path.read_text(encoding="utf-8"))
        self.assertEqual(1, payload["schema_version"])
        self.assertNotIn("token", payload)

    def test_rejects_unknown_override_and_corrupt_schema(self) -> None:
        override = ManualLightOverride(
            LightState.ON,
            datetime(2026, 8, 24, tzinfo=UTC) + timedelta(minutes=1),
        )
        with self.assertRaisesRegex(ValueError, "desconhecida"):
            self.store.save((self.schedule,), {"switch.unknown": override})
        self.path.write_text('{"schema_version":99}', encoding="utf-8")
        with self.assertRaisesRegex(ValueError, "incompatível"):
            self.store.load()

    def test_missing_file_never_silently_creates_empty_configuration(self) -> None:
        with self.assertRaisesRegex(ValueError, "ausente"):
            self.store.load()
