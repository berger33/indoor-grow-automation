from unittest import TestCase

from hub.growhub.domain.electrical import (
    CircuitProfile,
    ControlInterface,
    CurrentBasis,
    ElectricalLoad,
)


class ElectricalLoadTests(TestCase):
    def make_load(self, **changes: object) -> ElectricalLoad:
        values = {
            "load_id": "exhaust_fan",
            "name": "Exaustor",
            "rated_power_w": 100.0,
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
        self.assertAlmostEqual(100 / (127 * 0.9), estimate.amperes)  # type: ignore[union-attr]

    def test_rejects_invalid_power_factor(self) -> None:
        with self.assertRaisesRegex(ValueError, "power_factor"):
            self.make_load(power_factor=1.1)

    def test_rejects_unsupported_voltage(self) -> None:
        with self.assertRaisesRegex(ValueError, "127 ou 220"):
            self.make_load(supply_voltage_v=110)

    def test_accepts_documented_future_zero_to_ten_volt_interface(self) -> None:
        load = self.make_load(control_interface=ControlInterface.ZERO_TO_TEN_V)
        self.assertEqual(ControlInterface.ZERO_TO_TEN_V, load.control_interface)


class CircuitProfileTests(TestCase):
    def test_profile_reports_unknown_current_without_nameplate(self) -> None:
        load = ElectricalLoad("exhaust_fan", "Exaustor", 100, 127)
        profile = CircuitProfile(127, 60, (load,))
        self.assertEqual(("exhaust_fan",), profile.loads_missing_current())
        self.assertIsNone(profile.total_current_a())

    def test_profile_sums_mixed_environment_loads(self) -> None:
        fan = ElectricalLoad(
            "exhaust_fan", "Exaustor", 100, 127, measured_current_a=1.0
        )
        humidifier = ElectricalLoad(
            "humidifier",
            "Umidificador",
            50,
            127,
            nameplate_current_a=0.5,
        )
        profile = CircuitProfile(127, 60, (fan, humidifier))
        self.assertEqual(150, profile.rated_power_w)
        self.assertEqual(1.5, profile.total_current_a())

    def test_rejects_load_from_another_voltage_variant(self) -> None:
        load = ElectricalLoad("fan", "Exaustor", 100, 220)
        with self.assertRaisesRegex(ValueError, "incompatível"):
            CircuitProfile(127, 60, (load,))

    def test_rejects_duplicate_load_identifiers(self) -> None:
        load = ElectricalLoad("pump", "Bomba", 20, 127)
        with self.assertRaisesRegex(ValueError, "duplicado"):
            CircuitProfile(127, 60, (load, load))
