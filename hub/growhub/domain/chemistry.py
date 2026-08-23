"""Compensação térmica explícita para medições de pH e EC."""

from __future__ import annotations

import math
from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class TemperatureCompensation:
    sample_temperature_c: float

    def __post_init__(self) -> None:
        if not math.isfinite(self.sample_temperature_c):
            raise ValueError("temperatura de compensação deve ser finita")
        if not 0.0 <= self.sample_temperature_c <= 60.0:
            raise ValueError("temperatura de compensação fora da faixa operacional")

    def atlas_command(self) -> str:
        """Comando comum enviado aos circuitos EZO-pH e EZO-EC."""
        return f"T,{self.sample_temperature_c:.2f}"


def normalize_ec_to_reference(
    measured_ms_cm: float,
    compensation: TemperatureCompensation,
    *,
    reference_c: float = 25.0,
    coefficient_per_c: float = 0.019,
) -> float:
    """Normaliza EC por coeficiente cadastrado; não escolhe receita agronômica."""
    if not math.isfinite(measured_ms_cm) or measured_ms_cm < 0:
        raise ValueError("EC medida deve ser finita e não negativa")
    if not 0.0 <= reference_c <= 60.0:
        raise ValueError("temperatura de referência inválida")
    if not 0.0 <= coefficient_per_c <= 0.1:
        raise ValueError("coeficiente térmico inválido")
    denominator = 1.0 + coefficient_per_c * (
        compensation.sample_temperature_c - reference_c
    )
    if denominator <= 0:
        raise ValueError("configuração gera divisor térmico inválido")
    return measured_ms_cm / denominator
