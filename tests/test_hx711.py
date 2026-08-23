from unittest import TestCase

from hub.growhub.drivers.hx711 import LoadCellCalibration


class LoadCellCalibrationTests(TestCase):
    def test_converts_counts_to_mass_after_tare(self) -> None:
        calibration = LoadCellCalibration(tare_counts=100_000, counts_per_gram=42.0)
        self.assertEqual(2.0, calibration.mass_kg(184_000))

    def test_round_trip_preserves_persisted_calibration(self) -> None:
        original = LoadCellCalibration(1234, 36.25)
        self.assertEqual(original, LoadCellCalibration.from_dict(original.to_dict()))

    def test_rejects_incomplete_or_invalid_calibration(self) -> None:
        with self.assertRaises(ValueError):
            LoadCellCalibration(0, 0.0)
        with self.assertRaises(ValueError):
            LoadCellCalibration.from_dict({"tare_counts": 0})

    def test_does_not_hide_negative_mass_diagnostic(self) -> None:
        calibration = LoadCellCalibration(1_000, 10.0)
        self.assertEqual(-0.01, calibration.mass_kg(900))
