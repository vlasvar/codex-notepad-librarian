"""Shared plain-text helpers."""

from __future__ import annotations

import re
from pathlib import Path


SLUG_RE = re.compile(r"[^a-z0-9]+")
TOKEN_RE = re.compile(r"[A-Za-z0-9]+")


def slugify(value: str, *, fallback: str = "note") -> str:
    slug = SLUG_RE.sub("-", value.lower()).strip("-")
    return slug or fallback


def display_title(path: Path) -> str:
    return path.stem.replace("-", " ").replace("_", " ").strip().title() or "Untitled"


def tokens(text: str) -> list[str]:
    return [token.lower() for token in TOKEN_RE.findall(text)]


def rel_path(path: Path, root: Path) -> str:
    return path.relative_to(root).as_posix()
