---
name: notepad-librarian
description: Use when the user wants to set up or maintain a Windows-first Notepad note library and local Markdown memory loop with Codex.
---

# Notepad Librarian

Help users write simple notes in Windows Notepad or plain folders while Codex maintains a local, searchable memory library.

The user edits saved files with Notepad. Do not automate live Notepad windows. Work on files in the selected folder.

## Library Shape

Use this folder layout:

```text
Inbox/
Library/
  Documents/
  Reviews/
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
  processed-files.json
  action-state.json
  retrieval-index.json
  settings.json
```

Inbox sources can be `.txt`, `.md`, or PDF files that may need OCR setup. Generated document memory lives in portable Markdown under `Library\Documents\`, and dated processing reviews live under `Library\Reviews\`. Keep the library Obsidian-compatible, but do not require Obsidian, `.obsidian/`, community plugins, or `.canvas` files.

## Setup

When the user asks to set up a Notepad library, run:

```powershell
python scripts\setup_library.py <folder> --json
```

Then explain where to write notes: save rough `.txt` files in `Inbox\` or directly in the library root.

To run the memory loop for Inbox sources:

```powershell
python scripts\process_library.py <folder> --json
```

To inspect OCR readiness for scanned PDFs:

```powershell
python scripts\ocr_status.py <folder> --json
```

PDF extraction first tries a searchable text layer. For scanned PDFs, OCR can run when Tesseract, a PDF renderer, and configured language data are available. Missing OCR setup must be reported without failing the whole processing loop.

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

Future calendar events are auto-create eligible by default, and past calendar events are ignored based on the current date. Use the action runner to avoid duplicates:

```powershell
python scripts\run_actions.py <folder> --json
python scripts\run_actions.py <folder> --record-created <action_id> --external-id <event_id> --json
```

If `.notepad-librarian\settings.json` has `auto_act_on_ntl: true`, explicit non-calendar `NTL:` actions may also be acted on without another confirmation. Otherwise, ask before non-calendar outward actions.

## Safety

- Never silently delete user content.
- Preserve original notes in `Library\Archive\Originals\` before removing an Inbox/root copy.
- Skip `Library\Archive\Originals\` and `.notepad-librarian\`.
- Create future calendar events when the action runner marks them ready, then record the created action.
- Ask before email, reminder, task, document, spreadsheet, PDF, or presentation actions unless automatic explicit action mode allows them.
- Keep output readable in Notepad.
- Treat OCR as optional setup: report missing Tesseract or language data, but do not fail the whole processing loop.
- Use fake paths in public examples, such as `C:\Users\Alex\Documents\NotepadLibrary`.
