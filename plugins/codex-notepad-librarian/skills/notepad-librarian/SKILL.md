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
  settings.json
```

All user-facing notes are plain `.txt` files. Do not create Markdown frontmatter, Obsidian wikilinks, `.obsidian/`, or `.canvas` files.

## Setup

When the user asks to set up a Notepad library, run:

```powershell
python scripts\setup_library.py <folder> --json
```

Then explain where to write notes: save rough `.txt` files in `Inbox\` or directly in the library root.

## Action Notes

Users can write explicit action requests with:

```text
NTL: make a calendar event for dinner with Cassy at Belvedere Hotel Prague on 27/1/2027
note to librarian: create a task to call the hotel on 27/1/2027
```

Run:

```powershell
python scripts\scan_actions.py <folder> --json
```

Default behavior asks before any outward action. If `.notepad-librarian\settings.json` has `auto_act_on_ntl: true`, explicit `NTL:` actions may be acted on without another confirmation. Inferred actions, such as a dated dinner note without `NTL:`, always require confirmation.

## Safety

- Never silently delete user content.
- Preserve original notes in `Library\Archive\Originals\` before removing an Inbox/root copy.
- Skip `Library\Archive\Originals\` and `.notepad-librarian\`.
- Ask before inferred calendar, email, reminder, or task actions.
- Keep output readable in Notepad.
- Use fake paths in public examples, such as `C:\Users\Alex\Documents\NotepadLibrary`.
