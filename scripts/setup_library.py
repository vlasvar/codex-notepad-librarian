"""Create or verify a plain-text Notepad Librarian folder."""

from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path


REQUIRED_DIRS = [
    "Inbox",
    "Library",
    "Library/Sources",
    "Library/Ideas",
    "Library/People",
    "Library/Topics",
    "Library/Archive",
    "Library/Archive/Originals",
    ".notepad-librarian",
]

REQUIRED_FILES = {
    "Library/Index.txt": (
        "Notepad Librarian Index\n"
        "=======================\n\n"
        "This file lists the organized notes in this plain-text library.\n\n"
        "Sources:\n"
        "- No source notes yet.\n\n"
        "Ideas:\n"
        "- No idea notes yet.\n\n"
        "People:\n"
        "- No people notes yet.\n\n"
        "Topics:\n"
        "- No topic notes yet.\n"
    ),
    "Library/Hot.txt": (
        "Notepad Librarian Hot File\n"
        "==========================\n\n"
        "Last updated: not yet organized\n\n"
        "Recent context:\n"
        "- The library has been set up and is ready for saved Notepad notes.\n"
    ),
    "Library/Log.txt": (
        "Notepad Librarian Log\n"
        "=====================\n\n"
        "No operations recorded yet.\n"
    ),
}


def _write_if_missing(path: Path, content: str) -> bool:
    if path.exists():
        return False
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")
    return True


def setup_library(root: Path) -> dict[str, object]:
    root = root.expanduser().resolve()
    created: list[str] = []
    root.mkdir(parents=True, exist_ok=True)

    for rel in REQUIRED_DIRS:
        target = root / rel
        if not target.exists():
            target.mkdir(parents=True, exist_ok=True)
            created.append(rel)

    for rel, content in REQUIRED_FILES.items():
        if _write_if_missing(root / rel, content):
            created.append(rel)

    index_rel = ".notepad-librarian/retrieval-index.json"
    if _write_if_missing(root / index_rel, json.dumps({"pages": []}, indent=2) + "\n"):
        created.append(index_rel)

    settings_rel = ".notepad-librarian/settings.json"
    default_settings = {
        "auto_act_on_ntl": False,
        "date_order": "dmy",
    }
    if _write_if_missing(root / settings_rel, json.dumps(default_settings, indent=2) + "\n"):
        created.append(settings_rel)

    return {
        "library": str(root),
        "created": created,
        "updated": datetime.now(timezone.utc).replace(microsecond=0).isoformat(),
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Set up a plain-text Notepad Librarian folder.")
    parser.add_argument("folder", type=Path)
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args(argv)

    result = setup_library(args.folder)
    if args.json:
        print(json.dumps(result, indent=2))
    else:
        print(f"library ready: {result['library']}")
        if result["created"]:
            print("created:")
            for item in result["created"]:
                print(f"- {item}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
