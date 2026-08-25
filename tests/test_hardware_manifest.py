from unittest import TestCase

from scripts.validate_hardware_manifest import (
    expected_output_channels,
    expand_reference_expression,
    expand_reference_group,
    validate_actuator_rows,
    validate_manifests,
)


class ReferenceExpansionTests(TestCase):
    def test_expands_numeric_range(self) -> None:
        self.assertEqual(("Q1", "Q2", "Q3"), expand_reference_group("Q1-Q3"))

    def test_expands_comma_separated_groups(self) -> None:
        self.assertEqual(
            ("R1", "R2", "C1"),
            expand_reference_expression("R1-R2,C1"),
        )

    def test_rejects_mixed_prefix_range(self) -> None:
        with self.assertRaisesRegex(ValueError, "prefixos"):
            expand_reference_group("R1-C3")

    def test_rejects_reverse_range(self) -> None:
        with self.assertRaisesRegex(ValueError, "invertido"):
            expand_reference_group("J9-J2")


class HardwareManifestTests(TestCase):
    def test_repository_manifests_are_structurally_coherent(self) -> None:
        result = validate_manifests()
        self.assertEqual((), result.errors)
        self.assertIn("CTRL-001", result.pending_validation)
        self.assertIn("MCU1", result.references)
        self.assertIn("PD6", result.references)
        self.assertEqual("1620", str(result.total_brl))


class ActuatorMapTests(TestCase):
    def test_formats_expected_channels_with_leading_zero(self) -> None:
        self.assertEqual(("OUT01", "OUT02", "OUT03"), expected_output_channels(3))

    def test_rejects_missing_channel(self) -> None:
        rows = [
            {
                "channel": "OUT01",
                "function": "pump",
                "safe_state": "OFF",
                "interlock": "timeout",
            },
            {
                "channel": "OUT03",
                "function": "fan",
                "safe_state": "OFF",
                "interlock": "sensor",
            },
        ]
        errors = validate_actuator_rows(rows, 2)
        self.assertTrue(any("exatamente" in error for error in errors))

    def test_rejects_duplicate_function_and_missing_safety_fields(self) -> None:
        rows = [
            {
                "channel": "OUT01",
                "function": "pump",
                "safe_state": "",
                "interlock": "",
            },
            {
                "channel": "OUT02",
                "function": "pump",
                "safe_state": "OFF",
                "interlock": "timeout",
            },
        ]
        errors = validate_actuator_rows(rows, 2)
        self.assertTrue(any("duplicadas" in error for error in errors))
        self.assertTrue(any("safe_state" in error for error in errors))
        self.assertTrue(any("interlock" in error for error in errors))
