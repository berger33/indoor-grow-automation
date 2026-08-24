from unittest import TestCase

from hub.growhub.control.gpio import OutputDefinition, SafeOutputBank


class SafeOutputBankTests(TestCase):
    def bank(self) -> SafeOutputBank:
        return SafeOutputBank(
            (
                OutputDefinition("pump", active_high=True),
                OutputDefinition("relay", active_high=False),
            )
        )

    def test_initializes_each_polarity_at_electrical_safe_level(self) -> None:
        bank = self.bank()
        self.assertEqual({"pump": False, "relay": True}, bank.initialize_safe_levels())
        self.assertFalse(bank.enabled)

    def test_cannot_enable_or_energize_before_safe_initialization(self) -> None:
        bank = self.bank()
        with self.assertRaises(PermissionError):
            bank.enable()
        with self.assertRaises(PermissionError):
            bank.command("pump", True)

    def test_emergency_disable_forces_all_outputs_safe(self) -> None:
        bank = self.bank()
        bank.initialize_safe_levels()
        bank.enable()
        bank.command("pump", True)
        bank.command("relay", True)
        self.assertEqual({"pump": True, "relay": False}, bank.electrical_levels())
        self.assertEqual({"pump": False, "relay": True}, bank.emergency_disable())
        self.assertFalse(bank.enabled)

    def test_rejects_duplicate_unknown_and_non_boolean_outputs(self) -> None:
        with self.assertRaisesRegex(ValueError, "duplicado"):
            SafeOutputBank((OutputDefinition("pump", True), OutputDefinition("pump", False)))
        bank = self.bank()
        bank.initialize_safe_levels()
        with self.assertRaises(KeyError):
            bank.command("missing", False)
        with self.assertRaises(TypeError):
            bank.command("pump", 1)  # type: ignore[arg-type]
