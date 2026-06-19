---
name: notepad-find
description: Use when the user asks what they wrote about a topic, wants to find notes, search a Notepad library, or retrieve relevant plain .txt notes.
---

# Notepad Find

Search the user's plain-text Notepad Librarian library and answer with file paths and snippets.

## Workflow

1. Resolve the library folder.
2. Refresh the retrieval index:

```powershell
python scripts\retrieve_library.py <folder> --json
```

3. Search with the user's topic:

```powershell
python scripts\retrieve_library.py <folder> --query "<topic>" --json
```

4. Read the most relevant returned files before answering when synthesis is needed.
5. Answer with:
   - exact `.txt` file path
   - short quote or snippet
   - a plain-language summary

## Rules

- Separate text-supported facts from inference.
- If the library lacks evidence, say what is missing.
- Keep references as normal file paths that make sense in Notepad and File Explorer.
