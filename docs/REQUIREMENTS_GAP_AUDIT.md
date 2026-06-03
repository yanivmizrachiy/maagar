# ביקורת פערים — דרישות לעומת יישום

**ריפו:** `yanivmizrachiy/maagar`
**עודכן:** 2026-06-03
**בסיס:** `RULES.md` (24 סעיפים), `AGENTS.md`, `STATE/full-repo-truth-report.md`, בדיקת קוד ישירה

---

## סיכום מנהלים

| קטגוריה | סטטוס |
|---------|-------|
| תשתית ותיעוד | ✅ מלא |
| ממשק משתמש | ✅ מיושם |
| כלי ייבוא | ✅ מיושם |
| תוכן אמיתי | ⏳ ממתין ליניב |
| Analytics | 📋 תועד, ממתין לאישור |
| Scale readiness | 📋 תועד |
| Maintainability guide | 📋 תועד |

---

## רשימת פערים מפורטת

| # | דרישה | מקור | סטטוס | עדות | פעולה הבאה |
|---|-------|------|--------|------|------------|
| 1 | אתר עברי RTL עם גופן Heebo | RULES.md §1 | ✅ מיושם | `index.html` line 10, `dir="rtl"` | — |
| 2 | ניווט: ז׳ / ח׳ / ט׳ / חטיבה עליונה | RULES.md §2–3 | ✅ מיושם | `GRADE_IDENTITY` + JS nav | — |
| 3 | קטגוריות: algebra/geometry/summaries/exams | RULES.md §4 | ✅ מיושם | `CAT_IDENTITY` + taxonomy.json | — |
| 4 | חטיבה עליונה: 3/4/5 יחידות | RULES.md §11 | ✅ מיושם | `UNIT_IDENTITY` + hs-list | — |
| 5 | מבנה תיקיות `files/` | RULES.md §11 | ✅ מיושם | `files/middle-school/` + `files/high-school/` | — |
| 6 | `metadata/index.json` עם 4 רשומות | RULES.md §19 | ✅ מיושם | 4 PDF, content_hash מאומת | — |
| 7 | content_hash integrity | RULES.md §19 | ✅ מיושם | `validate-all.sh` check §2 | — |
| 8 | PDF embed עם iframe + fallback | RULES.md §16 | ✅ מיושם | Playwright verified, PR #6 | — |
| 9 | חיפוש client-side + filters | RULES.md §20 | ✅ מיושם | `renderSearch()`, PR #7 | — |
| 10 | כלי ייבוא: add-file.py | RULES.md §10 | ✅ מיושם | `scripts/add-file.py` | — |
| 11 | כלי ייבוא: batch-add.py | RULES.md §10 | ✅ מיושם | `scripts/batch-add.py` | — |
| 12 | מניפסט CSV לייבוא batch | AGENTS.md §10 | ✅ מיושם | `scripts/manifest-example.csv` | — |
| 13 | פרוטוקול handoff GPT→Claude | AGENTS.md §10 | ✅ מיושם | `docs/GPT_TO_CLAUDE_FILE_HANDOFF.md` | — |
| 14 | validate-all.sh — 26 בדיקות | RULES.md §15 | ✅ מיושם | 26/26 PASSED | — |
| 15 | test-logic.py | RULES.md §15 | ✅ מיושם | 4/4 files reached | — |
| 16 | Playwright QA | RULES.md §15 | ✅ מיושם | 53/53 PASSED (PR #6) | — |
| 17 | כפתורי הורדה + הדפסה | RULES.md §16 | ✅ מיושם | `.act-download`, `.act-print` | — |
| 18 | Responsive (mobile) | RULES.md §14 | ✅ מיושם | `@media (max-width: 520px)` | — |
| 19 | empty state בעברית | RULES.md §14 | ✅ מיושם | `.empty-state` | — |
| 20 | breadcrumbs ניווטיים | RULES.md §14 | ✅ מיושם | `<button>` בסרגל breadcrumbs | — |
| 21 | אין קבצי דמו | RULES.md §22 | ✅ מיושם | contamination scan | — |
| 22 | .gitattributes LF | RULES.md §3 | ✅ מיושם | `.gitattributes` | — |
| 23 | AUTHORS.md / authors.json | AGENTS.md §1 | ✅ מיושם (ריק) | `metadata/authors.json` ריק לפי כלל | ממתין ליניב |
| 24 | מידע scale readiness | דרישה חדשה | ✅ תועד | `docs/SCALE_READINESS.md` | — |
| 25 | מידע analytics options | דרישה חדשה | ✅ תועד | `docs/ANALYTICS_OPTIONS.md` | ממתין לאישור יניב |
| 26 | מדריך עריכה (EDITING_GUIDE) | דרישה חדשה | ✅ תועד | `docs/EDITING_GUIDE.md` | — |
| 27 | Design tokens מרוכזים | RULES.md §14 | ✅ בקוד | CSS `:root` vars | — |
| 28 | קבצים לכל שכבה/קטגוריה | RULES.md §23 | ⏳ ממתין | רק grade-7/8/9 חלקי | ממתין ליניב לספק קבצים |
| 29 | קבצים לחטיבה עליונה | RULES.md §23 | ⏳ ממתין | `high-school/` ריק | ממתין ליניב |
| 30 | year + author אמיתיים | RULES.md §19 | ⏳ ממתין | כרגע `"unknown"` | ממתין ליניב |
| 31 | `metadata/authors.json` מאוכלס | AGENTS.md §1 | ⏳ ממתין | ריק | ממתין ליניב |
| 32 | Analytics implementation | RULES.md §21 | 📋 ממתין לאישור | `docs/ANALYTICS_OPTIONS.md` | ממתין לאישור יניב |

---

## פערים שנסגרו ב-PR הנוכחי

| פריט | נסגר |
|------|------|
| `docs/SCALE_READINESS.md` | ✅ |
| `docs/ANALYTICS_OPTIONS.md` | ✅ |
| `docs/REQUIREMENTS_GAP_AUDIT.md` | ✅ (מסמך זה) |
| `docs/EDITING_GUIDE.md` | ✅ |

---

## פערים שממתינים ליניב (לא ניתן ל-AI לסגור)

| פריט | סיבה |
|------|------|
| תוכן אמיתי לכל שכבה | יניב צריך לספק קבצים |
| חטיבה עליונה | יניב צריך לספק קבצים |
| year/author אמיתיים | יניב יודע מי כתב ומתי |
| Analytics | דורש אישור מפורש של יניב |

---

## לגבי "מה לא חסר"

כל הדרישות הבאות **נוצרו ונשמרו בריפו** (לא רק בשיחה):
- `RULES.md` — מקור האמת
- `AGENTS.md` — הוראות ל-AI
- `STATE/full-repo-truth-report.md` — מצב אמיתי
- כל ה-docs/ — תיעוד מלא
- כל ה-scripts/ — כלים אוטומטיים
