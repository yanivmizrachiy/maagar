# הוספת קבצים אמיתיים למאגר

מדריך מלא להוספת קבצי לימוד חדשים לריפוזיטורי `yanivmizrachiy/maagar`.

---

## עקרונות יסוד

1. **הריפו הוא מקור האמת** — כל קובץ, כל מטאדאטה, כל סיווג — חייב להיות שמור בריפו.
2. **אין המצאת מטאדאטה** — אם שנה/מחבר לא ידועים, כותבים `"unknown"`.
3. **אין קבצי דמו** — רק קבצים אמיתיים מגיעים לריפו.
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

## שלב 1 — הכנת הקובץ

לפני הרצת הסקריפט, החלט:

| שאלה | ערכים אפשריים |
|------|--------------|
| לאיזה כיתה? | `7`, `8`, `9` (חט"ב) · `3-unit`, `4-unit`, `5-unit` (ת"ע) |
| לאיזה תחום? | `algebra`, `geometry`, `summaries`, `exams`, `uncategorized` |
| איזה סוג מסמך? | `worksheet`, `summary-work`, `exam`, `link`, `digital-task`, `printable-task`, `embedded-resource`, `mixed` |
| מה הנושאים? | רשימה מופרדת בפסיקים, עברית בסדר |

---

## שלב 2 — הרצת הסקריפט

**מ-root של הריפו:**

```bash
python3 scripts/add-file.py \
  --file /path/to/myfile.pdf \
  --grade 8 \
  --category algebra \
  --doctype worksheet \
  --year 2024 \
  --author "שם המחבר" \
  --topics "יחס,פרופורציה,קנה מידה" \
  --title "כותרת בעברית"
```

### תצוגה מקדימה (dry run)

```bash
python3 scripts/add-file.py --file myfile.pdf --grade 8 --category algebra --doctype worksheet --dry-run
```

לא כותב שום דבר — רק מציג מה *יקרה*.

### פרמטרים מלאים

| פרמטר | חובה? | תיאור |
|-------|-------|-------|
| `--file` | ✓ | נתיב לקובץ המקור |
| `--grade` | ✓ (או `--unit-level`) | כיתה: `7`, `8`, `9` |
| `--unit-level` | ✓ (או `--grade`) | רמה: `3-unit`, `4-unit`, `5-unit` |
| `--category` | ✓ | תחום לימוד |
| `--doctype` | ✓ | סוג מסמך |
| `--title` | לא | כותרת (ברירת מחדל: שם הקובץ) |
| `--year` | לא | שנה (ברירת מחדל: `unknown`) |
| `--author` | לא | מחבר (ברירת מחדל: `unknown`) |
| `--topics` | לא | נושאים מופרדים בפסיק |
| `--tags` | לא | תגיות נוספות |
| `--notes` | לא | הערות חופשיות |
| `--dry-run` | לא | תצוגה מקדימה בלי שמירה |
| `--grades` | לא | כיתות מרובות: `"7,8"` |

---

## שלב 3 — בדיקה ו-commit

אחרי שהסקריפט מסיים בהצלחה:

```bash
# בדוק שהקובץ נוסף
git status

# הוסף לגיט
git add files/ metadata/index.json

# commit
git commit -m "feat(files): add [כותרת הקובץ]"

# push
git push
```

---

## מה הסקריפט עושה אוטומטית

1. ✅ מאמת שהקלט חוקי (category, doctype, grade)
2. ✅ מחשב SHA-1 של תוכן הקובץ
3. ✅ בודק אם כבר קיים קובץ זהה ב-index.json
4. ✅ קובע את הנתיב הנכון תחת `files/`
5. ✅ מעתיק את הקובץ לנתיב הנכון
6. ✅ בונה רשומת מטאדאטה ומוסיף ל-`metadata/index.json`
7. ✅ מריץ `validate-all.sh` ו-`test-logic.py`

---

## שגיאות נפוצות

### "File not found"
וודא שהנתיב ל-`--file` נכון ושהקובץ קיים.

### "Invalid category"
הקטגוריות המותרות: `algebra`, `geometry`, `summaries`, `exams`, `uncategorized`

### "DUPLICATE DETECTED"
הקובץ כבר קיים במאגר (לפי תוכן). אם צריך לעדכן מטאדאטה, ערוך `metadata/index.json` ישירות.

### "validate-all.sh FAILED"
הסקריפט יציג את השגיאה. בדרך כלל: מסלול קובץ שגוי או שדה חסר.

---

## הוספת קובץ לכמה כיתות

אם קובץ מתאים לכיתות ז' **וגם** ח':

```bash
python3 scripts/add-file.py \
  --file myfile.pdf \
  --grade 7 \
  --grades "7,8" \
  --category algebra \
  --doctype worksheet
```

---

## דוגמה מלאה

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
  Source      : /home/user/Downloads/משוואות-כיתה-ח.pdf
  Destination : files/middle-school/grade-8/algebra/דף-עבודה-משוואות-כיתה-ח.pdf
  Record ID   : 8__algebra__דף-עבודה-משוואות-כיתה-ח__worksheet__2023__001
  ...
Proceed? [y/N] y
  ✓ File copied to files/middle-school/grade-8/algebra/...
  ✓ Record added to metadata/index.json
  ✓ validate-all.sh PASSED
  ✓ test-logic.py PASSED
──────────────────────────────────────────────────────
  ✓ FILE ADDED SUCCESSFULLY
──────────────────────────────────────────────────────
```
