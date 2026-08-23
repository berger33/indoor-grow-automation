from unittest import TestCase

from hub.growhub.domain.faults import SensorFaultCode
from hub.growhub.drivers.ds18b20 import decode_temperature


class DS18B20DecoderTests(TestCase):
    def test_accepts_temperature_inside_datasheet_range(self) -> None:
        result = decode_temperature(21.625)
        self.assertTrue(result.valid)
        self.assertEqual(21.625, result.celsius)

    def test_identifies_disconnect_and_power_on_sentinels(self) -> None:
        self.assertEqual(
            SensorFaultCode.DISCONNECTED,
            decode_temperature(-127.0).fault,
        )
        self.assertEqual(
            SensorFaultCode.SENSOR_NOT_READY,
            decode_temperature(85.0).fault,
        )

    def test_identifies_timeout_and_out_of_range(self) -> None:
        self.assertEqual(SensorFaultCode.TIMEOUT, decode_temperature(None).fault)
        self.assertEqual(
            SensorFaultCode.OUT_OF_RANGE,
            decode_temperature(126.0).fault,
        )
