import json
from datetime import UTC, datetime
from unittest import TestCase
from uuid import uuid4

from hub.growhub.contracts.alarms import AlarmEnvelope, AlarmSeverity


NOW = datetime(2026, 8, 24, 12, tzinfo=UTC)


class AlarmContractTests(TestCase):
    def alarm(self) -> AlarmEnvelope:
        return AlarmEnvelope(
            alarm_id=str(uuid4()),
            station_id="grow-01",
            code="leak_detected",
            severity=AlarmSeverity.CRITICAL,
            cause="Detector inferior confirmou água.",
            procedure="Mantenha as saídas desligadas, inspecione e reconheça depois de seco.",
            raised_at=NOW,
        )

    def test_round_trip_preserves_latched_alarm(self) -> None:
        alarm = self.alarm()
        self.assertEqual(alarm, AlarmEnvelope.from_json(alarm.to_json()))

    def test_rejects_unlatched_unknown_and_extra_fields(self) -> None:
        raw = json.loads(self.alarm().to_json())
        raw["latched"] = False
        with self.assertRaises(ValueError):
            AlarmEnvelope.from_json(json.dumps(raw))
        raw["latched"] = True
        raw["extra"] = "not-allowed"
        with self.assertRaises(ValueError):
            AlarmEnvelope.from_json(json.dumps(raw))
