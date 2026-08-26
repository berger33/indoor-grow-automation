from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
MQTT_HEADER = ROOT / "firmware/controller/src/GrowMqtt.h"
MAIN = ROOT / "firmware/controller/src/main.cpp"
EXAMPLE = ROOT / "firmware/controller/include/secrets.example.h"


class FirmwareMqttTests(unittest.TestCase):
    def test_firmware_uses_verified_mutual_tls(self) -> None:
        source = MQTT_HEADER.read_text(encoding="utf-8")

        self.assertIn("WiFiClientSecure", source)
        self.assertIn("setCACert", source)
        self.assertIn("setCertificate", source)
        self.assertIn("setPrivateKey", source)
        self.assertNotIn("setInsecure", source)
        self.assertIn("GROW_MQTT_PORT == 8883", source)

    def test_firmware_identifies_only_the_diy_controller(self) -> None:
        source = MQTT_HEADER.read_text(encoding="utf-8")

        self.assertIn('kClientId[] = "grow-01-controller"', source)
        self.assertIn(
            '"grow/v1/grow-01/controller/state/availability"', source
        )
        self.assertIn('"grow/v1/grow-01/controller/state/heartbeat"', source)

    def test_hub_connectivity_drives_local_fail_safe(self) -> None:
        source = MAIN.read_text(encoding="utf-8")

        self.assertIn("hub_connection.loop(now);", source)
        self.assertIn("hub_connection.connected()", source)
        self.assertNotIn(
            "controller.tick(now, leak_confirmed, true, local_stop)", source
        )

    def test_local_secrets_are_empty_examples_and_ignored(self) -> None:
        example = EXAMPLE.read_text(encoding="utf-8")
        gitignore = (ROOT / ".gitignore").read_text(encoding="utf-8")

        self.assertIn('#define GROW_WIFI_SSID ""', example)
        self.assertIn('#define GROW_WIFI_PASSWORD ""', example)
        self.assertIn('#define GROW_MQTT_CA ""', example)
        self.assertIn('#define GROW_MQTT_CLIENT_CERT ""', example)
        self.assertIn('#define GROW_MQTT_CLIENT_KEY ""', example)
        self.assertIn("firmware/controller/include/secrets.h", gitignore)
