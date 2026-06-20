import tempfile
import unittest
from pathlib import Path

import _paths
from scripts.scan_actions import load_settings, scan_actions, update_settings
from scripts.setup_library import setup_library


class ScanActionsTests(unittest.TestCase):
    def test_setup_creates_default_action_settings_that_ask_first(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp) / "NotepadLibrary"
            setup_library(root)

            settings = load_settings(root)

            self.assertFalse(settings["auto_act_on_ntl"])

    def test_explicit_ntl_calendar_action_requires_confirmation_by_default(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp) / "NotepadLibrary"
            setup_library(root)
            note = root / "Inbox" / "calendar note.txt"
            note.write_text(
                "NTL: make a calendar event for dinner with Cassy at Belvedere Hotel Prague on 27/1/2027\n",
                encoding="utf-8",
            )

            result = scan_actions(root)

            self.assertEqual(1, len(result["actions"]))
            action = result["actions"][0]
            self.assertEqual("explicit", action["trigger"])
            self.assertEqual("calendar", action["kind"])
            self.assertEqual("2027-01-27", action["date"])
            self.assertTrue(action["requires_confirmation"])

    def test_settings_file_accepts_utf8_bom(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp) / "NotepadLibrary"
            setup_library(root)
            settings = root / ".notepad-librarian" / "settings.json"
            settings.write_text(
                '{"auto_act_on_ntl": false, "date_order": "dmy"}\n',
                encoding="utf-8-sig",
            )
            (root / "Inbox" / "calendar note.txt").write_text(
                "NTL: make a calendar event for dinner with Cassy at Belvedere Hotel Prague on 27/1/2027\n",
                encoding="utf-8",
            )

            result = scan_actions(root)

            self.assertEqual(1, len(result["actions"]))
            self.assertTrue(result["actions"][0]["requires_confirmation"])

    def test_explicit_ntl_can_be_auto_allowed_when_setting_is_enabled(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp) / "NotepadLibrary"
            setup_library(root)
            update_settings(root, auto_act_on_ntl=True)
            (root / "Inbox" / "task note.txt").write_text(
                "note to librarian: create a task to call the hotel on 27/1/2027\n",
                encoding="utf-8",
            )

            result = scan_actions(root)

            self.assertEqual(1, len(result["actions"]))
            action = result["actions"][0]
            self.assertEqual("task", action["kind"])
            self.assertEqual("explicit", action["trigger"])
            self.assertFalse(action["requires_confirmation"])

    def test_plain_dated_note_is_inferred_calendar_proposal(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp) / "NotepadLibrary"
            setup_library(root)
            (root / "Inbox" / "dinner.txt").write_text(
                "27/1/2027 dinner with Cassy at Belvedere Hotel Prague\n",
                encoding="utf-8",
            )

            result = scan_actions(root)

            self.assertEqual(1, len(result["actions"]))
            action = result["actions"][0]
            self.assertEqual("inferred", action["trigger"])
            self.assertEqual("calendar", action["kind"])
            self.assertEqual("2027-01-27", action["date"])
            self.assertIn("dinner with Cassy", action["title"])
            self.assertTrue(action["requires_confirmation"])


if __name__ == "__main__":
    unittest.main()
