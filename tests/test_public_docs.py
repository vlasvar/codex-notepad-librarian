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


if __name__ == "__main__":
    unittest.main()
