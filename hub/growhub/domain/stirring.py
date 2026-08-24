"""Intertravamento local do banco de agitadores magnéticos."""

from __future__ import annotations

import math
from dataclasses import dataclass
from datetime import datetime
from enum import StrEnum


CHANNEL_COUNT = 6


class StirrerState(StrEnum):
    OFF = "off"
    SPINUP = "spinup"
    PRE_STIR = "pre_stir"
    READY = "ready"
    ALARM = "alarm"


@dataclass(frozen=True, slots=True)
class TachSample:
    rpm: float
    captured_at: datetime

    def __post_init__(self) -> None:
        if not math.isfinite(self.rpm) or self.rpm < 0:
            raise ValueError("rpm deve ser finito e não negativo")
        if self.captured_at.tzinfo is None:
            raise ValueError("captured_at deve incluir fuso horário")


@dataclass(frozen=True, slots=True)
class StirrerPolicy:
    minimum_rpm: tuple[float, ...]
    spinup_seconds: float = 2.0
    pre_stir_seconds: float = 0.0
    tach_max_age_seconds: float = 2.0

    def __post_init__(self) -> None:
        if len(self.minimum_rpm) != CHANNEL_COUNT:
            raise ValueError("minimum_rpm deve conter seis limites")
        if any(not math.isfinite(value) or value <= 0 for value in self.minimum_rpm):
            raise ValueError("limites de rpm devem ser positivos e finitos")
        for name, value in (
            ("spinup_seconds", self.spinup_seconds),
            ("pre_stir_seconds", self.pre_stir_seconds),
            ("tach_max_age_seconds", self.tach_max_age_seconds),
        ):
            if not math.isfinite(value) or value < 0:
                raise ValueError(f"{name} deve ser finito e não negativo")


class StirrerBank:
    """Só libera uma bomba após confirmar rotação do canal correspondente."""

    def __init__(self, policy: StirrerPolicy) -> None:
        self.policy = policy
        self.state = StirrerState.OFF
        self.output_enabled = False
        self.alarm_reason: str | None = None
        self._started_at: datetime | None = None
        self._pre_stir_at: datetime | None = None
        self._required_channels: frozenset[int] = frozenset()

    @staticmethod
    def _require_aware(now: datetime) -> None:
        if now.tzinfo is None:
            raise ValueError("instante deve incluir fuso horário")

    @staticmethod
    def _validate_channels(channels: frozenset[int]) -> None:
        if not channels:
            raise ValueError("ao menos um canal deve ser solicitado")
        if any(isinstance(index, bool) or not 0 <= index < CHANNEL_COUNT for index in channels):
            raise ValueError("canal deve estar entre 0 e 5")

    def start(self, now: datetime, required_channels: frozenset[int]) -> None:
        self._require_aware(now)
        self._validate_channels(required_channels)
        if self.state is not StirrerState.OFF:
            raise RuntimeError("banco só pode partir no estado OFF")
        self._required_channels = required_channels
        self._started_at = now
        self._pre_stir_at = None
        self.alarm_reason = None
        self.output_enabled = True
        self.state = StirrerState.SPINUP

    def _healthy(self, channel: int, now: datetime, samples: tuple[TachSample | None, ...]) -> bool:
        sample = samples[channel]
        if sample is None or sample.captured_at > now:
            return False
        age = (now - sample.captured_at).total_seconds()
        return age <= self.policy.tach_max_age_seconds and sample.rpm >= self.policy.minimum_rpm[channel]

    def _trip(self, failed: tuple[int, ...]) -> None:
        listed = ",".join(str(index) for index in failed)
        self.alarm_reason = f"stirrer_rotation_failed:{listed}"
        self.output_enabled = False
        self.state = StirrerState.ALARM

    def update(self, now: datetime, samples: tuple[TachSample | None, ...]) -> StirrerState:
        self._require_aware(now)
        if len(samples) != CHANNEL_COUNT:
            raise ValueError("samples deve conter seis canais")
        if self.state in (StirrerState.OFF, StirrerState.ALARM):
            return self.state
        assert self._started_at is not None

        if self.state is StirrerState.SPINUP:
            if (now - self._started_at).total_seconds() < self.policy.spinup_seconds:
                return self.state
            failed = tuple(
                channel
                for channel in sorted(self._required_channels)
                if not self._healthy(channel, now, samples)
            )
            if failed:
                self._trip(failed)
                return self.state
            self.state = StirrerState.PRE_STIR
            self._pre_stir_at = now

        failed = tuple(
            channel
            for channel in sorted(self._required_channels)
            if not self._healthy(channel, now, samples)
        )
        if failed:
            self._trip(failed)
            return self.state
        assert self._pre_stir_at is not None
        if (now - self._pre_stir_at).total_seconds() >= self.policy.pre_stir_seconds:
            self.state = StirrerState.READY
        return self.state

    def can_dose(self, channel: int) -> bool:
        self._validate_channels(frozenset({channel}))
        return self.state is StirrerState.READY and channel in self._required_channels

    def stop(self) -> None:
        self.output_enabled = False
        if self.state is not StirrerState.ALARM:
            self.state = StirrerState.OFF
            self._required_channels = frozenset()

    def reset_alarm(self) -> bool:
        if self.state is not StirrerState.ALARM or self.output_enabled:
            return False
        self.state = StirrerState.OFF
        self.alarm_reason = None
        self._required_channels = frozenset()
        return True
