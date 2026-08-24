from pathlib import Path
from unittest import TestCase


ROOT = Path(__file__).resolve().parents[1]


class DeploymentTests(TestCase):
    def test_compose_is_arm64_portable_and_secrets_are_files(self) -> None:
        compose = (ROOT / "deploy/docker-compose.yml").read_text(encoding="utf-8")
        self.assertNotIn("platform: linux/amd64", compose)
        self.assertIn("postgres:17.6-bookworm", compose)
        self.assertIn("eclipse-mosquitto:2.0.22", compose)
        self.assertIn("POSTGRES_PASSWORD_FILE", compose)
        self.assertIn("GROWHUB_SESSION_KEY_FILE", compose)
        self.assertIn("127.0.0.1:${GROWHUB_HTTP_PORT", compose)

    def test_restore_requires_confirmation_checksum_and_prebackup(self) -> None:
        restore = (ROOT / "scripts/restore.sh").read_text(encoding="utf-8")
        self.assertIn('"--confirm"', restore)
        self.assertIn("sha256sum --check", restore)
        self.assertIn("pre-restore", restore)
        self.assertNotIn("rm -rf", restore)

    def test_document_marks_power_as_forecast(self) -> None:
        guide = (ROOT / "docs/RASPBERRY_PI_OPERACAO.md").read_text(encoding="utf-8")
        self.assertIn("estimativa de planejamento", guide)
        self.assertIn("não uma medição", guide)
