from pathlib import Path
from tempfile import TemporaryDirectory
from unittest import TestCase

from scripts.init_lighting_state import initialize


class InitLightingStateTests(TestCase):
    def setUp(self) -> None:
        self.temporary = TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.path = Path(self.temporary.name) / "lighting.json"
        self.entities = [f"switch.grow_light_{number}" for number in range(1, 5)]

    def test_creates_four_disabled_unique_schedules(self) -> None:
        initialize(self.path, self.entities)
        content = self.path.read_text(encoding="utf-8")
        self.assertEqual(4, content.count('"entity_id"'))
        self.assertEqual(4, content.count('"enabled":false'))

    def test_refuses_wrong_count_duplicates_and_overwrite(self) -> None:
        with self.assertRaisesRegex(ValueError, "exatamente quatro"):
            initialize(self.path, self.entities[:3])
        with self.assertRaisesRegex(ValueError, "únicas"):
            initialize(self.path, [self.entities[0]] * 4)
        initialize(self.path, self.entities)
        with self.assertRaises(FileExistsError):
            initialize(self.path, self.entities)
