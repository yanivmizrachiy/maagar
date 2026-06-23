# MAAGAR RULES — דף הכללים היחיד

Repository: `yanivmizrachiy/maagar`
Last updated: 2026-06-23

## 1. כלל עליון

`RULES.md` הוא **דף הכללים היחיד** של הריפו.

אין לשמור כללים מחייבים ב־`AGENTS.md`, `STATE/`, `docs/`, הודעות צ׳אט, קומיטים או PR descriptions. אם יש כלל חדש, החלטת ארגון, מדיניות AI, מדיניות תצוגה, מדיניות סיווג או דרישת עבודה — היא נכנסת לכאן בלבד.

שאר הקבצים מותרים, אבל תפקידם מוגבל:
- `metadata/` — נתונים פעילים של המאגר.
- `AGENTS.md` — הפניה קצרה לסוכנים: לקרוא את `RULES.md` ולעבוד לפי פקודות הבדיקה.
- `STATE/full-repo-truth-report.md` — דוח מצב בלבד, לא כללים.
- `docs/` — מדריכים והסברים בלבד, לא כללים.
- `scripts/` — כלים אוטומטיים בלבד.

אם יש סתירה: `RULES.md` גובר. אם יש ספק: לא מנחשים.

## 2. מטרת הריפו

הריפו הוא מאגר אמיתי של חומרי מתמטיקה, וגם אתר סטטי עברי להצגת החומרים לפי שכבה, תחום, נושא, סוג ורמה.

הריפו חייב לתמוך ב:
- שמירת קבצים אמיתיים בלבד.
- הצגת קבצים באתר GitHub Pages בעברית RTL.
- סיווג חומרים לפי metadata.
- חיפוש וסינון חכמים לפי שכבה, נושא, סוג, כותרת ותגיות.
- מניעת כפילויות לפי `content_hash`.
- התאמת קובץ אחד לכמה כיתות/נושאים בלי לשכפל אותו פיזית.

אסור ליצור דמו, קובץ פיקטיבי, כרטיסייה פיקטיבית, metadata מומצא או טענה שפיצ׳ר עובד אם לא אומת.

## 3. מצב אמת נוכחי

נכון ל־2026-06-23:

- ריפו: `yanivmizrachiy/maagar`.
- אתר חי: GitHub Pages.
- מבנה: סטטי, ללא backend.
- מקור אמת לקבצים: `metadata/index.json`.
- קבצים חיים באתר: 321.
- חלוקה מדווחת: ז׳ 104, ח׳ 134, ט׳ 80, חטיבה עליונה 3.
- PR #13 הכניס מאגר גדול של קבצים אמיתיים.
- PR #15 הוסיף כלי סידור נושאים: `scripts/topic-organizer.py`.

אין להחזיר את הריפו למצב הישן של “4 קבצים”. כל מסמך ישן שטוען זאת נחשב לא מעודכן.

## 4. מבנה אתר מחייב

עמוד ראשי:
1. שכבת ז׳
2. שכבת ח׳
3. שכבת ט׳
4. חטיבה עליונה

בכל שכבת ז׳/ח׳/ט׳:
1. אלגברה
2. גיאומטריה
3. משימות מסכמות
4. מבחנים
5. חומרים שונים — מוצג רק כשיש קבצים לא מסווגים/unknown.

בחטיבה עליונה:
1. 3 יחידות
2. 4 יחידות
3. 5 יחידות

הסינון האמיתי נעשה לפי `metadata/index.json`; התיקיות הן כלי עזר בלבד.

## 5. מבנה תיקיות מחייב

```text
files/
  middle-school/
    grade-7/
      algebra/
      geometry/
      summaries/
      exams/
      uncategorized/
    grade-8/
      algebra/
      geometry/
      summaries/
      exams/
      uncategorized/
    grade-9/
      algebra/
      geometry/
      summaries/
      exams/
      uncategorized/
  high-school/
    3-unit/
    4-unit/
    5-unit/
    unknown/
metadata/
scripts/
STATE/
docs/
```

לא משכפלים קובץ כדי שיופיע בכמה מקומות. קובץ נשמר פיזית פעם אחת, ושיוך לכמה כיתות/נושאים נעשה דרך `grades`, `topics`, ו־metadata.

## 6. שדות חובה ב־metadata

כל פריט ב־`metadata/index.json` חייב לכלול לפחות:

- `id`
- `title`
- `path` או `source_url`
- `file_name`
- `extension`
- `content_hash` כשזה קובץ פיזי
- `school_stage`
- `grade`
- `grades`
- `unit_level`
- `track`
- `primary_category`
- `topics`
- `document_type`
- `exam_kind`
- `bagrut_questionnaire`
- `year`
- `author`
- `source_type`
- `source_url`
- `embed_url`
- `can_embed`
- `print_ready`
- `download_ready`
- `tags`
- `notes`

אם פרט לא ידוע: לכתוב `unknown`. לא לנחש מחבר, שנה, נושא, רמה או מקור.

## 7. ערכים חוקיים מרכזיים

`school_stage`: `middle-school`, `high-school`, `unknown`.

`grade`: `7`, `8`, `9`, `high-school`, `unknown`.

`unit_level`: `3-unit`, `4-unit`, `5-unit`, `unknown`.

`primary_category`: `algebra`, `geometry`, `summaries`, `exams`, `uncategorized`, `unknown`.

`document_type`: `worksheet`, `summary-work`, `exam`, `link`, `digital-task`, `printable-task`, `embedded-resource`, `mixed`, `unknown`.

`source_type`: `repo-file`, `external-link`, `embed`, `mixed`, `unknown`.

`can_embed`, `print_ready`, `download_ready`: `true`, `false`, או `unknown`.

אם מוסיפים ערך חדש — חובה לעדכן גם `metadata/taxonomy.json` וגם את הדף הזה.

## 8. סידור נושאים

המטרה: קבצים מאותו נושא יופיעו אחד ליד השני באתר וב־metadata.

כל קובץ צריך לקבל `topics` אמיתיים ככל האפשר. דוגמאות לנושאים קנוניים:

אלגברה:
- ביטויים אלגבריים
- הצבה
- משוואות
- משוואות בשני נעלמים
- מערכת משוואות
- פונקציה קווית
- פונקציה ריבועית
- משוואות ריבועיות
- יחס ופרופורציה
- אחוזים
- חוקיות וסדרות
- מערכת צירים
- מספרים מכוונים

גיאומטריה:
- זוויות
- משולשים
- חפיפת משולשים
- דמיון משולשים
- דלתון
- מלבן וריבוע
- מקבילית
- מעוין
- טרפז
- קטע אמצעים
- משפט פיתגורס
- גיאומטריה אנליטית

מבחנים וסיכומים:
- מבחן מיון והקבצה
- מבחן מחצית
- מבחן סוף שנה
- קורס קיץ
- עבודת סיכום

כלי הסידור: `python3 scripts/topic-organizer.py`.
ברירת מחדל: dry-run בלבד.
שינוי אמיתי: `python3 scripts/topic-organizer.py --apply`.

אין להפעיל `--apply` בלי להריץ אחר כך:

```bash
bash scripts/validate-all.sh && python3 scripts/test-logic.py
```

## 9. כפילויות

כפילות נקבעת לפי תוכן, לא לפי שם.

- אם `content_hash` כבר קיים — לא מוסיפים עותק נוסף.
- אם אותו קובץ מתאים לכמה כיתות — מעדכנים `grades`.
- אם אותו קובץ מתאים לכמה נושאים — מעדכנים `topics`.
- אם יש קבצים עם אותו שם אבל hash שונה — לא מוחקים אוטומטית; מסמנים לבדיקה.

## 10. קבצים גדולים והטמעה

- קובצי PDF רגילים יכולים להיות ב־`files/`.
- קובץ מעל 10MB דורש תשומת לב.
- קובץ מעל 50MB לא מיועד להטמעה רגילה באתר.
- קובץ כבד יכול להיות `download_ready=true`, אבל `can_embed=false` ו־`print_ready=false` אם הוא לא מתאים לנייד.
- הדוגמה הקיימת: `חוברת.pdf` בגודל 97MB מסומן כבד מדי להטמעה.

אין להבטיח הדפסה שקטה, הורדה או הטמעה אם הדפדפן/הקובץ לא מאפשרים זאת.

## 11. עבודה עם AI / Codex / GPT / Claude

לפני כל שינוי בריפו:

```bash
git status
bash scripts/validate-all.sh
python3 scripts/test-logic.py
```

אחרי כל שינוי:

```bash
bash scripts/validate-all.sh && python3 scripts/test-logic.py
```

אם שינוי משפיע על UI:

```bash
node scripts/qa-browser.js
```

מותר ל־AI לבצע בלי לשאול:
- תיקוני metadata בטוחים.
- סידור נושאים לפי כותרת/נתיב קיימים.
- תיקון תיעוד לא מעודכן.
- הוספת בדיקות או כלי dry-run.
- PR/merge כאשר השינוי בטוח והבדיקות עוברות.

חובה לשאול לפני:
- מחיקת קובץ אמיתי.
- Force push.
- שינוי נראות הריפו.
- שימוש בשירותים בתשלום.
- טיפול בסיסמאות/סודות.
- שינוי ארכיטקטורה גדול.

## 12. סדר עדיפויות קבוע

1. אמת בלבד.
2. לא למחוק קבצים אמיתיים בלי אישור.
3. `RULES.md` הוא דף הכללים היחיד.
4. `metadata/index.json` הוא מקור האמת של הקבצים הפעילים.
5. קובץ פיזי פעם אחת; שיוכים דרך metadata.
6. נושאים דומים צריכים להיות מקובצים יחד.
7. כל שינוי חייב לעבור validation.
8. לא להשאיר סתירות תיעודיות שמטעות סוכני AI.
