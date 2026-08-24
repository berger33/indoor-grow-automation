"""Máquina de estados segura para preparo sequencial de nutrientes."""

from __future__ import annotations

import math
from dataclasses import dataclass
from datetime import datetime, timedelta
from enum import StrEnum


class NutrientChannel(StrEnum):
    CALMAG = "calmag"
    MICRO = "micro"
    BLOOM = "bloom"
    GROW = "grow"


CHANNEL_ORDER = (
    NutrientChannel.CALMAG,
    NutrientChannel.MICRO,
    NutrientChannel.BLOOM,
    NutrientChannel.GROW,
)


@dataclass(frozen=True, slots=True)
class NutrientRecipe:
    batch_volume_l: float
    target_ec_ms_cm: float
    calmag_ml_l: float
    micro_ml_l: float
    bloom_ml_l: float
    grow_ml_l: float

    def __post_init__(self) -> None:
        values = (
            self.batch_volume_l,
            self.target_ec_ms_cm,
            self.calmag_ml_l,
            self.micro_ml_l,
            self.bloom_ml_l,
            self.grow_ml_l,
        )
        if any(not math.isfinite(value) for value in values):
            raise ValueError("receita deve conter apenas valores finitos")
        if not 5 <= self.batch_volume_l <= 60:
            raise ValueError("volume do lote deve estar entre 5 e 60 L")
        if not 0.5 <= self.target_ec_ms_cm <= 2.5:
            raise ValueError("EC alvo deve estar entre 0,5 e 2,5 mS/cm")
        if any(not 0 <= value <= 10 for value in values[2:]):
            raise ValueError("cada nutriente deve estar entre 0 e 10 mL/L")
        if not any(value > 0 for value in values[2:]):
            raise ValueError("receita precisa de ao menos um nutriente")

    def doses(self) -> tuple[tuple[NutrientChannel, float], ...]:
        ratios = {
            NutrientChannel.CALMAG: self.calmag_ml_l,
            NutrientChannel.MICRO: self.micro_ml_l,
            NutrientChannel.BLOOM: self.bloom_ml_l,
            NutrientChannel.GROW: self.grow_ml_l,
        }
        return tuple(
            (channel, ratios[channel] * self.batch_volume_l)
            for channel in CHANNEL_ORDER
            if ratios[channel] > 0
        )


class BatchState(StrEnum):
    IDLE = "idle"
    FILLING = "filling"
    PREMIX = "premix"
    WAITING_AFTER_DOSE = "waiting_after_dose"
    READY_FOR_DILUTION = "ready_for_dilution"
    ABORTED = "aborted"


class BatchAction(StrEnum):
    HOLD = "hold"
    FILL_WATER = "fill_water"
    START_MIXING_AND_STIRRERS = "start_mixing_and_stirrers"
    DOSE_NUTRIENT = "dose_nutrient"
    STOP_STIRRERS = "stop_stirrers"
    READY_FOR_DILUTION = "ready_for_dilution"
    ABORT_ALL = "abort_all"


@dataclass(frozen=True, slots=True)
class BatchDecision:
    state: BatchState
    action: BatchAction
    reason: str
    channel: NutrientChannel | None = None
    volume_ml: float = 0


class NutrientBatchController:
    def __init__(
        self,
        *,
        premix_time: timedelta = timedelta(seconds=5),
        interval_between_nutrients: timedelta = timedelta(seconds=60),
    ) -> None:
        if not timedelta(seconds=1) <= premix_time <= timedelta(minutes=10):
            raise ValueError("premix_time inválido")
        if not timedelta(seconds=10) <= interval_between_nutrients <= timedelta(hours=1):
            raise ValueError("intervalo entre nutrientes inválido")
        self._premix_time = premix_time
        self._interval = interval_between_nutrients
        self._recipe: NutrientRecipe | None = None
        self._state = BatchState.IDLE
        self._state_started_at: datetime | None = None
        self._dose_index = 0
        self._last_now: datetime | None = None

    @property
    def state(self) -> BatchState:
        return self._state

    def start(
        self,
        recipe: NutrientRecipe,
        *,
        now: datetime,
        tank_capacity_l: float,
        stock_ml: dict[NutrientChannel, float],
    ) -> None:
        self._validate_time(now)
        if self._state is not BatchState.IDLE:
            raise PermissionError("já existe lote em execução")
        if not math.isfinite(tank_capacity_l) or recipe.batch_volume_l > tank_capacity_l:
            raise ValueError("volume do lote excede a capacidade do tanque")
        required = dict(recipe.doses())
        missing = [
            channel.value
            for channel, volume in required.items()
            if not math.isfinite(stock_ml.get(channel, -1)) or stock_ml.get(channel, -1) < volume
        ]
        if missing:
            raise ValueError(f"estoque insuficiente: {', '.join(missing)}")
        self._recipe = recipe
        self._state = BatchState.FILLING
        self._state_started_at = now
        self._last_now = now

    def advance(
        self,
        *,
        now: datetime,
        current_volume_l: float,
        safe_to_operate: bool = True,
    ) -> BatchDecision:
        self._validate_monotonic(now)
        if not math.isfinite(current_volume_l) or current_volume_l < 0:
            raise ValueError("volume atual inválido")
        if self._recipe is None or self._state is BatchState.IDLE:
            raise PermissionError("nenhum lote em execução")
        if self._state is BatchState.ABORTED:
            return BatchDecision(self._state, BatchAction.HOLD, "aborted")
        if not safe_to_operate:
            self._state = BatchState.ABORTED
            return BatchDecision(self._state, BatchAction.ABORT_ALL, "safety_interlock")

        if self._state is BatchState.FILLING:
            if current_volume_l < self._recipe.batch_volume_l:
                return BatchDecision(self._state, BatchAction.FILL_WATER, "below_batch_volume")
            self._state = BatchState.PREMIX
            self._state_started_at = now
            return BatchDecision(
                self._state,
                BatchAction.START_MIXING_AND_STIRRERS,
                "batch_volume_reached",
            )
        if self._state is BatchState.PREMIX:
            if now - self._state_started_at < self._premix_time:  # type: ignore[operator]
                return BatchDecision(self._state, BatchAction.HOLD, "premixing")
            return self._emit_dose(now)
        if self._state is BatchState.WAITING_AFTER_DOSE:
            if now - self._state_started_at < self._interval:  # type: ignore[operator]
                return BatchDecision(self._state, BatchAction.HOLD, "mixing_between_doses")
            if self._dose_index < len(self._recipe.doses()):
                return self._emit_dose(now)
            self._state = BatchState.READY_FOR_DILUTION
            return BatchDecision(
                self._state,
                BatchAction.STOP_STIRRERS,
                "recipe_complete",
            )
        return BatchDecision(
            self._state,
            BatchAction.READY_FOR_DILUTION,
            "recipe_complete",
        )

    def _emit_dose(self, now: datetime) -> BatchDecision:
        doses = self._recipe.doses()  # type: ignore[union-attr]
        channel, volume_ml = doses[self._dose_index]
        self._dose_index += 1
        self._state = BatchState.WAITING_AFTER_DOSE
        self._state_started_at = now
        return BatchDecision(
            self._state,
            BatchAction.DOSE_NUTRIENT,
            "dose_in_order",
            channel,
            volume_ml,
        )

    def _validate_monotonic(self, value: datetime) -> None:
        self._validate_time(value)
        if self._last_now is not None and value < self._last_now:
            raise ValueError("tempo do lote deve ser monotônico")
        self._last_now = value

    @staticmethod
    def _validate_time(value: datetime) -> None:
        if value.tzinfo is None or value.utcoffset() is None:
            raise ValueError("timestamp deve conter timezone")
