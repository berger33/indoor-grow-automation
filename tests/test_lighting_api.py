from datetime import UTC, datetime, time
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest import TestCase

from fastapi.testclient import TestClient

from hub.growhub.api import create_app
from hub.growhub.domain.remote_lighting import RemoteLightSchedule
from hub.growhub.services.lighting_application import LightingApplicationService
from hub.growhub.services.lighting_store import FileLightingStore


class LightingApiTests(TestCase):
    def setUp(self) -> None:
        self.temporary = TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        store = FileLightingStore(Path(self.temporary.name) / "lighting.json")
        store.save(
            (
                RemoteLightSchedule(
                    entity_id="switch.grow_light_1",
                    on_time=time(18),
                    off_time=time(6),
                    weekdays=frozenset(range(7)),
                ),
            ),
            {},
        )
        service = LightingApplicationService(
            store, clock=lambda: datetime(2026, 8, 24, 22, tzinfo=UTC)
        )
        self.client = TestClient(create_app(service))

    def test_health_and_unconfirmed_state(self) -> None:
        self.assertEqual({"status": "ok"}, self.client.get("/health").json())
        response = self.client.get("/api/v1/lighting")
        self.assertEqual(200, response.status_code)
        channel = response.json()["channels"][0]
        self.assertEqual("unavailable", channel["status"])
        self.assertIsNone(channel["observed"])

    def test_schedule_and_override_contract_match_panel(self) -> None:
        schedule = self.client.put(
            "/api/v1/lighting/switch.grow_light_1/schedule",
            json={
                "onTime": "20:00",
                "offTime": "08:00",
                "weekdays": [0, 2, 4],
                "timezone": "America/Sao_Paulo",
                "enabled": True,
            },
        )
        self.assertEqual(200, schedule.status_code)
        self.assertEqual("20:00", schedule.json()["schedule"]["onTime"])
        override = self.client.post(
            "/api/v1/lighting/switch.grow_light_1/override",
            json={"state": "on", "durationMinutes": 30},
        )
        self.assertEqual(200, override.status_code)
        self.assertEqual("manual_override", override.json()["source"])

    def test_rejects_unknown_entity_and_invalid_duration(self) -> None:
        missing = self.client.post(
            "/api/v1/lighting/switch.unknown/override",
            json={"state": "off", "durationMinutes": 30},
        )
        self.assertEqual(404, missing.status_code)
        invalid = self.client.post(
            "/api/v1/lighting/switch.grow_light_1/override",
            json={"state": "on", "durationMinutes": 0},
        )
        self.assertEqual(422, invalid.status_code)
