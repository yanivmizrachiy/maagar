# maagar — מאגר מתמטיקה

מאגר קבצים ואתר סטטי בעברית לחומרי מתמטיקה.

## מצב נוכחי

- אתר GitHub Pages סטטי בעברית RTL.
- 321 קבצים חיים באתר לפי `metadata/index.json`.
- חלוקה מדווחת: ז׳ 104, ח׳ 134, ט׳ 80, חטיבה עליונה 3.
- אין backend.
- הקבצים עצמם נשמרים תחת `files/`.
- הסינון והחיפוש מבוססים על `metadata/index.json`.

## כלל עבודה מרכזי

`RULES.md` הוא דף הכללים היחיד של הריפו.

כל מסמך אחר הוא נתונים, דוח מצב, מדריך או כלי — לא מקור כללים.

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
