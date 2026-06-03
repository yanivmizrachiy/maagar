# דוח אמת מלא — maagar
# Full Repository Truth Report

**ריפו:** `yanivmizrachiy/maagar`
**תאריך עדכון:** 2026-06-03
**ענף ראשי:** `main` (SHA: `d87c80a` + commits in this session)

---

## A. סיכום מצב נוכחי

| פריט | ערך |
|------|-----|
| ריפו | `yanivmizrachiy/maagar` |
| נראות | ציבורי (public) |
| שפה | עברית RTL |
| GitHub Pages | **פעיל** ✅ |
| Last Pages Deploy | SHA `d87c80a`, `conclusion: success` |
| אתר חי | `https://yanivmizrachiy.github.io/maagar/` |
| קבצים אמיתיים | 4 PDF |
| רשומות באינדקס | 4 |
| Backend | אין — הכל סטטי |

---

## B. קבצי מפתח

```
index.html                    ← אתר סטטי עברי RTL (חי על GitHub Pages)
RULES.md                      ← מקור האמת המחייב
AGENTS.md                     ← הוראות עבודה + workflow הוספת קבצים
README.md                     ← תיאור הריפו
metadata/
  index.json                  ← אינדקס 4 פריטים אמיתיים
  taxonomy.json               ← מילון סיווגים
  site-structure.json         ← מבנה ניווט ועיצוב
  authors.json                ← מילון מחברים
files/
  middle-school/grade-7/uncategorized/  ← 1 PDF (מאגר ז׳)
  middle-school/grade-8/algebra/        ← 1 PDF (יחס/פרופורציה/קנה מידה)
  middle-school/grade-8/summaries/      ← 1 PDF (דפי סיכום)
  middle-school/grade-9/geometry/       ← 1 PDF (ריכוז שאלות דלתון)
  high-school/                          ← ריק (.gitkeep)
scripts/
  validate-all.sh             ← 21 בדיקות: JSON, שדות, taxonomy, site-structure, contamination, logic
  validate-index.sh           ← אימות אינדקס בלבד
  test-logic.py               ← בדיקת כיסוי ניווט: כל הקבצים נגישים
  serve-local.sh              ← שרת פיתוח מקומי
STATE/
  full-repo-truth-report.md   ← המסמך הזה
```

---

## C. 4 הקבצים האמיתיים — מצב מפורט

| כיתה | קטגוריה | כותרת | download | print | can_embed |
|------|---------|-------|----------|-------|-----------|
| 7 | uncategorized → "חומרים שונים" | מאגר ז | ✅ | ✅ | unknown |
| 8 | algebra | יחס-פרופ-קנה מידה... | ✅ | ✅ | unknown |
| 8 | summaries | כיתה ח - יחס פרופורציה... | ✅ | ✅ | unknown |
| 9 | geometry | ריכוז שאלות דלתון | ✅ | ✅ | unknown |

**הערה על `can_embed`:** PDFs מסומנים `"unknown"` — embedding ב-iframe אפשרי טכנית (same-origin GitHub Pages), אך לא נבדק עדיין בדפדפן אמיתי. יש fallback מלא בממשק.

---

## D. כיסוי ניווט (אומת ב-test-logic.py)

| נתיב | קבצים |
|------|-------|
| בית → שכבת ז׳ → חומרים שונים | 1 ✅ |
| בית → שכבת ח׳ → אלגברה | 1 ✅ |
| בית → שכבת ח׳ → משימות מסכמות | 1 ✅ |
| בית → שכבת ט׳ → גיאומטריה | 1 ✅ |
| בית → חטיבה עליונה → כל רמה | 0 (ריק, empty state מוצג) |

**קבצים יתומים:** אין ✅

---

## E. תוצאות אימות מלאות

```
bash scripts/validate-all.sh
→ 21/21 PASSED, 0 FAILED

python3 scripts/test-logic.py
→ ALL LOGIC CHECKS PASSED
→ Files total: 4, Files reached: 4, Errors: 0
```

---

## F. תכונות האתר הפעיל

| תכונה | מצב |
|-------|-----|
| עברית RTL | ✅ |
| גופן Heebo | ✅ |
| 4 כפתורי בית (ז/ח/ט/חטיבה עליונה) | ✅ |
| 4 כפתורי קטגוריה לכל שכבה | ✅ |
| כפתור "חומרים שונים" כשיש קבצים לא מסווגים | ✅ |
| 3 כפתורי יחידות בחטיבה עליונה | ✅ |
| כרטיסיות קבצים אמיתיות | ✅ |
| empty state בעברית | ✅ |
| כפתורי הורדה | ✅ (כשdownload_ready=true) |
| כפתורי הדפסה | ✅ (כשprint_ready=true) |
| מודאל צפייה PDF (iframe + fallback) | ✅ |
| breadcrumbs + כפתור חזרה | ✅ |
| Responsive (נייד + מחשב) | ✅ |
| focus-visible accessibility | ✅ |
| גרמר עברי נכון (קובץ אחד / X קבצים) | ✅ |
| ללא תוכן דמו | ✅ |

---

## G. מה חסר / עדיין לא בוצע

| פריט | מצב | עדיפות |
|------|-----|--------|
| בדיקת PDF iframe בדפדפן אמיתי | ❌ | גבוהה |
| `can_embed` עדכון לפי בדיקה אמיתית | ❌ | גבוהה |
| תוכן קטגוריות ריקות (גיאומטריה ז׳, מבחנים כולם, חטיבה עליונה) | ❌ | עתידי — דורש קבצים אמיתיים |
| metadata/authors.json עם מחברים אמיתיים | ❌ | נמוכה |
| Playwright / browser automation tests | ❌ | בינונית |

---

## H. כיצד להוסיף קובץ חדש

ראה `AGENTS.md` סעיף 10 — תהליך מלא.

תמצית:
1. קבל קובץ מיניב + מטא-דאטה
2. חשב SHA-1, בדוק כפילות
3. שמור ב-`files/<path>/`
4. הוסף רשומה ל-`metadata/index.json`
5. הרץ `bash scripts/validate-all.sh && python3 scripts/test-logic.py`
6. Commit + push + PR + merge

---

## I. פקודות שימושיות

```bash
# אימות מלא לפני כל push
bash scripts/validate-all.sh && python3 scripts/test-logic.py

# שרת פיתוח מקומי
bash scripts/serve-local.sh
# → http://localhost:8080

# בדיקה בדפדפן
# פתח http://localhost:8080
# נווט לשכבת ח׳ → אלגברה → לחץ "צפייה" על כרטיסייה
# אם PDF מוצג ב-iframe: עדכן can_embed=true בindex.json
# אם לא: can_embed=false
```

---

*דוח זה עודכן אוטומטית. כל הנתונים מבוססים על קריאה ישירה מהריפו ועל הרצת סקריפטי אימות.*
