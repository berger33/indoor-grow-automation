from unittest import TestCase

from hub.growhub.control.climate_priority import arbitrate_climate
from hub.growhub.control.exhaust import ExhaustAction, ExhaustDecision
from hub.growhub.control.humidity import HumidifierAction, HumidityDecision


class ClimatePriorityTests(TestCase):
    def test_ventilation_wins_when_both_outputs_request_on(self) -> None:
        result = arbitrate_climate(
            ExhaustDecision(ExhaustAction.ON, "both_sensors_hot"),
            HumidityDecision(HumidifierAction.ON, "lower_hysteresis"),
        )
        self.assertEqual(ExhaustAction.ON, result.exhaust)
        self.assertEqual(HumidifierAction.OFF, result.humidifier)
        self.assertEqual("ventilation_priority", result.reason)

    def test_preserves_compatible_commands(self) -> None:
        result = arbitrate_climate(
            ExhaustDecision(ExhaustAction.OFF, "both_sensors_cool"),
            HumidityDecision(HumidifierAction.ON, "lower_hysteresis"),
        )
        self.assertEqual(ExhaustAction.OFF, result.exhaust)
        self.assertEqual(HumidifierAction.ON, result.humidifier)
        self.assertEqual("commands_compatible", result.reason)
