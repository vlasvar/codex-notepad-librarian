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

    def test_repo_declares_local_marketplace(self):
        marketplace = json.loads(Path(".agents/plugins/marketplace.json").read_text(encoding="utf-8"))

        self.assertEqual("codex-notepad-librarian", marketplace["name"])
        self.assertEqual("Codex Notepad Librarian", marketplace["interface"]["displayName"])
        self.assertEqual("codex-notepad-librarian", marketplace["plugins"][0]["name"])
        self.assertEqual("./", marketplace["plugins"][0]["source"]["path"])


if __name__ == "__main__":
    unittest.main()
