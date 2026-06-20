# Codex Notepad Librarian

A Windows-first Codex plugin for people who want to write notes in Notepad and still have an organized, searchable personal library.

Write plain `.txt` notes. Save them in a folder. Ask Codex to organize them. The Librarian files notes, preserves originals, builds simple indexes, and helps you find what you wrote later.

No Obsidian. No special app. No database. Just text files.

## Simple Example

Create this file:

```text
C:\Users\Alex\Documents\NotepadLibrary\Inbox\lease note.txt
```

Write:

```text
Met with Sam about the office lease.
Rent review is due on 1/8/2026.
Need to check the lease terms before then.
```

Then ask Codex:

```text
Organize my Notepad notes in C:\Users\Alex\Documents\NotepadLibrary.
```

Codex can create:

```text
Library\Sources\lease-note.txt
Library\Archive\Originals\lease note.txt
Library\Index.txt
Library\Hot.txt
Library\Log.txt
```

Later ask:

```text
Find what I wrote about the office lease.
```

Codex searches the text library and answers with the relevant file path and snippet.

## Action Notes

You can leave instructions for the Librarian inside a note:

```text
NTL: make a calendar event for dinner with Cassy at Belvedere Hotel Prague on 27/1/2027
```

or:

```text
note to librarian: create a task to call the hotel on 27/1/2027
```

Codex scans these lines and proposes calendar, email, reminder, or task actions.

The Librarian can also notice date-like notes even without `NTL:`:

```text
27/1/2027 dinner with Cassy at Belvedere Hotel Prague
```

Codex should ask:

```text
Shall I create a calendar event for "dinner with Cassy at Belvedere Hotel Prague" on 27 January 2027?
```

By default, the plugin asks before creating anything outside the text library. You can enable automatic action mode for explicit `NTL:` lines, but inferred events always require confirmation.

## Installation

### 1. Install Codex

Install Codex using the current OpenAI instructions for your computer. Then check it works:

```powershell
codex --version
```

### 2. Download This Plugin

Open PowerShell in any folder where you want to download the plugin. Keep this folder after installation, because Codex will use it as the local plugin source.

```powershell
git clone https://github.com/vlasvar/codex-notepad-librarian.git
cd codex-notepad-librarian
```

### 3. Add The Plugin To Codex

Run this from inside the `codex-notepad-librarian` folder:

```powershell
codex plugin add codex-notepad-librarian@personal
```

Start a new Codex thread after installing so the skills load.

### 4. Set Up A Notes Folder

Ask Codex:

```text
Set up my Notepad library at C:\Users\Alex\Documents\NotepadLibrary.
```

Or run the helper directly:

```powershell
python scripts\setup_library.py C:\Users\Alex\Documents\NotepadLibrary --json
```

## Folder Layout

```text
NotepadLibrary\
  Inbox\
  Library\
    Sources\
    Ideas\
    People\
    Topics\
    Archive\
      Originals\
    Index.txt
    Hot.txt
    Log.txt
  .notepad-librarian\
    retrieval-index.json
    settings.json
```

Write rough notes in `Inbox\`. Codex organizes them into `Library\`.

## Useful Prompts

```text
Organize my Notepad notes in C:\Users\Alex\Documents\NotepadLibrary.
```

```text
Find what I wrote about lease terms in my Notepad library.
```

```text
Save this conversation to my Notepad library.
```

```text
Show me the most recent context from my Notepad library.
```

```text
Check my Notepad notes for actions.
```

## Helper Commands

```powershell
python scripts\setup_library.py C:\Users\Alex\Documents\NotepadLibrary --json
python scripts\organize_library.py C:\Users\Alex\Documents\NotepadLibrary --json
python scripts\retrieve_library.py C:\Users\Alex\Documents\NotepadLibrary --json
python scripts\retrieve_library.py C:\Users\Alex\Documents\NotepadLibrary --query "lease terms" --json
python scripts\scan_actions.py C:\Users\Alex\Documents\NotepadLibrary --json
python scripts\scan_actions.py C:\Users\Alex\Documents\NotepadLibrary --enable-auto-ntl --json
```

## Safety

- The plugin works on local `.txt` files.
- It does not automate live Notepad windows.
- It does not silently delete your notes.
- Originals are copied to `Library\Archive\Originals\` before Inbox/root copies are removed.
- Calendar, email, reminder, and task actions are confirmation-gated by default.
- Automatic action mode applies only to explicit `NTL:` or `note to librarian:` lines.
- Inferred actions, such as a dated dinner note, always require confirmation.
- Generated notes are drafts. Review important material before relying on it.
- This is not financial, legal, medical, travel, or professional advice.
- The plugin is not a backup system. Keep your own backups.

## Status

This public version supports setup, organizing saved `.txt` notes, preserving originals, indexing, text retrieval, and action proposal scanning for calendar, email, reminder, and task workflows.

## License

MIT License. See `LICENSE`.
