from pathlib import Path
from unittest import TestCase


ROOT = Path(__file__).resolve().parents[1]
TUTORIALS = ROOT / "docs" / "tutorial"


class TutorialTests(TestCase):
    def test_diy_tutorial_has_the_required_order(self) -> None:
        index = (TUTORIALS / "README.md").read_text(encoding="utf-8")
        required = (
            "01-compras.md",
            "02-protoboard-e-reles.md",
            "03-prateleira-e-potes.md",
            "04-bombas-e-fiacao.md",
            "05-sensores-ph-ec-clima.md",
            "06-firmware-esp32.md",
            "07-hub-no-notebook.md",
            "08-primeiro-teste-com-agua.md",
            "09-primeira-receita.md",
        )
        positions = [index.index(name) for name in required]
        self.assertEqual(sorted(positions), positions)
        for name in required:
            self.assertTrue((TUTORIALS / name).is_file())

    def test_every_main_chapter_has_steps_gate_and_basic_safety(self) -> None:
        for chapter in range(1, 10):
            matches = list(TUTORIALS.glob(f"{chapter:02d}-*.md"))
            self.assertEqual(1, len(matches), chapter)
            text = matches[0].read_text(encoding="utf-8")
            self.assertGreaterEqual(text.count("1."), 1)
            self.assertIn("Gate", text)
            self.assertTrue(
                any(term in text.lower() for term in ("água", "deslig", "supervision")),
                matches[0].name,
            )

    def test_tutorial_does_not_reactivate_heavy_hardware(self) -> None:
        active = "\n".join(
            path.read_text(encoding="utf-8") for path in TUTORIALS.glob("*.md")
        ).lower()
        for forbidden in ("sn74hct595", "mcp23017", "atlas ezo", "painel industrial"):
            self.assertNotIn(forbidden, active)
        self.assertIn("notebook", active)
        self.assertIn("placa perfurada", active)
