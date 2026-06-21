import json
import unittest
from pathlib import Path

from _paths import PLUGIN_ROOT


class PluginManifestTests(unittest.TestCase):
    def test_manifest_declares_plugin_and_skills(self):
        manifest = json.loads((PLUGIN_ROOT / ".codex-plugin" / "plugin.json").read_text(encoding="utf-8"))

        self.assertEqual("codex-notepad-librarian", manifest["name"])
        self.assertEqual("0.2.0", manifest["version"])
        self.assertEqual("./skills/", manifest["skills"])
        self.assertIn("Notepad Librarian", manifest["interface"]["displayName"])
        self.assertIn("folder-based notes", manifest["description"])

    def test_repo_declares_local_marketplace(self):
        marketplace = json.loads(Path(".agents/plugins/marketplace.json").read_text(encoding="utf-8"))

        self.assertEqual("codex-notepad-librarian", marketplace["name"])
        self.assertEqual("Codex Notepad Librarian", marketplace["interface"]["displayName"])
        self.assertEqual("codex-notepad-librarian", marketplace["plugins"][0]["name"])
        self.assertEqual("./plugins/codex-notepad-librarian", marketplace["plugins"][0]["source"]["path"])
        self.assertTrue((PLUGIN_ROOT / ".codex-plugin" / "plugin.json").is_file())


if __name__ == "__main__":
    unittest.main()
