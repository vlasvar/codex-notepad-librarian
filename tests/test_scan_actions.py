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

    def test_fuzzy_librarian_prefix_accepts_common_misspelling(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp) / "NotepadLibrary"
            setup_library(root)
            (root / "Inbox" / "misspelled command.txt").write_text(
                "not to librari: remind me to check the contract on 21/2/2026\n",
                encoding="utf-8",
            )

            result = scan_actions(root)

            self.assertEqual(1, len(result["actions"]))
            action = result["actions"][0]
            self.assertEqual("explicit", action["trigger"])
            self.assertEqual("reminder", action["kind"])
            self.assertEqual("2026-02-21", action["date"])

    def test_greek_ntl_appointment_is_calendar_action(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp) / "NotepadLibrary"
            setup_library(root)
            (root / "Inbox" / "appointment.txt").write_text(
                "NTL: \u03a1\u03b1\u03bd\u03c4\u03b5\u03b2\u03bf\u03cd \u03b3\u03b9\u03b1 \u03a3\u03c5\u03bc\u03b2\u03cc\u03bb\u03b1\u03b9\u03b1 \u03a4\u03b5\u03bd\u03ad\u03b4\u03bf\u03c5 16, \u03a3\u03ac\u03b2\u03b2\u03b1\u03c4\u03bf 20/6/2026\n",
                encoding="utf-8",
            )

            result = scan_actions(root)

            self.assertEqual(1, len(result["actions"]))
            action = result["actions"][0]
            self.assertEqual("calendar", action["kind"])
            self.assertEqual("2026-06-20", action["date"])
            self.assertTrue(action["requires_confirmation"])

    def test_greek_coffee_note_with_date_is_calendar_proposal(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp) / "NotepadLibrary"
            setup_library(root)
            (root / "Inbox" / "coffee.txt").write_text(
                "\u03b8\u03b1 \u03c0\u03b1\u03c9 \u03b3\u03b9\u03b1 \u03ba\u03b1\u03c6\u03ad \u03bc\u03b5 \u03a4\u03af\u03bc\u03b7 21/2/2026 7\u03bc\u03bc\n",
                encoding="utf-8",
            )

            result = scan_actions(root)

            self.assertEqual(1, len(result["actions"]))
            action = result["actions"][0]
            self.assertEqual("inferred", action["trigger"])
            self.assertEqual("calendar", action["kind"])
            self.assertEqual("2026-02-21", action["date"])
            self.assertTrue(action["requires_confirmation"])

    def test_greeklish_email_request_is_email_action(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp) / "NotepadLibrary"
            setup_library(root)
            (root / "Inbox" / "email.txt").write_text(
                "note to librarian: steile meil to accountant about the invoice\n",
                encoding="utf-8",
            )

            result = scan_actions(root)

            self.assertEqual(1, len(result["actions"]))
            self.assertEqual("email", result["actions"][0]["kind"])

    def test_word_document_request_is_document_action(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp) / "NotepadLibrary"
            setup_library(root)
            (root / "Inbox" / "word.txt").write_text(
                "NTL: \u03c6\u03c4\u03b9\u03ac\u03be\u03b5 \u03b1\u03c5\u03c4\u03ae \u03c4\u03b7 \u03c3\u03b7\u03bc\u03b5\u03af\u03c9\u03c3\u03b7 \u03c9\u03c2 word document\n",
                encoding="utf-8",
            )

            result = scan_actions(root)

            self.assertEqual(1, len(result["actions"]))
            self.assertEqual("word_document", result["actions"][0]["kind"])

    def test_google_sheet_request_is_spreadsheet_action(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp) / "NotepadLibrary"
            setup_library(root)
            (root / "Inbox" / "sheet.txt").write_text(
                "NTL: make a google sheet out of this note\n",
                encoding="utf-8",
            )

            result = scan_actions(root)

            self.assertEqual(1, len(result["actions"]))
            self.assertEqual("spreadsheet", result["actions"][0]["kind"])

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
