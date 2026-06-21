import re
import unittest
from pathlib import Path


class PublicDocsTests(unittest.TestCase):
    def test_readme_uses_fake_paths_and_no_secret_like_strings(self):
        text = Path("README.md").read_text(encoding="utf-8")

        self.assertNotIn("v" + "vare", text.lower())
        self.assertNotIn("00" + "_Notes", text)
        self.assertNotRegex(text, re.compile(r"C:\\Users\\(?!Alex)", re.IGNORECASE))
        self.assertNotRegex(text, re.compile(r"sk-[A-Za-z0-9_-]{20,}"))
        self.assertNotRegex(text, re.compile(r"ghp_[A-Za-z0-9_]{20,}"))
        self.assertIn(r"C:\Users\Alex\Documents\NotepadLibrary", text)

    def test_public_scripts_do_not_contain_personal_paths_or_secrets(self):
        text = Path("install.ps1").read_text(encoding="utf-8")

        self.assertNotIn("v" + "vare", text.lower())
        self.assertNotIn("00" + "_Notes", text)
        self.assertNotRegex(text, re.compile(r"C:\\Users\\(?!Alex)", re.IGNORECASE))
        self.assertNotRegex(text, re.compile(r"sk-[A-Za-z0-9_-]{20,}"))
        self.assertNotRegex(text, re.compile(r"ghp_[A-Za-z0-9_]{20,}"))

    def test_readme_explains_tesseract_setup_as_codex_assisted(self):
        text = Path("README.md").read_text(encoding="utf-8")

        self.assertIn("PDFs And OCR", text)
        self.assertIn('Add Tesseract configuration to my Notepad library.', text)
        self.assertIn("does not need Tesseract to process normal `.txt` or `.md` notes", text)

    def test_installer_creates_public_v02_memory_loop_structure(self):
        text = Path("install.ps1").read_text(encoding="utf-8")

        self.assertIn('"Library\\Documents"', text)
        self.assertIn('"Library\\Reviews"', text)
        self.assertIn('"processed-files.json"', text)
        self.assertIn('"ocr"', text)
        self.assertIn('"tesseract_path"', text)
        self.assertIn('"tessdata_dir"', text)
        self.assertIn('"languages"', text)
        self.assertIn("Process my Notepad library", text)

    def test_readme_links_to_greek_user_guide(self):
        text = Path("README.md").read_text(encoding="utf-8")

        self.assertIn("🇬🇷 Ελληνικά / Greek Users", text)
        self.assertIn("[README.el.md](README.el.md)", text)

    def test_greek_readme_is_public_safe_and_practical(self):
        text = Path("README.el.md").read_text(encoding="utf-8")

        self.assertIn("# Codex Notepad Librarian - Ελληνικός οδηγός", text)
        self.assertIn(".\\install.ps1", text)
        self.assertIn("Process my Notepad library", text)
        self.assertIn("Add Tesseract configuration to my Notepad library.", text)
        self.assertIn(r"C:\Users\Alex\Documents\NotepadLibrary", text)
        self.assertNotIn("v" + "vare", text.lower())
        self.assertNotIn("00" + "_Notes", text)
        self.assertNotRegex(text, re.compile(r"C:\\Users\\(?!Alex)", re.IGNORECASE))
        self.assertNotRegex(text, re.compile(r"sk-[A-Za-z0-9_-]{20,}"))
        self.assertNotRegex(text, re.compile(r"ghp_[A-Za-z0-9_]{20,}"))


if __name__ == "__main__":
    unittest.main()
