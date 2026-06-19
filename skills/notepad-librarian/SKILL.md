---
name: notepad-librarian
description: Use when the user wants to set up or maintain a Windows-first plain-text Notepad note library with Codex.
---

# Notepad Librarian

Help users write simple `.txt` notes in Windows Notepad while Codex maintains a local, searchable text library.

The user edits saved files with Notepad. Do not automate live Notepad windows. Work on files in the selected folder.

## Library Shape

Use this folder layout:

```text
Inbox/
Library/
  Sources/
  Ideas/
  People/
  Topics/
  Archive/
    Originals/
  Index.txt
  Hot.txt
  Log.txt
.notepad-librarian/
  retrieval-index.json
```

All user-facing notes are plain `.txt` files. Do not create Markdown frontmatter, Obsidian wikilinks, `.obsidian/`, or `.canvas` files.

## Setup

When the user asks to set up a Notepad library, run:

```powershell
python scripts\setup_library.py <folder> --json
```

Then explain where to write notes: save rough `.txt` files in `Inbox\` or directly in the library root.

## Safety

- Never silently delete user content.
- Preserve original notes in `Library\Archive\Originals\` before removing an Inbox/root copy.
- Skip `Library\Archive\Originals\` and `.notepad-librarian\`.
- Keep output readable in Notepad.
- Use fake paths in public examples, such as `C:\Users\Alex\Documents\NotepadLibrary`.
