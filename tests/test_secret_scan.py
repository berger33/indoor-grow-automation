from pathlib import Path
from unittest import TestCase

from scripts.secret_scan import scan_text


class SecretScanTests(TestCase):
    def test_accepts_empty_environment_variable(self) -> None:
        self.assertEqual([], scan_text(Path(".env.example"), "MQTT_PASSWORD=\n"))

    def test_detects_github_token(self) -> None:
        token = "ghp_" + ("A" * 36)
        findings = scan_text(Path("config.txt"), token)
        self.assertEqual("github-token", findings[0].rule)

    def test_detects_private_key_header(self) -> None:
        header = "-----BEGIN " + "PRIVATE KEY-----"
        findings = scan_text(Path("key.pem"), header)
        self.assertEqual("private-key", findings[0].rule)

    def test_detects_assigned_password(self) -> None:
        value = "PASS" + "WORD=" + chr(34) + ("s" * 16) + chr(34)
        findings = scan_text(Path("settings.py"), value)
        self.assertEqual("assigned-secret", findings[0].rule)
