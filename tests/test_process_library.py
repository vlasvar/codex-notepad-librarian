import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

import _paths
from scripts.process_library import process_library
from scripts.setup_library import setup_library


class ProcessLibraryTests(unittest.TestCase):
    def test_process_detects_txt_and_md_inbox_files_and_writes_state(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp) / "NotepadLibrary"
            setup_library(root)
            (root / "Inbox" / "lease note.txt").write_text("Lease terms due soon.\n", encoding="utf-8")
            (root / "Inbox" / "project.md").write_text("# Project\n\nShip the memory loop.\n", encoding="utf-8")

            result = process_library(root)

            self.assertEqual([], result["skipped"])
            self.assertEqual(["Inbox/lease note.txt", "Inbox/project.md"], [item["source_path"] for item in result["processed"]])
            self.assertEqual(["text/plain", "text/markdown"], [item["content_type"] for item in result["processed"]])
            self.assertEqual(["direct_text", "direct_text"], [item["text_strategy"] for item in result["processed"]])

            state_path = root / ".notepad-librarian" / "processed-files.json"
            state = json.loads(state_path.read_text(encoding="utf-8"))
            self.assertEqual(["Inbox/lease note.txt", "Inbox/project.md"], sorted(state["files"]))
            entry = state["files"]["Inbox/lease note.txt"]
            self.assertEqual("text/plain", entry["content_type"])
            self.assertEqual("direct_text", entry["text_strategy"])
            self.assertTrue(entry["document_id"].startswith("lease-note-"))
            self.assertEqual([f"Library/Documents/{entry['document_id']}.md"], entry["memory_paths"])
            self.assertTrue((root / entry["memory_paths"][0]).is_file())
            self.assertRegex(entry["processed_at"], r"^\d{4}-\d{2}-\d{2}T")
            self.assertRegex(entry["sha256"], r"^[a-f0-9]{64}$")

    def test_process_skips_unchanged_files_and_reprocesses_changed_files(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp) / "NotepadLibrary"
            setup_library(root)
            source = root / "Inbox" / "lease note.txt"
            source.write_text("Lease terms due soon.\n", encoding="utf-8")

            first = process_library(root)
            second = process_library(root)
            source.write_text("Lease terms changed.\n", encoding="utf-8")
            third = process_library(root)

            self.assertEqual(["Inbox/lease note.txt"], [item["source_path"] for item in first["processed"]])
            self.assertEqual([], first["skipped"])
            self.assertEqual([], second["processed"])
            self.assertEqual(["Inbox/lease note.txt"], [item["source_path"] for item in second["skipped"]])
            self.assertEqual(["Inbox/lease note.txt"], [item["source_path"] for item in third["processed"]])
            self.assertEqual([], third["skipped"])
            self.assertNotEqual(first["processed"][0]["sha256"], third["processed"][0]["sha256"])

    def test_process_records_pdf_extraction_status_without_crashing(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp) / "NotepadLibrary"
            setup_library(root)
            (root / "Inbox" / "scan.pdf").write_bytes(b"%PDF-1.4\n% placeholder\n")

            result = process_library(root)

            self.assertEqual(["Inbox/scan.pdf"], [item["source_path"] for item in result["processed"]])
            entry = result["processed"][0]
            self.assertEqual("application/pdf", entry["content_type"])
            self.assertEqual("pdf_pending_ocr", entry["text_strategy"])
            self.assertEqual("needs_ocr_setup", entry["extraction_status"])
            self.assertIn("PDF extraction/OCR is not configured yet.", entry["extraction_issues"])

    def test_process_writes_portable_markdown_document_memory(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp) / "NotepadLibrary"
            setup_library(root)
            source = root / "Inbox" / "lease note.txt"
            source.write_text("Met with Sam about the lease.\nReview rent by August.\n", encoding="utf-8")

            result = process_library(root)

            entry = result["processed"][0]
            memory_path = root / entry["memory_paths"][0]
            content = memory_path.read_text(encoding="utf-8")
            self.assertEqual(f"Library/Documents/{entry['document_id']}.md", entry["memory_paths"][0])
            self.assertIn("---\n", content)
            self.assertIn('source_path: "Inbox/lease note.txt"', content)
            self.assertIn('content_type: "text/plain"', content)
            self.assertIn('extraction_status: "ok"', content)
            self.assertIn("# Lease Note", content)
            self.assertIn("## Summary", content)
            self.assertIn("## Extracted Entities", content)
            self.assertIn("## Related Memory", content)
            self.assertIn("## Open Questions", content)
            self.assertIn("## Source Notes", content)
            self.assertIn("Met with Sam about the lease.", content)

    def test_process_writes_dated_review_note(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp) / "NotepadLibrary"
            setup_library(root)
            (root / "Inbox" / "lease note.txt").write_text("Met with Sam about the lease.\n", encoding="utf-8")
            (root / "Inbox" / "scan.pdf").write_bytes(b"%PDF-1.4\n% placeholder\n")

            first = process_library(root)
            second = process_library(root)

            review_paths = sorted((root / "Library" / "Reviews").glob("* Processing Review.md"))
            self.assertEqual(1, len(review_paths))
            content = review_paths[0].read_text(encoding="utf-8")
            self.assertEqual(str(review_paths[0].relative_to(root)).replace("\\", "/"), second["review_path"])
            self.assertIn("# Processing Review", content)
            self.assertIn("## Processed Files", content)
            self.assertIn("- Inbox/lease note.txt", content)
            self.assertIn("- Inbox/scan.pdf", content)
            self.assertIn("## Skipped Files", content)
            self.assertIn("- Inbox/lease note.txt", content)
            self.assertIn("## Documents Created Or Updated", content)
            self.assertIn(first["processed"][0]["memory_paths"][0], content)
            self.assertIn("## OCR Statuses", content)
            self.assertIn("needs_ocr_setup", content)
            self.assertIn("## Low-Confidence Assumptions", content)
            self.assertIn("## Suggested Links And Actions", content)
            self.assertIn("## Questions For Review", content)

    def test_cli_prints_json_report(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp) / "NotepadLibrary"
            setup_library(root)
            (root / "Inbox" / "meeting.md").write_text("# Meeting\n", encoding="utf-8")

            completed = subprocess.run(
                [
                    sys.executable,
                    str(_paths.PLUGIN_ROOT / "scripts" / "process_library.py"),
                    str(root),
                    "--json",
                ],
                check=True,
                capture_output=True,
                text=True,
            )

            result = json.loads(completed.stdout)
            self.assertEqual(["Inbox/meeting.md"], [item["source_path"] for item in result["processed"]])
            self.assertEqual([], result["skipped"])


if __name__ == "__main__":
    unittest.main()
