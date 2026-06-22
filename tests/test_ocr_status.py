import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

import _paths
from scripts.ocr_status import ocr_status
from scripts.process_library import process_library
from scripts.setup_library import setup_library


class OcrStatusTests(unittest.TestCase):
    def test_missing_ocr_setup_reports_repair_hints_and_queued_pdf(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp) / "NotepadLibrary"
            setup_library(root)
            (root / "Inbox" / "scan.pdf").write_bytes(b"%PDF-1.4\n% placeholder\n")
            process_library(root)

            result = ocr_status(root)

            self.assertIn(result["status"], {"missing_tesseract", "missing_tessdata", "missing_languages", "ready"})
            self.assertEqual(["ell", "eng"], result["languages"]["configured"])
            self.assertEqual(["Inbox/scan.pdf"], [item["source_path"] for item in result["queued_files"]])
            if result["status"] != "ready":
                self.assertTrue(result["repair_hints"])

    def test_configured_ocr_setup_reports_available_and_missing_languages(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp) / "NotepadLibrary"
            setup_library(root)
            tesseract = root / "tools" / "tesseract.exe"
            tessdata = root / "tools" / "tessdata"
            tesseract.parent.mkdir(parents=True)
            tessdata.mkdir()
            tesseract.write_text("fake executable\n", encoding="utf-8")
            (tessdata / "eng.traineddata").write_text("fake language data\n", encoding="utf-8")
            settings_path = root / ".notepad-librarian" / "settings.json"
            settings = json.loads(settings_path.read_text(encoding="utf-8"))
            settings["ocr"] = {
                "tesseract_path": str(tesseract),
                "tessdata_dir": str(tessdata),
                "languages": ["eng", "ell"],
            }
            settings_path.write_text(json.dumps(settings, indent=2) + "\n", encoding="utf-8")

            result = ocr_status(root)

            self.assertEqual("missing_languages", result["status"])
            self.assertTrue(result["tesseract"]["found"])
            self.assertTrue(result["tessdata"]["found"])
            self.assertEqual(["eng", "ell"], result["languages"]["configured"])
            self.assertEqual(["eng"], result["languages"]["available"])
            self.assertEqual(["ell"], result["languages"]["missing"])
            self.assertIn("Install tessdata for missing languages: ell.", result["repair_hints"])

    def test_cli_prints_json_report(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp) / "NotepadLibrary"
            setup_library(root)

            completed = subprocess.run(
                [
                    sys.executable,
                    str(_paths.PLUGIN_ROOT / "scripts" / "ocr_status.py"),
                    str(root),
                    "--json",
                ],
                check=True,
                capture_output=True,
                text=True,
            )

            result = json.loads(completed.stdout)
            self.assertIn(result["status"], {"missing_tesseract", "missing_tessdata", "missing_languages", "ready"})
            self.assertEqual([], result["queued_files"])


if __name__ == "__main__":
    unittest.main()
