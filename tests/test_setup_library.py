import json
import tempfile
import unittest
from pathlib import Path

from scripts.setup_library import REQUIRED_DIRS, REQUIRED_FILES, setup_library


class SetupLibraryTests(unittest.TestCase):
    def test_setup_creates_required_structure_and_seed_files(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp) / "NotepadLibrary"

            result = setup_library(root)

            for rel in REQUIRED_DIRS:
                self.assertTrue((root / rel).is_dir(), rel)
            for rel in REQUIRED_FILES:
                self.assertTrue((root / rel).is_file(), rel)
            self.assertTrue((root / ".notepad-librarian" / "retrieval-index.json").is_file())
            self.assertIn("Library/Index.txt", result["created"])

            index = json.loads((root / ".notepad-librarian" / "retrieval-index.json").read_text(encoding="utf-8"))
            self.assertEqual({"pages": []}, index)

    def test_setup_preserves_existing_files(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp) / "NotepadLibrary"
            hot = root / "Library" / "Hot.txt"
            hot.parent.mkdir(parents=True)
            hot.write_text("custom hot cache\n", encoding="utf-8")

            result = setup_library(root)

            self.assertEqual("custom hot cache\n", hot.read_text(encoding="utf-8"))
            self.assertNotIn("Library/Hot.txt", result["created"])


if __name__ == "__main__":
    unittest.main()
