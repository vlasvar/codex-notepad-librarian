import tempfile
import unittest
from pathlib import Path

import _paths
from scripts.extract_text import extract_text


class ExtractTextTests(unittest.TestCase):
    def test_extracts_txt_with_direct_text_status(self):
        with tempfile.TemporaryDirectory() as tmp:
            source = Path(tmp) / "note.txt"
            source.write_text("Remember the lease review.\n", encoding="utf-8")

            result = extract_text(source)

            self.assertEqual("ok", result["status"])
            self.assertEqual("text/plain", result["content_type"])
            self.assertEqual("direct_text", result["text_strategy"])
            self.assertEqual("Remember the lease review.\n", result["text"])
            self.assertEqual([], result["issues"])

    def test_extracts_markdown_with_direct_text_status(self):
        with tempfile.TemporaryDirectory() as tmp:
            source = Path(tmp) / "note.md"
            source.write_text("# Note\n\n- Keep Markdown portable.\n", encoding="utf-8")

            result = extract_text(source)

            self.assertEqual("ok", result["status"])
            self.assertEqual("text/markdown", result["content_type"])
            self.assertEqual("direct_text", result["text_strategy"])
            self.assertIn("Keep Markdown portable", result["text"])
            self.assertEqual([], result["issues"])

    def test_pdf_reports_needs_ocr_setup_without_crashing(self):
        with tempfile.TemporaryDirectory() as tmp:
            source = Path(tmp) / "scan.pdf"
            source.write_bytes(b"%PDF-1.4\n% minimal placeholder\n")

            result = extract_text(source)

            self.assertEqual("needs_ocr_setup", result["status"])
            self.assertEqual("application/pdf", result["content_type"])
            self.assertEqual("pdf_ocr_pending_setup", result["text_strategy"])
            self.assertEqual("", result["text"])
            self.assertTrue(any("Tesseract" in issue for issue in result["issues"]))

    def test_unsupported_file_reports_unsupported_status(self):
        with tempfile.TemporaryDirectory() as tmp:
            source = Path(tmp) / "image.png"
            source.write_bytes(b"not text")

            result = extract_text(source)

            self.assertEqual("unsupported", result["status"])
            self.assertEqual("application/octet-stream", result["content_type"])
            self.assertEqual("unsupported", result["text_strategy"])
            self.assertEqual("", result["text"])


if __name__ == "__main__":
    unittest.main()
