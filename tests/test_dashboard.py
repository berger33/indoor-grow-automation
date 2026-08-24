from unittest import TestCase

from hub.growhub.domain.remote_lighting import LightState
from hub.growhub.services.dashboard import (
    ControlTileStatus,
    local_actuator_tile,
    remote_light_tile,
)
from hub.growhub.services.remote_lighting import ReconciliationResult


class DashboardViewModelTests(TestCase):
    def test_remote_light_never_reports_success_without_confirmation(self) -> None:
        tile = remote_light_tile(
            ReconciliationResult(
                entity_id="switch.grow_light_1",
                desired=LightState.ON,
                observed=LightState.OFF,
                source="schedule",
                command_sent=True,
                confirmed=False,
            )
        )
        self.assertEqual(ControlTileStatus.DIVERGENT, tile.status)
        self.assertFalse(tile.feedback_confirmed)
        self.assertIn("não confirmou", tile.explanation)

    def test_local_actuator_explains_inhibition(self) -> None:
        tile = local_actuator_tile(
            "exhaust_fan",
            desired_on=True,
            observed_on=False,
            feedback_confirmed=False,
            inhibit_reason="falha de corrente retida",
        )
        self.assertEqual(ControlTileStatus.INHIBITED, tile.status)
        self.assertFalse(tile.desired_on)
        self.assertEqual("falha de corrente retida", tile.explanation)

    def test_local_actuator_separates_unknown_and_confirmed_feedback(self) -> None:
        unavailable = local_actuator_tile(
            "mixing_pump",
            desired_on=True,
            observed_on=None,
            feedback_confirmed=False,
        )
        self.assertEqual(ControlTileStatus.UNAVAILABLE, unavailable.status)
        confirmed = local_actuator_tile(
            "mixing_pump",
            desired_on=True,
            observed_on=True,
            feedback_confirmed=True,
        )
        self.assertEqual(ControlTileStatus.CONFIRMED, confirmed.status)
