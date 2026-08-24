"""Monitoramento somente leitura de CO₂ para o MVP."""

from __future__ import annotations

import math
from dataclasses import dataclass
from datetime import datetime, timedelta
from enum import StrEnum

from .sensors import ReadingQuality, SensorKind, SensorReading


class CO2Status(StrEnum):
    NORMAL = "normal"
    WARNING = "warning"
    CRITICAL = "critical"
    UNAVAILABLE = "unavailable"


@dataclass(frozen=True, slots=True)
class CO2Config:
    warning_ppm: float = 1_200
    critical_ppm: float = 2_000
    maximum_age: timedelta = timedelta(minutes=2)

    def __post_init__(self) -> None:
        if not all(math.isfinite(value) for value in (self.warning_ppm, self.critical_ppm)):
            raise ValueError("limites de CO₂ devem ser finitos")
        if not 600 <= self.warning_ppm < self.critical_ppm <= 10_000:
            raise ValueError("limites de CO₂ inválidos")
        if not timedelta(seconds=10) <= self.maximum_age <= timedelta(minutes=30):
            raise ValueError("idade máxima de CO₂ inválida")


@dataclass(frozen=True, slots=True)
class CO2Assessment:
    status: CO2Status
    ppm: float | None
    alarm_code: str | None
    explanation: str


class CO2Monitor:
    """Classifica leitura e emite alerta; deliberadamente não possui atuador."""

    def __init__(self, config: CO2Config = CO2Config()) -> None:
        self._config = config

    def assess(self, reading: SensorReading | None, *, now: datetime) -> CO2Assessment:
        if now.tzinfo is None or now.utcoffset() is None:
            raise ValueError("now deve conter timezone")
        if reading is None:
            return self._unavailable("co2_missing", "Sensor de CO₂ sem leitura.")
        if reading.kind is not SensorKind.CO2:
            raise ValueError("leitura não pertence ao sensor de CO₂")
        if reading.observed_at > now:
            raise ValueError("leitura de CO₂ está no futuro")
        if reading.quality is not ReadingQuality.VALID:
            return self._unavailable("co2_invalid", "Leitura de CO₂ inválida; nenhum comando foi emitido.")
        if now - reading.observed_at > self._config.maximum_age:
            return self._unavailable("co2_stale", "Leitura de CO₂ antiga; verifique sensor e rede.")
        if reading.value >= self._config.critical_ppm:
            return CO2Assessment(
                CO2Status.CRITICAL,
                reading.value,
                "co2_critical_high",
                "CO₂ crítico: ventile e inspecione o ambiente; o sistema não injeta gás.",
            )
        if reading.value >= self._config.warning_ppm:
            return CO2Assessment(
                CO2Status.WARNING,
                reading.value,
                "co2_warning_high",
                "CO₂ elevado: acompanhe a tendência; o sistema permanece somente em monitoramento.",
            )
        return CO2Assessment(
            CO2Status.NORMAL,
            reading.value,
            None,
            "CO₂ dentro da faixa monitorada.",
        )

    @staticmethod
    def _unavailable(code: str, explanation: str) -> CO2Assessment:
        return CO2Assessment(CO2Status.UNAVAILABLE, None, code, explanation)
