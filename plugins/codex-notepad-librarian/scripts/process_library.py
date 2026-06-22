"""Process Inbox sources into durable Notepad Librarian state."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
from datetime import datetime, timezone
from pathlib import Path

try:
    from .extract_text import TEXT_TYPES, extract_text
    from .setup_library import setup_library
    from .text_utils import display_title, rel_path, slugify
except ImportError:
    from extract_text import TEXT_TYPES, extract_text
    from setup_library import setup_library
    from text_utils import display_title, rel_path, slugify


STATE_REL = ".notepad-librarian/processed-files.json"
SUPPORTED_SUFFIXES = set(TEXT_TYPES) | {".pdf"}
DATE_RE = re.compile(r"\b\d{1,2}[/-]\d{1,2}[/-]\d{4}\b")


def _now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _load_state(path: Path) -> dict[str, object]:
    if not path.exists():
        return {"files": {}}
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict) or not isinstance(data.get("files"), dict):
        return {"files": {}}
    return data


def _write_state(path: Path, state: dict[str, object]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(state, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def _inbox_candidates(root: Path) -> list[Path]:
    inbox = root / "Inbox"
    if not inbox.exists():
        return []
    return sorted(
        path
        for path in inbox.rglob("*")
        if path.is_file() and path.suffix.lower() in SUPPORTED_SUFFIXES
    )


def _state_entry(source: Path, root: Path, sha256: str, extraction: dict[str, object]) -> dict[str, object]:
    source_rel = rel_path(source, root)
    document_id = f"{slugify(source.stem, fallback='document')}-{sha256[:12]}"
    return {
        "source_path": source_rel,
        "sha256": sha256,
        "processed_at": _now(),
        "content_type": extraction["content_type"],
        "text_strategy": extraction["text_strategy"],
        "extraction_status": extraction["status"],
        "extraction_issues": extraction["issues"],
        "document_id": document_id,
        "memory_paths": [f"Library/Documents/{document_id}.md"],
    }


def _yaml_string(value: object) -> str:
    text = str(value).replace("\\", "\\\\").replace('"', '\\"')
    return f'"{text}"'


def _date_mentions(text: str) -> list[str]:
    return sorted(set(DATE_RE.findall(text)))


def _likely_entities(text: str) -> list[str]:
    candidates = re.findall(r"\b[A-Z][A-Za-z]{2,}(?:\s+[A-Z][A-Za-z]{2,}){0,3}\b", text)
    stop = {"The", "This", "That", "Summary", "Source", "Notes"}
    entities: list[str] = []
    for candidate in candidates:
        if candidate in stop or candidate in entities:
            continue
        entities.append(candidate)
        if len(entities) == 10:
            break
    return entities


def _bullet_lines(values: list[str], empty: str) -> str:
    if not values:
        return f"- {empty}\n"
    return "".join(f"- {value}\n" for value in values)


def _markdown_document(source: Path, root: Path, entry: dict[str, object], extraction: dict[str, object]) -> str:
    title = display_title(source)
    issues = entry.get("extraction_issues", [])
    issue_lines = "\n".join(f"- {issue}" for issue in issues) if issues else "- None."
    source_text = str(extraction.get("text", "")).strip()
    if not source_text:
        source_text = "_No extracted source text yet._"
    return (
        "---\n"
        f"document_id: {_yaml_string(entry['document_id'])}\n"
        f"source_path: {_yaml_string(entry['source_path'])}\n"
        f"sha256: {_yaml_string(entry['sha256'])}\n"
        f"processed_at: {_yaml_string(entry['processed_at'])}\n"
        f"content_type: {_yaml_string(entry['content_type'])}\n"
        f"text_strategy: {_yaml_string(entry['text_strategy'])}\n"
        f"extraction_status: {_yaml_string(entry['extraction_status'])}\n"
        "---\n\n"
        f"# {title}\n\n"
        "## Summary\n\n"
        "_Summary pending review._\n\n"
        "## Date Mentions\n\n"
        f"{_bullet_lines(_date_mentions(source_text), 'No date-like strings detected.')}\n"
        "## Extracted Entities\n\n"
        f"{_bullet_lines(_likely_entities(source_text), 'None identified yet.')}\n"
        "## Related Memory\n\n"
        "- [[Index|Library Index]]\n\n"
        "## Open Questions\n\n"
        "- What should this source be linked to?\n"
        "- Should any extracted dates become calendar events or reminders?\n\n"
        "## Extraction Notes\n\n"
        f"{issue_lines}\n\n"
        "## Source Notes\n\n"
        f"{source_text}\n"
    )


def _write_memory_document(source: Path, root: Path, entry: dict[str, object], extraction: dict[str, object]) -> None:
    memory_paths = entry.get("memory_paths", [])
    if not memory_paths:
        return
    target = root / str(memory_paths[0])
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(_markdown_document(source, root, entry, extraction), encoding="utf-8")


def _review_path(root: Path, now: str) -> Path:
    day = now[:10]
    return root / "Library" / "Reviews" / f"{day} Processing Review.md"


def _entry_lines(entries: list[dict[str, object]], empty: str) -> str:
    if not entries:
        return f"- {empty}\n"
    return "".join(f"- {entry.get('source_path', '')}\n" for entry in entries)


def _document_lines(entries: list[dict[str, object]]) -> str:
    rows: list[str] = []
    for entry in entries:
        for memory_path in entry.get("memory_paths", []):
            rows.append(f"- {memory_path}\n")
    return "".join(rows) if rows else "- No documents created or updated.\n"


def _ocr_lines(entries: list[dict[str, object]]) -> str:
    rows = [
        f"- {entry.get('source_path', '')}: {entry.get('extraction_status', '')}\n"
        for entry in entries
        if entry.get("content_type") == "application/pdf" or entry.get("extraction_status") == "needs_ocr_setup"
    ]
    return "".join(rows) if rows else "- No OCR issues reported.\n"


def _append_review(root: Path, processed: list[dict[str, object]], skipped: list[dict[str, object]], now: str) -> str:
    path = _review_path(root, now)
    path.parent.mkdir(parents=True, exist_ok=True)
    existing = path.read_text(encoding="utf-8") if path.exists() else "# Processing Review\n\n"
    entries = processed + skipped
    run = (
        f"## Run {now}\n\n"
        "## Processed Files\n\n"
        f"{_entry_lines(processed, 'No files processed.')}\n"
        "## Skipped Files\n\n"
        f"{_entry_lines(skipped, 'No files skipped.')}\n"
        "## Documents Created Or Updated\n\n"
        f"{_document_lines(processed)}\n"
        "## OCR Statuses\n\n"
        f"{_ocr_lines(entries)}\n"
        "## Low-Confidence Assumptions\n\n"
        "- Entity extraction and relationship linking are pending review.\n\n"
        "## Suggested Links And Actions\n\n"
        "- Review generated document memory and add links where useful.\n\n"
        "## Questions For Review\n\n"
        "- Which generated notes should be connected to existing memory?\n\n"
    )
    path.write_text(existing.rstrip() + "\n\n" + run, encoding="utf-8")
    return rel_path(path, root)


def process_library(root: Path) -> dict[str, object]:
    root = root.expanduser().resolve()
    setup_library(root)

    state_path = root / STATE_REL
    state = _load_state(state_path)
    files = state["files"]

    processed: list[dict[str, object]] = []
    skipped: list[dict[str, object]] = []
    now = _now()

    for source in _inbox_candidates(root):
        source_rel = rel_path(source, root)
        source_sha = _sha256(source)
        existing = files.get(source_rel)
        if isinstance(existing, dict) and existing.get("sha256") == source_sha:
            skipped.append(existing)
            continue

        extraction = extract_text(source, root)
        entry = _state_entry(source, root, source_sha, extraction)
        _write_memory_document(source, root, entry, extraction)
        files[source_rel] = entry
        processed.append(entry)

    state["updated"] = now
    review_path = _append_review(root, processed, skipped, now)
    _write_state(state_path, state)

    return {
        "library": str(root),
        "state_path": STATE_REL,
        "review_path": review_path,
        "processed": processed,
        "skipped": skipped,
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Process Inbox .txt, .md, and PDF sources into Notepad Librarian state.")
    parser.add_argument("folder", type=Path)
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args(argv)

    result = process_library(args.folder)
    if args.json:
        print(json.dumps(result, indent=2))
    else:
        print(f"processed: {len(result['processed'])} files")
        print(f"skipped: {len(result['skipped'])} files")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
