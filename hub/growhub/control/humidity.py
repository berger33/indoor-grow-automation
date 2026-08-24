"""Umidificação com histerese, anti-ciclo e intertravamentos locais."""

from __future__ import annotations

import math
from dataclasses import dataclass
from datetime import datetime, timedelta
from enum import StrEnum


class HumidifierAction(StrEnum):
    ON = "on"
    OFF = "off"


@dataclass(frozen=True, slots=True)
class HumidityDecision:
    action: HumidifierAction
    reason: str


@dataclass(frozen=True, slots=True)
class HumidityConfig:
    target_percent: float
    deadband_percent: float = 5
    minimum_on_time: timedelta = timedelta(seconds=30)
    minimum_off_time: timedelta = timedelta(seconds=30)
    absolute_high_percent: float = 90

    def __post_init__(self) -> None:
        values = (
            self.target_percent,
            self.deadband_percent,
            self.absolute_high_percent,
        )
        if any(not math.isfinite(value) for value in values):
            raise ValueError("configuração de umidade deve ser finita")
        if not 20 <= self.target_percent <= 85:
            raise ValueError("alvo de umidade deve estar entre 20 e 85%")
        if not 1 <= self.deadband_percent <= 15:
            raise ValueError("histerese de umidade deve estar entre 1 e 15%")
        if self.absolute_high_percent <= self.target_percent + self.deadband_percent:
            raise ValueError("limite absoluto deve superar a banda de controle")
        for duration in (self.minimum_on_time, self.minimum_off_time):
            if not timedelta(0) <= duration <= timedelta(minutes=30):
                raise ValueError("tempo mínimo de ciclo inválido")


class HumidityController:
    def __init__(self, config: HumidityConfig) -> None:
        self._config = config
        self._on = False
        self._changed_at: datetime | None = None
        self._last_now: datetime | None = None

    def evaluate(
        self,
        humidity_percent: float,
        *,
        now: datetime,
        reading_valid: bool,
        water_level_ok: bool,
        leak_detected: bool,
    ) -> HumidityDecision:
        self._validate_monotonic(now)
        if not math.isfinite(humidity_percent) or not 0 <= humidity_percent <= 100:
            raise ValueError("umidade fora do envelope físico")
        if not reading_valid:
            return self._force_off(now, "invalid_or_stale_reading")
        if leak_detected:
            return self._force_off(now, "leak_detected")
        if not water_level_ok:
            return self._force_off(now, "humidifier_level_low")
        if humidity_percent >= self._config.absolute_high_percent:
            return self._force_off(now, "absolute_humidity_high")

        if self._on:
            if humidity_percent >= self._config.target_percent + self._config.deadband_percent:
                if self._elapsed(now) >= self._config.minimum_on_time:
                    return self._force_off(now, "upper_hysteresis")
                return HumidityDecision(HumidifierAction.ON, "minimum_on_time")
            return HumidityDecision(HumidifierAction.ON, "inside_hysteresis")
        if humidity_percent <= self._config.target_percent - self._config.deadband_percent:
            if self._changed_at is None or self._elapsed(now) >= self._config.minimum_off_time:
                self._on = True
                self._changed_at = now
                return HumidityDecision(HumidifierAction.ON, "lower_hysteresis")
            return HumidityDecision(HumidifierAction.OFF, "minimum_off_time")
        return HumidityDecision(HumidifierAction.OFF, "inside_hysteresis")

    def _force_off(self, now: datetime, reason: str) -> HumidityDecision:
        if self._on:
            self._on = False
            self._changed_at = now
        return HumidityDecision(HumidifierAction.OFF, reason)

    def _elapsed(self, now: datetime) -> timedelta:
        return now - self._changed_at  # type: ignore[operator]

    def _validate_monotonic(self, value: datetime) -> None:
        if value.tzinfo is None or value.utcoffset() is None:
            raise ValueError("now deve conter timezone")
        if self._last_now is not None and value < self._last_now:
            raise ValueError("avaliações de umidade devem ser monotônicas")
        self._last_now = value
