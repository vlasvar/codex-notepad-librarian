import json
import subprocess
import sys
import tempfile
import unittest
from datetime import date
from pathlib import Path

import _paths
from scripts.run_actions import prepare_actions, record_action
from scripts.setup_library import setup_library


RUN_DATE = date(2026, 6, 22)


class RunActionsTests(unittest.TestCase):
    def test_prepare_actions_returns_future_calendar_events_without_confirmation(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp) / "NotepadLibrary"
            setup_library(root)
            (root / "Inbox" / "calendar.txt").write_text(
                "NTL: make a calendar event for contract signing on 24/6/2026\n",
                encoding="utf-8",
            )

            result = prepare_actions(root, today=RUN_DATE)

            self.assertEqual(1, len(result["ready"]))
            action = result["ready"][0]
            self.assertEqual("ready_to_create", action["action_status"])
            self.assertEqual("calendar", action["kind"])
            self.assertEqual("2026-06-24", action["date"])
            self.assertFalse(action["requires_confirmation"])
            self.assertRegex(action["action_id"], r"^[a-f0-9]{16}$")

    def test_prepare_actions_skips_recorded_actions(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp) / "NotepadLibrary"
            setup_library(root)
            (root / "Inbox" / "calendar.txt").write_text(
                "NTL: make a calendar event for contract signing on 24/6/2026\n",
                encoding="utf-8",
            )
            first = prepare_actions(root, today=RUN_DATE)
            action_id = first["ready"][0]["action_id"]

            record_action(root, action_id, status="created", external_id="event-123")
            second = prepare_actions(root, today=RUN_DATE)

            self.assertEqual([], second["ready"])
            self.assertEqual(1, len(second["skipped"]))
            self.assertEqual("event-123", second["skipped"][0]["external_id"])

    def test_cli_prints_json_report(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp) / "NotepadLibrary"
            setup_library(root)
            (root / "Inbox" / "calendar.txt").write_text(
                "NTL: make a calendar event for contract signing on 24/6/2026\n",
                encoding="utf-8",
            )

            completed = subprocess.run(
                [
                    sys.executable,
                    str(_paths.PLUGIN_ROOT / "scripts" / "run_actions.py"),
                    str(root),
                    "--today",
                    RUN_DATE.isoformat(),
                    "--json",
                ],
                check=True,
                capture_output=True,
                text=True,
            )

            result = json.loads(completed.stdout)
            self.assertEqual(1, len(result["ready"]))


if __name__ == "__main__":
    unittest.main()
