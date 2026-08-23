from unittest import TestCase

from hub.growhub.domain.faults import SensorFaultCode
from hub.growhub.drivers.ultrasonic_level import TankGeometry, UltrasonicLevelEstimator


class UltrasonicLevelEstimatorTests(TestCase):
    def setUp(self) -> None:
        geometry = TankGeometry(10.0, 60.0, 50.0)
        self.estimator = UltrasonicLevelEstimator(geometry, window_size=3)

    def test_maps_midpoint_distance_to_half_capacity(self) -> None:
        result = self.estimator.update(35.0)
        self.assertEqual(25.0, result.liters)

    def test_median_rejects_single_distance_spike(self) -> None:
        self.estimator.update(20.0)
        self.estimator.update(21.0)
        result = self.estimator.update(300.0)
        self.assertEqual(21.0, result.filtered_distance_cm)

    def test_reports_timeout_and_dead_zone(self) -> None:
        self.assertEqual(SensorFaultCode.TIMEOUT, self.estimator.update(None).fault)
        self.assertEqual(
            SensorFaultCode.OUT_OF_RANGE,
            self.estimator.update(1.0).fault,
        )

    def test_rejects_inverted_tank_geometry(self) -> None:
        with self.assertRaises(ValueError):
            TankGeometry(60.0, 10.0, 50.0)
