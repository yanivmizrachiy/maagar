# דוח אמת מלא — maagar
# Full Repository Truth Report

**ריפו:** `yanivmizrachiy/maagar`
**תאריך הדוח:** 2026-06-03
**ענף נוכחי:** `claude/wonderful-meitner-XCkuz`

---

## A. סיכום הריפו הפעיל

| פריט | ערך |
|------|-----|
| ריפו | `yanivmizrachiy/maagar` |
| שפה | עברית RTL |
| מטרה | מאגר קבצי מתמטיקה + בסיס לאתר עתידי גדול |
| ענף ראשי | `main` |
| ענף פיתוח נוכחי | `claude/wonderful-meitner-XCkuz` |
| GitHub Pages | לא פעיל עדיין |
| Backend | אין — הכל סטטי |
| קבצים אמיתיים | 4 PDF |
| רשומות באינדקס | 4 |

---

## B. מבנה הקבצים הפעיל

```
metadata/
  index.json        ← אינדקס 4 פריטים
  taxonomy.json     ← מילון סיווגים
  site-structure.json ← מבנה ניווט ועיצוב
  authors.json      ← מילון מחברים (כרגע: unknown בלבד)

files/
  middle-school/
    grade-7/uncategorized/   ← 1 PDF (מאגר ז׳)
    grade-8/algebra/         ← 1 PDF (יחס/פרופורציה/קנה מידה)
    grade-8/summaries/       ← 1 PDF (דפי סיכום יחס/פרופורציה)
    grade-9/geometry/        ← 1 PDF (ריכוז שאלות דלתון)
  high-school/               ← ריק (.gitkeep)

scripts/
  validate-index.sh          ← סקריפט אימות מטא-דאטה וקבצים

STATE/
  full-repo-truth-report.md  ← המסמך הזה

RULES.md                     ← מקור האמת המחייב
AGENTS.md                    ← הוראות ל-AI
README.md                    ← תיאור הריפו
```

---

## C. 4 הקבצים האמיתיים — מצב מפורט

| מזהה | כיתה | קטגוריה | document_type | download | print | can_embed |
|------|------|---------|---------------|----------|-------|-----------|
| `7__uncategorized__maagar-z__unknown__001` | 7 | uncategorized | worksheet | ✅ true | ✅ true | unknown |
| `8__algebra__ratio-proportion-scale...` | 8 | algebra | worksheet | ✅ true | ✅ true | unknown |
| `8__summaries__grade-8-ratio-proportion...` | 8 | summaries | summary-work | ✅ true | ✅ true | unknown |
| `grade-9__geometry__deltoid__worksheet...` | 9 | geometry | worksheet | ✅ true | ✅ true | unknown |

**הערה על `can_embed`:** כל הקבצים הם PDF מהריפו. הטמעה ב-iframe אפשרית טכנית (דרך GitHub raw URL או Google Docs viewer), אך לא נבדקה עדיין. סומן `unknown` עד לבדיקה אמיתית.

---

## D. מבנה אתר עתידי — כפי שמוגדר

### עמוד ראשי
| כפתור | צבע | מצב |
|-------|-----|-----|
| שכבת ז׳ | Emerald `#064E3B → #10B981` | קיים בניווט, 1 קובץ |
| שכבת ח׳ | Blue `#1E3A8A → #38BDF8` | קיים בניווט, 2 קבצים |
| שכבת ט׳ | Purple `#581C87 → #A855F7` | קיים בניווט, 1 קובץ |
| חטיבה עליונה | Dark Gold `#111827 → #D97706` | קיים בניווט, 0 קבצים |

### כל שכבת חט"ב
| קטגוריה | צבע | ז׳ | ח׳ | ט׳ |
|---------|-----|---|---|---|
| אלגברה | Blue `#172554 → #2563EB` | ריק | 1 | ריק |
| גיאומטריה | Green `#14532D → #22C55E` | ריק | ריק | 1 |
| משימות מסכמות | Orange `#7C2D12 → #F97316` | ריק | 1 | ריק |
| מבחנים | Red `#881337 → #E11D48` | ריק | ריק | ריק |

### חטיבה עליונה
| כפתור | צבע | קבצים |
|-------|-----|-------|
| 3 יחידות | Teal `#0F766E → #14B8A6` | 0 |
| 4 יחידות | Indigo `#1D4ED8 → #4F46E5` | 0 |
| 5 יחידות | Crimson/Gold `#9F1239 → #F97316` | 0 |

---

## E. עקביות — RULES.md מול מצב בפועל

| בדיקה | תוצאה |
|-------|--------|
| כל קבצי האינדקס קיימים פיזית | ✅ כן (אומת ב-validate-index.sh) |
| אין כפילויות content_hash | ✅ אין |
| אין כפילויות id | ✅ אין |
| כל רשומות מכילות `source_type` | ✅ כן (תוקן בסשן זה) |
| כל רשומות מכילות `grades` (array) | ✅ כן (תוקן בסשן זה) |
| כל רשומות מכילות `can_embed` | ✅ כן (תוקן בסשן זה) |
| כל רשומות מכילות `print_ready` | ✅ כן (תוקן בסשן זה) |
| כל רשומות מכילות `download_ready` | ✅ כן (תוקן בסשן זה) |
| מבנה תיקיות מחייב ב-RULES.md מעודכן | ✅ כן (תוקן בסשן זה) |
| `metadata/taxonomy.json` עקבי עם RULES.md | ✅ כן |
| `metadata/site-structure.json` עקבי עם RULES.md | ✅ כן |
| אין קבצי דמו או מטא-דאטה מומצא | ✅ אין |

---

## F. מה חסר / לא נוצר עדיין

| פריט | מצב | עדיפות |
|------|-----|--------|
| אתר סטטי (HTML/CSS/JS) | ❌ לא קיים | גבוהה |
| GitHub Pages מוגדר | ❌ לא | גבוהה |
| `can_embed` נבדק בפועל לכל PDF | ❌ לא | בינונית |
| `metadata/authors.json` מעודכן | רק "unknown" | נמוכה |
| תוכן חטיבה עליונה | ❌ ריק | עתידי |
| `review/pending_clarification/` | ❌ לא קיים | נמוכה |

---

## G. סיכון

| סיכון | רמה | הערה |
|-------|-----|------|
| הוספת קבצים בלי עדכון אינדקס | בינוני | validate-index.sh מזהה |
| שכפול קבצים | נמוך | content_hash מגן |
| קבצי דמו/מומצאים | נמוך | RULES.md מחייב אמת |
| הצגת כפתורים שאינם עובדים | בינוני | `can_embed=unknown` מסומן נכון |
| אתר שנראה ריק | גבוה | קטגוריות ריקות רבות — צריך הודעה ברורה |

---

## H. פקודת אימות לריצה מקומית

```bash
bash scripts/validate-index.sh
```

פלט תקין:
```
VALIDATION PASSED
Records checked : 4
Errors          : 0
Warnings        : 0
```

---

## I. פעולה הבאה מומלצת

**הצעדים הבאים לפי סדר עדיפות:**

1. **בניית עמוד בית סטטי** (`index.html`) — HTML/CSS/JS עם 4 כפתורים, RTL, פרימיום.
2. **הגדרת GitHub Pages** על ענף `main`, קובץ `index.html` בשורש.
3. **בדיקת `can_embed`** — ניסיון הטמעת ה-PDFs וסימון `true`/`false` בהתאם.
4. **הוספת קבצים אמיתיים** — במיוחד לחטיבה עליונה ולקטגוריות הריקות.

---

*דוח זה נוצר אוטומטית. כל הנתונים מבוססים על קריאה ישירה מהריפו ועל הרצת סקריפט אימות.*
