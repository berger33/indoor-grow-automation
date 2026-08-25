from datetime import UTC, datetime
from unittest import TestCase

from hub.growhub.services.calibration import evaluate_calibration


NOW = datetime(2026, 8, 24, tzinfo=UTC)


class CalibrationAssistantTests(TestCase):
    def test_calculates_mass_and_pump_coefficients(self) -> None:
        mass = evaluate_calibration("mass", {"tareCounts": 1000, "referenceCounts": 501000, "referenceMassKg": 5}, device_id="scale_1", now=NOW)
        self.assertEqual("calculated", mass.status)
        self.assertEqual(100, mass.coefficients["counts_per_gram"])
        pump = evaluate_calibration(
            "pump",
            {"durationsSeconds": [5, 10, 15], "volumesMl": [10, 20, 30], "supplyVoltageV": 12},
            device_id="pump_1",
            now=NOW,
        )
        self.assertAlmostEqual(2, pump.coefficients["flowMlS"])

    def test_ph_and_ec_never_claim_completion_without_atlas_ack(self) -> None:
        ph = evaluate_calibration("ph", {"standardsPh": [4, 7, 10]}, device_id="ph_1", now=NOW)
        ec = evaluate_calibration("ec", {"standardMsCm": 1.413, "observedMsCm": 1.4}, device_id="ec_1", now=NOW)
        self.assertEqual("requires_device_ack", ph.status)
        self.assertEqual("requires_device_ack", ec.status)
        self.assertIn("ACK", ph.explanation)

    def test_rejects_inconsistent_measurements(self) -> None:
        with self.assertRaises(ValueError):
            evaluate_calibration("mass", {"tareCounts": 1000, "referenceCounts": 900, "referenceMassKg": 5}, device_id="scale_1", now=NOW)
        with self.assertRaisesRegex(ValueError, "repetibilidade"):
            evaluate_calibration("pump", {"durationsSeconds": [5, 10, 15], "volumesMl": [10, 50, 30], "supplyVoltageV": 12}, device_id="pump_1", now=NOW)
