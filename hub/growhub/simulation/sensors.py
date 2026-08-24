"""Geração reproduzível de leituras para bancada e testes automatizados."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta

from ..domain.sensors import SensorKind, SensorReading, Unit


@dataclass(frozen=True, slots=True)
class SimulationFrame:
    """Um valor e o deslocamento temporal esperado de uma leitura simulada."""

    value: float
    offset: timedelta = timedelta(0)

    def __post_init__(self) -> None:
        if self.offset < timedelta(0):
            raise ValueError("offset da simulação não pode ser negativo")


class SequenceSensorSimulator:
    """Emite uma sequência finita e repetível, sem relógio ou aleatoriedade ocultos."""

    def __init__(
        self,
        *,
        station_id: str,
        sensor_id: str,
        kind: SensorKind,
        unit: Unit,
        frames: tuple[SimulationFrame, ...],
    ) -> None:
        if not frames:
            raise ValueError("simulação precisa de ao menos um frame")
        self._station_id = station_id
        self._sensor_id = sensor_id
        self._kind = kind
        self._unit = unit
        self._frames = frames
        self._index = 0

    @property
    def exhausted(self) -> bool:
        return self._index >= len(self._frames)

    def reset(self) -> None:
        self._index = 0

    def next_reading(self, *, started_at: datetime) -> SensorReading:
        if started_at.tzinfo is None or started_at.utcoffset() is None:
            raise ValueError("started_at deve conter timezone")
        if self.exhausted:
            raise StopIteration("sequência simulada concluída")
        frame = self._frames[self._index]
        self._index += 1
        return SensorReading(
            station_id=self._station_id,
            sensor_id=self._sensor_id,
            kind=self._kind,
            value=frame.value,
            unit=self._unit,
            observed_at=started_at + frame.offset,
        )
