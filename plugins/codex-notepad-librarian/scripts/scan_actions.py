"""Scan Notepad Librarian notes for action requests and date-like events."""

from __future__ import annotations

import argparse
import json
import re
from datetime import date
from pathlib import Path

try:
    from .setup_library import setup_library
    from .text_utils import rel_path
except ImportError:
    from setup_library import setup_library
    from text_utils import rel_path


SETTINGS_REL = ".notepad-librarian/settings.json"
DEFAULT_SETTINGS = {
    "auto_act_on_ntl": False,
    "date_order": "dmy",
}

EXPLICIT_RE = re.compile(r"^\s*(?:NTL|note\s+to\s+librarian)\s*:\s*(?P<text>.+?)\s*$", re.IGNORECASE)
DATE_RE = re.compile(r"\b(?P<day>\d{1,2})[/-](?P<month>\d{1,2})[/-](?P<year>\d{4})\b")


def load_settings(root: Path) -> dict[str, object]:
    root = root.expanduser().resolve()
    path = root / SETTINGS_REL
    if not path.exists():
        setup_library(root)
    if not path.exists():
        return dict(DEFAULT_SETTINGS)
    loaded = json.loads(path.read_text(encoding="utf-8-sig"))
    settings = dict(DEFAULT_SETTINGS)
    settings.update({key: loaded[key] for key in DEFAULT_SETTINGS.keys() & loaded.keys()})
    return settings


def update_settings(root: Path, *, auto_act_on_ntl: bool | None = None) -> dict[str, object]:
    root = root.expanduser().resolve()
    setup_library(root)
    settings = load_settings(root)
    if auto_act_on_ntl is not None:
        settings["auto_act_on_ntl"] = auto_act_on_ntl
    path = root / SETTINGS_REL
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(settings, indent=2) + "\n", encoding="utf-8")
    return settings


def _iter_note_files(root: Path) -> list[Path]:
    return sorted(
        path
        for path in root.rglob("*.txt")
        if path.is_file()
        and ".notepad-librarian" not in path.relative_to(root).parts
        and not path.relative_to(root).parts[:3] == ("Library", "Archive", "Originals")
    )


def _parse_dmy_date(text: str) -> str | None:
    match = DATE_RE.search(text)
    if not match:
        return None
    try:
        parsed = date(
            int(match.group("year")),
            int(match.group("month")),
            int(match.group("day")),
        )
    except ValueError:
        return None
    return parsed.isoformat()


def _classify_explicit(text: str) -> str:
    lower = text.lower()
    if any(word in lower for word in ["calendar", "event", "appointment", "meeting", "dinner"]):
        return "calendar"
    if any(word in lower for word in ["email", "mail", "send", "reply"]):
        return "email"
    if "remind" in lower or "reminder" in lower:
        return "reminder"
    return "task"


def _title_from_line(text: str) -> str:
    cleaned = DATE_RE.sub("", text).strip(" -:,.")
    cleaned = re.sub(
        r"^(?:make|create|add|schedule|set up)\s+(?:a\s+)?(?:calendar\s+)?(?:event\s+)?(?:for\s+)?",
        "",
        cleaned,
        flags=re.IGNORECASE,
    ).strip(" -:,.")
    cleaned = re.sub(r"\s+on\s*$", "", cleaned, flags=re.IGNORECASE).strip(" -:,.")
    return cleaned[:120] or text[:120]


def _action(
    *,
    root: Path,
    source: Path,
    line_number: int,
    trigger: str,
    kind: str,
    text: str,
    settings: dict[str, object],
) -> dict[str, object]:
    is_explicit = trigger == "explicit"
    date_value = _parse_dmy_date(text)
    return {
        "source": rel_path(source, root),
        "line": line_number,
        "trigger": trigger,
        "kind": kind,
        "text": text,
        "title": _title_from_line(text),
        "date": date_value,
        "requires_confirmation": not (is_explicit and bool(settings["auto_act_on_ntl"])),
    }


def scan_actions(root: Path) -> dict[str, object]:
    root = root.expanduser().resolve()
    setup_library(root)
    settings = load_settings(root)
    actions: list[dict[str, object]] = []

    for path in _iter_note_files(root):
        for index, line in enumerate(path.read_text(encoding="utf-8-sig").splitlines(), start=1):
            stripped = line.strip()
            if not stripped:
                continue
            explicit = EXPLICIT_RE.match(stripped)
            if explicit:
                text = explicit.group("text")
                actions.append(
                    _action(
                        root=root,
                        source=path,
                        line_number=index,
                        trigger="explicit",
                        kind=_classify_explicit(text),
                        text=text,
                        settings=settings,
                    )
                )
                continue
            if DATE_RE.search(stripped):
                actions.append(
                    _action(
                        root=root,
                        source=path,
                        line_number=index,
                        trigger="inferred",
                        kind="calendar",
                        text=stripped,
                        settings=settings,
                    )
                )

    return {"library": str(root), "settings": settings, "actions": actions}


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Scan a Notepad Librarian folder for action proposals.")
    parser.add_argument("folder", type=Path)
    parser.add_argument("--json", action="store_true")
    parser.add_argument("--enable-auto-ntl", action="store_true")
    parser.add_argument("--disable-auto-ntl", action="store_true")
    args = parser.parse_args(argv)

    if args.enable_auto_ntl and args.disable_auto_ntl:
        parser.error("choose either --enable-auto-ntl or --disable-auto-ntl")
    if args.enable_auto_ntl:
        update_settings(args.folder, auto_act_on_ntl=True)
    elif args.disable_auto_ntl:
        update_settings(args.folder, auto_act_on_ntl=False)

    result = scan_actions(args.folder)
    if args.json:
        print(json.dumps(result, indent=2))
    else:
        print(f"actions found: {len(result['actions'])}")
        for action in result["actions"]:
            confirm = "ask first" if action["requires_confirmation"] else "auto allowed"
            print(f"- {action['kind']} ({action['trigger']}, {confirm}): {action['title']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
