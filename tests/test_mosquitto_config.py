from pathlib import Path
from unittest import TestCase


ROOT = Path(__file__).resolve().parents[1]


class MosquittoConfigTests(TestCase):
    def test_listener_requires_mutual_tls_and_acl(self) -> None:
        config = (ROOT / "deploy/mosquitto/mosquitto.conf").read_text(encoding="utf-8")
        required = {
            "listener 8883 0.0.0.0",
            "allow_anonymous false",
            "require_certificate true",
            "use_identity_as_username true",
            "tls_version tlsv1.2",
            "acl_file /mosquitto/config/growhub.acl",
        }
        self.assertTrue(required.issubset(set(config.splitlines())))
        self.assertNotIn("listener 1883", config)

    def test_single_controller_can_only_read_own_commands(self) -> None:
        acl = (ROOT / "deploy/mosquitto/growhub.acl").read_text(encoding="utf-8")
        self.assertIn("user grow-01-controller", acl)
        self.assertIn("topic read grow/v1/grow-01/controller/command/#", acl)
        self.assertIn("topic write grow/v1/grow-01/controller/telemetry/#", acl)
        self.assertNotIn("grow-01-fertigation", acl)
        self.assertNotIn("grow-01-climate", acl)
        self.assertNotIn("grow-01-safety", acl)
        self.assertNotIn("topic readwrite grow/v1/grow-01/controller/#", acl)
