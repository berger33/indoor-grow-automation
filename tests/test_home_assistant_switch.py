from unittest import TestCase

from hub.growhub.integrations.home_assistant import HomeAssistantSwitchClient


class FakeTransport:
    def __init__(self) -> None:
        self.calls = []
        self.state = "off"

    def request(self, method, url, headers, payload=None):
        self.calls.append((method, url, headers, payload))
        if method == "POST":
            self.state = "on" if url.endswith("turn_on") else "off"
            return []
        return {"entity_id": "switch.grow_light_1", "state": self.state}


class HomeAssistantSwitchClientTests(TestCase):
    def setUp(self) -> None:
        self.transport = FakeTransport()
        self.client = HomeAssistantSwitchClient(
            base_url="http://homeassistant.local:8123",
            access_token="runtime-token",
            transport=self.transport,
        )

    def test_commands_switch_then_confirms_observed_state(self) -> None:
        observation = self.client.set_switch("switch.grow_light_1", on=True)
        self.assertTrue(observation.is_on)
        self.assertEqual("POST", self.transport.calls[0][0])
        self.assertTrue(self.transport.calls[0][1].endswith("/switch/turn_on"))
        self.assertEqual("GET", self.transport.calls[1][0])

    def test_sends_token_only_in_authorization_header(self) -> None:
        self.client.read_switch("switch.grow_light_1")
        _, url, headers, _ = self.transport.calls[0]
        self.assertNotIn("runtime-token", url)
        self.assertEqual("Bearer runtime-token", headers["Authorization"])

    def test_rejects_unknown_entity_state_and_configuration(self) -> None:
        with self.assertRaisesRegex(ValueError, "switch"):
            self.client.read_switch("light.grow")
        with self.assertRaisesRegex(ValueError, "base_url"):
            HomeAssistantSwitchClient(base_url="homeassistant.local", access_token="x")
        with self.assertRaisesRegex(ValueError, "runtime"):
            HomeAssistantSwitchClient(base_url="http://localhost:8123", access_token="")

    def test_rejects_non_boolean_command(self) -> None:
        with self.assertRaises(TypeError):
            self.client.set_switch("switch.grow_light_1", on=1)  # type: ignore[arg-type]
