"""Correção de pH por degraus, histerese e tempo de estabilização."""

from __future__ import annotations

import math
from dataclasses import dataclass
from datetime import datetime, timedelta
from enum import StrEnum

from .dosing import PHChannel


class PHAction(StrEnum):
    HOLD = "hold"
    DOSE_UP = "dose_up"
    DOSE_DOWN = "dose_down"


@dataclass(frozen=True, slots=True)
class PHControlConfig:
    target: float
    dose_ml: float
    deadband: float = 0.1
    evaluation_interval: timedelta = timedelta(minutes=1)
    settling_time: timedelta = timedelta(minutes=5)

    def __post_init__(self) -> None:
        if not math.isfinite(self.target) or not 5.8 <= self.target <= 6.5:
            raise ValueError("target de pH deve estar entre 5,8 e 6,5")
        if not math.isfinite(self.dose_ml) or self.dose_ml <= 0:
            raise ValueError("dose_ml deve ser finita e positiva")
        if not math.isfinite(self.deadband) or not 0.05 <= self.deadband <= 0.5:
            raise ValueError("deadband deve estar entre 0,05 e 0,5")
        if not timedelta(seconds=10) <= self.evaluation_interval <= timedelta(hours=1):
            raise ValueError("intervalo de avaliação inválido")
        if not timedelta(seconds=30) <= self.settling_time <= timedelta(hours=2):
            raise ValueError("tempo de estabilização inválido")


@dataclass(frozen=True, slots=True)
class PHDecision:
    action: PHAction
    reason: str
    channel: PHChannel | None = None
    volume_ml: float = 0


class PHStepController:
    def __init__(self, config: PHControlConfig) -> None:
        self._config = config
        self._last_evaluation: datetime | None = None
        self._settling_until: datetime | None = None

    def evaluate(
        self,
        ph: float,
        *,
        now: datetime,
        reading_fresh: bool,
        mixing: bool,
        level_ok: bool,
    ) -> PHDecision:
        self._validate_time(now)
        if not math.isfinite(ph) or not 0 <= ph <= 14:
            raise ValueError("pH deve estar no envelope físico")
        if self._last_evaluation is not None and now < self._last_evaluation:
            raise ValueError("avaliações de pH devem ser monotônicas")
        if self._settling_until is not None and now < self._settling_until:
            return PHDecision(PHAction.HOLD, "settling")
        if (
            self._last_evaluation is not None
            and now - self._last_evaluation < self._config.evaluation_interval
        ):
            return PHDecision(PHAction.HOLD, "evaluation_interval")

        self._last_evaluation = now
        if not reading_fresh:
            return PHDecision(PHAction.HOLD, "invalid_or_stale_reading")
        if not mixing:
            return PHDecision(PHAction.HOLD, "mixing_required")
        if not level_ok:
            return PHDecision(PHAction.HOLD, "insufficient_level")

        if ph >= self._config.target + self._config.deadband:
            return self._dose(PHChannel.DOWN, PHAction.DOSE_DOWN, now)
        if ph <= self._config.target - self._config.deadband:
            return self._dose(PHChannel.UP, PHAction.DOSE_UP, now)
        return PHDecision(PHAction.HOLD, "inside_deadband")

    def _dose(
        self,
        channel: PHChannel,
        action: PHAction,
        now: datetime,
    ) -> PHDecision:
        self._settling_until = now + self._config.settling_time
        return PHDecision(action, "correction_required", channel, self._config.dose_ml)

    @staticmethod
    def _validate_time(value: datetime) -> None:
        if value.tzinfo is None or value.utcoffset() is None:
            raise ValueError("now deve conter timezone")
