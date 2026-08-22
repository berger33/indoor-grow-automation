from unittest import TestCase

from hub.growhub.domain.electrical import (
    CircuitProfile,
    CurrentBasis,
    ElectricalLoad,
    default_yuxinou_profile,
)


class ElectricalLoadTests(TestCase):
    def make_load(self, **changes: object) -> ElectricalLoad:
        values = {
            "load_id": "grow_light_1",
            "name": "Painel 120 W",
            "rated_power_w": 120.0,
            "supply_voltage_v": 127,
        }
        values.update(changes)
        return ElectricalLoad(**values)  # type: ignore[arg-type]

    def test_prefers_measured_current_over_nameplate(self) -> None:
        estimate = self.make_load(
            measured_current_a=1.05,
            nameplate_current_a=1.2,
            power_factor=0.9,
        ).current()
        self.assertIsNotNone(estimate)
        self.assertEqual(CurrentBasis.MEASURED, estimate.basis)  # type: ignore[union-attr]
        self.assertEqual(1.05, estimate.amperes)  # type: ignore[union-attr]

    def test_uses_nameplate_when_measurement_is_absent(self) -> None:
        estimate = self.make_load(nameplate_current_a=1.2).current()
        self.assertEqual(CurrentBasis.NAMEPLATE, estimate.basis)  # type: ignore[union-attr]

    def test_requires_explicit_power_factor_for_estimate(self) -> None:
        self.assertIsNone(self.make_load().current())

    def test_estimates_current_with_explicit_factor(self) -> None:
        estimate = self.make_load().current(assumed_power_factor=0.9)
        self.assertIsNotNone(estimate)
        self.assertEqual(CurrentBasis.ESTIMATED, estimate.basis)  # type: ignore[union-attr]
        self.assertAlmostEqual(120 / (127 * 0.9), estimate.amperes)  # type: ignore[union-attr]

    def test_rejects_invalid_power_factor(self) -> None:
        with self.assertRaisesRegex(ValueError, "power_factor"):
            self.make_load(power_factor=1.1)

    def test_rejects_unsupported_voltage(self) -> None:
        with self.assertRaisesRegex(ValueError, "127 ou 220"):
            self.make_load(supply_voltage_v=110)


class CircuitProfileTests(TestCase):
    def test_default_lighting_profile_totals_390_watts(self) -> None:
        profile = default_yuxinou_profile()
        self.assertEqual(390.0, profile.rated_power_w)
        self.assertEqual(4, len(profile.loads))

    def test_default_profile_exposes_missing_nameplate_data(self) -> None:
        profile = default_yuxinou_profile()
        self.assertEqual(
            ("grow_light_1", "grow_light_2", "grow_light_3", "grow_light_4"),
            profile.loads_missing_current(),
        )
        self.assertIsNone(profile.total_current_a())

    def test_provisional_390w_current_at_127v_and_pf_090(self) -> None:
        current = default_yuxinou_profile().total_current_a(
            assumed_power_factor=0.9
        )
        self.assertIsNotNone(current)
        self.assertAlmostEqual(3.4121, current, places=4)  # type: ignore[arg-type]

    def test_rejects_load_from_another_voltage_variant(self) -> None:
        load = ElectricalLoad("fan", "Exaustor", 100, 220)
        with self.assertRaisesRegex(ValueError, "incompatível"):
            CircuitProfile(127, 60, (load,))

    def test_rejects_duplicate_load_identifiers(self) -> None:
        load = ElectricalLoad("pump", "Bomba", 20, 127)
        with self.assertRaisesRegex(ValueError, "duplicado"):
            CircuitProfile(127, 60, (load, load))
