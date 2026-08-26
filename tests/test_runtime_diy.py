from unittest import TestCase

from hub.growhub.api.runtime import DIY_SENSOR_LAYOUT
from hub.growhub.domain.sensors import SensorKind
from hub.growhub.services.mqtt_gateway import COMMAND_ROUTES


class DiyRuntimeIdentityTests(TestCase):
    def test_every_command_targets_the_single_controller(self) -> None:
        self.assertTrue(COMMAND_ROUTES)
        self.assertEqual({"controller"}, {node for node, _ in COMMAND_ROUTES.values()})

    def test_runtime_registers_only_sensors_present_in_diy_bom(self) -> None:
        self.assertEqual(
            {
                "ph_tank": SensorKind.PH,
                "ec_tank": SensorKind.EC,
                "air_temperature": SensorKind.AIR_TEMPERATURE,
                "humidity": SensorKind.HUMIDITY,
                "leak": SensorKind.LEAK,
            },
            {sensor_id: kind for sensor_id, _label, kind, _node in DIY_SENSOR_LAYOUT},
        )
        self.assertEqual({"controller"}, {node for *_rest, node in DIY_SENSOR_LAYOUT})
