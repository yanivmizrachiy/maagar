# AGENTS.md

קובץ זה מיועד ל־GPT / Codex / AI / סוכן אוטומטי שעובד עם הריפו `yanivmizrachiy/maagar`.

## 1. לפני כל פעולה

חובה לקרוא קודם:

1. `RULES.md`
2. `metadata/index.json`
3. `metadata/taxonomy.json`
4. `metadata/authors.json`
5. `metadata/site-structure.json` אם קיים

`RULES.md` הוא מקור האמת המחייב.
אם יש סתירה בין קובץ ישן לבין `RULES.md`, פועלים לפי `RULES.md`.

---

## 2. מהו הריפו הזה

זהו מאגר קבצים אמיתי לחומרי מתמטיקה, וגם מקור נתונים מוכן לאתר אינטרנט עברי גדול בעתיד.

הריפו צריך לתמוך ב:
- שמירת קבצים אמיתיים.
- סיווג קבצים לפי שכבה, תחום, נושא, סוג, שנה, מחבר, רמה ותגיות.
- הצגת קבצים באתר עתידי לפי ניווט קבוע.
- הטמעה של קבצים/משימות כאשר אפשר.
- קישור רגיל כאשר הטמעה אינה אפשרית.
- התאמה של קובץ אחד לכמה כיתות או נושאים בלי לשכפל אותו.

אסור להתייחס לריפו כאל “לא אתר” יותר. ההגדרה החדשה: הריפו הוא מאגר קבצים וגם בסיס נתונים/מבנה לאתר עתידי.

---

## 3. מבנה אתר מחייב

עמוד ראשי עתידי:

1. שכבת ז׳
2. שכבת ח׳
3. שכבת ט׳
4. חטיבה עליונה

בכל שכבה ז׳/ח׳/ט׳:

1. אלגברה
2. גיאומטריה
3. משימות מסכמות
4. מבחנים

בחטיבה עליונה:

1. בגרות במתמטיקה ברמת שלוש יחידות
2. בגרות במתמטיקה ברמת ארבע יחידות
3. בגרות במתמטיקה ברמת חמש יחידות

כל כפתור ורמה צריכים להיות מובחנים בצבעי פרימיום לפי `metadata/site-structure.json`.

---

## 4. מה לעשות כשמוסיפים קובץ

1. לבדוק מה המשתמש נתן במפורש: שם, כיתה, רמה, תחום, סוג, שנה, מחבר, קישור, התאמה לכמה כיתות.
2. לא לנחש פרטים חסרים.
3. לחשב או לזהות `content_hash` אם מדובר בקובץ פיזי.
4. לבדוק אם `content_hash` כבר מופיע ב־`metadata/index.json`.
5. אם `content_hash` כבר קיים — לא להוסיף קובץ חדש; לעדכן שיוכים/מטא־דאטה אם צריך.
6. אם הקובץ חדש — לשמור אותו פעם אחת במיקום פיזי מתאים.
7. להוסיף רשומה ל־`metadata/index.json`.
8. אם הקובץ מתאים לכמה כיתות — להשתמש בשדה `grades` כרשימה.
9. אם הוא מתאים לכמה נושאים — להשתמש בשדה `topics` כרשימה.
10. אם הוא קישור — להשתמש ב־`source_type=external-link`, `source_url`, וללא `content_hash` אלא אם יש דרך אמיתית לחשב תוכן.
11. אם ניתן להטמעה — להוסיף `can_embed=true` ו־`embed_url`.
12. אם לא ניתן להטמעה — `can_embed=false`.
13. אם לא ידוע — `can_embed=unknown`.
14. אם יש סיווג חדש אמיתי — לעדכן גם `metadata/taxonomy.json` וגם `RULES.md`.

---

## 5. שדות מטא־דאטה חשובים

בעת הוספת פריט חדש, יש לשאוף למלא:

- `id`
- `title`
- `path` או `source_url`
- `file_name`
- `extension`
- `content_hash`
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
- `embed_url`
- `can_embed`
- `print_ready`
- `download_ready`
- `tags`
- `notes`

אם שדה לא ידוע, לכתוב `unknown` ולא לנחש.

---

## 6. איך לחשוב על בקשות של המשתמש

דוגמאות:

### בקשה: “תן לי את כל האלגברה של כיתה ט׳”

לסנן לפי:
- `grades` כולל `9` או `grade=9`
- `primary_category=algebra` או `topics` כוללים נושא אלגברי ברור

### בקשה: “תן לי את כל בגרויות 3 יחידות”

לסנן לפי:
- `school_stage=high-school`
- `track=bagrut`
- `unit_level=3-unit`

### בקשה: “תן לי מבחנים של כיתה ח׳”

לסנן לפי:
- `grades` כולל `8` או `grade=8`
- `primary_category=exams` או `document_type=exam`

### בקשה: “תוסיף קישור למשימה מתוקשבת שמתאימה לז׳ וח׳”

להוסיף רשומה עם:
- `source_type=external-link`
- `document_type=digital-task`
- `grades=["7", "8"]`
- `can_embed=true/false/unknown` לפי מצב אמיתי בלבד

---

## 7. סדר עדיפויות

1. דרישות יניב בשיחה הנוכחית.
2. `RULES.md`.
3. `metadata/taxonomy.json`.
4. `metadata/site-structure.json`.
5. מצב הקבצים בפועל בריפו.
6. קבצים ישנים אחרים.

---

## 8. מצב מאומת נוכחי

לפי `metadata/index.json`, קיימות כרגע ארבע רשומות פעילות:

1. `מאגר ז`
2. קובץ כיתה ח׳ בנושא יחס / פרופורציה / קנה מידה
3. קובץ כיתה ח׳ של דפי סיכום על יחס / פרופורציה / קנה מידה
4. ריכוז שאלות דלתון לכיתה ט׳

כל קובץ אחר שלא מופיע באינדקס התקף אינו חלק מהמצב הפעיל.

---

## 9. כלל ברזל

לא להמציא, לא להוסיף דמו, לא לסמן כקיים מה שלא קיים, לא לשכפל קבצים, ולא לבצע שינוי שסותר את `RULES.md`.

---

## 10. תהליך הוספת קובץ אמיתי (New File Workflow)

### כלל מוחלט: לא מוסיפים קבצים עד שיניב מספק קבצים אמיתיים

- אין קבצי דמו.
- אין מטאדאטה מומצאת.
- אין רשומות ב-`metadata/index.json` לקבצים שלא קיימים פיזית.
- תמיד מריצים `--dry-run` לפני כל ייבוא אמיתי.
- אם מטאדאטה לא ידועה — כותבים `unknown`, לא מנחשים.

### פרוטוקול handoff מ-ChatGPT לקלוד

כשיניב עובד עם ChatGPT לסיווג קבצים, ChatGPT מכין בלוק handoff בפורמט מוגדר.
קלוד קורא את הבלוק, מריץ dry-run, מציג תצוגה מקדימה, ורק אחרי אישור מייבא.

פרוטוקול מלא: `docs/GPT_TO_CLAUDE_FILE_HANDOFF.md`

### הדרך המהירה — השתמש בסקריפט האוטומטי:

```bash
python3 scripts/add-file.py \
  --file /path/to/file.pdf \
  --grade 8 \
  --category algebra \
  --doctype worksheet \
  --year 2024 \
  --topics "נושא1,נושא2"
```

הסקריפט עושה את כל השלבים אוטומטית: hash, בדיקת כפילות, העתקה, עדכון index.json, ואימות.

למדריך מלא: `docs/ADDING_REAL_FILES.md`

**שלבים ידניים (אם הסקריפט לא מספיק):**

**שלב 1 — אימות:**
- לחשב `content_hash` (SHA-1 של תוכן הקובץ)
- לבדוק אם ה-hash כבר קיים ב-`metadata/index.json`
- אם קיים — לא להוסיף, לעדכן שיוכים בלבד

**שלב 2 — מיקום פיזי:**
- לשמור את הקובץ ב-`files/<school_stage>/<grade>/<category>/`
- לשמור פעם אחת בלבד — לא לשכפל לכמה תיקיות

**שלב 3 — עדכון אינדקס:**
- להוסיף רשומה ל-`metadata/index.json`
- לכלול את כל שדות החובה לפי RULES.md סעיף 19
- `source_type: "repo-file"`, `download_ready: true`
- `print_ready: true` אם worksheet/exam/summary-work
- `can_embed: "unknown"` עד לבדיקה אמיתית

**שלב 4 — אימות:**
```bash
bash scripts/validate-all.sh
python3 scripts/test-logic.py
```
שניהם חייבים לעבור לפני commit.

**שלב 5 — commit:**
```bash
git add files/<path> metadata/index.json
git commit -m "feat(files): add <description>"
```

---

## 11. סקריפטי אימות

```bash
bash scripts/validate-all.sh     # 26 בדיקות: JSON, שדות, content_hash, taxonomy, site-structure, contamination, key files, nav logic
python3 scripts/test-logic.py    # בדיקת לוגיקת ניווט: כל הקבצים נגישים מהממשק
node scripts/qa-browser.js http://localhost:8181   # 53 בדיקות Playwright (desktop + mobile)
bash scripts/serve-local.sh      # שרת פיתוח מקומי: http://localhost:8080
```
