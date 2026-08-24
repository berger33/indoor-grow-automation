from unittest import TestCase

from scripts.validate_hardware_manifest import (
    expected_output_channels,
    expand_reference_expression,
    expand_reference_group,
    validate_actuator_rows,
    validate_layout_contract,
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
        self.assertIn("J31", result.references)


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


class LayoutContractTests(TestCase):
    def setUp(self) -> None:
        self.contract = {
            "schema_version": 1,
            "lighting_included": False,
            "arrangement": "vertical_stacked",
            "rack_envelope_max_mm": {
                "width": 900,
                "depth": 600,
                "height": 2000,
            },
            "tanks": [
                {
                    "id": "TK-101",
                    "role": "source_water",
                    "nominal_volume_l": 50,
                    "tier": "upper",
                    "platform": "PL1",
                    "shelf": "LV1",
                },
                {
                    "id": "TK-201",
                    "role": "mix_irrigation",
                    "nominal_volume_l": 50,
                    "tier": "lower",
                    "platform": "PL2",
                    "shelf": "LV2",
                },
            ],
            "containment": {
                "upper_collector": "CT2",
                "upper_drain_count": 2,
                "drains_to": "CT1",
                "base": "CT1",
                "base_free_volume_l": 110,
            },
        }

    def test_accepts_stacked_independent_tanks(self) -> None:
        self.assertEqual((), validate_layout_contract(self.contract))

    def test_rejects_side_by_side_arrangement(self) -> None:
        self.contract["arrangement"] = "side_by_side"
        errors = validate_layout_contract(self.contract)
        self.assertTrue(any("vertical_stacked" in error for error in errors))

    def test_rejects_shared_platform_and_shelf(self) -> None:
        tanks = self.contract["tanks"]
        tanks[1]["platform"] = "PL1"
        tanks[1]["shelf"] = "LV1"
        errors = validate_layout_contract(self.contract)
        self.assertTrue(any("plataformas" in error for error in errors))
        self.assertTrue(any("prateleiras" in error for error in errors))

    def test_rejects_insufficient_containment(self) -> None:
        containment = self.contract["containment"]
        containment["upper_drain_count"] = 1
        containment["base_free_volume_l"] = 50
        errors = validate_layout_contract(self.contract)
        self.assertTrue(any("dois drenos" in error for error in errors))
        self.assertTrue(any("110 L livres" in error for error in errors))
