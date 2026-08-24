import json
from pathlib import Path
from unittest import TestCase

from scripts.generate_sbom import document


ROOT = Path(__file__).resolve().parents[1]


class ReleaseArtifactTests(TestCase):
    def test_sbom_is_spdx_and_matches_generator(self) -> None:
        path = ROOT / "sbom/indoor-grow.spdx.json"
        stored = json.loads(path.read_text(encoding="utf-8"))
        self.assertEqual("SPDX-2.3", stored["spdxVersion"])
        self.assertEqual(document(), stored)
        self.assertGreaterEqual(len(stored["packages"]), 80)

    def test_unknown_license_and_physical_holds_are_not_hidden(self) -> None:
        licenses = (ROOT / "docs/SBOM_E_LICENCAS.md").read_text(encoding="utf-8")
        readiness = (ROOT / "docs/RELATORIO_PRONTIDAO_V1.md").read_text(encoding="utf-8")
        self.assertIn("NOASSERTION", licenses)
        self.assertIn("A0/HOLD", readiness)
        self.assertIn("HIL físico", readiness)
        self.assertIn("profissional habilitado", readiness)
