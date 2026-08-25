from datetime import UTC, datetime, time
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest import TestCase

from alembic import command
from alembic.config import Config

from hub.growhub.persistence.database import create_database_engine, create_session_factory
from hub.growhub.persistence.operations import SqlOperations
from hub.growhub.persistence.security import SqlUserRepository
from hub.growhub.services.operations import CalibrationRecord, IrrigationWindow, Recipe, RecipeStep, SensorDefinition, Setpoints, StationDefinition
from hub.growhub.services.security import AuthService, UserRole


ROOT = Path(__file__).resolve().parents[1]
NOW = datetime(2026, 8, 24, tzinfo=UTC)


class SqlOperationsTests(TestCase):
    def test_configuration_users_and_audit_survive_restart(self) -> None:
        with TemporaryDirectory() as directory:
            url = f"sqlite:///{Path(directory) / 'grow.db'}"
            config = Config(str(ROOT / "alembic.ini"))
            config.set_main_option("sqlalchemy.url", url)
            command.upgrade(config, "head")
            sessions = create_session_factory(create_database_engine(url))
            users = SqlUserRepository(sessions)
            auth = AuthService(b"0123456789abcdef0123456789abcdef", repository=users)
            auth.add_user("admin", "Administrador", UserRole.ADMIN, "administrator-password")
            operations = SqlOperations(sessions)
            operations.bootstrap_station(
                StationDefinition("grow_a", "Estufa A"),
                ((SensorDefinition("grow_a", "ph_tank", "pH", 30), "fertigation", "ph", "pH"),),
                now=NOW,
            )
            operations.save_setpoints("grow_a", Setpoints(5.8, 1.8, 25, 65, 1.1), user_id="admin", now=NOW)
            recipe = Recipe("vegetative", "Vegetativo", 20, 5.8, 1.8, (RecipeStep(1, 20, 1),))
            operations.save_recipe("grow_a", recipe, user_id="admin", now=NOW)
            operations.save_irrigation("grow_a", (IrrigationWindow("morning", time(8), 90, frozenset(range(7))),))
            operations.save_calibration(CalibrationRecord("00000000-0000-0000-0000-000000000001", "grow_a", "scale_1", "mass", {"counts": 100.0}, "calculated", NOW, "admin"))
            operations.record_audit("admin", "grow_a", "save_recipe", "vegetative", "applied", NOW)

            reloaded = SqlOperations(sessions)
            self.assertEqual(5.8, reloaded.setpoints["grow_a"].ph)
            self.assertEqual(recipe, reloaded.recipes["grow_a"]["vegetative"])
            self.assertEqual("morning", reloaded.irrigation["grow_a"][0].window_id)
            self.assertEqual("scale_1", reloaded.calibrations[0].device_id)
            self.assertEqual("save_recipe", reloaded.audit[0].action)
            self.assertTrue(AuthService(b"0123456789abcdef0123456789abcdef", repository=users).has_users)

    def test_bootstrap_is_idempotent(self) -> None:
        with TemporaryDirectory() as directory:
            url = f"sqlite:///{Path(directory) / 'grow.db'}"
            config = Config(str(ROOT / "alembic.ini"))
            config.set_main_option("sqlalchemy.url", url)
            command.upgrade(config, "head")
            operations = SqlOperations(create_session_factory(create_database_engine(url)))
            station = StationDefinition("grow_a", "Estufa A")
            sensors = ((SensorDefinition("grow_a", "ph_tank", "pH", 30), "fertigation", "ph", "pH"),)
            operations.bootstrap_station(station, sensors, now=NOW)
            operations.bootstrap_station(station, sensors, now=NOW)
            self.assertEqual(1, len(operations.stations))
