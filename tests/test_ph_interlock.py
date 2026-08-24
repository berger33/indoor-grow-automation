from unittest import TestCase

from hub.growhub.control.dosing import PHChannel, PHDirectionInterlock


class PHDirectionInterlockTests(TestCase):
    def test_allows_only_one_direction_at_a_time(self) -> None:
        interlock = PHDirectionInterlock()
        interlock.request(PHChannel.UP)
        self.assertEqual(PHChannel.UP, interlock.active)
        interlock.stop(PHChannel.UP)
        interlock.request(PHChannel.DOWN)
        self.assertEqual(PHChannel.DOWN, interlock.active)

    def test_conflict_deenergizes_and_latches_block(self) -> None:
        interlock = PHDirectionInterlock()
        interlock.request(PHChannel.UP)
        with self.assertRaisesRegex(RuntimeError, "jamais"):
            interlock.request(PHChannel.DOWN)
        self.assertIsNone(interlock.active)
        with self.assertRaises(PermissionError):
            interlock.request(PHChannel.UP)

    def test_conflict_requires_explicit_reset(self) -> None:
        interlock = PHDirectionInterlock()
        interlock.request(PHChannel.UP)
        with self.assertRaises(RuntimeError):
            interlock.request(PHChannel.DOWN)
        interlock.reset()
        interlock.request(PHChannel.DOWN)
        self.assertEqual(PHChannel.DOWN, interlock.active)

    def test_repeated_request_is_idempotent(self) -> None:
        interlock = PHDirectionInterlock()
        interlock.request(PHChannel.UP)
        interlock.request(PHChannel.UP)
        self.assertEqual(PHChannel.UP, interlock.active)
