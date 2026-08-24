"""Persistência transacional das agendas e overrides EKAZA."""

from __future__ import annotations

from datetime import UTC, datetime, time

from sqlalchemy import delete, select
from sqlalchemy.orm import Session, sessionmaker

from ..domain.remote_lighting import LightState, ManualLightOverride, RemoteLightSchedule
from .models import LightingOverrideRow, LightingScheduleRow


class SqlLightingStore:
    def __init__(self, sessions: sessionmaker[Session]) -> None:
        self._sessions = sessions

    def is_empty(self) -> bool:
        with self._sessions() as session:
            return session.scalar(select(LightingScheduleRow.entity_id).limit(1)) is None

    def load(self) -> tuple[tuple[RemoteLightSchedule, ...], dict[str, ManualLightOverride]]:
        with self._sessions() as session:
            rows = session.scalars(select(LightingScheduleRow).order_by(LightingScheduleRow.entity_id)).all()
            if not rows:
                raise ValueError("nenhuma tomada EKAZA cadastrada no banco")
            schedules = tuple(
                RemoteLightSchedule(
                    entity_id=row.entity_id,
                    on_time=time.fromisoformat(row.on_time),
                    off_time=time.fromisoformat(row.off_time),
                    weekdays=frozenset(row.weekdays),
                    timezone=row.timezone,
                    enabled=row.enabled,
                )
                for row in rows
            )
            overrides = {
                row.entity_id: ManualLightOverride(
                    LightState(row.state),
                    row.expires_at if row.expires_at.tzinfo is not None else row.expires_at.replace(tzinfo=UTC),
                )
                for row in session.scalars(select(LightingOverrideRow)).all()
            }
            if set(overrides) - {item.entity_id for item in schedules}:
                raise ValueError("overrides EKAZA órfãos no banco")
            return schedules, overrides

    def save(
        self,
        schedules: tuple[RemoteLightSchedule, ...],
        overrides: dict[str, ManualLightOverride],
    ) -> None:
        ids = [schedule.entity_id for schedule in schedules]
        if not schedules or len(ids) != len(set(ids)):
            raise ValueError("agendas devem ser não vazias e únicas")
        if unknown := set(overrides) - set(ids):
            raise ValueError(f"override de tomada desconhecida: {sorted(unknown)}")
        now = datetime.now(UTC)
        with self._sessions.begin() as session:
            session.execute(delete(LightingOverrideRow))
            existing = {row.entity_id: row for row in session.scalars(select(LightingScheduleRow)).all()}
            for entity_id in set(existing) - set(ids):
                session.delete(existing[entity_id])
            for schedule in schedules:
                row = existing.get(schedule.entity_id)
                if row is None:
                    row = LightingScheduleRow(
                        entity_id=schedule.entity_id,
                        label=schedule.entity_id.removeprefix("switch.").replace("_", " ").title(),
                        on_time=schedule.on_time.isoformat(timespec="minutes"),
                        off_time=schedule.off_time.isoformat(timespec="minutes"),
                        weekdays=sorted(schedule.weekdays),
                        timezone=schedule.timezone,
                        enabled=schedule.enabled,
                        updated_at=now,
                    )
                    session.add(row)
                else:
                    row.on_time = schedule.on_time.isoformat(timespec="minutes")
                    row.off_time = schedule.off_time.isoformat(timespec="minutes")
                    row.weekdays = sorted(schedule.weekdays)
                    row.timezone = schedule.timezone
                    row.enabled = schedule.enabled
                    row.updated_at = now
            session.flush()
            session.add_all(
                LightingOverrideRow(entity_id=entity_id, state=override.state.value, expires_at=override.expires_at)
                for entity_id, override in overrides.items()
            )
