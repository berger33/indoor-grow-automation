"""Controle liga/desliga do exaustor atual por temperatura, UR e VPD."""

from __future__ import annotations

import math
from dataclasses import dataclass
from datetime import datetime, timedelta
from enum import StrEnum


class ExhaustAction(StrEnum):
    ON = "on"
    OFF = "off"


@dataclass(frozen=True, slots=True)
class ExhaustDecision:
    action: ExhaustAction
    reason: str
    degraded: bool = False


@dataclass(frozen=True, slots=True)
class ExhaustConfig:
    target_temperature_c: float
    minimum_vpd_kpa: float = 0.6
    on_delta_c: float = 2
    off_delta_c: float = 1
    absolute_high_temperature_c: float = 35
    absolute_high_humidity_percent: float = 85
    minimum_cycle_time: timedelta = timedelta(seconds=30)

    def __post_init__(self) -> None:
        values = (
            self.target_temperature_c,
            self.minimum_vpd_kpa,
            self.on_delta_c,
            self.off_delta_c,
            self.absolute_high_temperature_c,
            self.absolute_high_humidity_percent,
        )
        if any(not math.isfinite(value) for value in values):
            raise ValueError("configuração do exaustor deve ser finita")
        if not 15 <= self.target_temperature_c <= 30:
            raise ValueError("temperatura alvo deve estar entre 15 e 30 °C")
        if not 0 <= self.minimum_vpd_kpa <= 3:
            raise ValueError("VPD mínimo inválido")
        if not 0.5 <= self.on_delta_c <= 10 or not 0.5 <= self.off_delta_c <= 10:
            raise ValueError("deltas de temperatura inválidos")
        if self.absolute_high_temperature_c <= self.target_temperature_c + self.on_delta_c:
            raise ValueError("limite absoluto de temperatura inválido")
        if not 60 <= self.absolute_high_humidity_percent <= 100:
            raise ValueError("limite absoluto de umidade inválido")
        if not timedelta(0) <= self.minimum_cycle_time <= timedelta(minutes=30):
            raise ValueError("tempo mínimo de ciclo inválido")


class OnOffExhaustController:
    def __init__(self, config: ExhaustConfig) -> None:
        self._config = config
        self._on = False
        self._changed_at: datetime | None = None
        self._last_now: datetime | None = None

    def evaluate(
        self,
        temperatures_c: tuple[float | None, float | None],
        *,
        humidity_percent: float,
        vpd_kpa: float,
        now: datetime,
    ) -> ExhaustDecision:
        self._validate_monotonic(now)
        valid_temperatures = tuple(
            value
            for value in temperatures_c
            if value is not None and math.isfinite(value) and -20 <= value <= 80
        )
        if not math.isfinite(humidity_percent) or not 0 <= humidity_percent <= 100:
            raise ValueError("umidade fora do envelope físico")
        if not math.isfinite(vpd_kpa) or not -5 <= vpd_kpa <= 10:
            raise ValueError("VPD fora do envelope físico")

        if not valid_temperatures:
            return self._switch(True, now, "no_valid_temperature", degraded=True, force=True)
        if max(valid_temperatures) >= self._config.absolute_high_temperature_c:
            return self._switch(True, now, "absolute_temperature_high", force=True)
        if humidity_percent >= self._config.absolute_high_humidity_percent:
            return self._switch(True, now, "absolute_humidity_high", force=True)
        if vpd_kpa <= self._config.minimum_vpd_kpa:
            return self._switch(True, now, "vpd_too_low")

        degraded = len(valid_temperatures) == 1
        if degraded:
            demand_on = valid_temperatures[0] >= self._config.target_temperature_c
            if demand_on:
                return self._switch(True, now, "single_sensor_hot", degraded=True)
            return ExhaustDecision(
                ExhaustAction.ON if self._on else ExhaustAction.OFF,
                "single_sensor_hold",
                True,
            )

        if all(
            value >= self._config.target_temperature_c + self._config.on_delta_c
            for value in valid_temperatures
        ):
            return self._switch(True, now, "both_sensors_hot")
        if all(
            value <= self._config.target_temperature_c - self._config.off_delta_c
            for value in valid_temperatures
        ):
            return self._switch(False, now, "both_sensors_cool")
        return ExhaustDecision(
            ExhaustAction.ON if self._on else ExhaustAction.OFF,
            "inside_hysteresis",
        )

    def _switch(
        self,
        on: bool,
        now: datetime,
        reason: str,
        degraded: bool = False,
        force: bool = False,
    ) -> ExhaustDecision:
        if self._on is on:
            return ExhaustDecision(ExhaustAction.ON if on else ExhaustAction.OFF, reason, degraded)
        if (
            not force
            and self._changed_at is not None
            and now - self._changed_at < self._config.minimum_cycle_time
        ):
            return ExhaustDecision(
                ExhaustAction.ON if self._on else ExhaustAction.OFF,
                "minimum_cycle_time",
                degraded,
            )
        self._on = on
        self._changed_at = now
        return ExhaustDecision(ExhaustAction.ON if on else ExhaustAction.OFF, reason, degraded)

    def _validate_monotonic(self, value: datetime) -> None:
        if value.tzinfo is None or value.utcoffset() is None:
            raise ValueError("now deve conter timezone")
        if self._last_now is not None and value < self._last_now:
            raise ValueError("avaliações do exaustor devem ser monotônicas")
        self._last_now = value
