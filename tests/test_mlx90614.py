from unittest import TestCase

from hub.growhub.domain.faults import SensorFaultCode
from hub.growhub.drivers.mlx90614 import decode_leaf_temperature


class MLX90614DecoderTests(TestCase):
    def test_applies_leaf_temperature_offset(self) -> None:
        result = decode_leaf_temperature(25.0, offset_c=-0.4)
        self.assertAlmostEqual(24.6, result.leaf_temperature_c)
        self.assertIsNone(result.fault)

    def test_rejects_missing_and_implausible_sample(self) -> None:
        self.assertEqual(
            SensorFaultCode.TIMEOUT,
            decode_leaf_temperature(None).fault,
        )
        self.assertEqual(
            SensorFaultCode.OUT_OF_RANGE,
            decode_leaf_temperature(120.0).fault,
        )

    def test_rejects_unsafe_offset_configuration(self) -> None:
        with self.assertRaises(ValueError):
            decode_leaf_temperature(25.0, offset_c=15.0)
