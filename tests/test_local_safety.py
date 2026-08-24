from unittest import TestCase

from hub.growhub.control.safety import LocalSafetySupervisor
from hub.growhub.control.state_machine import (
    ControlEvent,
    ControlState,
    LocalControlStateMachine,
)
from hub.growhub.domain.leak import LeakLatch


class LocalSafetySupervisorTests(TestCase):
    def setUp(self) -> None:
        self.machine = LocalControlStateMachine()
        self.machine.dispatch(ControlEvent.BOOT_COMPLETE)
        self.machine.dispatch(ControlEvent.START_BATCH)
        self.safety = LocalSafetySupervisor(
            self.machine,
            leak_latch=LeakLatch(wet_confirmations=2, dry_confirmations=2),
        )

    def test_confirmed_leak_cuts_active_outputs_and_latches_alarm(self) -> None:
        self.assertTrue(self.safety.outputs_permitted)
        self.assertFalse(self.safety.update_leak(True))
        self.assertTrue(self.safety.update_leak(True))
        self.assertEqual(ControlState.ALARM, self.machine.state)
        self.assertEqual("leak_detected", self.machine.alarm_reason)
        self.assertFalse(self.safety.outputs_permitted)

    def test_alarm_requires_dry_confirmation_and_explicit_reset(self) -> None:
        self.safety.update_leak(True)
        self.safety.update_leak(True)
        self.assertFalse(self.safety.reset_leak_alarm())
        self.safety.update_leak(False)
        self.assertFalse(self.safety.reset_leak_alarm())
        self.safety.update_leak(False)
        self.assertTrue(self.safety.reset_leak_alarm())
        self.assertEqual(ControlState.IDLE, self.machine.state)

    def test_dry_samples_never_stop_a_normal_batch(self) -> None:
        for _ in range(5):
            self.assertFalse(self.safety.update_leak(False))
        self.assertEqual(ControlState.BATCH, self.machine.state)
