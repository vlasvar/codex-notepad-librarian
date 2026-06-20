---
name: notepad-organize
description: Use when the user says organize, tidy, file, clean up, or maintain my Notepad notes or plain .txt library.
---

# Notepad Organize

Organize saved `.txt` notes into the Notepad Librarian library.

## Workflow

1. Resolve the library folder.
2. Run setup first so missing folders exist:

```powershell
python scripts\setup_library.py <folder> --json
```

3. Run the organizer:

```powershell
python scripts\organize_library.py <folder> --json
```

4. Report a short summary:
   - notes created
   - originals archived
   - notes skipped
   - updated `Library\Index.txt`, `Library\Hot.txt`, and `Library\Log.txt`
5. Scan for possible actions:

```powershell
python scripts\scan_actions.py <folder> --json
```

Report proposed actions after the organization summary. Ask before acting on inferred actions. Follow `requires_confirmation` for explicit `NTL:` actions.

## Rules

- Scan `Inbox\` and loose root `.txt` files.
- Skip `Library\Archive\Originals\` and `.notepad-librarian\`.
- Keep files as `.txt`.
- Do not create Obsidian files or Markdown-only syntax.
