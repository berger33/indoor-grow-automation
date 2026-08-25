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
        self.assertGreaterEqual(len(stored["packages"]), 75)

    def test_licenses_and_physical_validation_are_not_hidden(self) -> None:
        licenses = (ROOT / "docs/SBOM_E_LICENCAS.md").read_text(encoding="utf-8")
        readiness = (ROOT / "docs/RELATORIO_PRONTIDAO_V1.md").read_text(encoding="utf-8")
        self.assertIn("77 dependências", licenses)
        self.assertIn("montagem física DIY ainda não validada", readiness)
        self.assertIn("somente com água", readiness)
        self.assertIn("pessoa qualificada", (ROOT / "docs/ESCOPO_V1.md").read_text(encoding="utf-8"))

    def test_ack_and_alarm_schemas_are_strict_and_versioned(self) -> None:
        ack = json.loads((ROOT / "contracts/mqtt/ack-v1.schema.json").read_text(encoding="utf-8"))
        alarm = json.loads((ROOT / "contracts/mqtt/alarm-v1.schema.json").read_text(encoding="utf-8"))
        self.assertFalse(ack["additionalProperties"])
        self.assertEqual(1, ack["properties"]["schema_version"]["const"])
        self.assertEqual(["ack", "nack"], ack["properties"]["status"]["enum"])
        self.assertFalse(alarm["additionalProperties"])
        self.assertTrue(alarm["properties"]["latched"]["const"])

    def test_legacy_delivery_map_is_preserved_only_in_archive(self) -> None:
        delivery = (ROOT / "archive/engenharia-pesada/docs/ENTREGA_TAREFAS_01_30.md").read_text(encoding="utf-8")
        for number in range(1, 31):
            self.assertIn(f"| {number} |", delivery)
        self.assertFalse((ROOT / "docs/ENTREGA_TAREFAS_01_30.md").exists())
