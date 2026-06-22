# Codex Notepad Librarian - Ελληνικός οδηγός

Αυτός είναι ένας πρακτικός οδηγός για Έλληνες χρήστες. Δεν είναι λέξη-προς-λέξη μετάφραση του αγγλικού README. Είναι ο γρήγορος δρόμος για να το εγκαταστήσετε, να γράψετε σημειώσεις, και να αφήσετε το Codex να τις οργανώσει σε τοπική μνήμη.

Το plugin είναι για ανθρώπους που θέλουν να γράφουν απλά αρχεία σε Notepad ή σε έναν φάκελο, χωρίς ειδική εφαρμογή γνώσης. Τα αρχεία μένουν τοπικά στον υπολογιστή σας.

## Τι κάνει

- Διαβάζει σημειώσεις από έναν φάκελο `Inbox`.
- Υποστηρίζει `.txt` και `.md` αρχεία.
- Αναγνωρίζει PDF ως πηγές που μπορεί να χρειάζονται OCR setup.
- Δημιουργεί Markdown memory files στο `Library\Documents`.
- Δημιουργεί ημερήσιο review στο `Library\Reviews`.
- Φτιάχνει index ώστε μετά να ρωτάτε το Codex τι έχετε γράψει.
- Μπορεί να εντοπίζει απλές ενέργειες από σημειώσεις.
- Τα μελλοντικά calendar events μπορούν να δημιουργηθούν χωρίς νέο approval prompt.
- Τα παλιά calendar events αγνοούνται αυτόματα με βάση την ημερομηνία του run.
- Κρατά action state ώστε να μην δημιουργεί διπλά calendar events στο επόμενο run.

Δεν χρειάζεται Obsidian. Τα Markdown αρχεία είναι απλά αρχεία που μπορείτε να ανοίξετε και με Notepad.

## 1. Εγκαταστήστε το Codex CLI

Ανοίξτε PowerShell και γράψτε:

```powershell
codex --version
```

Αν δείτε version number, είστε έτοιμοι.

Αν το PowerShell πει ότι δεν βρίσκει το `codex`, εγκαταστήστε το με:

```powershell
powershell -ExecutionPolicy ByPass -c "irm https://chatgpt.com/codex/install.ps1 | iex"
```

Κλείστε το PowerShell, ανοίξτε το ξανά, και ελέγξτε πάλι:

```powershell
codex --version
```

## 2. Κατεβάστε το plugin

Σε έναν φάκελο όπου θέλετε να κρατήσετε το plugin, γράψτε:

```powershell
git clone https://github.com/vlasvar/codex-notepad-librarian.git
cd codex-notepad-librarian
```

Κρατήστε αυτόν τον φάκελο. Το Codex θα τον χρησιμοποιεί ως local plugin source.

## 3. Αυτόματη εγκατάσταση

Μέσα από τον φάκελο `codex-notepad-librarian`, τρέξτε:

```powershell
.\install.ps1
```

Αυτό θα δημιουργήσει έναν φάκελο σημειώσεων, συνήθως εδώ:

```text
C:\Users\Alex\Documents\NotepadLibrary
```

Θα δημιουργήσει επίσης τη βασική δομή:

```text
NotepadLibrary\
  Inbox\
  Library\
    Documents\
    Reviews\
    Sources\
    Archive\
      Originals\
  .notepad-librarian\
    processed-files.json
    action-state.json
    retrieval-index.json
    settings.json
```

Μετά την εγκατάσταση, ανοίξτε νέο Codex thread ώστε να φορτωθούν τα plugin skills.

## 4. Η πρώτη σας σημείωση

Φτιάξτε ένα αρχείο:

```text
C:\Users\Alex\Documents\NotepadLibrary\Inbox\lease note.txt
```

Γράψτε μέσα κάτι απλό:

```text
Μίλησα με τον Sam για το lease του γραφείου.
Πρέπει να ξαναδώ τους όρους πριν τον Αύγουστο.
```

Μετά ρωτήστε το Codex:

```text
Process my Notepad library in C:\Users\Alex\Documents\NotepadLibrary.
```

Το plugin θα δημιουργήσει ένα Markdown memory file στο:

```text
Library\Documents\
```

και ένα review note στο:

```text
Library\Reviews\
```

## 5. Πώς ψάχνετε μετά τις σημειώσεις

Μπορείτε να ρωτήσετε:

```text
Find what I wrote about lease terms in my Notepad library.
```

ή πιο φυσικά:

```text
What did I write about the office lease?
```

Το Codex θα ψάξει τα `.txt` και τα Markdown memory files και θα απαντήσει με paths και snippets.

## 6. PDF και Tesseract

Μπορείτε να βάλετε PDF στο `Inbox`. Το plugin πρώτα δοκιμάζει να βρει έτοιμο text layer στο PDF. Αν το PDF είναι scanned, μπορεί να χρησιμοποιήσει Tesseract OCR όταν υπάρχουν τα τοπικά εργαλεία και τα σωστά language data.

Αν λείπει κάτι από το OCR setup, θα το σημειώσει καθαρά και θα συνεχίσει κανονικά με τα `.txt` και `.md` αρχεία.

Το plugin δεν χρειάζεται Tesseract για απλές `.txt` ή `.md` σημειώσεις.

Όταν θελήσετε να δουλέψετε με scanned PDFs, ρωτήστε το Codex:

```text
Add Tesseract configuration to my Notepad library.
```

Το Codex μπορεί να σας βοηθήσει να εγκαταστήσετε ή να δηλώσετε Tesseract, να συμπληρώσετε το `tesseract_path`, το `tessdata_dir`, και τις γλώσσες OCR στο `.notepad-librarian\settings.json`. Τα νέα libraries ξεκινούν με Greek και English OCR:

```json
{
  "ocr": {
    "languages": ["ell", "eng"]
  }
}
```

## 7. Ενέργειες και calendar events

Μπορείτε να γράψετε μέσα σε σημείωση:

```text
NTL: make a calendar event for contract signing on 24/6/2026
```

Το plugin μπορεί να προετοιμάσει μελλοντικά calendar events χωρίς να ξαναρωτήσει. Αν η ημερομηνία έχει περάσει, το event αγνοείται. Μετά τη δημιουργία, το action γράφεται στο:

```text
.notepad-librarian\action-state.json
```

Έτσι το ίδιο note δεν δημιουργεί διπλό event στο επόμενο run.

## 8. Χρήσιμα prompts

```text
Set up my Notepad library at C:\Users\Alex\Documents\NotepadLibrary.
```

```text
Process my Notepad library in C:\Users\Alex\Documents\NotepadLibrary.
```

```text
Find what I wrote about lease terms in my Notepad library.
```

```text
Check my Notepad notes for actions.
```

```text
Show me the most recent context from my Notepad library.
```

## 9. Ασφάλεια και προσωπικά δεδομένα

- Το plugin δουλεύει με τοπικά αρχεία.
- Δεν αυτοματοποιεί live Notepad windows.
- Δεν διαγράφει σιωπηλά τις σημειώσεις σας.
- Οι κλασικές `.txt` σημειώσεις αρχειοθετούνται πριν αφαιρεθούν από το Inbox.
- Τα μελλοντικά calendar events μπορούν να δημιουργηθούν χωρίς νέο approval prompt και καταγράφονται για να μην γίνουν διπλά.
- Τα emails και άλλες μη-calendar ενέργειες παραμένουν πιο προσεκτικές εκτός αν ενεργοποιήσετε explicit auto mode.
- Τα generated Markdown notes είναι drafts. Ελέγχετε σημαντικές πληροφορίες πριν βασιστείτε πάνω τους.
- Το plugin δεν είναι backup system. Κρατήστε δικά σας backups.

## 10. Αν κάτι δεν δουλεύει

Πρώτα δοκιμάστε:

```powershell
.\install.ps1
```

Μετά ανοίξτε νέο Codex thread και ρωτήστε:

```text
Set up my Notepad library at C:\Users\Alex\Documents\NotepadLibrary.
```

Αν το θέμα είναι PDF/OCR, ρωτήστε:

```text
Add Tesseract configuration to my Notepad library.
```

Αν θέλετε διαφορετικό φάκελο σημειώσεων:

```powershell
.\install.ps1 -LibraryPath C:\Users\Alex\Documents\MyNotes
```
