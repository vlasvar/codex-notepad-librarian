---
name: notepad-organize
description: Use when the user says organize, tidy, file, clean up, process, or maintain my Notepad notes or local memory library.
---

# Notepad Organize

Organize saved `.txt` notes into the classic Notepad Librarian library, or process Inbox `.txt`, `.md`, and PDF sources into Markdown document memory.

## Workflow

1. Resolve the library folder.
2. Run setup first so missing folders exist:

```powershell
python scripts\setup_library.py <folder> --json
```

3. For the classic `.txt` organizer, run:

```powershell
python scripts\organize_library.py <folder> --json
```

4. For the memory loop, run:

```powershell
python scripts\process_library.py <folder> --json
```

5. Report a short summary:
   - notes created
   - originals archived
   - notes skipped
   - updated `Library\Index.txt`, `Library\Hot.txt`, and `Library\Log.txt`
   - processed and skipped Inbox sources
   - generated `Library\Documents\*.md`
   - dated `Library\Reviews\* Processing Review.md`
6. Scan for possible actions:

```powershell
python scripts\scan_actions.py <folder> --json
```

Report proposed actions after the organization summary. Ask before acting on inferred actions. Follow `requires_confirmation` for explicit `NTL:` actions.

## Rules

- Scan `Inbox\` and loose root `.txt` files for classic organization.
- Scan `Inbox\` `.txt`, `.md`, and PDF files for the memory loop.
- Skip `Library\Archive\Originals\` and `.notepad-librarian\`.
- Keep classic organized files as `.txt`.
- Generated memory files may use portable Markdown with frontmatter and wikilinks, but do not require Obsidian.
