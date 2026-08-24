"""Confirma corrente/contato do exaustor e retém falhas de acionamento."""

from __future__ import annotations

from datetime import datetime, timedelta
from enum import StrEnum


class FanFeedbackState(StrEnum):
    OFF_CONFIRMED = "off_confirmed"
    ON_CONFIRMED = "on_confirmed"
    TRANSITIONING = "transitioning"
    FAULT_NO_FEEDBACK = "fault_no_feedback"
    FAULT_STUCK_ON = "fault_stuck_on"


class FanFeedbackMonitor:
    def __init__(
        self,
        *,
        transition_grace: timedelta = timedelta(seconds=5),
        mismatch_confirmations: int = 2,
    ) -> None:
        if not timedelta(milliseconds=100) <= transition_grace <= timedelta(minutes=1):
            raise ValueError("janela de transição inválida")
        if isinstance(mismatch_confirmations, bool) or not 1 <= mismatch_confirmations <= 10:
            raise ValueError("confirmações devem estar entre 1 e 10")
        self._transition_grace = transition_grace
        self._required = mismatch_confirmations
        self._commanded_on = False
        self._commanded_at: datetime | None = None
        self._mismatches = 0
        self._fault: FanFeedbackState | None = None
        self._last_now: datetime | None = None

    def command(self, on: bool, *, now: datetime) -> None:
        self._validate_monotonic(now)
        if not isinstance(on, bool):
            raise TypeError("comando do exaustor deve ser bool")
        if self._fault is not None and on:
            raise PermissionError("falha de feedback exige rearme")
        if self._commanded_on is not on or self._commanded_at is None:
            self._commanded_on = on
            self._commanded_at = now
            self._mismatches = 0

    def observe(self, current_present: bool, *, now: datetime) -> FanFeedbackState:
        self._validate_monotonic(now)
        if not isinstance(current_present, bool):
            raise TypeError("feedback deve ser bool")
        if self._fault is not None:
            return self._fault
        if self._commanded_at is None:
            if current_present:
                return self._register_mismatch(FanFeedbackState.FAULT_STUCK_ON)
            return FanFeedbackState.OFF_CONFIRMED
        if now - self._commanded_at < self._transition_grace:
            return FanFeedbackState.TRANSITIONING
        if current_present is self._commanded_on:
            self._mismatches = 0
            return (
                FanFeedbackState.ON_CONFIRMED
                if current_present
                else FanFeedbackState.OFF_CONFIRMED
            )
        fault = (
            FanFeedbackState.FAULT_NO_FEEDBACK
            if self._commanded_on
            else FanFeedbackState.FAULT_STUCK_ON
        )
        return self._register_mismatch(fault)

    def reset(self, *, current_present: bool) -> None:
        if self._commanded_on or current_present:
            raise PermissionError("desligue e confirme ausência de corrente antes do rearme")
        self._fault = None
        self._mismatches = 0

    def _register_mismatch(self, fault: FanFeedbackState) -> FanFeedbackState:
        self._mismatches += 1
        if self._mismatches >= self._required:
            self._fault = fault
            self._commanded_on = False
        return self._fault or FanFeedbackState.TRANSITIONING

    def _validate_monotonic(self, value: datetime) -> None:
        if value.tzinfo is None or value.utcoffset() is None:
            raise ValueError("timestamp deve conter timezone")
        if self._last_now is not None and value < self._last_now:
            raise ValueError("eventos de feedback devem ser monotônicos")
        self._last_now = value
