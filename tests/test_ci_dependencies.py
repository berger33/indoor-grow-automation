from pathlib import Path
from unittest import TestCase


ROOT = Path(__file__).resolve().parents[1]


class CiDependencyTests(TestCase):
    def test_fastapi_test_client_dependency_is_installed(self) -> None:
        requirements = (
            ROOT / "requirements-dev.txt"
        ).read_text(encoding="utf-8").splitlines()

        self.assertIn("httpx==0.28.1", requirements)
        self.assertFalse(any(line.startswith("httpx2==") for line in requirements))
