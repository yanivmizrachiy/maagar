# מדריך המשכיות — maagar

**ריפו:** `yanivmizrachiy/maagar`
**עודכן:** 2026-06-03

> **המטרה:** יניב יכול להמשיך לעבוד עם Claude מכל מחשב, בכל זמן, בלי להתחיל מחדש.
> הריפו הוא זיכרון הפרויקט — לא הזיכרון של Claude.

---

## 1. איך ממשיכים את אותו session

אם עדיין פתוחה שיחת Claude Code:
- פשוט המשיכו לכתוב בשיחה הנוכחית.
- Claude זוכר את ההקשר מהשיחה הנוכחית.

---

## 2. איך ממשיכים ממחשב אחר (session חדש)

### שלב 1 — קלוד קורא את הריפו

Claude Code יכול לפתוח את הריפו מחדש. פשוט כתבו:

```
Continue `yanivmizrachiy/maagar`.
Read STATE/full-repo-truth-report.md and continue from where we left off.
```

### שלב 2 — Claude מריץ את הבדיקות

Claude חייב להריץ:
```bash
git remote -v
git branch --show-current
git status
bash scripts/validate-all.sh
python3 scripts/test-logic.py
```

### שלב 3 — Claude מציג מצב נוכחי

Claude יאמר לכם מה הסטטוס הנוכחי לפי `STATE/full-repo-truth-report.md`.

---

## 3. קבצים ש-Claude חייב לקרוא בתחילת כל session

סדר חובה:
1. `RULES.md` — כללי ה-repo (מקור האמת)
2. `AGENTS.md` — הוראות עבודה ל-AI
3. `STATE/full-repo-truth-report.md` — מצב עדכני
4. `docs/CONTINUITY_GUIDE.md` — מסמך זה
5. `metadata/index.json` — קבצים קיימים
6. `metadata/site-structure.json` — מבנה ניווט
7. `metadata/taxonomy.json` — סיווגים חוקיים

---

## 4. הבדיקות שחייב להריץ בתחילת session

```bash
# חובה:
bash scripts/validate-all.sh
python3 scripts/test-logic.py

# לבדיקת UI (כשרלוונטי):
node scripts/qa-browser.js
```

---

## 5. איך להימנע מזיהום Gmail/Calendar

> **חשוב:** Claude Code יכול להתחבר לשירותים נוספים. יניב מחובר ל-Gmail וCalendar.
> **חד-משמעי: אין לעשות שום פעולה על Gmail / Calendar / כל שירות שאינו `maagar`.**

- עובדים **רק** על `yanivmizrachiy/maagar`
- אם Claude מציע משהו שקשור ל-Gmail, Calendar, Sheets — **דחה**
- contamination scan רץ בכל `validate-all.sh` לגלות חדירת קוד לא קשור

---

## 6. CLAUDE_CONTINUATION_HANDOFF — בלוק המשכיות

בסוף כל session משמעותי, Claude מוציא בלוק זה.
יניב יכול להדביק אותו בתחילת session חדש:

```
CLAUDE_CONTINUATION_HANDOFF

repo:          yanivmizrachiy/maagar
branch:        main
sha:           [SHA עדכני — ראה STATE/full-repo-truth-report.md]
last_pr:       [מספר וכותרת PR אחרון]
site:          https://yanivmizrachiy.github.io/maagar/
files_changed: [רשימה]
tests_passed:  validate-all.sh ✅ | test-logic.py ✅ | qa-browser.js ✅
status:        [מה בוצע]
next_action:   [הפעולה הבאה המומלצת]
warning:       Work ONLY on maagar — never Gmail/Calendar/other
```

---

## 7. מה Claude עושה אוטומטית (לא צריך לבקש)

| פעולה | אוטומטי |
|-------|---------|
| קריאת RULES.md | ✅ |
| קריאת STATE | ✅ |
| הרצת validate-all.sh לפני push | ✅ |
| dry-run לפני ייבוא קבצים | ✅ |
| בדיקת content_hash | ✅ |
| commit + push | ✅ |
| פתיחת PR | ✅ |
| עדכון STATE אחרי merge | ✅ |

---

## 8. מה Claude לא עושה ללא אישור מפורש

| פעולה | דרוש אישור |
|-------|------------|
| הוספת analytics/tracking | ✅ |
| שינוי מבנה תיקיות קיים | ✅ |
| מחיקת קבצים אמיתיים | ✅ |
| force push ל-main | ✅ |
| שינוי RULES.md באופן דרסטי | ✅ |
| שימוש בשירות חיצוני בתשלום | ✅ |

---

## 9. מבנה הריפו — מפה מהירה

```
index.html              ← האתר הסטטי החי
RULES.md                ← כללים מחייבים (מקור האמת)
AGENTS.md               ← הוראות ל-AI/Claude
STATE/
  full-repo-truth-report.md  ← זיכרון הפרויקט
metadata/
  index.json            ← רשימת כל הקבצים
  site-structure.json   ← מבנה ניווט
  taxonomy.json         ← סיווגים חוקיים
  authors.json          ← מחברים
files/
  middle-school/        ← PDF כיתות ז-ט
  high-school/          ← PDF חטיבה עליונה
scripts/
  add-file.py           ← הוספת קובץ בודד
  batch-add.py          ← הוספת קבצים מרובים
  validate-all.sh       ← 32 בדיקות
  test-logic.py         ← בדיקת ניווט
  qa-browser.js         ← QA Playwright
docs/
  ADDING_REAL_FILES.md        ← מדריך הוספת קבצים
  EDITING_GUIDE.md            ← מדריך עריכה
  GPT_TO_CLAUDE_FILE_HANDOFF.md ← פרוטוקול handoff
  SCALE_READINESS.md          ← מדיניות גדילה
  ANALYTICS_OPTIONS.md        ← אפשרויות tracking
  REQUIREMENTS_GAP_AUDIT.md   ← ביקורת פערים
  CONTINUITY_GUIDE.md         ← מסמך זה
```

---

## 10. הפרויקט עדיין בשלב ראשוני

מה קיים:
- ✅ 4 קבצי PDF אמיתיים
- ✅ אתר חי ב-GitHub Pages
- ✅ כלי ייבוא מוכנים
- ✅ תיעוד מלא

מה חסר:
- ⏳ עשרות/מאות קבצים אמיתיים (ממתין ליניב)
- ⏳ קבצים לחטיבה עליונה (ממתין ליניב)
- ⏳ שנה/מחבר לקבצים קיימים (ממתין ליניב)

**הפרויקט יהיה 100% כשיניב יוסיף קבצים אמיתיים לכל שכבה ורמה.**

ראה: `docs/ADDING_REAL_FILES.md` ו-`docs/GPT_TO_CLAUDE_FILE_HANDOFF.md`
