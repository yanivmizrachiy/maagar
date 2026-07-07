# maagar — מאגר מתמטיקה

מאגר קבצים ואתר סטטי בעברית לחומרי מתמטיקה.

## מצב נוכחי

- אתר GitHub Pages סטטי בעברית RTL.
- 319 קבצים חיים באתר לפי מקור האמת המחייב `RULES.md` ו־`metadata/index.json`.
- אין backend.
- הקבצים עצמם נשמרים תחת `files/`.
- הסינון והחיפוש מבוססים על `metadata/index.json`.
- האתר ממיין ומארגן את הקבצים לפי שכבה › תחום › קבצים, כאשר `topics` נשארים metadata, תגיות וחיפוש.
- באתר קיימים כפתורי מיון נוחים: מיון חכם, חדש → ישן, לפי שם, לפי סוג.
- האתר כולל שער שכבות יוקרתי עם כרטיסי כניסה גדולים לכיתה ז׳, כיתה ח׳, כיתה ט׳ וחטיבה עליונה.
- הניווט הפעיל הוא: בית (בחירת שכבה) → שכבה (כפתורי תחום: אלגברה, גיאומטריה, עבודות סיכום, מבחנים, שונות) → רשימת קבצים ישירה בתחום.
- אין שלב נושא חובה בין תחום לרשימת הקבצים.
- לחיצה על שם משימה/קובץ פותחת מסך צפייה מפוצל: תצוגה מוטמעת בצד אחד ופרטי המשימה + כפתורי פעולה בצד השני.
- בכל רמה מוצג כפתור "חזרה" שעולה רמה אחת.
- החיפוש והסידור משתמשים במפתחות מחושבים מראש לשיפור ביצועים.
- קבצי `repo-file` מקבלים הורדה ישירה אמיתית רק כאשר יש `path`, `file_name`, ו־`download_ready=true`.
- שכבת הניווט היוקרתי למורים נמצאת ב־`assets/site-premium-nav.css`.
- שכבת רשימת המשימות הישירה והמסך המפוצל נמצאת ב־`assets/site-direct-tasks.js` וב־`assets/site-direct-tasks.css`.
- סיווג מבחנים בטוח מתבצע באמצעות `scripts/classify-exams.py` במצב dry-run כברירת מחדל.

## כלל עבודה מרכזי

`RULES.md` הוא דף הכללים היחיד של הריפו.

כל מסמך אחר הוא נתונים, דוח מצב, מדריך או כלי — לא מקור כללים.

## הגנות אוטומטיות חשובות

הריפו כולל בדיקות קבועות:

```bash
python3 scripts/validate-site-shell.py
python3 scripts/validate-direct-task-flow.py
python3 scripts/validate-real-buttons.py
```

הבדיקות מוודאות:

- אין כיתובי פיתוח גלויים באתר הפעיל.
- אין קישורי placeholder או ערכי בדיקה לא אמיתיים ב־metadata הפעיל.
- כפתורי צפייה והורדה נשענים על קבצים אמיתיים תחת `files/`.
- כפתור `הורדה מהירה` מופיע רק כשיש הורדה ישירה אמיתית.
- ארגון הקבצים באתר נשמר לפי שכבה › תחום › קבצים.
- אין חזרה לזרימת תחום › נושא › קבצים כשלב חובה.
- לחיצה על משימה פותחת split viewer עם פרטים וכפתורי פעולה.
- כפתורי המיון הנוחים ומפתחות הביצועים נשארים חלק מהאתר.
- ההגנות מחוברות גם ל־`.github/workflows/validate.yml` וגם ל־`.github/workflows/site-button-smoke.yml`.

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
assets/
  site.js
  site-direct-tasks.js
  site-direct-tasks.css
  site-url-state.js
scripts/
  validate-all.sh
  test-logic.py
  topic-organizer.py
  classify-exams.py
  validate-site-shell.py
  validate-direct-task-flow.py
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

המטרה: קבצים באותו נושא, למשל `משוואות בשני נעלמים`, יקבלו topic אחיד ויופיעו יחד ב־metadata, בחיפוש, בתגיות ובסינונים — בלי להפוך topic לשלב ניווט חובה.
