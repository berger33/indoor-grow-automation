from unittest import TestCase

from hub.growhub.domain.faults import SensorFaultCode
from hub.growhub.drivers.atlas_ezo import AtlasStatus, status_fault
from hub.growhub.drivers.atlas_ph import decode_ph


class AtlasPHDecoderTests(TestCase):
    def test_decodes_successful_ph(self) -> None:
        result = decode_ph(AtlasStatus.SUCCESS, "6.125")
        self.assertEqual(6.125, result.ph)
        self.assertIsNone(result.fault)

    def test_maps_documented_status_codes(self) -> None:
        self.assertEqual(
            SensorFaultCode.PROTOCOL_ERROR,
            status_fault(AtlasStatus.SYNTAX_ERROR),
        )
        self.assertEqual(
            SensorFaultCode.SENSOR_NOT_READY,
            status_fault(AtlasStatus.PROCESSING),
        )
        self.assertEqual(
            SensorFaultCode.DISCONNECTED,
            status_fault(AtlasStatus.NO_DATA),
        )

    def test_rejects_invalid_payload_and_out_of_range_ph(self) -> None:
        self.assertEqual(
            SensorFaultCode.PROTOCOL_ERROR,
            decode_ph(AtlasStatus.SUCCESS, "?").fault,
        )
        self.assertEqual(
            SensorFaultCode.OUT_OF_RANGE,
            decode_ph(AtlasStatus.SUCCESS, "15").fault,
        )
