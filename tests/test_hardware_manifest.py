from copy import deepcopy
from unittest import TestCase

from scripts.validate_hardware_manifest import (
    expected_output_channels,
    expand_reference_expression,
    expand_reference_group,
    validate_actuator_rows,
    validate_exhaust_contract,
    validate_layout_contract,
    validate_manifests,
    validate_stirrer_contract,
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


class StirrerContractTests(TestCase):
    def setUp(self) -> None:
        names = ("ph_down", "calmag", "micro", "bloom", "veg", "ph_up")
        self.contract = {
            "schema_version": 1,
            "release_state": "HOLD",
            "channel_count": 6,
            "channels": [
                {
                    "index": index,
                    "name": name,
                    "pump": f"PD{index + 1}",
                    "stirrer": f"M{index + 1}",
                    "tach": f"STIR_TACH_{index + 1}",
                }
                for index, name in enumerate(names)
            ],
            "drive": {
                "enable_output": "OUT07",
                "supply_vdc": 12,
                "mode": "grouped_full_speed",
                "converter": "DC2",
                "branch_fusing_required": True,
            },
            "mechanics": {
                "magnets_per_fan": 2,
                "magnet_retention_guard_required": True,
                "stir_bar_coating": "PTFE",
            },
            "feedback": {
                "required_before_dosing": True,
                "required_during_dosing": True,
            },
            "reference_sequence": {
                "nutrient_order": ["calmag", "micro", "bloom", "veg"],
                "settling_between_nutrients_seconds": 60,
                "ph_channels_excluded_from_batch_recipe": ["ph_down", "ph_up"],
            },
        }
        self.references = {
            "DC2",
            *(f"PD{number}" for number in range(1, 7)),
            *(f"M{number}" for number in range(1, 7)),
        }

    def test_accepts_complete_six_channel_contract(self) -> None:
        self.assertEqual((), validate_stirrer_contract(self.contract, self.references))

    def test_rejects_wrong_order_voltage_and_missing_tach(self) -> None:
        broken = deepcopy(self.contract)
        broken["channels"][1]["name"] = "bloom"
        broken["channels"][1]["tach"] = "STIR_TACH_1"
        broken["drive"]["supply_vdc"] = 24
        errors = validate_stirrer_contract(broken, self.references)
        self.assertTrue(any("ordem química" in error for error in errors))
        self.assertTrue(any("tacômetro exclusivo" in error for error in errors))
        self.assertTrue(any("supply_vdc" in error for error in errors))

    def test_rejects_dosing_without_rotation_interlock(self) -> None:
        broken = deepcopy(self.contract)
        broken["feedback"]["required_during_dosing"] = False
        errors = validate_stirrer_contract(broken, self.references)
        self.assertTrue(any("intertravar" in error for error in errors))


class ExhaustContractTests(TestCase):
    def setUp(self) -> None:
        self.contract = {
            "schema_version": 1,
            "release_state": "HOLD",
            "installed_profile": {"control_mode": "contactor_on_off_only"},
            "target_profile": {
                "mpn": "AI-CLS6",
                "duct_in": 6,
                "airflow_cfm": 402,
                "direct_control_state": "HOLD_UNTIL_EXACT_REVISION_PINOUT",
            },
            "control_requirements": {
                "local_fallback_required": True,
                "loss_of_esp32_must_not_stop_required_ventilation": True,
                "anti_cycle_required": True,
                "command_feedback_separation_required": True,
                "absolute_temperature_and_humidity_limits_override_vpd": True,
            },
        }

    def test_accepts_fail_safe_transition_profile(self) -> None:
        self.assertEqual(
            (), validate_exhaust_contract(self.contract, {"FAN1", "IF-F1"})
        )

    def test_rejects_direct_control_release_and_missing_fallback(self) -> None:
        broken = deepcopy(self.contract)
        broken["release_state"] = "APPROVED"
        broken["target_profile"]["direct_control_state"] = "APPROVED"
        broken["control_requirements"]["local_fallback_required"] = False
        errors = validate_exhaust_contract(broken, {"FAN1", "IF-F1"})
        self.assertTrue(any("HOLD" in error for error in errors))
        self.assertTrue(any("pinagem" in error for error in errors))
        self.assertTrue(any("fail-safe" in error for error in errors))
