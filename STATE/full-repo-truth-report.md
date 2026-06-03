# דוח אמת מלא — maagar
# Full Repository Truth Report

**ריפו:** `yanivmizrachiy/maagar`
**תאריך עדכון:** 2026-06-03
**ענף ראשי:** `main` (SHA: `4ff5ce4` — PR #11 מוזג)

---

## A. סיכום מצב נוכחי

| פריט | ערך |
|------|-----|
| ריפו | `yanivmizrachiy/maagar` |
| נראות | ציבורי (public) |
| שפה | עברית RTL |
| GitHub Pages | **פעיל** ✅ |
| Last Pages Deploy | PR #11 → SHA `4ff5ce4` |
| אתר חי | `https://yanivmizrachiy.github.io/maagar/` |
| קבצים אמיתיים | 4 PDF |
| רשומות באינדקס | 4 |
| Backend | אין — הכל סטטי |
| עיצוב | Premium redesign v2 (PR #11) ✅ |
| חיפוש | חיפוש חי client-side + פילטרים (PR #7) ✅ |
| כלי ייבוא | add-file.py + batch-add.py + _ingest.py (PR #9) ✅ |
| פרוטוקול handoff | docs/GPT_TO_CLAUDE_FILE_HANDOFF.md (PR #10) ✅ |
| תיעוד | RULES.md 25 סעיפים + AGENTS.md + 6 docs/ מסונכרנים |
| validate-all.sh | 32 בדיקות (היה 26) |

---

## B. היסטוריית PR

| PR | כותרת | מיזוג |
|----|-------|-------|
| #1 | feat: Hebrew RTL static website + metadata + validation | ✅ merged |
| #2 | fix+feat: QA pass — uncategorized visibility, logic tests, accessibility | ✅ merged |
| #3 | feat: UI improvements + LF line endings (.gitattributes) | ✅ merged |
| #4 | feat(design): premium UI redesign | ✅ merged |
| #5 | feat: mobile polish + STATE update | ✅ merged |
| #6 | feat: Playwright QA + add-file.py + can_embed verified | ✅ merged |
| #7 | feat: client-side search + docs/ADDING_REAL_FILES.md | ✅ merged |
| #8 | chore: sync RULES.md requirements, fix HS folder structure | ✅ merged |
| #9 | feat(ingestion): batch-add.py, _ingest.py, hash integrity, improved add-file.py | ✅ merged |
| #10 | docs: GPT→Claude handoff protocol, first-import checklist, AGENTS sync | ✅ merged |
| #11 | feat: docs, maintainability, visual design upgrade | ✅ merged |
| #12 | feat: continuity system, CONTINUITY_GUIDE.md, startup protocol | 🔄 in progress |

---

## C. קבצי מפתח

```
index.html                    ← אתר סטטי עברי RTL (חי על GitHub Pages)
.gitattributes                ← אכיפת LF על כל ה-OS
RULES.md                      ← מקור האמת המחייב
AGENTS.md                     ← הוראות עבודה + workflow הוספת קבצים
README.md                     ← תיאור הריפו
metadata/
  index.json                  ← אינדקס 4 פריטים אמיתיים
  taxonomy.json               ← מילון סיווגים
  site-structure.json         ← מבנה ניווט ועיצוב
  authors.json                ← מילון מחברים
files/
  middle-school/grade-7/uncategorized/  ← 1 PDF (מאגר ז׳) — 15.6MB
  middle-school/grade-8/algebra/        ← 1 PDF (יחס/פרופורציה/קנה מידה) — 375KB
  middle-school/grade-8/summaries/      ← 1 PDF (דפי סיכום) — 439KB
  middle-school/grade-9/geometry/       ← 1 PDF (ריכוז שאלות דלתון) — 2.9KB
  high-school/                          ← ריק (.gitkeep)
docs/
  ADDING_REAL_FILES.md        ← מדריך + First Import Checklist (7 שלבים)
  GPT_TO_CLAUDE_FILE_HANDOFF.md ← פרוטוקול handoff מ-ChatGPT לקלוד
  SCALE_READINESS.md          ← מדיניות גדילה + GitHub Pages limits
  ANALYTICS_OPTIONS.md        ← אפשרויות tracking (ממתין לאישור יניב)
  REQUIREMENTS_GAP_AUDIT.md   ← ביקורת פערים
  EDITING_GUIDE.md            ← מדריך עריכה בעברית
  CONTINUITY_GUIDE.md         ← מדריך המשכיות + startup protocol
scripts/
  validate-all.sh             ← 33 בדיקות: JSON, content_hash, שדות, taxonomy, contamination, key files, nav
  validate-index.sh           ← אימות אינדקס בלבד
  test-logic.py               ← בדיקת כיסוי ניווט: כל הקבצים נגישים
  serve-local.sh              ← שרת פיתוח מקומי
  add-file.py                 ← CLI לקובץ בודד (hash, dup-check, --yes, --can-embed, --dry-run)
  batch-add.py                ← CLI לבאץ׳: --folder או --manifest CSV
  _ingest.py                  ← מודול שיתופי (sha1, slugify, build_record, run_checks)
  manifest-example.csv        ← תבנית CSV לייבוא batch
  qa-browser.js               ← Playwright QA suite (53 בדיקות, desktop + mobile)
STATE/
  full-repo-truth-report.md   ← המסמך הזה
```

---

## D. 4 הקבצים האמיתיים — מצב מפורט

| כיתה | קטגוריה | כותרת | גודל | download | print | can_embed |
|------|---------|-------|------|----------|-------|-----------|
| 7 | uncategorized → "חומרים שונים" | מאגר ז | 15.6MB | ✅ | ✅ | ✅ **true** (Playwright verified) |
| 8 | algebra | יחס-פרופ-קנה מידה | 375KB | ✅ | ✅ | ✅ **true** (Playwright verified) |
| 8 | summaries | כיתה ח - יחס פרופורציה | 439KB | ✅ | ✅ | ✅ **true** (Playwright verified) |
| 9 | geometry | ריכוז שאלות דלתון | 2.9KB | ✅ | ✅ | ✅ **true** (Playwright verified) |

**`can_embed` status:** כל 4 ה-PDF נבדקו בהצלחה עם Playwright (iframe נטען ללא fallback — PR #6).

**הערה על grade-9 PDF:** 2.9KB — קובץ PDF תקין (header מאומת), אך קטן מאוד. ייתכן שהוא דף בודד פשוט.

**הערה על grade-7 PDF:** 15.6MB — גדול יחסית. עשוי לטעון לאט על ניידים.

---

## E. כיסוי ניווט (אומת ב-test-logic.py)

| נתיב | קבצים |
|------|-------|
| בית → שכבת ז׳ → חומרים שונים | 1 ✅ |
| בית → שכבת ח׳ → אלגברה | 1 ✅ |
| בית → שכבת ח׳ → משימות מסכמות | 1 ✅ |
| בית → שכבת ט׳ → גיאומטריה | 1 ✅ |
| בית → חטיבה עליונה → כל רמה | 0 (ריק, empty state מוצג) |

**קבצים יתומים:** אין ✅

---

## F. תוצאות אימות מלאות (POST PR #11)

```
bash scripts/validate-all.sh
→ 32/32 PASSED, 0 FAILED  (היה 26 — נוספו 6 בדיקות docs)

python3 scripts/test-logic.py
→ ALL LOGIC CHECKS PASSED
→ Files total: 4, Files reached: 4, Errors: 0

node scripts/qa-browser.js
→ 53/53 PASSED (desktop + mobile)
```

---

## G. תכונות האתר הפעיל (POST PR #11)

| תכונה | מצב |
|-------|-----|
| עברית RTL | ✅ |
| גופן Heebo | ✅ |
| Hero section + stats bar | ✅ |
| אנימציית כניסה לכל מסך | ✅ |
| 4 כרטיסי שכבה עם זהות צבעונית ייחודית | ✅ |
| 4 כרטיסי קטגוריה עם זהות צבעונית | ✅ |
| כפתור "חומרים שונים" כשיש קבצים לא מסווגים | ✅ |
| 3 כרטיסי יחידות לחטיבה עליונה | ✅ |
| כרטיסיות קבצים אמיתיות עם סרט צבע לפי סוג מסמך | ✅ |
| empty state בעברית עם עיצוב premium | ✅ |
| כפתורי הורדה | ✅ |
| כפתורי הדפסה | ✅ |
| מודאל PDF עם backdrop blur + slide-up | ✅ |
| breadcrumbs כ-`<button>` אמיתי | ✅ |
| כפתור חזרה | ✅ |
| Responsive (נייד + מחשב) | ✅ |
| focus-visible accessibility | ✅ |
| גרמר עברי נכון (קובץ אחד / X קבצים) | ✅ |
| LF line endings אכופים דרך .gitattributes | ✅ |
| ללא תוכן דמו | ✅ |
| חיפוש חי עם פילטר-chips (grade + doctype) | ✅ |
| PDF embed + loading state + fallback | ✅ |
| מודאל PDF מאומת (Playwright) | ✅ |
| add-file.py — CLI לקובץ בודד | ✅ |
| batch-add.py — CLI לבאץ׳ (folder + CSV manifest) | ✅ |
| _ingest.py — מודול שיתופי | ✅ |
| validate-all.sh — content_hash integrity check | ✅ |
| docs/ADDING_REAL_FILES.md — מדריך + first-import checklist | ✅ |
| docs/GPT_TO_CLAUDE_FILE_HANDOFF.md — פרוטוקול handoff | ✅ |
| docs/SCALE_READINESS.md — מדיניות גדילה + GitHub Pages limits | ✅ |
| docs/ANALYTICS_OPTIONS.md — אפשרויות tracking (ממתין לאישור) | ✅ |
| docs/REQUIREMENTS_GAP_AUDIT.md — ביקורת פערים | ✅ |
| docs/EDITING_GUIDE.md — מדריך עריכה בעברית | ✅ |
| docs/CONTINUITY_GUIDE.md — מדריך המשכיות + startup protocol | ✅ |
| RULES.md §25 — כלל תחזוקה ועיצוב נקי | ✅ |
| validate-all.sh — 26 → 32 → 33 בדיקות | ✅ |
| עיצוב ויזואלי v2 — unit cards grid, type strip 4px, hover glow | ✅ |

---

## H. מה חסר / עדיין לא בוצע

| פריט | מצב | עדיפות |
|------|-----|--------|
| **קבצים אמיתיים** — הרחבה (כל שכבה/קטגוריה) | ⏳ ממתין ליניב | **גבוהה ביותר** |
| קבצים לחטיבה עליונה (3/4/5 יחידות) | ⏳ ממתין ליניב | **גבוהה** |
| `year` + `author` אמיתיים ל-4 קבצים קיימים | ⏳ ממתין ליניב | בינונית |
| metadata/authors.json עם מחברים אמיתיים | ⏳ ממתין ליניב | נמוכה |
| סינון מורחב / מיון / ייצוא | ❌ | עתידי |

**הכלים מוכנים. הפעולה הבאה היא של יניב:** לספק קבצים אמיתיים לייבוא.
ראה: `docs/ADDING_REAL_FILES.md` → First Import Checklist.

---

## I. כיצד לאמת `can_embed`

```bash
# הרץ שרת פיתוח
bash scripts/serve-local.sh
# פתח http://localhost:8080
# נווט לשכבת ח׳ → אלגברה → לחץ "צפייה"
# אם PDF מוצג ב-iframe: עדכן can_embed=true
# אם לא: can_embed=false
```

---

## J. כיצד להוסיף קובץ חדש

ראה `AGENTS.md` סעיף 10 — תהליך מלא.

תמצית:
1. קבל קובץ מיניב + מטא-דאטה
2. חשב SHA-1, בדוק כפילות
3. שמור ב-`files/<path>/`
4. הוסף רשומה ל-`metadata/index.json`
5. הרץ `bash scripts/validate-all.sh && python3 scripts/test-logic.py`
6. Commit + push + PR + merge

---

## K. פקודות שימושיות

```bash
# אימות מלא לפני כל push
bash scripts/validate-all.sh && python3 scripts/test-logic.py

# שרת פיתוח מקומי
bash scripts/serve-local.sh
# → http://localhost:8080
```

---

*דוח זה עודכן אוטומטית. כל הנתונים מבוססים על קריאה ישירה מהריפו ועל הרצת סקריפטי אימות.*
