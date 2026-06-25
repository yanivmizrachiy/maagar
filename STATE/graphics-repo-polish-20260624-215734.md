# משימת שדרוג גרפיקה וסידור ריפו — 20260624-215734

## מטרה
לשדרג את אתר maagar לרמה יוקרתית, מסודרת ונוחה למורים, בלי דמו, בלי קבצים פיקטיביים ובלי לשבור metadata.

## קבצים שמותר לשפר
- assets/site.css
- assets/site-premium-nav.css
- assets/site-highschool-units.css
- assets/site.js רק אם צריך שיפור מבנה UI אמיתי
- index.html רק אם צריך חיבור CSS/JS אמיתי
- docs/README רק לתיעוד, לא לכללים
- RULES.md רק אם נוסף כלל מחייב אמיתי

## אסור
- לא למחוק קבצים אמיתיים
- לא להמציא metadata
- לא להוסיף placeholder או demo
- לא לשכפל קובץ כדי שיופיע בכמה שכבות
- לא לשנות סיווג בלי ראיה מהשם/נתיב/metadata

## שדרוג גרפי נדרש
- שער שכבות יוקרתי וברור
- מרכז שכבה נוח: אלגברה, גיאומטריה, עבודות סיכום, מבחנים
- חטיבה עליונה לפי 3/4/5 יחידות
- כרטיסי קובץ נקיים עם מחבר, שנה, שכבות, יחידה, תחום, סוג, מקור
- עיצוב רגוע, יוקרתי, קריא בזום ובטלפון
- RTL מלא
- אין עומס חזותי

## סידור ריפו נדרש
- בדיקת קבצי מפתח
- בדיקת metadata/index.json
- בדיקת unit_level לחטיבה עליונה
- בדיקת שאין כפתורי דמו
- בדיקת שכל JS עובר node --check

## פקודות חובה אחרי שינוי
python scripts/validate-site-shell.py
python scripts/validate-real-buttons.py
python scripts/validate-highschool-units.py
python scripts/audit-highschool-units.py
node --check assets/site.js
node --check assets/site-url-state.js
git status --short

## תוצאה רצויה
קומיט אחד נקי עם שדרוג גרפי וסידור ריפו, בלי שבירת CI.
