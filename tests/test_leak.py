from unittest import TestCase

from hub.growhub.domain.leak import LeakLatch


class LeakLatchTests(TestCase):
    def test_requires_multiple_wet_samples_to_latch(self) -> None:
        latch = LeakLatch(wet_confirmations=3)
        self.assertFalse(latch.update(True))
        self.assertFalse(latch.update(True))
        self.assertTrue(latch.update(True))

    def test_single_dry_sample_breaks_wet_confirmation(self) -> None:
        latch = LeakLatch(wet_confirmations=2)
        latch.update(True)
        latch.update(False)
        self.assertFalse(latch.update(True))

    def test_never_clears_without_explicit_reset(self) -> None:
        latch = LeakLatch(wet_confirmations=1, dry_confirmations=2)
        latch.update(True)
        latch.update(False)
        self.assertFalse(latch.reset())
        latch.update(False)
        self.assertTrue(latch.latched)
        self.assertTrue(latch.reset())
        self.assertFalse(latch.latched)

    def test_wet_sample_revokes_reset_permission(self) -> None:
        latch = LeakLatch(wet_confirmations=1, dry_confirmations=1)
        latch.update(True)
        latch.update(False)
        self.assertTrue(latch.reset_permitted)
        latch.update(True)
        self.assertFalse(latch.reset_permitted)
