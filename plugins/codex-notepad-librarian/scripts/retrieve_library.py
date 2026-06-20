"""Build and query a lightweight retrieval index for Notepad libraries."""

from __future__ import annotations

import argparse
import json
from collections import Counter
from pathlib import Path

try:
    from .text_utils import display_title, rel_path, tokens
except ImportError:
    from text_utils import display_title, rel_path, tokens


def _library_txt_files(root: Path) -> list[Path]:
    library = root / "Library"
    if not library.exists():
        return []
    return sorted(
        path
        for path in library.rglob("*.txt")
        if path.is_file() and "Archive" not in path.relative_to(library).parts
    )


def build_retrieval_index(root: Path) -> dict[str, object]:
    root = root.expanduser().resolve()
    pages = []
    for path in _library_txt_files(root):
        text = path.read_text(encoding="utf-8")
        counts = Counter(tokens(text))
        pages.append(
            {
                "path": rel_path(path, root),
                "title": display_title(path),
                "token_count": sum(counts.values()),
                "top_terms": [term for term, _ in counts.most_common(12)],
            }
        )

    index = {"pages": pages}
    index_path = root / ".notepad-librarian" / "retrieval-index.json"
    index_path.parent.mkdir(parents=True, exist_ok=True)
    index_path.write_text(json.dumps(index, indent=2) + "\n", encoding="utf-8")
    return index


def _snippet(text: str, query_terms: set[str]) -> str:
    lines = [line.strip() for line in text.splitlines() if line.strip()]
    for line in lines:
        lower = line.lower()
        if any(term in lower for term in query_terms):
            return line[:240]
    return (lines[0] if lines else "")[:240]


def search_library(root: Path, query: str, *, limit: int = 5) -> list[dict[str, object]]:
    root = root.expanduser().resolve()
    query_terms = set(tokens(query))
    if not query_terms:
        return []

    results: list[dict[str, object]] = []
    for path in _library_txt_files(root):
        text = path.read_text(encoding="utf-8")
        title = display_title(path)
        body_counts = Counter(tokens(text))
        path_text = rel_path(path, root).lower()
        score = sum(body_counts[term] for term in query_terms)
        score += sum(20 for term in query_terms if term in title.lower())
        score += sum(10 for term in query_terms if term in path_text)
        if score <= 0:
            continue
        results.append(
            {
                "path": rel_path(path, root),
                "title": title,
                "score": score,
                "snippet": _snippet(text, query_terms),
            }
        )

    return sorted(results, key=lambda item: (-int(item["score"]), str(item["path"])))[:limit]


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Search a Notepad Librarian text library.")
    parser.add_argument("folder", type=Path)
    parser.add_argument("--query")
    parser.add_argument("--limit", type=int, default=5)
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args(argv)

    if args.query:
        result: object = search_library(args.folder, args.query, limit=args.limit)
    else:
        result = build_retrieval_index(args.folder)

    if args.json:
        print(json.dumps(result, indent=2))
    else:
        if isinstance(result, list):
            for item in result:
                print(f"{item['path']}: {item['snippet']}")
        else:
            print(f"indexed: {len(result['pages'])} pages")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
