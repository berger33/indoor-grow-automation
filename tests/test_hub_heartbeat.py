from datetime import UTC, datetime, timedelta
from unittest import TestCase

from hub.growhub.control.connectivity import (
    HubHeartbeatMonitor,
    HubLinkState,
    HubLossAction,
)
from hub.growhub.control.state_machine import ControlState


class HubHeartbeatMonitorTests(TestCase):
    def setUp(self) -> None:
        self.now = datetime(2026, 8, 24, tzinfo=UTC)
        self.monitor = HubHeartbeatMonitor(
            degraded_after=timedelta(seconds=10),
            lost_after=timedelta(seconds=30),
        )

    def test_progresses_from_online_to_degraded_and_lost(self) -> None:
        self.monitor.observe(1, now=self.now)
        self.assertEqual(HubLinkState.ONLINE, self.monitor.state(now=self.now))
        self.assertEqual(
            HubLinkState.DEGRADED,
            self.monitor.state(now=self.now + timedelta(seconds=10)),
        )
        self.assertEqual(
            HubLinkState.LOST,
            self.monitor.state(now=self.now + timedelta(seconds=30)),
        )

    def test_never_accepts_replayed_heartbeat(self) -> None:
        self.monitor.observe(2, now=self.now)
        with self.assertRaisesRegex(ValueError, "fora de ordem"):
            self.monitor.observe(2, now=self.now + timedelta(seconds=1))

    def test_loss_trips_active_control_but_idle_only_rejects_commands(self) -> None:
        self.assertEqual(
            HubLossAction.TRIP_LOCAL_CONTROL,
            self.monitor.loss_action(ControlState.BATCH),
        )
        self.assertEqual(
            HubLossAction.TRIP_LOCAL_CONTROL,
            self.monitor.loss_action(ControlState.MANUAL),
        )
        self.assertEqual(
            HubLossAction.REJECT_REMOTE_COMMANDS,
            self.monitor.loss_action(ControlState.IDLE),
        )

    def test_loss_trips_every_state_that_can_energize_outputs(self) -> None:
        for state in (
            ControlState.MANUAL,
            ControlState.BATCH,
            ControlState.IRRIGATING,
            ControlState.MAINTENANCE,
        ):
            with self.subTest(state=state):
                self.assertEqual(
                    HubLossAction.TRIP_LOCAL_CONTROL,
                    self.monitor.loss_action(state),
                )

    def test_is_lost_before_first_heartbeat(self) -> None:
        self.assertEqual(HubLinkState.LOST, self.monitor.state(now=self.now))
