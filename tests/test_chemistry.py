from unittest import TestCase

from hub.growhub.domain.chemistry import (
    TemperatureCompensation,
    normalize_ec_to_reference,
)


class TemperatureCompensationTests(TestCase):
    def test_builds_same_validated_command_for_ph_and_ec_circuits(self) -> None:
        compensation = TemperatureCompensation(22.375)
        self.assertEqual("T,22.38", compensation.atlas_command())

    def test_normalizes_ec_to_reference_temperature(self) -> None:
        result = normalize_ec_to_reference(2.0, TemperatureCompensation(30.0))
        self.assertAlmostEqual(2.0 / 1.095, result)

    def test_reference_temperature_preserves_ec(self) -> None:
        result = normalize_ec_to_reference(1.8, TemperatureCompensation(25.0))
        self.assertEqual(1.8, result)

    def test_rejects_unsafe_temperature_and_coefficient(self) -> None:
        with self.assertRaises(ValueError):
            TemperatureCompensation(70.0)
        with self.assertRaises(ValueError):
            normalize_ec_to_reference(
                1.8,
                TemperatureCompensation(25.0),
                coefficient_per_c=0.2,
            )
