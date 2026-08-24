from datetime import UTC, datetime, timedelta
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest import TestCase
from uuid import uuid4

from alembic import command
from alembic.config import Config
from sqlalchemy import inspect

from hub.growhub.contracts.telemetry import TelemetryEnvelope
from hub.growhub.domain.sensors import SensorKind, SensorReading, Unit
from hub.growhub.persistence.database import create_database_engine, create_session_factory
from hub.growhub.persistence.telemetry import SqlTelemetryRepository, TelemetryCapacityPlan


ROOT = Path(__file__).resolve().parents[1]


class PersistenceTests(TestCase):
    def migrated_repository(self, path: Path) -> SqlTelemetryRepository:
        url = f"sqlite:///{path}"
        config = Config(str(ROOT / "alembic.ini"))
        config.set_main_option("sqlalchemy.url", url)
        command.upgrade(config, "head")
        engine = create_database_engine(url)
        return SqlTelemetryRepository(create_session_factory(engine))

    def test_initial_migration_creates_operational_tables(self) -> None:
        with TemporaryDirectory() as directory:
            path = Path(directory) / "grow.db"
            repository = self.migrated_repository(path)
            tables = set(inspect(repository._sessions.kw["bind"]).get_table_names())
            self.assertTrue({"stations", "sensors", "telemetry", "telemetry_hourly", "lighting_schedules", "lighting_overrides"}.issubset(tables))

    def test_telemetry_is_idempotent_and_retention_is_explicit(self) -> None:
        now = datetime(2026, 8, 24, 15, tzinfo=UTC)
        with TemporaryDirectory() as directory:
            repository = self.migrated_repository(Path(directory) / "grow.db")
            repository.add_station("grow-01", "Estufa", "America/Sao_Paulo", now=now)
            repository.add_sensor("grow-01", "air_temp", "climate", "air_temperature", "°C", 120)
            reading = SensorReading("grow-01", "air_temp", SensorKind.AIR_TEMPERATURE, 26.5, Unit.CELSIUS, now)
            envelope = TelemetryEnvelope(str(uuid4()), 1, now, reading)
            self.assertTrue(repository.save(envelope, received_at=now))
            self.assertFalse(repository.save(envelope, received_at=now))
            self.assertEqual(26.5, repository.latest("grow-01")[0].value)
            self.assertEqual(1, repository.purge_raw(now=now + timedelta(days=91), keep_for=timedelta(days=90)))

    def test_capacity_forecast_matches_documented_baseline(self) -> None:
        plan = TelemetryCapacityPlan()
        self.assertEqual(16_819_200, plan.records_per_year)
        self.assertAlmostEqual(3.45, plan.primary_gib_per_year, places=2)
        self.assertAlmostEqual(8.61, plan.provisioned_gib_per_year, places=2)
