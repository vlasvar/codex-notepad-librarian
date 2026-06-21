---
name: notepad-find
description: Use when the user asks what they wrote about a topic, wants to find notes, search a Notepad library, or retrieve relevant .txt and Markdown memory notes.
---

# Notepad Find

Search the user's Notepad Librarian library and answer with file paths and snippets from classic `.txt` notes and generated Markdown document memory.

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
   - exact `.txt` or `.md` file path
   - short quote or snippet
   - a plain-language summary

## Rules

- Separate text-supported facts from inference.
- If the library lacks evidence, say what is missing.
- Keep references as normal file paths that make sense in Notepad and File Explorer.
- Markdown memory files are portable; do not assume Obsidian is installed.
