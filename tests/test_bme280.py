from unittest import TestCase

from hub.growhub.domain.faults import SensorFaultCode
from hub.growhub.drivers.bme280 import BME280Offsets, decode_environment


class BME280DecoderTests(TestCase):
    def test_applies_device_offsets_and_clamps_humidity(self) -> None:
        result = decode_environment(24.0, 99.0, BME280Offsets(0.5, 3.0))
        self.assertEqual(24.5, result.temperature_c)
        self.assertEqual(100.0, result.humidity_percent)
        self.assertIsNone(result.fault)

    def test_rejects_out_of_datasheet_range(self) -> None:
        result = decode_environment(24.0, 101.0)
        self.assertEqual(SensorFaultCode.OUT_OF_RANGE, result.fault)

    def test_reports_missing_channel_as_timeout(self) -> None:
        result = decode_environment(24.0, None)
        self.assertEqual(SensorFaultCode.TIMEOUT, result.fault)

    def test_limits_configurable_offsets(self) -> None:
        with self.assertRaises(ValueError):
            BME280Offsets(temperature_c=11.0)
