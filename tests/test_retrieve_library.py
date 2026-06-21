import tempfile
import unittest
from pathlib import Path

import _paths
from scripts.organize_library import organize_library
from scripts.process_library import process_library
from scripts.retrieve_library import build_retrieval_index, search_library
from scripts.setup_library import setup_library


class RetrieveLibraryTests(unittest.TestCase):
    def test_retrieve_indexes_txt_notes_and_returns_snippets(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp) / "NotepadLibrary"
            setup_library(root)
            (root / "Inbox" / "lease terms.txt").write_text(
                "Office lease terms include a rent review date and renewal clause.\n",
                encoding="utf-8",
            )
            organize_library(root)

            index = build_retrieval_index(root)
            results = search_library(root, "rent review", limit=3)

            self.assertGreaterEqual(len(index["pages"]), 1)
            self.assertEqual("Library/Sources/lease-terms.txt", results[0]["path"])
            self.assertIn("rent review", results[0]["snippet"].lower())
            self.assertGreater(results[0]["score"], 0)

    def test_retrieve_indexes_markdown_document_memory(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp) / "NotepadLibrary"
            setup_library(root)
            (root / "Inbox" / "memory loop.md").write_text(
                "# Memory Loop\n\nPortable Markdown should remain searchable.\n",
                encoding="utf-8",
            )
            process_library(root)

            index = build_retrieval_index(root)
            results = search_library(root, "portable markdown", limit=3)

            md_pages = [page for page in index["pages"] if page["path"].startswith("Library/Documents/")]
            self.assertEqual(1, len(md_pages))
            self.assertEqual(md_pages[0]["path"], results[0]["path"])
            self.assertIn("portable markdown", results[0]["snippet"].lower())


if __name__ == "__main__":
    unittest.main()
