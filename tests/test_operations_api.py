import asyncio
from datetime import UTC, datetime, timedelta
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest import TestCase

from fastapi.testclient import TestClient

from hub.growhub.api import create_app
from hub.growhub.domain.sensors import SensorKind, SensorReading, Unit
from hub.growhub.services.lighting_application import LightingApplicationService
from hub.growhub.services.lighting_store import FileLightingStore
from hub.growhub.services.mqtt_gateway import MqttUnavailable
from hub.growhub.services.operations import (
    AlarmRecord,
    InMemoryOperations,
    SensorDefinition,
    Setpoints,
    StationDefinition,
)
from hub.growhub.services.realtime import RealtimeBuffer
from hub.growhub.services.security import AuthService, PasswordHasher, UserAccount, UserRole


NOW = datetime(2026, 8, 24, 12, tzinfo=UTC)


class OperationsApiTests(TestCase):
    def setUp(self) -> None:
        self.temporary = TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.lighting = LightingApplicationService(FileLightingStore(Path(self.temporary.name) / "lighting.json"), clock=lambda: NOW)
        hasher = PasswordHasher()
        self.auth = AuthService(
            b"0123456789abcdef0123456789abcdef",
            (
                UserAccount("viewer", "Leitor", UserRole.VIEWER, hasher.hash("viewer-password")),
                UserAccount("operator", "Operador", UserRole.OPERATOR, hasher.hash("operator-password")),
                UserAccount("admin", "Administrador", UserRole.ADMIN, hasher.hash("administrator-password")),
            ),
        )
        self.operations = InMemoryOperations()
        self.operations.stations["grow_a"] = StationDefinition("grow_a", "Estufa A")
        self.operations.sensors[("grow_a", "ph_tank")] = SensorDefinition("grow_a", "ph_tank", "pH do tanque", 60)
        self.operations.record_reading(
            SensorReading("grow_a", "ph_tank", SensorKind.PH, 5.8, Unit.PH, NOW - timedelta(seconds=10))
        )
        self.operations.setpoints["grow_a"] = Setpoints(5.8, 1.8, 25, 65, 1.1)
        self.operations.alarms["alarm_low"] = AlarmRecord(
            "alarm_low", "grow_a", "reservoir_low", "critical", "Nível abaixo do mínimo", "Parar bombas e completar com água", NOW
        )
        self.realtime = RealtimeBuffer()
        app = create_app(
            self.lighting,
            operations=self.operations,
            auth=self.auth,
            realtime=self.realtime,
            operations_clock=lambda: NOW,
        )
        self.client = TestClient(app, base_url="https://testserver")

    def login(self, user_id: str, password: str) -> None:
        response = self.client.post("/api/v1/auth/login", json={"userId": user_id, "password": password})
        self.assertEqual(200, response.status_code, response.text)
        self.assertTrue(response.cookies.get("growhub_session"))

    def test_requires_session_and_enforces_roles(self) -> None:
        self.assertEqual(401, self.client.get("/api/v1/stations").status_code)
        self.assertEqual(401, self.client.get("/api/v1/lighting").status_code)
        self.login("viewer", "viewer-password")
        self.assertEqual(200, self.client.get("/api/v1/stations").status_code)
        forbidden = self.client.put(
            "/api/v1/stations/grow_a/setpoints",
            json={"ph": 5.9, "ecMsCm": 1.9, "airTemperatureC": 24, "humidityPercent": 60, "vpdKpa": 1.2},
        )
        self.assertEqual(403, forbidden.status_code)

    def test_station_sensor_age_history_and_setpoints(self) -> None:
        self.login("operator", "operator-password")
        station = self.client.get("/api/v1/stations").json()["stations"][0]
        self.assertEqual("healthy", station["health"])
        sensor = self.client.get("/api/v1/stations/grow_a/sensors").json()["sensors"][0]
        self.assertEqual(10, sensor["ageSeconds"])
        self.assertEqual("valid", sensor["quality"])
        history = self.client.get("/api/v1/stations/grow_a/history?sensorId=ph_tank&hours=1").json()
        self.assertEqual(1, len(history["samples"]))
        updated = self.client.put(
            "/api/v1/stations/grow_a/setpoints",
            json={"ph": 5.9, "ecMsCm": 1.9, "airTemperatureC": 24, "humidityPercent": 60, "vpdKpa": 1.2},
        )
        self.assertEqual(200, updated.status_code, updated.text)
        self.assertEqual(5.9, updated.json()["ph"])
        self.assertEqual("update_setpoints", self.operations.audit[-1].action)

    def test_recipe_irrigation_alarm_and_command_workflows(self) -> None:
        self.login("operator", "operator-password")
        recipe = self.client.post(
            "/api/v1/stations/grow_a/recipes",
            json={
                "recipeId": "vegetative",
                "name": "Vegetativo",
                "batchLiters": 20,
                "targetPh": 5.8,
                "targetEcMsCm": 1.8,
                "steps": [
                    {"channel": 1, "volumeMl": 20, "order": 1},
                    {"channel": 2, "volumeMl": 30, "order": 2},
                ],
            },
        )
        self.assertEqual(201, recipe.status_code, recipe.text)
        calibration = self.client.post(
            "/api/v1/stations/grow_a/calibrations",
            json={"deviceId": "scale_1", "kind": "mass", "measurements": {"tareCounts": 1000, "referenceCounts": 501000, "referenceMassKg": 5}},
        )
        self.assertEqual(201, calibration.status_code, calibration.text)
        self.assertEqual("calculated", calibration.json()["status"])
        irrigation = self.client.put(
            "/api/v1/stations/grow_a/irrigation-schedules",
            json=[{"windowId": "morning", "startTime": "08:00", "durationSeconds": 90, "weekdays": [0, 1, 2, 3, 4, 5, 6]}],
        )
        self.assertEqual({"saved": 1}, irrigation.json())
        alarm = self.client.post("/api/v1/alarms/alarm_low/ack")
        self.assertEqual("acknowledged", alarm.json()["status"])
        command = self.client.post(
            "/api/v1/stations/grow_a/commands",
            json={"action": "start_irrigation", "target": "bed_a"},
        )
        self.assertEqual(202, command.status_code)
        self.assertEqual("queued", command.json()["status"])
        self.assertIn("ACK/NACK", command.json()["explanation"])
        batch = self.client.post(
            "/api/v1/stations/grow_a/commands",
            json={"action": "start_batch", "target": "vegetative"},
        )
        self.assertEqual(202, batch.status_code, batch.text)
        run = self.client.get("/api/v1/stations/grow_a/batch-runs").json()["runs"][0]
        self.assertEqual("awaiting_ack", run["currentStep"])

    def test_production_transport_failure_is_explicit_and_fail_safe(self) -> None:
        class UnavailableDispatcher:
            def start(self, _loop) -> None: pass
            def stop(self) -> None: pass
            def health(self): return {"status": "disconnected"}
            def expire_pending(self): return 0
            def dispatch(self, **_kwargs):
                raise MqttUnavailable("broker MQTT desconectado; comando não foi enviado")

        app = create_app(
            self.lighting,
            operations=self.operations,
            auth=self.auth,
            realtime=self.realtime,
            operations_clock=lambda: NOW,
            mqtt_gateway=UnavailableDispatcher(),  # type: ignore[arg-type]
        )
        with TestClient(app, base_url="https://testserver") as client:
            login = client.post("/api/v1/auth/login", json={"userId": "operator", "password": "operator-password"})
            self.assertEqual(200, login.status_code)
            response = client.post(
                "/api/v1/stations/grow_a/commands",
                json={"action": "safe_stop", "target": "station"},
            )
            self.assertEqual(503, response.status_code)
            self.assertIn("não foi enviado", response.json()["detail"])
            self.assertEqual("transport_unavailable", self.operations.audit[-1].status)

    def test_admin_creates_user_and_reads_audit(self) -> None:
        self.login("admin", "administrator-password")
        created = self.client.post(
            "/api/v1/users",
            json={"userId": "new_operator", "displayName": "Nova Operação", "role": "operator", "password": "a-strong-password"},
        )
        self.assertEqual(201, created.status_code, created.text)
        self.assertEqual("operator", created.json()["role"])
        audit = self.client.get("/api/v1/audit")
        self.assertEqual("create_user", audit.json()["records"][0]["action"])

    def test_websocket_replays_buffer_and_rejects_anonymous(self) -> None:
        asyncio.run(self.realtime.publish("sensor.updated", "grow_a", NOW, {"sensorId": "ph_tank"}))
        with self.assertRaises(WebSocketDisconnectLike):
            with TestClient(self.client.app, base_url="https://testserver").websocket_connect("/api/v1/realtime"):
                pass
        self.login("viewer", "viewer-password")
        token = self.client.cookies.get("growhub_session")
        with self.client.websocket_connect(
            "/api/v1/realtime?last_event_id=0",
            headers={"cookie": f"growhub_session={token}"},
        ) as websocket:
            event = websocket.receive_json()
        self.assertEqual(1, event["eventId"])
        self.assertEqual("sensor.updated", event["kind"])


class WebSocketDisconnectLike(Exception):
    """Adaptador substituído no teste abaixo para aceitar a exceção do cliente."""


try:
    from starlette.websockets import WebSocketDisconnect as WebSocketDisconnectLike
except ImportError:  # pragma: no cover
    pass
