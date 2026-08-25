from unittest import TestCase

from hub.growhub.contracts.topics import (
    MqttTopic,
    TopicDirection,
    acknowledgement_topic,
    command_topic,
    telemetry_topic,
)


class MqttTopicTests(TestCase):
    def test_renders_and_parses_versioned_station_tree(self) -> None:
        topic = telemetry_topic("grow-01", "climate", "air_temperature")
        self.assertEqual("grow/v1/grow-01/climate/telemetry/air_temperature", topic)
        parsed = MqttTopic.parse(topic)
        self.assertEqual(TopicDirection.TELEMETRY, parsed.direction)
        self.assertEqual("grow-01", parsed.station_id)
        self.assertEqual("climate", parsed.node_id)

    def test_command_and_ack_share_function_but_not_direction(self) -> None:
        self.assertEqual(
            "grow/v1/grow-01/fertigation/command/mixer",
            command_topic("grow-01", "fertigation", "mixer"),
        )
        self.assertEqual(
            "grow/v1/grow-01/fertigation/ack/mixer",
            acknowledgement_topic("grow-01", "fertigation", "mixer"),
        )

    def test_rejects_wildcards_unknown_direction_and_unversioned_topic(self) -> None:
        for topic in (
            "grow/grow-01/climate/telemetry/co2",
            "grow/v1/+/climate/telemetry/co2",
            "grow/v1/grow-01/climate/injection/co2",
        ):
            with self.assertRaises(ValueError):
                MqttTopic.parse(topic)
