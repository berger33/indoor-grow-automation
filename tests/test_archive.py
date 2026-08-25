from unittest import TestCase

from scripts.validate_archive import ARCHIVE, archive_errors


class EngineeringArchiveTests(TestCase):
    def test_heavy_engineering_is_archived_and_not_active(self) -> None:
        self.assertEqual((), archive_errors())

    def test_archive_has_inventory_and_legacy_drawings(self) -> None:
        inventory = (ARCHIVE / "README.md").read_text(encoding="utf-8")
        self.assertIn("Não o utilize", inventory)
        self.assertGreaterEqual(len(list((ARCHIVE / "desenhos").glob("REV-A-*.svg"))), 8)
