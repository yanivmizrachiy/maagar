# GPT → Claude File Import Handoff Protocol

This document defines the exact format ChatGPT should use when handing off
file-import requests to Claude for the `yanivmizrachiy/maagar` repository.

Yaniv may classify files with ChatGPT's help, then paste the result into a
Claude session. Claude will run the repo scripts, validate, and commit.

---

## When to use this protocol

Use this handoff when:
- Yaniv uploads or describes real mathematics learning files to ChatGPT
- ChatGPT helps classify grade / category / document type / topics
- The result needs to be imported into the maagar repository

**ChatGPT prepares the handoff. Claude executes it.**

---

## Single-file handoff format

Paste this block into the Claude session, filled with real data:

```
FILE_IMPORT_REQUEST

file_name:      worksheet.pdf
local_path:     /Users/yaniv/Downloads/worksheet.pdf
title:          דף עבודה יחס ופרופורציה — כיתה ח

grade:          8
unit_level:
grades:         8
school_stage:   middle-school
category:       algebra
document_type:  worksheet

topics:         יחס | פרופורציה | קנה מידה
year:           2024
author:         unknown
can_embed:      unknown
print_ready:    true
download_ready: true

notes:          דף עבודה בנושא יחס ופרופורציה לכיתה ח
```

### Field reference

| Field | Required | Values / notes |
|-------|----------|----------------|
| `file_name` | ✓ | actual filename with extension |
| `local_path` | ✓ | full path on Yaniv's machine, OR "uploaded to session" |
| `title` | — | Hebrew title; default = filename stem |
| `grade` | ✓ (or `unit_level`) | `7` / `8` / `9` |
| `unit_level` | ✓ (or `grade`) | `3-unit` / `4-unit` / `5-unit` |
| `grades` | — | pipe-separated if multi-grade: `7\|8` |
| `school_stage` | — | `middle-school` / `high-school` (inferred from grade/unit_level) |
| `category` | ✓ | `algebra` / `geometry` / `summaries` / `exams` / `uncategorized` |
| `document_type` | ✓ | `worksheet` / `summary-work` / `exam` / `link` / `digital-task` / `printable-task` / `embedded-resource` / `mixed` |
| `topics` | — | pipe-separated Hebrew topics: `יחס\|פרופורציה` |
| `year` | — | e.g. `2024`; write `unknown` if not known |
| `author` | — | author name; write `unknown` if not known |
| `can_embed` | — | `true` / `false` / `unknown` |
| `print_ready` | — | `true` / `false` (auto-set to `true` for worksheet/exam/summary-work) |
| `download_ready` | — | `true` / `false` (always `true` for repo files) |
| `notes` | — | free text in Hebrew or English |

### Rules for ChatGPT when filling this form

- **Write `unknown` — never invent** year, author, or metadata you are not sure about.
- `topics` must be real mathematical topics, not categories.
- `category` must be exactly one of the five valid values.
- `document_type` must be exactly one of the eight valid values.
- If the file fits multiple grades, list them all in `grades` separated by `|`.
- `local_path` must be the actual file path on Yaniv's machine. If Yaniv uploaded the file to ChatGPT, write `uploaded_to_chatgpt` and note that the file must be saved locally before Claude can import it.

---

## Multi-file handoff format (CSV)

For importing several files at once, provide a CSV block:

```
FILE_IMPORT_BATCH_CSV

file_name,local_path,title,grade,unit_level,grades,category,document_type,topics,year,author,can_embed,notes
worksheet1.pdf,/path/worksheet1.pdf,יחס ופרופ ח,8,,8,algebra,worksheet,יחס|פרופורציה,2024,unknown,unknown,
exam_geometry.pdf,/path/exam_geo.pdf,מבחן גיאו ט,9,,,geometry,exam,גיאומטריה|שטחים,2023,unknown,unknown,
bagrut_5u.pdf,/path/bagrut.pdf,בגרות 5 יח,,5-unit,,algebra,exam,אלגברה|בגרות,2022,unknown,unknown,
```

Claude will save this CSV to a file and run:
```bash
python3 scripts/batch-add.py --manifest handoff.csv --dry-run
```
then confirm with Yaniv before the real import.

---

## What Claude does after receiving a handoff

1. **Confirms** the format is valid and all required fields are present.
2. **Asks Yaniv** to confirm the file is available at `local_path` (or to upload it).
3. **Runs dry-run:**
   ```bash
   python3 scripts/add-file.py \
     --file "<local_path>" \
     --grade <grade> \
     --category <category> \
     --doctype <document_type> \
     --title "<title>" \
     --topics "<topics>" \
     --year <year> \
     --author "<author>" \
     --can-embed <can_embed> \
     --dry-run
   ```
4. **Shows the preview** — destination path, record ID, all metadata.
5. **Waits for Yaniv's approval** (or proceeds with `--yes` if Yaniv said to).
6. **Runs the real import** (same command without `--dry-run`).
7. **Runs all validations:**
   ```bash
   bash scripts/validate-all.sh
   python3 scripts/test-logic.py
   ```
8. **Commits and pushes:**
   ```bash
   git add "files/..." metadata/index.json
   git commit -m "feat(files): add <title>"
   git push
   ```
9. **Opens a PR** and merges if clean.

---

## Example: complete handoff message Yaniv pastes to Claude

```
FILE_IMPORT_REQUEST

file_name:      דף_עבודה_משוואות_ח.pdf
local_path:     /Users/yaniv/Desktop/קבצים/דף_עבודה_משוואות_ח.pdf
title:          דף עבודה משוואות — כיתה ח

grade:          8
grades:         8
category:       algebra
document_type:  worksheet

topics:         משוואות | אלגברה
year:           unknown
author:         unknown
can_embed:      unknown

notes:          דף עבודה שהכנתי לתלמידי כיתה ח
```

---

## Example: ChatGPT instruction to give Yaniv

When Yaniv asks ChatGPT to classify files, ChatGPT should output this:

> כדי שקלוד יוכל לייבא את הקבצים, העתק את הבלוק הבא לשיחה עם קלוד:
>
> ```
> FILE_IMPORT_REQUEST
> file_name:     [שם הקובץ]
> local_path:    [הנתיב המלא בתיקייה שלך]
> title:         [כותרת בעברית]
> grade:         [7 / 8 / 9]
> category:      [algebra / geometry / summaries / exams / uncategorized]
> document_type: [worksheet / exam / summary-work / ...]
> topics:        [נושא1 | נושא2]
> year:          [שנה או unknown]
> author:        unknown
> ```

---

## Template file

A blank template is available at: `scripts/manifest-example.csv`

---

## What this protocol does NOT cover

- ChatGPT cannot run repo scripts — Claude must do that.
- ChatGPT cannot verify file hashes or check for duplicates — Claude does that.
- ChatGPT cannot push to git — Claude does that.
- If metadata is unclear, write `unknown`. Do not guess.
