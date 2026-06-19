import tempfile
import unittest
from pathlib import Path

from scripts.organize_library import organize_library
from scripts.setup_library import setup_library


class OrganizeLibraryTests(unittest.TestCase):
    def test_organize_reads_inbox_txt_and_preserves_original(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp) / "NotepadLibrary"
            setup_library(root)
            source = root / "Inbox" / "office lease note.txt"
            source.write_text(
                "Met with Sam about the office lease.\n"
                "Rent review is due on 1/8/2026.\n"
                "Need to check the lease terms before then.\n",
                encoding="utf-8",
            )

            result = organize_library(root)

            self.assertEqual(["Library/Sources/office-lease-note.txt"], result["created"])
            self.assertTrue((root / "Library" / "Sources" / "office-lease-note.txt").is_file())
            self.assertTrue((root / "Library" / "Archive" / "Originals" / "office lease note.txt").is_file())
            self.assertFalse(source.exists())
            self.assertIn("office-lease-note.txt", (root / "Library" / "Index.txt").read_text(encoding="utf-8"))
            self.assertIn("office lease note.txt", (root / "Library" / "Log.txt").read_text(encoding="utf-8"))
            self.assertIn("office lease", (root / "Library" / "Hot.txt").read_text(encoding="utf-8").lower())

    def test_organize_skips_archive_and_internal_txt_files(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp) / "NotepadLibrary"
            setup_library(root)
            archived = root / "Library" / "Archive" / "Originals" / "old.txt"
            archived.write_text("do not organize this again\n", encoding="utf-8")
            internal = root / ".notepad-librarian" / "internal.txt"
            internal.write_text("ignore internal notes\n", encoding="utf-8")

            result = organize_library(root)

            self.assertEqual([], result["created"])
            self.assertTrue(archived.exists())
            self.assertTrue(internal.exists())


if __name__ == "__main__":
    unittest.main()
