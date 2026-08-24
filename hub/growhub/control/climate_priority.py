"""Arbitra comandos incompatíveis de exaustão e umidificação."""

from __future__ import annotations

from dataclasses import dataclass

from .exhaust import ExhaustAction, ExhaustDecision
from .humidity import HumidifierAction, HumidityDecision


@dataclass(frozen=True, slots=True)
class ClimateActuation:
    exhaust: ExhaustAction
    humidifier: HumidifierAction
    reason: str


def arbitrate_climate(
    exhaust: ExhaustDecision,
    humidifier: HumidityDecision,
) -> ClimateActuation:
    if exhaust.action is ExhaustAction.ON and humidifier.action is HumidifierAction.ON:
        return ClimateActuation(
            exhaust=ExhaustAction.ON,
            humidifier=HumidifierAction.OFF,
            reason="ventilation_priority",
        )
    return ClimateActuation(
        exhaust=exhaust.action,
        humidifier=humidifier.action,
        reason="commands_compatible",
    )
