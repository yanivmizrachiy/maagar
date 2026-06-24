# maagar — מאגר מתמטיקה

מאגר קבצים ואתר סטטי בעברית לחומרי מתמטיקה.

## מצב נוכחי

- אתר GitHub Pages סטטי בעברית RTL.
- 321 קבצים חיים באתר לפי `metadata/index.json`.
- חלוקה מדווחת: ז׳ 104, ח׳ 134, ט׳ 80, חטיבה עליונה 3.
- אין backend.
- הקבצים עצמם נשמרים תחת `files/`.
- הסינון והחיפוש מבוססים על `metadata/index.json`.
- האתר ממיין ומארגן את הקבצים לפי שכבה › תחום › נושא › סוג קובץ › שנה › כותרת.
- קבצי `repo-file` מקבלים הורדה ישירה אמיתית רק כאשר יש `path`, `file_name`, ו־`download_ready=true`.

## כלל עבודה מרכזי

`RULES.md` הוא דף הכללים היחיד של הריפו.

כל מסמך אחר הוא נתונים, דוח מצב, מדריך או כלי — לא מקור כללים.

## הגנות אוטומטיות חשובות

הריפו כולל בדיקה קבועה:

```bash
python3 scripts/validate-real-buttons.py
```

הבדיקה מוודאת:

- אין כיתובי דמו גלויים באתר הפעיל.
- אין ערכי `#`, `javascript:void(0)` או `demo` ב־metadata הפעיל.
- כפתורי צפייה והורדה נשענים על קבצים אמיתיים תחת `files/`.
- כפתור `הורדה מהירה` מופיע רק כשיש הורדה ישירה אמיתית.
- ארגון הקבצים באתר נשמר לפי שכבה › תחום › נושא.
- ההגנה מחוברת גם ל־`.github/workflows/validate.yml` וגם ל־`.github/workflows/site-button-smoke.yml`.

## מבנה עיקרי

```text
index.html
RULES.md
AGENTS.md
metadata/
  index.json
  taxonomy.json
  site-structure.json
files/
  middle-school/
  high-school/
scripts/
  validate-all.sh
  test-logic.py
  topic-organizer.py
  validate-real-buttons.py
STATE/
docs/
```

## סידור נושאים

המאגר כולל כלי ראשון לסידור נושאים וקיבוץ קבצים דומים:

```bash
python3 scripts/topic-organizer.py
python3 scripts/topic-organizer.py --apply
bash scripts/validate-all.sh && python3 scripts/test-logic.py
```

המטרה: קבצים באותו נושא, למשל `משוואות בשני נעלמים`, יקבלו topic אחיד ויופיעו יחד באתר וב־metadata.
