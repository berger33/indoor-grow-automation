import re
from pathlib import Path
from unittest import TestCase


ROOT = Path(__file__).resolve().parents[1]
TUTORIALS = ROOT / "docs/tutorial"


class TutorialTests(TestCase):
    def test_chapters_03_to_14_have_images_steps_acceptance_and_hold(self) -> None:
        for chapter in range(3, 15):
            matches = list(TUTORIALS.glob(f"{chapter:02d}-*.md"))
            self.assertEqual(1, len(matches), chapter)
            text = matches[0].read_text(encoding="utf-8")
            self.assertRegex(text, r"!\[[^]]+\]\(([^)]+\.svg)\)")
            self.assertIn("HOLD", text)
            self.assertGreaterEqual(len(re.findall(r"(?m)^\d+\. ", text)), 8)
            image = re.search(r"!\[[^]]+\]\(([^)]+\.svg)\)", text)
            self.assertTrue((TUTORIALS / image.group(1)).is_file())

    def test_ac_chapter_never_authorizes_layperson(self) -> None:
        text = (TUTORIALS / "08-instalacao-ca-profissional.md").read_text(encoding="utf-8")
        self.assertIn("exclusiva de profissional", text)
        self.assertIn("Não pode", text)
