from datetime import UTC, datetime, time, timedelta
from unittest import TestCase

from hub.growhub.domain.remote_lighting import (
    LightState,
    ManualLightOverride,
    RemoteLightSchedule,
)
from hub.growhub.integrations.home_assistant import SwitchObservation
from hub.growhub.services.remote_lighting import LightingReconciler


class FakeSwitchClient:
    def __init__(self, state=False, confirm=True):
        self.state = state
        self.confirm = confirm
        self.commands = []

    def read_switch(self, entity_id):
        return SwitchObservation(entity_id, self.state, datetime.now(UTC))

    def set_switch(self, entity_id, *, on):
        self.commands.append((entity_id, on))
        if self.confirm:
            self.state = on
        return SwitchObservation(entity_id, self.state, datetime.now(UTC))


class LightingReconcilerTests(TestCase):
    def schedule(self):
        return RemoteLightSchedule(
            entity_id="switch.grow_light_1",
            on_time=time(6),
            off_time=time(18),
            weekdays=frozenset(range(7)),
        )

    def test_sends_command_only_when_observed_state_differs(self) -> None:
        client = FakeSwitchClient(state=False)
        result = LightingReconciler(client, (self.schedule(),)).reconcile(
            now=datetime(2026, 8, 24, 12, tzinfo=UTC)
        )[0]
        self.assertEqual([("switch.grow_light_1", True)], client.commands)
        self.assertTrue(result.command_sent)
        self.assertTrue(result.confirmed)

    def test_does_not_repeat_command_when_state_already_matches(self) -> None:
        client = FakeSwitchClient(state=True)
        result = LightingReconciler(client, (self.schedule(),)).reconcile(
            now=datetime(2026, 8, 24, 12, tzinfo=UTC)
        )[0]
        self.assertEqual([], client.commands)
        self.assertFalse(result.command_sent)
        self.assertTrue(result.confirmed)

    def test_exposes_unconfirmed_command_as_failure(self) -> None:
        client = FakeSwitchClient(state=False, confirm=False)
        result = LightingReconciler(client, (self.schedule(),)).reconcile(
            now=datetime(2026, 8, 24, 12, tzinfo=UTC)
        )[0]
        self.assertFalse(result.confirmed)
        self.assertEqual(LightState.OFF, result.observed)

    def test_manual_override_has_priority_and_expiration(self) -> None:
        now = datetime(2026, 8, 24, 12, tzinfo=UTC)
        override = ManualLightOverride(LightState.OFF, now + timedelta(minutes=5))
        result = LightingReconciler(FakeSwitchClient(True), (self.schedule(),)).reconcile(
            now=now,
            overrides={"switch.grow_light_1": override},
        )[0]
        self.assertEqual("manual_override", result.source)
        self.assertEqual(LightState.OFF, result.desired)
