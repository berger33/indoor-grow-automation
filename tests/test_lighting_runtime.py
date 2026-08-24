from datetime import UTC, datetime, time, timedelta
from unittest import TestCase

from hub.growhub.domain.remote_lighting import (
    LightState,
    ManualLightOverride,
    RemoteLightSchedule,
)
from hub.growhub.integrations.home_assistant import SwitchObservation
from hub.growhub.services.lighting_runtime import LightingReconciliationLoop


class MemoryStore:
    def __init__(self, schedules, overrides=None):
        self.schedules = schedules
        self.overrides = overrides or {}
        self.saves = []

    def load(self):
        return self.schedules, dict(self.overrides)

    def save(self, schedules, overrides):
        self.schedules = schedules
        self.overrides = dict(overrides)
        self.saves.append((schedules, dict(overrides)))


class FlakyClient:
    def __init__(self, failures=0):
        self.failures = failures
        self.state = False
        self.reads = 0

    def read_switch(self, entity_id):
        self.reads += 1
        if self.failures:
            self.failures -= 1
            raise ConnectionError("offline")
        return SwitchObservation(entity_id, self.state, datetime.now(UTC))

    def set_switch(self, entity_id, *, on):
        self.state = on
        return SwitchObservation(entity_id, self.state, datetime.now(UTC))


class LightingReconciliationLoopTests(TestCase):
    def setUp(self) -> None:
        self.now = datetime(2026, 8, 24, 12, tzinfo=UTC)
        self.schedule = RemoteLightSchedule(
            entity_id="switch.grow_light_1",
            on_time=time(6),
            off_time=time(18),
            weekdays=frozenset(range(7)),
        )

    def test_reconciles_every_thirty_seconds_without_busy_loop(self) -> None:
        client = FlakyClient()
        loop = LightingReconciliationLoop(client, MemoryStore((self.schedule,)))
        first = loop.run_once(now=self.now)
        self.assertTrue(first.attempted)
        early = loop.run_once(now=self.now + timedelta(seconds=29))
        self.assertFalse(early.attempted)
        loop.run_once(now=self.now + timedelta(seconds=30))
        self.assertEqual(2, client.reads)

    def test_applies_exponential_backoff_and_recovers(self) -> None:
        loop = LightingReconciliationLoop(
            FlakyClient(failures=2), MemoryStore((self.schedule,))
        )
        first = loop.run_once(now=self.now)
        self.assertEqual(1, first.consecutive_failures)
        self.assertEqual(self.now + timedelta(seconds=5), first.next_due_at)
        second = loop.run_once(now=first.next_due_at)
        self.assertEqual(self.now + timedelta(seconds=15), second.next_due_at)
        recovered = loop.run_once(now=second.next_due_at)
        self.assertEqual(0, recovered.consecutive_failures)
        self.assertIsNone(recovered.error)

    def test_removes_expired_override_before_reconciliation(self) -> None:
        expired = ManualLightOverride(LightState.OFF, self.now)
        store = MemoryStore((self.schedule,), {self.schedule.entity_id: expired})
        LightingReconciliationLoop(FlakyClient(), store).run_once(now=self.now)
        self.assertEqual({}, store.overrides)
        self.assertEqual(1, len(store.saves))

    def test_rejects_retrograde_execution_time(self) -> None:
        loop = LightingReconciliationLoop(FlakyClient(), MemoryStore((self.schedule,)))
        loop.run_once(now=self.now)
        with self.assertRaisesRegex(ValueError, "monotônicas"):
            loop.run_once(now=self.now - timedelta(seconds=1))
