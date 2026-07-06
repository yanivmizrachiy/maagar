# הוספת קבצים אמיתיים למאגר

מדריך מלא להוספת קבצי לימוד חדשים לריפוזיטורי `yanivmizrachiy/maagar`.

> **חשוב:** המאגר חי ומכיל מאות קבצים אמיתיים; מדריך זה מיועד להוספת קבצים *נוספים*.
> אין קבצי דמו. אין מטאדאטה מומצאת. תמיד מריצים dry-run לפני ייבוא אמיתי.
>
> לפרוטוקול הגשת קבצים מ-ChatGPT לקלוד, ראה: [`docs/GPT_TO_CLAUDE_FILE_HANDOFF.md`](GPT_TO_CLAUDE_FILE_HANDOFF.md)

---

## רשימת תיוג — ייבוא ראשון (First Import Checklist)

כשמוסיפים קבצים אמיתיים נוספים למאגר הקיים:

- [ ] **שלב 1 — אסוף קבצים אמיתיים** בתיקייה על המחשב
- [ ] **שלב 2 — החלט לכל קובץ:** כיתה / קטגוריה / סוג מסמך
  - כיתה: `7` / `8` / `9` / `3-unit` / `4-unit` / `5-unit`
  - קטגוריה: `algebra` / `geometry` / `summaries` / `exams` / `uncategorized`
  - סוג: `worksheet` / `exam` / `summary-work` / `link` / וכו׳
  - (אפשר לבקש מ-ChatGPT לעזור בסיווג — ראה `docs/GPT_TO_CLAUDE_FILE_HANDOFF.md`)
- [ ] **שלב 3 — הרץ dry-run** (אחד לכמה קבצים):
  ```bash
  python3 scripts/add-file.py --file /path/to/file.pdf \
    --grade 8 --category algebra --doctype worksheet --dry-run
  ```
  או לתיקייה שלמה:
  ```bash
  python3 scripts/batch-add.py --folder /path/to/folder/ \
    --grade 8 --category algebra --doctype worksheet --dry-run
  ```
- [ ] **שלב 4 — בדוק את התצוגה המקדימה** — ודא שהנתיב, ה-ID והמטאדאטה נכונים
- [ ] **שלב 5 — הרץ ייבוא אמיתי** (הסר `--dry-run`):
  ```bash
  python3 scripts/add-file.py --file /path/to/file.pdf \
    --grade 8 --category algebra --doctype worksheet --yes
  ```
- [ ] **שלב 6 — בדוק שהבדיקות עברו** (הסקריפט מריץ אוטומטית, אבל אפשר ידנית):
  ```bash
  bash scripts/validate-all.sh && python3 scripts/test-logic.py
  ```
- [ ] **שלב 7 — commit + push:**
  ```bash
  git add files/ metadata/index.json
  git commit -m "feat(files): add <כותרת>"
  git push
  ```

---

## עקרונות יסוד

1. **הריפו הוא מקור האמת** — כל קובץ, כל מטאדאטה, כל סיווג חייב להיות שמור בריפו.
2. **אין המצאת מטאדאטה** — אם שנה/מחבר לא ידועים, כותבים `"unknown"`.
3. **אין קבצי דמו** — רק קבצים אמיתיים.
4. **כפילויות נחסמות** — הסקריפט מחשב SHA-1 ומונע הוספה כפולה.

---

## מבנה תיקיות

```
files/
├── middle-school/
│   ├── grade-7/
│   │   ├── algebra/
│   │   ├── geometry/
│   │   ├── summaries/
│   │   ├── exams/
│   │   └── uncategorized/
│   ├── grade-8/   (אותו מבנה)
│   └── grade-9/   (אותו מבנה)
└── high-school/
    ├── 3-unit/
    ├── 4-unit/
    ├── 5-unit/
    └── unknown/
```

---

## שיטה א׳ — קובץ בודד (`add-file.py`)

מתאים ל: הוספת קובץ אחד עם מטאדאטה מדויקת.

### פקודה בסיסית

```bash
python3 scripts/add-file.py \
  --file /path/to/file.pdf \
  --grade 8 \
  --category algebra \
  --doctype worksheet
```

### עם מטאדאטה מלאה

```bash
python3 scripts/add-file.py \
  --file /path/to/file.pdf \
  --grade 8 \
  --category algebra \
  --doctype worksheet \
  --year 2024 \
  --author "שם המחבר" \
  --topics "יחס,פרופורציה,קנה מידה" \
  --title "כותרת בעברית"
```

### תצוגה מקדימה (dry run) — בלי לכתוב שום דבר

```bash
python3 scripts/add-file.py \
  --file /path/to/file.pdf \
  --grade 8 --category algebra --doctype worksheet \
  --dry-run
```

### ללא אישור ידני (עבור סקריפטים)

```bash
python3 scripts/add-file.py \
  --file /path/to/file.pdf \
  --grade 8 --category algebra --doctype worksheet \
  --yes
```

### כל הפרמטרים

| פרמטר | חובה? | תיאור |
|-------|-------|-------|
| `--file` | ✓ | נתיב לקובץ המקור |
| `--grade` | ✓ (או `--unit-level`) | כיתה: `7`, `8`, `9` |
| `--unit-level` | ✓ (או `--grade`) | רמה: `3-unit`, `4-unit`, `5-unit` |
| `--category` | ✓ | תחום לימוד |
| `--doctype` | ✓ | סוג מסמך |
| `--title` | — | כותרת (ברירת מחדל: שם הקובץ) |
| `--year` | — | שנה (ברירת מחדל: `unknown`) |
| `--author` | — | מחבר (ברירת מחדל: `unknown`) |
| `--topics` | — | נושאים מופרדים בפסיק |
| `--tags` | — | תגיות נוספות |
| `--notes` | — | הערות חופשיות |
| `--can-embed` | — | `true` / `false` / `unknown` |
| `--grades` | — | כיתות מרובות: `"7,8"` |
| `--dry-run` | — | תצוגה מקדימה בלי שמירה |
| `--yes` / `-y` | — | דילוג על אישור ידני |
| `--no-validate` | — | דילוג על הרצת בדיקות (לשימוש ב-batch) |

### ערכים חוקיים

**`--category`:** `algebra`, `geometry`, `summaries`, `exams`, `uncategorized`

**`--doctype`:** `worksheet`, `summary-work`, `exam`, `link`, `digital-task`, `printable-task`, `embedded-resource`, `mixed`

---

## שיטה ב׳ — הרבה קבצים מתיקייה (`batch-add.py`)

מתאים ל: הוספת קבוצת קבצים מאותה קטגוריה/כיתה בבת אחת.

```bash
python3 scripts/batch-add.py \
  --folder /path/to/pdfs/ \
  --grade 8 \
  --category algebra \
  --doctype worksheet \
  --dry-run
```

כל ה-PDF בתיקייה יתווספו עם אותו grade/category/doctype. הכותרת נלקחת מ-שם הקובץ.

**הרצה אמיתית (בלי dry-run):**

```bash
python3 scripts/batch-add.py \
  --folder /path/to/pdfs/ \
  --grade 8 \
  --category algebra \
  --doctype worksheet
```

---

## שיטה ג׳ — מניפסט CSV (`batch-add.py --manifest`)

מתאים ל: הרבה קבצים עם מטאדאטה שונה לכל אחד.

### שלב 1 — צור קובץ CSV

```csv
file,title,grade,unit_level,grades,category,doctype,year,author,topics,tags,notes,can_embed
/path/to/file1.pdf,יחס ופרופורציה,8,,,algebra,worksheet,2024,,יחס|פרופורציה,,
/path/to/file2.pdf,מבחן גיאומטריה,9,,,geometry,exam,2023,,גיאומטריה,,
/path/to/file3.pdf,בגרות אלגברה,,5-unit,,algebra,exam,2022,,אלגברה|בגרות,,
```

**הערות על העמודות:**
- `grades` — כיתות מרובות: `"7|8"` (מופרד בצינור)
- `topics` — נושאים: `"יחס|פרופורציה"` (מופרד בצינור)
- `tags` — תגיות: `"tag1|tag2"`
- `unit_level` — רק לחטיבה עליונה: `3-unit`, `4-unit`, `5-unit`
- `can_embed` — `true` / `false` / `unknown`

ראה: `scripts/manifest-example.csv` לדוגמה מלאה.

### שלב 2 — תצוגה מקדימה

```bash
python3 scripts/batch-add.py --manifest manifest.csv --dry-run
```

### שלב 3 — הוספה אמיתית

```bash
python3 scripts/batch-add.py --manifest manifest.csv
```

---

## שלב אחרון — commit ו-push

אחרי הרצת אחת מהשיטות:

```bash
# הוספת קובץ בודד
git add "files/path/to/file.pdf" metadata/index.json
git commit -m "feat(files): add כותרת הקובץ"
git push

# batch
git add files/ metadata/index.json
git commit -m "feat(files): batch add N files — grade 8 algebra"
git push
```

---

## מה הסקריפטים עושים אוטומטית

1. ✅ מאמת שהקלט חוקי (category, doctype, grade)
2. ✅ מחשב SHA-1 של תוכן הקובץ
3. ✅ בודק אם קיים כבר קובץ זהה ב-index.json (לפי תוכן)
4. ✅ בונה ID ייחודי (מונע התנגשויות)
5. ✅ מעתיק לנתיב הנכון תחת `files/`
6. ✅ מוסיף רשומת מטאדאטה ל-`metadata/index.json`
7. ✅ מריץ `validate-all.sh` (חבילת הבדיקות המלאה) ו-`test-logic.py`

---

## שגיאות נפוצות

| שגיאה | פתרון |
|-------|--------|
| `File not found` | ודא שהנתיב ל-`--file` נכון |
| `Invalid category` | ערכים חוקיים: `algebra`, `geometry`, `summaries`, `exams`, `uncategorized` |
| `DUPLICATE DETECTED` | הקובץ כבר קיים (לפי תוכן). לא יתווסף שוב. |
| `validate-all.sh FAILED` | הסקריפט יציג את הבעיה; בדרך כלל שדה חסר או נתיב שגוי |
| `content_hash mismatch` | הקובץ הפיזי שונה ממה שרשום בindex — עדכן ידנית |

---

## דוגמה מלאה — קובץ בודד

```bash
python3 scripts/add-file.py \
  --file ~/Downloads/משוואות-כיתה-ח.pdf \
  --grade 8 \
  --category algebra \
  --doctype worksheet \
  --year 2023 \
  --topics "משוואות,אלגברה" \
  --title "דף עבודה משוואות — כיתה ח"
```

פלט צפוי:
```
  Computing hash for משוואות-כיתה-ח.pdf...
  SHA-1: abc123...

  Source      : ~/Downloads/משוואות-כיתה-ח.pdf
  Destination : files/middle-school/grade-8/algebra/דף-עבודה-משוואות-כיתה-ח.pdf
  Record ID   : 8__algebra__דף-עבודה-משוואות-כיתה-ח__worksheet__2023__001
  ...

Proceed? [y/N] y
  ✓ File copied to files/middle-school/grade-8/algebra/...
  ✓ metadata/index.json updated
  ✓ validate-all.sh PASSED
  ✓ test-logic.py PASSED
────────────────────────────────────────────────────────
  ✓ FILE ADDED SUCCESSFULLY
────────────────────────────────────────────────────────
  Now run:
    git add "files/middle-school/grade-8/algebra/..." metadata/index.json
    git commit -m "feat(files): add דף עבודה משוואות — כיתה ח"
    git push
```
