from datetime import UTC, datetime, time, timedelta
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest import TestCase

from alembic import command
from alembic.config import Config

from hub.growhub.domain.remote_lighting import LightState, ManualLightOverride, RemoteLightSchedule
from hub.growhub.persistence.database import create_database_engine, create_session_factory
from hub.growhub.persistence.lighting import SqlLightingStore
from hub.growhub.services.lighting_store import FileLightingStore
from scripts.migrate_lighting_state import migrate


ROOT = Path(__file__).resolve().parents[1]


class SqlLightingStoreTests(TestCase):
    def setUp(self) -> None:
        self.temporary = TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.database = Path(self.temporary.name) / "grow.db"
        self.url = f"sqlite:///{self.database}"
        config = Config(str(ROOT / "alembic.ini"))
        config.set_main_option("sqlalchemy.url", self.url)
        command.upgrade(config, "head")
        self.store = SqlLightingStore(create_session_factory(create_database_engine(self.url)))
        self.schedule = RemoteLightSchedule("switch.grow_light_1", time(18), time(6), frozenset(range(7)))

    def test_round_trip_is_transactional(self) -> None:
        self.assertTrue(self.store.is_empty())
        override = ManualLightOverride(LightState.ON, datetime(2026, 8, 25, tzinfo=UTC) + timedelta(minutes=30))
        self.store.save((self.schedule,), {self.schedule.entity_id: override})
        schedules, overrides = self.store.load()
        self.assertEqual((self.schedule,), schedules)
        self.assertEqual(override, overrides[self.schedule.entity_id])

    def test_migration_is_dry_run_then_refuses_overwrite(self) -> None:
        state = Path(self.temporary.name) / "lighting.json"
        url_file = Path(self.temporary.name) / "database-url"
        url_file.write_text(self.url, encoding="utf-8")
        FileLightingStore(state).save((self.schedule,), {})
        self.assertEqual(1, migrate(state, url_file, apply=False))
        self.assertTrue(self.store.is_empty())
        self.assertEqual(1, migrate(state, url_file, apply=True))
        with self.assertRaisesRegex(ValueError, "não sobrescreve"):
            migrate(state, url_file, apply=True)
