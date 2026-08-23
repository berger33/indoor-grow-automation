from unittest import TestCase

from hub.growhub.domain.faults import SensorFaultCode
from hub.growhub.drivers.atlas_ec import decode_ec
from hub.growhub.drivers.atlas_ezo import AtlasStatus


class AtlasECDecoderTests(TestCase):
    def test_converts_microsiemens_to_millisiemens(self) -> None:
        result = decode_ec(AtlasStatus.SUCCESS, "1850")
        self.assertEqual(1.85, result.millisiemens_per_cm)
        self.assertIsNone(result.fault)

    def test_ignores_optional_fields_after_conductivity(self) -> None:
        result = decode_ec(AtlasStatus.SUCCESS, "2200,1100,1.2,1.0")
        self.assertEqual(2.2, result.millisiemens_per_cm)

    def test_rejects_invalid_or_implausible_conductivity(self) -> None:
        self.assertEqual(
            SensorFaultCode.PROTOCOL_ERROR,
            decode_ec(AtlasStatus.SUCCESS, "bad").fault,
        )
        self.assertEqual(
            SensorFaultCode.OUT_OF_RANGE,
            decode_ec(AtlasStatus.SUCCESS, "25000").fault,
        )

    def test_preserves_transport_failure(self) -> None:
        result = decode_ec(AtlasStatus.NO_DATA, None)
        self.assertEqual(SensorFaultCode.DISCONNECTED, result.fault)
