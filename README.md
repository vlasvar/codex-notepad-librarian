# Codex Notepad Librarian

<img width="1248" height="832" alt="bhSIE" src="https://github.com/user-attachments/assets/11adee67-6047-42e1-9c87-20fe8b2cd456" />

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

`NTL:` is the cleanest command, but the Librarian also understands close forms like `note to librarian:`, `note to librari:`, and `not to librari:`.

It can recognize simple Greek and Greeklish action language too, such as appointment, coffee, email, Word document, and Google Sheet requests.

Codex scans these lines and proposes calendar, email, reminder, task, Word document, spreadsheet, PDF, or presentation actions.

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

### 1. Install Codex CLI

Open PowerShell and check if Codex is already installed:

```powershell
codex --version
```

If you see a version number, you already have it.

If PowerShell says `codex` is not recognized, install Codex CLI:

```powershell
powershell -ExecutionPolicy ByPass -c "irm https://chatgpt.com/codex/install.ps1 | iex"
```

Close PowerShell, open it again, and check:

```powershell
codex --version
```

### 2. Download This Plugin

Open PowerShell in any folder where you want to download the plugin. Keep this folder after installation, because Codex will use it as the local plugin source.

```powershell
git clone https://github.com/vlasvar/codex-notepad-librarian.git
cd codex-notepad-librarian
```

### 3A. Automatic Setup

Run this from inside the `codex-notepad-librarian` folder:

```powershell
.\install.ps1
```

This will:

- create a notes folder in your Documents folder, like `C:\Users\Alex\Documents\NotepadLibrary`
- create the `Inbox`, `Library`, and index files
- add this plugin as a local Codex marketplace
- install the plugin into Codex

Start a new Codex thread after installing so the plugin skills load.

To use a different notes folder:

```powershell
.\install.ps1 -LibraryPath C:\Users\Alex\Documents\MyNotes
```

### 3B. Manual Setup

Use these steps if you want to do everything yourself.

Run this from the folder that contains `codex-notepad-librarian`:

```powershell
cd C:\Users\Alex\Documents
codex plugin marketplace add .\codex-notepad-librarian
```

Then install the plugin from that marketplace:

```powershell
codex plugin add codex-notepad-librarian@codex-notepad-librarian
```

Create your notes folder:

```powershell
mkdir C:\Users\Alex\Documents\NotepadLibrary
```

Start a new Codex thread and ask:

```text
Set up my Notepad library at C:\Users\Alex\Documents\NotepadLibrary.
```

Or run the helper directly:

```powershell
python plugins\codex-notepad-librarian\scripts\setup_library.py C:\Users\Alex\Documents\NotepadLibrary --json
```

Start a new Codex thread after installing so the plugin skills load.


## Updating

This plugin is installed from a local folder. After downloading new changes, reinstall it so Codex refreshes its cached copy:

```powershell
cd C:\Users\Alex\Documents\codex-notepad-librarian
git pull
.\install.ps1
```

Then start a new Codex thread so the updated skills load.

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
python plugins\codex-notepad-librarian\scripts\setup_library.py C:\Users\Alex\Documents\NotepadLibrary --json
python plugins\codex-notepad-librarian\scripts\organize_library.py C:\Users\Alex\Documents\NotepadLibrary --json
python plugins\codex-notepad-librarian\scripts\retrieve_library.py C:\Users\Alex\Documents\NotepadLibrary --json
python plugins\codex-notepad-librarian\scripts\retrieve_library.py C:\Users\Alex\Documents\NotepadLibrary --query "lease terms" --json
python plugins\codex-notepad-librarian\scripts\scan_actions.py C:\Users\Alex\Documents\NotepadLibrary --json
python plugins\codex-notepad-librarian\scripts\scan_actions.py C:\Users\Alex\Documents\NotepadLibrary --enable-auto-ntl --json
```

## Safety

- The plugin works on local `.txt` files.
- It does not automate live Notepad windows.
- It does not silently delete your notes.
- Originals are copied to `Library\Archive\Originals\` before Inbox/root copies are removed.
- Calendar, email, reminder, task, document, spreadsheet, PDF, and presentation actions are confirmation-gated by default.
- Automatic action mode applies only to explicit `NTL:` or `note to librarian:` lines.
- Inferred actions, such as a dated dinner note, always require confirmation.
- Generated notes are drafts. Review important material before relying on it.
- This is not financial, legal, medical, travel, or professional advice.
- The plugin is not a backup system. Keep your own backups.

## Status

This public version supports setup, organizing saved `.txt` notes, preserving originals, indexing, text retrieval, and action proposal scanning for calendar, email, reminder, task, document, spreadsheet, PDF, and presentation workflows.

## License

MIT License. See `LICENSE`.
