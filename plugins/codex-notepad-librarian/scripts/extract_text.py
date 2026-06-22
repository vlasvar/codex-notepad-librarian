"""Deterministic text extraction boundary for Notepad Librarian sources."""

from __future__ import annotations

import json
import os
import shutil
import subprocess
import tempfile
from pathlib import Path


TEXT_TYPES = {
    ".txt": "text/plain",
    ".md": "text/markdown",
}

DEFAULT_OCR = {
    "tesseract_path": "",
    "tessdata_dir": "",
    "languages": ["ell", "eng"],
}


def _result(
    *,
    status: str,
    content_type: str,
    text_strategy: str,
    text: str = "",
    issues: list[str] | None = None,
) -> dict[str, object]:
    return {
        "status": status,
        "content_type": content_type,
        "text_strategy": text_strategy,
        "text": text,
        "issues": issues or [],
    }


def _read_settings(root: Path | None) -> dict[str, object]:
    if root is None:
        return {}
    settings_path = root / ".notepad-librarian" / "settings.json"
    if not settings_path.exists():
        return {}
    data = json.loads(settings_path.read_text(encoding="utf-8-sig"))
    return data if isinstance(data, dict) else {}


def _ocr_settings(root: Path | None) -> dict[str, object]:
    settings = _read_settings(root)
    raw = settings.get("ocr")
    merged = DEFAULT_OCR.copy()
    if isinstance(raw, dict):
        merged.update(raw)
    languages = merged.get("languages")
    if not isinstance(languages, list) or not all(isinstance(item, str) for item in languages):
        merged["languages"] = list(DEFAULT_OCR["languages"])
    return merged


def _candidate_tesseract_paths(configured: object) -> list[Path]:
    candidates: list[Path] = []
    if isinstance(configured, str) and configured.strip():
        candidates.append(Path(configured).expanduser())
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


def _find_tesseract(configured: object) -> Path | None:
    for candidate in _candidate_tesseract_paths(configured):
        if candidate.is_file():
            return candidate
    return None


def _candidate_tessdata_dirs(configured: object, tesseract: Path | None) -> list[Path]:
    candidates: list[Path] = []
    if isinstance(configured, str) and configured.strip():
        candidates.append(Path(configured).expanduser())
    if "TESSDATA_PREFIX" in os.environ:
        candidates.append(Path(os.environ["TESSDATA_PREFIX"]).expanduser())
    if tesseract:
        candidates.append(tesseract.parent / "tessdata")
    for base in (os.environ.get("ProgramFiles"), os.environ.get("ProgramFiles(x86)")):
        if base:
            candidates.append(Path(base) / "Tesseract-OCR" / "tessdata")
    unique: list[Path] = []
    for candidate in candidates:
        if candidate not in unique:
            unique.append(candidate)
    return unique


def _find_tessdata(configured: object, tesseract: Path | None) -> Path | None:
    for candidate in _candidate_tessdata_dirs(configured, tesseract):
        if candidate.is_dir():
            return candidate
    return None


def _available_languages(tessdata_dir: Path | None) -> set[str]:
    if not tessdata_dir:
        return set()
    return {path.stem for path in tessdata_dir.glob("*.traineddata") if path.is_file()}


def _extract_pdf_text_layer(path: Path) -> tuple[str, list[str]]:
    issues: list[str] = []
    for module_name in ("pypdf", "PyPDF2"):
        try:
            module = __import__(module_name)
            reader = module.PdfReader(str(path))
            pages = [page.extract_text() or "" for page in reader.pages]
            text = "\n\n".join(page.strip() for page in pages if page.strip()).strip()
            if text:
                return text + "\n", []
        except ModuleNotFoundError:
            continue
        except Exception as exc:
            issues.append(f"PDF text-layer extraction with {module_name} failed: {exc}")
            break
    if not issues:
        issues.append("No PDF text-layer library is installed; install pypdf for searchable PDFs.")
    return "", issues


def _render_pdf_with_pymupdf(path: Path, output_dir: Path) -> tuple[list[Path], list[str]]:
    try:
        import fitz  # type: ignore
    except ModuleNotFoundError:
        return [], ["PyMuPDF is not installed; install pymupdf to render scanned PDFs for OCR."]
    except Exception as exc:
        return [], [f"PyMuPDF import failed: {exc}"]

    images: list[Path] = []
    try:
        document = fitz.open(str(path))
        for index, page in enumerate(document, start=1):
            pixmap = page.get_pixmap(dpi=300)
            image_path = output_dir / f"page-{index:04d}.png"
            pixmap.save(str(image_path))
            images.append(image_path)
    except Exception as exc:
        return [], [f"PDF rendering for OCR failed: {exc}"]
    return images, []


def _ocr_pdf(path: Path, root: Path | None) -> dict[str, object]:
    settings = _ocr_settings(root)
    tesseract = _find_tesseract(settings.get("tesseract_path"))
    tessdata = _find_tessdata(settings.get("tessdata_dir"), tesseract)
    languages = list(settings["languages"])
    available = _available_languages(tessdata)
    missing = sorted(language for language in languages if language not in available)

    issues: list[str] = []
    if not tesseract:
        issues.append("Tesseract was not found. Install Tesseract or configure ocr.tesseract_path in settings.json.")
    if not tessdata:
        issues.append("Tesseract language data was not found. Configure ocr.tessdata_dir in settings.json.")
    if tesseract and tessdata and missing:
        issues.append(f"Missing Tesseract language data: {', '.join(missing)}.")
    if issues:
        return _result(
            status="needs_ocr_setup",
            content_type="application/pdf",
            text_strategy="pdf_ocr_pending_setup",
            issues=issues,
        )

    with tempfile.TemporaryDirectory() as tmp:
        images, render_issues = _render_pdf_with_pymupdf(path, Path(tmp))
        if render_issues:
            return _result(
                status="needs_ocr_setup",
                content_type="application/pdf",
                text_strategy="pdf_ocr_pending_renderer",
                issues=render_issues,
            )
        texts: list[str] = []
        env = os.environ.copy()
        env["TESSDATA_PREFIX"] = str(tessdata)
        language_arg = "+".join(languages)
        for image in images:
            completed = subprocess.run(
                [str(tesseract), str(image), "stdout", "-l", language_arg],
                check=False,
                capture_output=True,
                text=True,
                encoding="utf-8",
                errors="replace",
                env=env,
            )
            if completed.returncode != 0:
                return _result(
                    status="ocr_failed",
                    content_type="application/pdf",
                    text_strategy="pdf_ocr_tesseract",
                    issues=[completed.stderr.strip() or "Tesseract OCR failed."],
                )
            texts.append(completed.stdout.strip())
        text = "\n\n".join(chunk for chunk in texts if chunk).strip()
        return _result(
            status="ok" if text else "empty",
            content_type="application/pdf",
            text_strategy="pdf_ocr_tesseract",
            text=(text + "\n") if text else "",
            issues=[] if text else ["OCR completed but no text was detected."],
        )


def _extract_pdf(path: Path, root: Path | None) -> dict[str, object]:
    text, text_issues = _extract_pdf_text_layer(path)
    if text.strip():
        return _result(
            status="ok",
            content_type="application/pdf",
            text_strategy="pdf_text_layer",
            text=text,
        )
    ocr = _ocr_pdf(path, root)
    if text_issues and ocr["issues"]:
        ocr["issues"] = text_issues + list(ocr["issues"])
    return ocr


def extract_text(path: Path, root: Path | None = None) -> dict[str, object]:
    suffix = path.suffix.lower()

    if suffix in TEXT_TYPES:
        return _result(
            status="ok",
            content_type=TEXT_TYPES[suffix],
            text_strategy="direct_text",
            text=path.read_text(encoding="utf-8"),
        )

    if suffix == ".pdf":
        return _extract_pdf(path, root)

    return _result(
        status="unsupported",
        content_type="application/octet-stream",
        text_strategy="unsupported",
        issues=[f"Unsupported source type: {suffix or 'no extension'}."],
    )
