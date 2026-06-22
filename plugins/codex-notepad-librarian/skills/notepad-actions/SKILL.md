---
name: notepad-actions
description: Use when the user asks to act on Notepad notes, scan NTL directives, create calendar events, reminders, emails, tasks, Word documents, PDFs, presentations, or spreadsheets from local notes, or identify dated events in notes.
---

# Notepad Actions

Scan a Notepad Librarian folder for explicit action directives and inferred dated events. Future calendar events are auto-create eligible by default; past calendar events are ignored based on the current run date. Other outward action types remain approval-first unless automatic explicit `NTL:` mode is enabled.

## Directive Forms

Explicit directives:

```text
NTL: make a calendar event for dinner with Cassy at Belvedere Hotel Prague on 27/1/2027
note to librarian: create a task to call the hotel on 27/1/2027
not to librari: remind me to check the contract on 21/2/2026
NTL: make a google sheet out of this note
```

`NTL:` is the main command form. Also accept close variants such as `note to librarian:`, `note to librari:`, `not to librarian:`, and `not to librari:`.

Inferred event example:

```text
27/1/2027 dinner with Cassy at Belvedere Hotel Prague
```

Dates are day-first: `27/1/2027` means 27 January 2027.

## Workflow

1. Resolve the library folder.
2. Run:

```powershell
python scripts\scan_actions.py <folder> --json
```

3. Run:

```powershell
python scripts\run_actions.py <folder> --json
```

4. Create each `ready` calendar event with the available Codex calendar connector or tool without asking for another approval.
5. After a successful external creation, record it:

```powershell
python scripts\run_actions.py <folder> --record-created <action_id> --external-id <event_id> --json
```

6. If a connector is unavailable, summarize the ready event and do not mark it created.
7. For non-calendar actions, if `requires_confirmation` is `true`, ask the user before creating anything outward-facing.
8. If `requires_confirmation` is `false`, automatic explicit `NTL:` action mode allows the action.

## Enabling Or Disabling Automatic NTL Mode

Use:

```powershell
python scripts\scan_actions.py <folder> --enable-auto-ntl --json
python scripts\scan_actions.py <folder> --disable-auto-ntl --json
```

Automatic mode applies only to explicit `NTL:` or recognized librarian directive lines. It does not apply to inferred dated text.

## Action Handling

- `calendar`: create future calendar events without another approval prompt, then record the created action id. Ignore past events.
- `email`: draft or send only after confirmation or when explicit NTL auto mode allows it.
- `reminder`: create a reminder through the available reminder/task tool when possible.
- `task`: create a task through the available task tool when possible.
- `word_document`: create or draft a Word document from the note when document tools are available.
- `spreadsheet`: create or draft an Excel file or Google Sheet from the note when spreadsheet tools are available.
- `pdf`: create or draft a PDF from the note when document/PDF tools are available.
- `presentation`: create or draft slides from the note when presentation tools are available.

When a connector is unavailable, summarize the action and tell the user what could not be completed.
