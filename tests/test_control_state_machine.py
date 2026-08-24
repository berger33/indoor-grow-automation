from unittest import TestCase

from hub.growhub.control.state_machine import (
    ControlEvent,
    ControlState,
    LocalControlStateMachine,
)


class LocalControlStateMachineTests(TestCase):
    def test_boot_requires_explicit_completion(self) -> None:
        machine = LocalControlStateMachine()
        self.assertEqual(ControlState.BOOT, machine.state)
        self.assertEqual(
            ControlState.IDLE, machine.dispatch(ControlEvent.BOOT_COMPLETE)
        )

    def test_runs_manual_and_batch_only_from_idle(self) -> None:
        machine = LocalControlStateMachine()
        machine.dispatch(ControlEvent.BOOT_COMPLETE)
        self.assertEqual(ControlState.MANUAL, machine.dispatch(ControlEvent.START_MANUAL))
        self.assertEqual(ControlState.IDLE, machine.dispatch(ControlEvent.STOP))
        self.assertEqual(ControlState.BATCH, machine.dispatch(ControlEvent.START_BATCH))
        self.assertEqual(ControlState.IDLE, machine.dispatch(ControlEvent.STOP))

    def test_trip_from_active_state_latches_alarm(self) -> None:
        machine = LocalControlStateMachine()
        machine.dispatch(ControlEvent.BOOT_COMPLETE)
        machine.dispatch(ControlEvent.START_BATCH)
        self.assertEqual(
            ControlState.ALARM,
            machine.dispatch(ControlEvent.TRIP, reason="leak_detected"),
        )
        self.assertEqual("leak_detected", machine.alarm_reason)
        self.assertEqual(ControlState.ALARM, machine.dispatch(ControlEvent.STOP))

    def test_reset_requires_physical_clearance(self) -> None:
        machine = LocalControlStateMachine()
        machine.dispatch(ControlEvent.TRIP, reason="emergency_stop")
        with self.assertRaises(PermissionError):
            machine.dispatch(ControlEvent.RESET)
        self.assertEqual(
            ControlState.IDLE,
            machine.dispatch(ControlEvent.RESET, alarm_clear=True),
        )
        self.assertIsNone(machine.alarm_reason)

    def test_rejects_invalid_transition_and_trip_without_reason(self) -> None:
        machine = LocalControlStateMachine()
        with self.assertRaisesRegex(ValueError, "transição inválida"):
            machine.dispatch(ControlEvent.START_BATCH)
        with self.assertRaisesRegex(ValueError, "motivo"):
            machine.dispatch(ControlEvent.TRIP)
