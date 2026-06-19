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

## Installation

### 1. Install Codex

Install Codex using the current OpenAI instructions for your computer. Then check it works:

```powershell
codex --version
```

### 2. Download This Plugin

Open PowerShell in a folder where you keep projects:

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

## Helper Commands

```powershell
python scripts\setup_library.py C:\Users\Alex\Documents\NotepadLibrary --json
python scripts\organize_library.py C:\Users\Alex\Documents\NotepadLibrary --json
python scripts\retrieve_library.py C:\Users\Alex\Documents\NotepadLibrary --json
python scripts\retrieve_library.py C:\Users\Alex\Documents\NotepadLibrary --query "lease terms" --json
```

## Safety

- The plugin works on local `.txt` files.
- It does not automate live Notepad windows.
- It does not silently delete your notes.
- Originals are copied to `Library\Archive\Originals\` before Inbox/root copies are removed.
- Generated notes are drafts. Review important material before relying on it.
- This is not financial, legal, medical, travel, or professional advice.
- The plugin is not a backup system. Keep your own backups.

## Status

This is the first public bootstrap version. It supports setup, organizing saved `.txt` notes, preserving originals, indexing, and text retrieval. Calendar, reminder, email, and task directives are intentionally deferred until the base workflow is stable.

## License

MIT License. See `LICENSE`.
