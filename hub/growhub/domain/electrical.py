"""Modelo seguro de cargas; dimensionamento físico continua sendo profissional."""

from __future__ import annotations

import math
from dataclasses import dataclass
from enum import StrEnum

from .sensors import IDENTIFIER


class ControlInterface(StrEnum):
    SWITCH = "switch"
    UNKNOWN = "unknown"
    ZERO_TO_TEN_V = "0-10v"
    PWM = "pwm"
    DIGITAL = "digital"


class CurrentBasis(StrEnum):
    NAMEPLATE = "nameplate"
    MEASURED = "measured"
    ESTIMATED = "estimated"


@dataclass(frozen=True, slots=True)
class CurrentEstimate:
    amperes: float
    basis: CurrentBasis
    power_factor: float | None = None


@dataclass(frozen=True, slots=True)
class ElectricalLoad:
    load_id: str
    name: str
    rated_power_w: float
    supply_voltage_v: int
    control_interface: ControlInterface = ControlInterface.SWITCH
    nameplate_current_a: float | None = None
    measured_current_a: float | None = None
    power_factor: float | None = None
    inrush_current_a: float | None = None

    def __post_init__(self) -> None:
        if not IDENTIFIER.fullmatch(self.load_id):
            raise ValueError(f"load_id inválido: {self.load_id!r}")
        if not self.name.strip():
            raise ValueError("name não pode ser vazio")
        if not math.isfinite(self.rated_power_w) or self.rated_power_w <= 0:
            raise ValueError("rated_power_w deve ser positivo e finito")
        if self.supply_voltage_v not in (127, 220):
            raise ValueError("supply_voltage_v deve ser 127 ou 220")
        for field_name, value in (
            ("nameplate_current_a", self.nameplate_current_a),
            ("measured_current_a", self.measured_current_a),
            ("inrush_current_a", self.inrush_current_a),
        ):
            if value is not None and (not math.isfinite(value) or value <= 0):
                raise ValueError(f"{field_name} deve ser positivo e finito")
        if self.power_factor is not None and not 0 < self.power_factor <= 1:
            raise ValueError("power_factor deve estar entre 0 e 1")

    def current(self, *, assumed_power_factor: float | None = None) -> CurrentEstimate | None:
        """Prioriza medição e plaqueta; hipótese precisa ser fornecida pelo chamador."""
        if self.measured_current_a is not None:
            return CurrentEstimate(self.measured_current_a, CurrentBasis.MEASURED)
        if self.nameplate_current_a is not None:
            return CurrentEstimate(self.nameplate_current_a, CurrentBasis.NAMEPLATE)
        factor = self.power_factor if self.power_factor is not None else assumed_power_factor
        if factor is None:
            return None
        if not 0 < factor <= 1:
            raise ValueError("assumed_power_factor deve estar entre 0 e 1")
        amperes = self.rated_power_w / (self.supply_voltage_v * factor)
        return CurrentEstimate(amperes, CurrentBasis.ESTIMATED, factor)


@dataclass(frozen=True, slots=True)
class CircuitProfile:
    supply_voltage_v: int
    frequency_hz: int
    loads: tuple[ElectricalLoad, ...]

    def __post_init__(self) -> None:
        if self.supply_voltage_v not in (127, 220):
            raise ValueError("supply_voltage_v deve ser 127 ou 220")
        if self.frequency_hz not in (50, 60):
            raise ValueError("frequency_hz deve ser 50 ou 60")
        identifiers = [load.load_id for load in self.loads]
        if len(identifiers) != len(set(identifiers)):
            raise ValueError("load_id duplicado")
        incompatible = [
            load.load_id
            for load in self.loads
            if load.supply_voltage_v != self.supply_voltage_v
        ]
        if incompatible:
            raise ValueError(f"cargas com tensão incompatível: {', '.join(incompatible)}")

    @property
    def rated_power_w(self) -> float:
        return sum(load.rated_power_w for load in self.loads)

    def current_estimates(
        self,
        *,
        assumed_power_factor: float | None = None,
    ) -> tuple[CurrentEstimate | None, ...]:
        return tuple(
            load.current(assumed_power_factor=assumed_power_factor)
            for load in self.loads
        )

    def total_current_a(self, *, assumed_power_factor: float | None = None) -> float | None:
        estimates = self.current_estimates(assumed_power_factor=assumed_power_factor)
        if any(estimate is None for estimate in estimates):
            return None
        return sum(estimate.amperes for estimate in estimates if estimate is not None)

    def loads_missing_current(self) -> tuple[str, ...]:
        return tuple(load.load_id for load in self.loads if load.current() is None)
