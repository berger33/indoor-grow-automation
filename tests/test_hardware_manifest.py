from unittest import TestCase

from scripts.validate_hardware_manifest import (
    expand_reference_expression,
    expand_reference_group,
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
        self.assertIn("PCB-001", result.holds)
        self.assertIn("U1", result.references)
        self.assertIn("J23", result.references)
