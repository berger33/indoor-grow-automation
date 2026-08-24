"""WebSocket com sequência, retomada e buffer offline limitado."""

from __future__ import annotations

import asyncio
from collections import deque
from dataclasses import dataclass
from datetime import datetime


@dataclass(frozen=True, slots=True)
class RealtimeEvent:
    event_id: int
    kind: str
    station_id: str
    occurred_at: datetime
    payload: dict[str, object]

    def as_dict(self) -> dict[str, object]:
        return {
            "eventId": self.event_id,
            "kind": self.kind,
            "stationId": self.station_id,
            "occurredAt": self.occurred_at.isoformat(),
            "payload": self.payload,
        }


class RealtimeBuffer:
    def __init__(self, maximum_events: int = 1000) -> None:
        if not 10 <= maximum_events <= 100_000:
            raise ValueError("tamanho do buffer em tempo real inválido")
        self._events: deque[RealtimeEvent] = deque(maxlen=maximum_events)
        self._subscribers: set[asyncio.Queue[RealtimeEvent]] = set()
        self._next_id = 1

    async def publish(self, kind: str, station_id: str, occurred_at: datetime, payload: dict[str, object]) -> RealtimeEvent:
        if occurred_at.tzinfo is None or occurred_at.utcoffset() is None:
            raise ValueError("evento em tempo real exige horário com timezone")
        if not kind.strip() or not station_id.strip():
            raise ValueError("evento em tempo real inválido")
        event = RealtimeEvent(self._next_id, kind, station_id, occurred_at, payload)
        self._next_id += 1
        self._events.append(event)
        for subscriber in tuple(self._subscribers):
            if subscriber.full():
                subscriber.get_nowait()
            subscriber.put_nowait(event)
        return event

    def after(self, event_id: int) -> tuple[RealtimeEvent, ...]:
        return tuple(event for event in self._events if event.event_id > event_id)

    def subscribe(self) -> asyncio.Queue[RealtimeEvent]:
        queue: asyncio.Queue[RealtimeEvent] = asyncio.Queue(maxsize=100)
        self._subscribers.add(queue)
        return queue

    def unsubscribe(self, queue: asyncio.Queue[RealtimeEvent]) -> None:
        self._subscribers.discard(queue)
