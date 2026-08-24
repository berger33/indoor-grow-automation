"""Agenda diária de até cinco fertirrigações sem eventos sobrepostos."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date, datetime, time, timedelta
from enum import StrEnum
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError


@dataclass(frozen=True, slots=True)
class IrrigationEvent:
    event_id: str
    start_time: time
    duration: timedelta

    def __post_init__(self) -> None:
        if not self.event_id or self.event_id.isspace():
            raise ValueError("event_id é obrigatório")
        if not timedelta(seconds=30) <= self.duration <= timedelta(minutes=10):
            raise ValueError("duração deve estar entre 30 s e 10 min")


@dataclass(frozen=True, slots=True)
class IrrigationSchedule:
    events: tuple[IrrigationEvent, ...]
    timezone: str = "America/Sao_Paulo"

    def __post_init__(self) -> None:
        if len(self.events) > 5:
            raise ValueError("agenda aceita no máximo cinco eventos")
        ids = [event.event_id for event in self.events]
        if len(ids) != len(set(ids)):
            raise ValueError("event_id duplicado")
        try:
            ZoneInfo(self.timezone)
        except ZoneInfoNotFoundError as exc:
            raise ValueError("timezone IANA inválido") from exc
        self._reject_overlaps()

    def _reject_overlaps(self) -> None:
        intervals = []
        for event in self.events:
            start = (
                event.start_time.hour * 3600
                + event.start_time.minute * 60
                + event.start_time.second
            )
            end = start + event.duration.total_seconds()
            intervals.append((event.event_id, start, end))
        for index, (left_id, left_start, left_end) in enumerate(intervals):
            for right_id, right_start, right_end in intervals[index + 1 :]:
                if any(
                    max(left_start, right_start + shift)
                    < min(left_end, right_end + shift)
                    for shift in (-86_400, 0, 86_400)
                ):
                    raise ValueError(f"eventos sobrepostos: {left_id}, {right_id}")


class IrrigationAction(StrEnum):
    ON = "on"
    OFF = "off"


@dataclass(frozen=True, slots=True)
class IrrigationDecision:
    action: IrrigationAction
    reason: str
    event_id: str | None = None
    ends_at: datetime | None = None


class IrrigationScheduler:
    def __init__(self, schedule: IrrigationSchedule) -> None:
        self._schedule = schedule
        self._zone = ZoneInfo(schedule.timezone)
        self._active_key: tuple[date, str] | None = None
        self._active_until: datetime | None = None
        self._completed: set[tuple[date, str]] = set()
        self._last_now: datetime | None = None

    def evaluate(
        self,
        *,
        now: datetime,
        alarm_active: bool,
        level_ok: bool,
        level_reading_fresh: bool,
    ) -> IrrigationDecision:
        self._validate_time(now)
        if self._last_now is not None and now < self._last_now:
            raise ValueError("avaliações de irrigação devem ser monotônicas")
        self._last_now = now
        if alarm_active or not level_ok or not level_reading_fresh:
            self._active_key = None
            self._active_until = None
            reason = (
                "alarm_active"
                if alarm_active
                else "insufficient_level"
                if not level_ok
                else "stale_level"
            )
            return IrrigationDecision(IrrigationAction.OFF, reason)
        if self._active_key is not None and self._active_until is not None:
            if now < self._active_until:
                return IrrigationDecision(
                    IrrigationAction.ON,
                    "event_active",
                    self._active_key[1],
                    self._active_until,
                )
            completed = self._active_key
            self._completed.add(completed)
            self._active_key = None
            self._active_until = None
            return IrrigationDecision(
                IrrigationAction.OFF,
                "event_complete",
                completed[1],
            )

        local = now.astimezone(self._zone)
        for day in (local.date(), local.date() - timedelta(days=1)):
            for event in self._schedule.events:
                key = (day, event.event_id)
                start = datetime.combine(day, event.start_time, tzinfo=self._zone)
                end = start + event.duration
                if key not in self._completed and start <= local < end:
                    self._active_key = key
                    self._active_until = end.astimezone(now.tzinfo)
                    return IrrigationDecision(
                        IrrigationAction.ON,
                        "event_started",
                        event.event_id,
                        self._active_until,
                    )
        self._discard_old(local.date())
        return IrrigationDecision(IrrigationAction.OFF, "no_event_due")

    def _discard_old(self, today: date) -> None:
        oldest = today - timedelta(days=1)
        self._completed = {key for key in self._completed if key[0] >= oldest}

    @staticmethod
    def _validate_time(value: datetime) -> None:
        if value.tzinfo is None or value.utcoffset() is None:
            raise ValueError("now deve conter timezone")
