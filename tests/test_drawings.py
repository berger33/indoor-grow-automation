from pathlib import Path
from tempfile import TemporaryDirectory
from unittest import TestCase

from scripts.validate_drawings import ROOT, validate_drawing, validate_drawings


class DrawingValidationTests(TestCase):
    def test_repository_rev_a_drawings_are_valid(self) -> None:
        self.assertGreaterEqual(validate_drawings(ROOT / "desenhos"), 10)

    def test_rejects_missing_hold_status(self) -> None:
        with TemporaryDirectory() as directory:
            path = Path(directory) / "REV-A-test.svg"
            path.write_text(
                '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 10 10"/>',
                encoding="utf-8",
            )
            with self.assertRaisesRegex(ValueError, "HOLD"):
                validate_drawing(path)

    def test_rejects_external_embedded_resource(self) -> None:
        with TemporaryDirectory() as directory:
            path = Path(directory) / "REV-A-test.svg"
            path.write_text(
                '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 10 10">'
                '<text>HOLD</text><image href="https://example.invalid/image.png"/>'
                "</svg>",
                encoding="utf-8",
            )
            with self.assertRaisesRegex(ValueError, "externo"):
                validate_drawing(path)
