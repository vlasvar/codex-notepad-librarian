# Codex Notepad Librarian

<img width="1248" height="832" alt="bhSIE" src="https://github.com/user-attachments/assets/11adee67-6047-42e1-9c87-20fe8b2cd456" />

A Windows-first Codex plugin for people who want to write notes in Notepad or plain folders and still have an organized, searchable local memory library.

Write plain `.txt` or `.md` notes. Save them in a folder. Ask Codex to organize or process them. The Librarian can still file classic `.txt` notes, and it can also process Inbox sources into portable Markdown document memory, dated review notes, OCR setup reports, simple indexes, and searchable snippets.

No required Obsidian. No special app. No database. Just local files.

## What's New

- Future calendar events found in explicit `NTL:` notes can be prepared for creation without another approval prompt.
- Past calendar events are ignored automatically based on the run date, so old notes do not create stale events.
- Action state is stored in `.notepad-librarian\action-state.json` to avoid duplicate event creation on later runs.
- PDF handling now tries searchable PDF text first, then Tesseract OCR for scanned PDFs when OCR tools are available.
- OCR setup reports can auto-detect common Windows Tesseract installs and check for Greek (`ell`) and English (`eng`) language data.
- Generated Markdown memory now includes detected date mentions and lightweight entity candidates to make review faster.

## 🇬🇷 Ελληνικά / Greek Users

Υπάρχει απλός ελληνικός οδηγός χρήσης εδώ: [README.el.md](README.el.md).

Αν γράφετε σημειώσεις στα ελληνικά ή greeklish, μπορείτε να χρησιμοποιήσετε το ίδιο installation flow. Το plugin δουλεύει με τοπικά αρχεία, δημιουργεί searchable Markdown memory files, και κρατά τις εξωτερικές ενέργειες confirmation-first.

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
Library\Documents\lease-note-<hash>.md
Library\Reviews\2026-06-21 Processing Review.md
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

For PDFs, the Librarian first tries to extract an existing searchable text layer. If the PDF is scanned, it can use Tesseract OCR when the local machine has Tesseract, a PDF renderer, and the configured language data.

## PDFs And OCR

You can put PDF files in `Inbox\` too. The Librarian treats PDFs conservatively: it records OCR setup issues and keeps processing your normal notes instead of failing the whole run.

The plugin does not need Tesseract to process normal `.txt` or `.md` notes.

When you are ready to work with scanned PDFs, ask Codex:

```text
Add Tesseract configuration to my Notepad library.
```

Codex can then help you install or point to Tesseract, set the `tesseract_path`, set the `tessdata_dir`, and choose OCR languages in `.notepad-librarian\settings.json`. New libraries default to Greek and English OCR:

```json
{
  "ocr": {
    "languages": ["ell", "eng"]
  }
}
```

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

Future calendar events are auto-allowed by default. Past events are ignored, and the action runner records created events in `.notepad-librarian\action-state.json` so the same note does not create duplicate calendar entries on the next run.

The Librarian can also notice date-like notes even without `NTL:`:

```text
27/1/2027 dinner with Cassy at Belvedere Hotel Prague
```

Codex should ask:

```text
Shall I create a calendar event for "dinner with Cassy at Belvedere Hotel Prague" on 27 January 2027?
```

Calendar events are prepared for creation without another approval prompt. Non-calendar outward actions can still use the safer approval flow unless you explicitly enable broader automatic action mode for `NTL:` lines.

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
- create folders for Markdown document memory and processing reviews
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
    Documents\
    Reviews\
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
    processed-files.json
    retrieval-index.json
    settings.json
```

Write rough notes in `Inbox\`. Codex can organize classic `.txt` notes into `Library\Sources\`, or process `.txt`, `.md`, and OCR-pending PDFs into `Library\Documents\` and `Library\Reviews\`.

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
python plugins\codex-notepad-librarian\scripts\process_library.py C:\Users\Alex\Documents\NotepadLibrary --json
python plugins\codex-notepad-librarian\scripts\ocr_status.py C:\Users\Alex\Documents\NotepadLibrary --json
python plugins\codex-notepad-librarian\scripts\retrieve_library.py C:\Users\Alex\Documents\NotepadLibrary --json
python plugins\codex-notepad-librarian\scripts\retrieve_library.py C:\Users\Alex\Documents\NotepadLibrary --query "lease terms" --json
python plugins\codex-notepad-librarian\scripts\scan_actions.py C:\Users\Alex\Documents\NotepadLibrary --json
python plugins\codex-notepad-librarian\scripts\run_actions.py C:\Users\Alex\Documents\NotepadLibrary --json
python plugins\codex-notepad-librarian\scripts\scan_actions.py C:\Users\Alex\Documents\NotepadLibrary --enable-auto-ntl --json
```

## Safety

- The plugin works on local `.txt`, `.md`, and OCR-pending PDF files.
- It does not automate live Notepad windows.
- It does not silently delete your notes.
- Originals are copied to `Library\Archive\Originals\` before Inbox/root copies are removed.
- Processing state is stored in `.notepad-librarian\processed-files.json` so unchanged Inbox files can be skipped.
- Missing Tesseract or language data is reported as OCR setup work; it is not a hard requirement for the processing loop.
- Future calendar events are auto-allowed by default and tracked in action state to prevent duplicates.
- Past calendar events are ignored based on the current run date.
- Automatic action mode for other action types applies only to explicit `NTL:` or `note to librarian:` lines.
- Generated notes are drafts. Review important material before relying on it.
- This is not financial, legal, medical, travel, or professional advice.
- The plugin is not a backup system. Keep your own backups.

## Status

This public version supports setup, organizing saved `.txt` notes, processing Inbox `.txt`/`.md`/PDF sources, generating portable Markdown document memory and dated review notes, indexing `.txt` and Markdown memory files, OCR setup reporting and OCR attempts when tools are available, text retrieval, action proposal scanning, and idempotent future calendar-event preparation.

## License

MIT License. See `LICENSE`.
