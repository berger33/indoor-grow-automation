from datetime import UTC, datetime
from unittest import TestCase

from hub.growhub.control.pump_calibration import CalibrationPoint, PumpCalibration


class PumpCalibrationTests(TestCase):
    def fit(self, points=None):
        return PumpCalibration.fit(
            "calmag",
            points
            or (
                CalibrationPoint(1, 3),
                CalibrationPoint(2, 6),
                CalibrationPoint(3, 9),
            ),
            supply_voltage_v=13.045,
            calibrated_at=datetime(2026, 8, 24, tzinfo=UTC),
        )

    def test_fits_volume_time_curve_and_round_trips(self) -> None:
        calibration = self.fit()
        self.assertAlmostEqual(3, calibration.flow_ml_s)
        self.assertAlmostEqual(2, calibration.duration_for(6))
        self.assertAlmostEqual(6, calibration.volume_for(2))
        self.assertEqual(13.045, calibration.supply_voltage_v)

    def test_rejects_inconsistent_measurements(self) -> None:
        with self.assertRaisesRegex(ValueError, "repetibilidade"):
            self.fit(
                (
                    CalibrationPoint(1, 3),
                    CalibrationPoint(2, 12),
                    CalibrationPoint(3, 9),
                )
            )

    def test_requires_three_durations_and_aware_timestamp(self) -> None:
        with self.assertRaisesRegex(ValueError, "três durações"):
            self.fit((CalibrationPoint(1, 3),) * 3)
        with self.assertRaisesRegex(ValueError, "timezone"):
            PumpCalibration.fit(
                "grow",
                (
                    CalibrationPoint(1, 3),
                    CalibrationPoint(2, 6),
                    CalibrationPoint(3, 9),
                ),
                supply_voltage_v=12,
                calibrated_at=datetime(2026, 8, 24),
            )

    def test_limits_manual_runtime(self) -> None:
        with self.assertRaisesRegex(ValueError, "tempo máximo"):
            self.fit().duration_for(200)
