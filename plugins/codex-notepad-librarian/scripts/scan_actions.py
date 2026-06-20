"""Scan Notepad Librarian notes for action requests and date-like events."""

from __future__ import annotations

import argparse
import json
import re
import unicodedata
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

EXPLICIT_PREFIX_RE = re.compile(
    r"^\s*(?P<prefix>[^:]{1,80})\s*:\s*(?P<text>.+?)\s*$",
    re.IGNORECASE,
)
DATE_RE = re.compile(r"\b(?P<day>\d{1,2})[/-](?P<month>\d{1,2})[/-](?P<year>\d{4})\b")

CALENDAR_KEYWORDS = [
    "calendar",
    "event",
    "appointment",
    "meeting",
    "dinner",
    "lunch",
    "coffee",
    "cafe",
    "rantevou",
    "randevou",
    "sinantisi",
    "synantisi",
    "kafes",
    "kafe",
    "fagito",
    "poto",
    "trapezi",
    "genethlia",
    "pame",
    "tha pao",
    "\u03c1\u03b1\u03bd\u03c4\u03b5\u03b2\u03bf\u03c5",
    "\u03c3\u03c5\u03bd\u03b1\u03bd\u03c4\u03b7\u03c3\u03b7",
    "\u03b4\u03b5\u03b9\u03c0\u03bd\u03bf",
    "\u03ba\u03b1\u03c6\u03b5",
    "\u03c6\u03b1\u03b3\u03b7\u03c4\u03bf",
    "\u03c0\u03bf\u03c4\u03bf",
    "\u03c4\u03c1\u03b1\u03c0\u03b5\u03b6\u03b9",
    "\u03b3\u03b5\u03bd\u03b5\u03b8\u03bb\u03b9\u03b1",
    "\u03c0\u03b1\u03bc\u03b5",
    "\u03b8\u03b1 \u03c0\u03b1\u03c9",
]
EMAIL_KEYWORDS = [
    "email",
    "e-mail",
    "mail",
    "reply",
    "send",
    "meil",
    "mailare",
    "steile",
    "stile",
    "apantise",
    "\u03b7\u03bc\u03b5\u03b7\u03bb",
    "\u03bc\u03b5\u03b9\u03bb",
    "\u03bc\u03b5\u03b9\u03bb",
    "\u03c3\u03c4\u03b5\u03b9\u03bb\u03b5",
    "\u03b1\u03c0\u03b1\u03bd\u03c4\u03b7\u03c3\u03b5",
    "\u03bc\u03b7\u03bd\u03c5\u03bc\u03b1",
]
REMINDER_KEYWORDS = [
    "remind",
    "reminder",
    "dont forget",
    "don't forget",
    "min ksexaso",
    "thimise mou",
    "ypenthymisi",
    "\u03bc\u03b7\u03bd \u03be\u03b5\u03c7\u03b1\u03c3\u03c9",
    "\u03b8\u03c5\u03bc\u03b9\u03c3\u03b5 \u03bc\u03bf\u03c5",
    "\u03c5\u03c0\u03b5\u03bd\u03b8\u03c5\u03bc\u03b9\u03c3\u03b7",
]
WORD_KEYWORDS = [
    "word",
    "doc",
    "docx",
    "document",
    "word document",
    "eggrafo",
    "keimeno",
    "\u03b5\u03b3\u03b3\u03c1\u03b1\u03c6\u03bf",
    "\u03ba\u03b5\u03b9\u03bc\u03b5\u03bd\u03bf",
]
SPREADSHEET_KEYWORDS = [
    "excel",
    "xlsx",
    "spreadsheet",
    "sheet",
    "google sheet",
    "google sheets",
    "pinakas",
    "\u03c0\u03b9\u03bd\u03b1\u03ba\u03b1\u03c2",
]
PDF_KEYWORDS = ["pdf"]
PRESENTATION_KEYWORDS = [
    "presentation",
    "powerpoint",
    "slides",
    "parousiasi",
    "\u03c0\u03b1\u03c1\u03bf\u03c5\u03c3\u03b9\u03b1\u03c3\u03b7",
]
TASK_KEYWORDS = [
    "task",
    "todo",
    "to do",
    "na kano",
    "prepei na",
    "douleia",
    "ekkremotita",
    "\u03bd\u03b1 \u03ba\u03b1\u03bd\u03c9",
    "\u03c0\u03c1\u03b5\u03c0\u03b5\u03b9 \u03bd\u03b1",
    "\u03b4\u03bf\u03c5\u03bb\u03b5\u03b9\u03b1",
    "\u03b5\u03ba\u03ba\u03c1\u03b5\u03bc\u03bf\u03c4\u03b7\u03c4\u03b1",
]


def _plain(text: str) -> str:
    decomposed = unicodedata.normalize("NFD", text.casefold())
    without_marks = "".join(char for char in decomposed if unicodedata.category(char) != "Mn")
    return re.sub(r"\s+", " ", without_marks).strip()


def _contains_any(text: str, keywords: list[str]) -> bool:
    normalized = _plain(text)
    return any(_plain(keyword) in normalized for keyword in keywords)


def _is_librarian_prefix(prefix: str) -> bool:
    normalized = _plain(prefix)
    normalized = re.sub(r"[^a-z0-9\u0370-\u03ff]+", " ", normalized).strip()
    if normalized == "ntl":
        return True
    if normalized in {"note to librarian", "note to librari", "not to librarian", "not to librari"}:
        return True
    words = normalized.split()
    return bool(words and words[0] in {"note", "not"} and any(word.startswith("librar") for word in words[1:]))


def _extract_explicit_text(line: str) -> str | None:
    match = EXPLICIT_PREFIX_RE.match(line)
    if not match:
        return None
    if not _is_librarian_prefix(match.group("prefix")):
        return None
    return match.group("text")


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
    if _contains_any(text, SPREADSHEET_KEYWORDS):
        return "spreadsheet"
    if _contains_any(text, WORD_KEYWORDS):
        return "word_document"
    if _contains_any(text, PDF_KEYWORDS):
        return "pdf"
    if _contains_any(text, PRESENTATION_KEYWORDS):
        return "presentation"
    if _contains_any(text, EMAIL_KEYWORDS):
        return "email"
    if _contains_any(text, REMINDER_KEYWORDS):
        return "reminder"
    if _contains_any(text, CALENDAR_KEYWORDS):
        return "calendar"
    if _contains_any(text, TASK_KEYWORDS):
        return "task"
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
            explicit_text = _extract_explicit_text(stripped)
            if explicit_text is not None:
                actions.append(
                    _action(
                        root=root,
                        source=path,
                        line_number=index,
                        trigger="explicit",
                        kind=_classify_explicit(explicit_text),
                        text=explicit_text,
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
