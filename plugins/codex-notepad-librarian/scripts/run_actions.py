"""Prepare idempotent outward actions from Notepad Librarian notes."""

from __future__ import annotations

import argparse
import hashlib
import json
from datetime import date, datetime, timezone
from pathlib import Path

try:
    from .scan_actions import scan_actions
    from .setup_library import setup_library
except ImportError:
    from scan_actions import scan_actions
    from setup_library import setup_library


ACTION_STATE_REL = ".notepad-librarian/action-state.json"


def _now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def _read_json(path: Path, default: dict[str, object]) -> dict[str, object]:
    if not path.exists():
        return default.copy()
    data = json.loads(path.read_text(encoding="utf-8-sig"))
    return data if isinstance(data, dict) else default.copy()


def _write_json(path: Path, data: dict[str, object]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def action_id(action: dict[str, object]) -> str:
    payload = {
        "source": action.get("source", ""),
        "line": action.get("line", ""),
        "kind": action.get("kind", ""),
        "date": action.get("date", ""),
        "title": str(action.get("title", "")).casefold().strip(),
        "text": str(action.get("text", "")).casefold().strip(),
    }
    raw = json.dumps(payload, sort_keys=True, ensure_ascii=False)
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()[:16]


def load_action_state(root: Path) -> dict[str, object]:
    return _read_json(root / ACTION_STATE_REL, {"actions": {}})


def record_action(
    root: Path,
    action_id_value: str,
    *,
    status: str,
    external_id: str = "",
    note: str = "",
) -> dict[str, object]:
    root = root.expanduser().resolve()
    setup_library(root)
    state = load_action_state(root)
    actions = state.setdefault("actions", {})
    if not isinstance(actions, dict):
        actions = {}
        state["actions"] = actions
    actions[action_id_value] = {
        "status": status,
        "external_id": external_id,
        "note": note,
        "updated_at": _now(),
    }
    state["updated"] = _now()
    _write_json(root / ACTION_STATE_REL, state)
    return state


def prepare_actions(root: Path, *, today: date | None = None) -> dict[str, object]:
    root = root.expanduser().resolve()
    setup_library(root)
    scanned = scan_actions(root, today=today)
    state = load_action_state(root)
    records = state.get("actions")
    if not isinstance(records, dict):
        records = {}

    ready: list[dict[str, object]] = []
    skipped: list[dict[str, object]] = []
    unsupported: list[dict[str, object]] = []

    for action in scanned["actions"]:
        prepared = dict(action)
        prepared["action_id"] = action_id(action)
        existing = records.get(prepared["action_id"])
        if isinstance(existing, dict) and existing.get("status") in {"created", "ignored", "skipped"}:
            prepared["action_status"] = existing.get("status")
            prepared["external_id"] = existing.get("external_id", "")
            skipped.append(prepared)
            continue
        if prepared.get("kind") == "calendar" and prepared.get("date"):
            prepared["action_status"] = "ready_to_create"
            prepared["requires_confirmation"] = False
            ready.append(prepared)
            continue
        prepared["action_status"] = "unsupported_by_runner"
        unsupported.append(prepared)

    return {
        "library": str(root),
        "state_path": ACTION_STATE_REL,
        "today": scanned["today"],
        "ready": ready,
        "skipped": skipped,
        "unsupported": unsupported,
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Prepare or record idempotent Notepad Librarian actions.")
    parser.add_argument("folder", type=Path)
    parser.add_argument("--json", action="store_true")
    parser.add_argument("--today", help="Override run date as YYYY-MM-DD, mainly for tests.")
    parser.add_argument("--record-created", metavar="ACTION_ID")
    parser.add_argument("--record-ignored", metavar="ACTION_ID")
    parser.add_argument("--external-id", default="")
    parser.add_argument("--note", default="")
    args = parser.parse_args(argv)

    if args.record_created and args.record_ignored:
        parser.error("choose either --record-created or --record-ignored")
    if args.record_created:
        result = record_action(args.folder, args.record_created, status="created", external_id=args.external_id, note=args.note)
    elif args.record_ignored:
        result = record_action(args.folder, args.record_ignored, status="ignored", note=args.note)
    else:
        today = date.fromisoformat(args.today) if args.today else None
        result = prepare_actions(args.folder, today=today)

    if args.json:
        print(json.dumps(result, indent=2, ensure_ascii=False))
    else:
        if "ready" in result:
            print(f"ready actions: {len(result['ready'])}")
            for action in result["ready"]:
                print(f"- {action['action_id']} calendar: {action['title']} on {action['date']}")
        else:
            print("action state updated")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
