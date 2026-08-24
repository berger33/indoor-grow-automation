from datetime import UTC, datetime, timedelta
from unittest import TestCase

from hub.growhub.domain.stirring import (
    StirrerBank,
    StirrerPolicy,
    StirrerState,
    TachSample,
)


class StirrerBankTests(TestCase):
    def setUp(self) -> None:
        self.now = datetime(2026, 8, 23, tzinfo=UTC)
        self.policy = StirrerPolicy(
            minimum_rpm=(500, 500, 500, 500, 500, 500),
            spinup_seconds=2,
            pre_stir_seconds=3,
            tach_max_age_seconds=2,
        )
        self.bank = StirrerBank(self.policy)

    def samples(self, at: datetime, rpm: float = 900) -> tuple[TachSample, ...]:
        return tuple(TachSample(rpm, at) for _ in range(6))

    def test_blocks_dosing_until_spinup_and_pre_stir_finish(self) -> None:
        self.bank.start(self.now, frozenset({1, 2, 3, 4}))
        self.assertTrue(self.bank.output_enabled)
        self.assertFalse(self.bank.can_dose(1))
        at_spinup = self.now + timedelta(seconds=2)
        self.assertEqual(
            StirrerState.PRE_STIR,
            self.bank.update(at_spinup, self.samples(at_spinup)),
        )
        ready_at = at_spinup + timedelta(seconds=3)
        self.assertEqual(
            StirrerState.READY,
            self.bank.update(ready_at, self.samples(ready_at)),
        )
        self.assertTrue(self.bank.can_dose(1))
        self.assertFalse(self.bank.can_dose(0))

    def test_low_rotation_latches_alarm_and_removes_power(self) -> None:
        self.bank.start(self.now, frozenset({1, 2}))
        checked_at = self.now + timedelta(seconds=2)
        samples = list(self.samples(checked_at))
        samples[2] = TachSample(100, checked_at)
        self.assertEqual(
            StirrerState.ALARM,
            self.bank.update(checked_at, tuple(samples)),
        )
        self.assertFalse(self.bank.output_enabled)
        self.assertEqual("stirrer_rotation_failed:2", self.bank.alarm_reason)

    def test_stale_tach_trips_after_system_was_ready(self) -> None:
        self.bank.start(self.now, frozenset({5}))
        ready_at = self.now + timedelta(seconds=2)
        self.bank.update(ready_at, self.samples(ready_at))
        later = ready_at + timedelta(seconds=3)
        self.assertEqual(
            StirrerState.ALARM,
            self.bank.update(later, self.samples(ready_at)),
        )

    def test_alarm_requires_explicit_reset(self) -> None:
        self.bank.start(self.now, frozenset({0}))
        checked_at = self.now + timedelta(seconds=2)
        self.bank.update(checked_at, (None, None, None, None, None, None))
        self.bank.stop()
        self.assertEqual(StirrerState.ALARM, self.bank.state)
        self.assertTrue(self.bank.reset_alarm())
        self.assertEqual(StirrerState.OFF, self.bank.state)

    def test_rejects_invalid_configuration_and_naive_time(self) -> None:
        with self.assertRaisesRegex(ValueError, "seis limites"):
            StirrerPolicy(minimum_rpm=(500,))
        with self.assertRaisesRegex(ValueError, "fuso"):
            self.bank.start(datetime(2026, 8, 23), frozenset({0}))
        with self.assertRaisesRegex(ValueError, "0 e 5"):
            self.bank.start(self.now, frozenset({6}))
