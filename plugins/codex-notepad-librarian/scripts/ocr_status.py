"""Report OCR configuration health for Notepad Librarian."""

from __future__ import annotations

import argparse
import json
import os
import shutil
from pathlib import Path

try:
    from .process_library import STATE_REL
    from .setup_library import setup_library
except ImportError:
    from process_library import STATE_REL
    from setup_library import setup_library


DEFAULT_OCR = {
    "tesseract_path": "",
    "tessdata_dir": "",
    "languages": ["ell", "eng"],
}


def _read_json(path: Path, default: dict[str, object]) -> dict[str, object]:
    if not path.exists():
        return default.copy()
    data = json.loads(path.read_text(encoding="utf-8"))
    return data if isinstance(data, dict) else default.copy()


def _ocr_settings(settings: dict[str, object]) -> dict[str, object]:
    raw = settings.get("ocr")
    merged = DEFAULT_OCR.copy()
    if isinstance(raw, dict):
        merged.update(raw)
    languages = merged.get("languages")
    if not isinstance(languages, list) or not all(isinstance(item, str) for item in languages):
        merged["languages"] = ["eng"]
    return merged


def _candidate_tesseract_paths(value: object) -> list[Path]:
    candidates: list[Path] = []
    if isinstance(value, str) and value.strip():
        candidates.append(Path(value).expanduser())
    found = shutil.which("tesseract")
    if found:
        candidates.append(Path(found))
    for base in (os.environ.get("ProgramFiles"), os.environ.get("ProgramFiles(x86)")):
        if base:
            candidates.append(Path(base) / "Tesseract-OCR" / "tesseract.exe")
    unique: list[Path] = []
    for candidate in candidates:
        if candidate not in unique:
            unique.append(candidate)
    return unique


def _candidate_tessdata_dirs(value: object, tesseract_path: Path | None) -> list[Path]:
    candidates: list[Path] = []
    if isinstance(value, str) and value.strip():
        candidates.append(Path(value).expanduser())
    if "TESSDATA_PREFIX" in os.environ:
        candidates.append(Path(os.environ["TESSDATA_PREFIX"]).expanduser())
    if tesseract_path:
        candidates.append(tesseract_path.parent / "tessdata")
    for base in (os.environ.get("ProgramFiles"), os.environ.get("ProgramFiles(x86)")):
        if base:
            candidates.append(Path(base) / "Tesseract-OCR" / "tessdata")
    unique: list[Path] = []
    for candidate in candidates:
        if candidate not in unique:
            unique.append(candidate)
    return unique


def _path_status(value: object, candidates: list[Path] | None = None) -> dict[str, object]:
    configured = isinstance(value, str) and bool(value.strip())
    checked = candidates or ([Path(value).expanduser()] if configured else [])
    found = next((path for path in checked if path.exists()), None)
    path = found or (Path(value).expanduser() if configured else None)
    return {
        "path": str(path) if path else "",
        "configured": configured,
        "found": bool(found),
        "auto_discovered": bool(found and not configured),
        "checked": [str(candidate) for candidate in checked],
    }


def _available_languages(tessdata_dir: Path | None) -> list[str]:
    if not tessdata_dir or not tessdata_dir.is_dir():
        return []
    return sorted(path.stem for path in tessdata_dir.glob("*.traineddata") if path.is_file())


def _queued_files(root: Path) -> list[dict[str, object]]:
    state = _read_json(root / STATE_REL, {"files": {}})
    files = state.get("files")
    if not isinstance(files, dict):
        return []
    queued: list[dict[str, object]] = []
    for entry in files.values():
        if isinstance(entry, dict) and entry.get("extraction_status") == "needs_ocr_setup":
            queued.append(
                {
                    "source_path": entry.get("source_path", ""),
                    "content_type": entry.get("content_type", ""),
                    "text_strategy": entry.get("text_strategy", ""),
                    "issues": entry.get("extraction_issues", []),
                }
            )
    return sorted(queued, key=lambda item: str(item["source_path"]))


def ocr_status(root: Path) -> dict[str, object]:
    root = root.expanduser().resolve()
    setup_library(root)

    settings = _read_json(root / ".notepad-librarian" / "settings.json", {})
    ocr = _ocr_settings(settings)
    tesseract_candidates = _candidate_tesseract_paths(ocr.get("tesseract_path"))
    tesseract = _path_status(ocr.get("tesseract_path"), tesseract_candidates)
    tesseract_path = Path(tesseract["path"]) if tesseract["found"] else None
    tessdata_candidates = _candidate_tessdata_dirs(ocr.get("tessdata_dir"), tesseract_path)
    tessdata = _path_status(ocr.get("tessdata_dir"), tessdata_candidates)
    tessdata_path = Path(tessdata["path"]) if tessdata["found"] else None
    configured_languages = list(ocr["languages"])
    available_languages = _available_languages(tessdata_path)
    missing_languages = sorted(language for language in configured_languages if language not in available_languages)

    repair_hints: list[str] = []
    if not tesseract["found"]:
        repair_hints.append("Install Tesseract or configure ocr.tesseract_path in settings.json.")
    if not tessdata["found"]:
        repair_hints.append("Configure ocr.tessdata_dir in settings.json.")
    if tesseract["found"] and tessdata["found"] and missing_languages:
        repair_hints.append(f"Install tessdata for missing languages: {', '.join(missing_languages)}.")

    if not tesseract["found"]:
        status = "missing_tesseract"
    elif not tessdata["found"]:
        status = "missing_tessdata"
    elif missing_languages:
        status = "missing_languages"
    else:
        status = "ready"

    return {
        "library": str(root),
        "status": status,
        "tesseract": tesseract,
        "tessdata": tessdata,
        "languages": {
            "configured": configured_languages,
            "available": available_languages,
            "missing": missing_languages,
        },
        "queued_files": _queued_files(root),
        "repair_hints": repair_hints,
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Report Notepad Librarian OCR configuration status.")
    parser.add_argument("folder", type=Path)
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args(argv)

    result = ocr_status(args.folder)
    if args.json:
        print(json.dumps(result, indent=2))
    else:
        print(f"ocr status: {result['status']}")
        for hint in result["repair_hints"]:
            print(f"- {hint}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
