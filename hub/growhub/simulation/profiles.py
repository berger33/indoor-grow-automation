"""Perfis nominais completos para simulação de uma estação v1."""

from __future__ import annotations

from datetime import timedelta

from ..domain.sensors import EXPECTED_UNIT, SensorKind
from .sensors import SequenceSensorSimulator, SimulationFrame

NOMINAL_VALUES = {
    SensorKind.PH: 6.0,
    SensorKind.EC: 1.8,
    SensorKind.WATER_TEMPERATURE: 22.0,
    SensorKind.AIR_TEMPERATURE: 25.0,
    SensorKind.LEAF_TEMPERATURE: 24.0,
    SensorKind.HUMIDITY: 60.0,
    SensorKind.CO2: 650.0,
    SensorKind.RESERVOIR_LEVEL: 40.0,
    SensorKind.FLOW: 2.0,
    SensorKind.LEAK: 0.0,
}


def nominal_station_profile(
    station_id: str = "grow-01",
) -> dict[SensorKind, SequenceSensorSimulator]:
    """Cria um simulador nominal para cada tipo de sensor suportado."""
    return {
        kind: SequenceSensorSimulator(
            station_id=station_id,
            sensor_id=f"sim-{kind.value}",
            kind=kind,
            unit=EXPECTED_UNIT[kind],
            frames=(
                SimulationFrame(value),
                SimulationFrame(value, timedelta(seconds=5)),
            ),
        )
        for kind, value in NOMINAL_VALUES.items()
    }
