"""Deterministic text extraction boundary for Notepad Librarian sources."""

from __future__ import annotations

from pathlib import Path


TEXT_TYPES = {
    ".txt": "text/plain",
    ".md": "text/markdown",
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


def extract_text(path: Path) -> dict[str, object]:
    suffix = path.suffix.lower()

    if suffix in TEXT_TYPES:
        return _result(
            status="ok",
            content_type=TEXT_TYPES[suffix],
            text_strategy="direct_text",
            text=path.read_text(encoding="utf-8"),
        )

    if suffix == ".pdf":
        return _result(
            status="needs_ocr_setup",
            content_type="application/pdf",
            text_strategy="pdf_pending_ocr",
            issues=["PDF extraction/OCR is not configured yet."],
        )

    return _result(
        status="unsupported",
        content_type="application/octet-stream",
        text_strategy="unsupported",
        issues=[f"Unsupported source type: {suffix or 'no extension'}."],
    )
