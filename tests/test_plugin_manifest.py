import json
import unittest
from pathlib import Path


class PluginManifestTests(unittest.TestCase):
    def test_manifest_declares_plugin_and_skills(self):
        manifest = json.loads(Path(".codex-plugin/plugin.json").read_text(encoding="utf-8"))

        self.assertEqual("codex-notepad-librarian", manifest["name"])
        self.assertEqual("./skills/", manifest["skills"])
        self.assertIn("Notepad Librarian", manifest["interface"]["displayName"])
        self.assertIn("plain .txt notes", manifest["description"])


if __name__ == "__main__":
    unittest.main()
