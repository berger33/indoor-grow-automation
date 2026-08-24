"""Simuladores determinísticos para testes e desenvolvimento sem hardware."""

from .sensors import SequenceSensorSimulator, SimulationFrame
from .profiles import nominal_station_profile

__all__ = ["SequenceSensorSimulator", "SimulationFrame", "nominal_station_profile"]
