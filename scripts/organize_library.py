"""Organize loose Notepad .txt notes into a plain-text library."""

from __future__ import annotations

import argparse
import json
import shutil
from datetime import datetime, timezone
from pathlib import Path

try:
    from .setup_library import setup_library
    from .text_utils import display_title, rel_path, slugify
except ImportError:
    from setup_library import setup_library
    from text_utils import display_title, rel_path, slugify


SKIP_PARTS = {".notepad-librarian", "Archive", "Originals"}


def _is_candidate(path: Path, root: Path) -> bool:
    if path.suffix.lower() != ".txt" or not path.is_file():
        return False
    rel = path.relative_to(root)
    parts = set(rel.parts)
    if ".notepad-librarian" in parts:
        return False
    if len(rel.parts) >= 3 and rel.parts[:3] == ("Library", "Archive", "Originals"):
        return False
    if rel.parts[0] == "Library":
        return False
    return rel.parts[0] == "Inbox" or len(rel.parts) == 1


def _unique_path(path: Path) -> Path:
    if not path.exists():
        return path
    stem = path.stem
    suffix = path.suffix
    counter = 2
    while True:
        candidate = path.with_name(f"{stem}-{counter}{suffix}")
        if not candidate.exists():
            return candidate
        counter += 1


def _organized_content(source: Path, root: Path, original_rel: str, body: str) -> str:
    title = display_title(source)
    now = datetime.now(timezone.utc).replace(microsecond=0).isoformat()
    return (
        f"{title}\n"
        f"{'=' * len(title)}\n\n"
        "Type: Source\n"
        f"Created: {now}\n"
        f"Original file: {original_rel}\n\n"
        "Text\n"
        "----\n\n"
        f"{body.strip()}\n\n"
        "Related files\n"
        "-------------\n\n"
        "- Library\\Index.txt\n"
        "- Library\\Hot.txt\n"
    )


def _append_log(root: Path, lines: list[str]) -> None:
    log = root / "Library" / "Log.txt"
    existing = log.read_text(encoding="utf-8") if log.exists() else ""
    entry = "\n".join(lines).rstrip() + "\n\n"
    log.write_text(existing.rstrip() + "\n\n" + entry if existing.strip() else entry, encoding="utf-8")


def _write_index(root: Path) -> None:
    sources = sorted((root / "Library" / "Sources").glob("*.txt"))
    ideas = sorted((root / "Library" / "Ideas").glob("*.txt"))
    people = sorted((root / "Library" / "People").glob("*.txt"))
    topics = sorted((root / "Library" / "Topics").glob("*.txt"))

    def section(title: str, paths: list[Path]) -> str:
        if not paths:
            return f"{title}:\n- No {title.lower()} notes yet.\n"
        rows = [f"- {rel_path(path, root)}" for path in paths]
        return f"{title}:\n" + "\n".join(rows) + "\n"

    content = (
        "Notepad Librarian Index\n"
        "=======================\n\n"
        + section("Sources", sources)
        + "\n"
        + section("Ideas", ideas)
        + "\n"
        + section("People", people)
        + "\n"
        + section("Topics", topics)
    )
    (root / "Library" / "Index.txt").write_text(content, encoding="utf-8")


def _write_hot(root: Path, created: list[str]) -> None:
    now = datetime.now(timezone.utc).replace(microsecond=0).isoformat()
    recent = (
        "\n".join(f"- {display_title(Path(item))}: {item}" for item in created)
        if created
        else "- No new notes organized."
    )
    content = (
        "Notepad Librarian Hot File\n"
        "==========================\n\n"
        f"Last updated: {now}\n\n"
        "Recent context:\n"
        f"{recent}\n"
    )
    (root / "Library" / "Hot.txt").write_text(content, encoding="utf-8")


def organize_library(root: Path) -> dict[str, object]:
    root = root.expanduser().resolve()
    setup_library(root)

    created: list[str] = []
    archived: list[str] = []
    skipped: list[str] = []

    candidates = sorted(path for path in root.rglob("*.txt") if _is_candidate(path, root))
    for source in candidates:
        body = source.read_text(encoding="utf-8")
        if not body.strip():
            skipped.append(rel_path(source, root))
            continue

        archive_path = _unique_path(root / "Library" / "Archive" / "Originals" / source.name)
        archive_path.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source, archive_path)

        slug = slugify(source.stem)
        organized_path = _unique_path(root / "Library" / "Sources" / f"{slug}.txt")
        original_rel = rel_path(archive_path, root)
        organized_path.write_text(_organized_content(source, root, original_rel, body), encoding="utf-8")

        if archive_path.exists() and organized_path.exists():
            source.unlink()

        created.append(rel_path(organized_path, root))
        archived.append(original_rel)

    _write_index(root)
    _write_hot(root, created)
    if created or archived or skipped:
        _append_log(
            root,
            [
                f"Organized at {datetime.now(timezone.utc).replace(microsecond=0).isoformat()}",
                *(f"Created: {item}" for item in created),
                *(f"Archived original: {item}" for item in archived),
                *(f"Skipped: {item}" for item in skipped),
            ],
        )

    return {"library": str(root), "created": created, "archived": archived, "skipped": skipped}


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Organize saved Notepad .txt notes into a text library.")
    parser.add_argument("folder", type=Path)
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args(argv)

    result = organize_library(args.folder)
    if args.json:
        print(json.dumps(result, indent=2))
    else:
        print(f"organized: {len(result['created'])} notes")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
