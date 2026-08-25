"""Árvore MQTT v1 por estação, nó, função e direção."""

from __future__ import annotations

import re
from dataclasses import dataclass
from enum import StrEnum

IDENTIFIER = r"[a-z][a-z0-9_-]{0,63}"
TOPIC_PATTERN = re.compile(
    rf"^grow/v(?P<version>[1-9][0-9]*)/(?P<station>{IDENTIFIER})/"
    rf"(?P<node>{IDENTIFIER})/(?P<direction>telemetry|state|alarm|command|ack)/"
    rf"(?P<function>{IDENTIFIER})$"
)


class TopicDirection(StrEnum):
    TELEMETRY = "telemetry"
    STATE = "state"
    ALARM = "alarm"
    COMMAND = "command"
    ACK = "ack"


@dataclass(frozen=True, slots=True)
class MqttTopic:
    station_id: str
    node_id: str
    direction: TopicDirection
    function: str
    version: int = 1

    def __post_init__(self) -> None:
        rendered = self.render()
        if TOPIC_PATTERN.fullmatch(rendered) is None:
            raise ValueError("componentes do tópico MQTT inválidos")

    def render(self) -> str:
        return (
            f"grow/v{self.version}/{self.station_id}/{self.node_id}/"
            f"{self.direction.value}/{self.function}"
        )

    @classmethod
    def parse(cls, topic: str) -> MqttTopic:
        match = TOPIC_PATTERN.fullmatch(topic)
        if match is None:
            raise ValueError("tópico MQTT fora da árvore suportada")
        return cls(
            station_id=match["station"],
            node_id=match["node"],
            direction=TopicDirection(match["direction"]),
            function=match["function"],
            version=int(match["version"]),
        )


def telemetry_topic(station_id: str, node_id: str, sensor_id: str) -> str:
    return MqttTopic(station_id, node_id, TopicDirection.TELEMETRY, sensor_id).render()


def command_topic(station_id: str, node_id: str, function: str) -> str:
    return MqttTopic(station_id, node_id, TopicDirection.COMMAND, function).render()


def acknowledgement_topic(station_id: str, node_id: str, function: str) -> str:
    return MqttTopic(station_id, node_id, TopicDirection.ACK, function).render()
