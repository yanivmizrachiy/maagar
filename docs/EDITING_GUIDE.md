# מדריך עריכה — maagar

**ריפו:** `yanivmizrachiy/maagar`
**עודכן:** 2026-06-03

מדריך פשוט לשינוי עיצוב, טקסטים, צבעים, כרטיסים ולוגיקת ניווט — בלי לשבור את האתר.

> אחרי כל שינוי: הרץ `bash scripts/validate-all.sh && python3 scripts/test-logic.py`

---

## 1. איך לשנות צבעים

### צבעי ממשק כללי (רקע, borders, טקסט)

נמצאים ב-`index.html` בתוך `<style>`, בלוק `:root {`:

```css
:root {
  --bg:        #070B14;   /* רקע ראשי */
  --bg2:       #0C1120;   /* רקע משני */
  --surface:   #111827;   /* פנל / קלף */
  --surface2:  #1A2236;   /* פנל כהה יותר */
  --text:      #F0F4FC;   /* טקסט ראשי */
  --text-muted:#8A9BC0;   /* טקסט משני */
  --text-dim:  #4A5878;   /* טקסט עמום */
  /* ... */
}
```

**כדי לשנות:** מצא את המשתנה הרצוי וערוך את הערך הhex.

---

### צבעי שכבות (ז׳ / ח׳ / ט׳ / חטיבה עליונה)

נמצאים ב-`index.html`, בחלק `// GRADE_IDENTITY` בתוך `<script>`:

```javascript
const GRADE_IDENTITY = {
  '7':           { bg: 'linear-gradient(135deg,#4338CA,#6D28D9)', accent: '#6366F1', ... },
  '8':           { bg: 'linear-gradient(135deg,#0369A1,#0891B2)', accent: '#22D3EE', ... },
  '9':           { bg: 'linear-gradient(135deg,#1D4ED8,#4F46E5)', accent: '#60A5FA', ... },
  'high-school': { bg: 'linear-gradient(135deg,#92400E,#B45309)', accent: '#F59E0B', ... }
};
```

**כדי לשנות צבע של שכבת ח׳:** ערוך את שורת `'8'`.

---

### צבעי קטגוריות (אלגברה / גיאומטריה / מסכמות / מבחנים)

נמצאים ב-`index.html`, בחלק `// CAT_IDENTITY`:

```javascript
const CAT_IDENTITY = {
  algebra:       { bg: 'linear-gradient(135deg,#3730A3,#5B21B6)', accent: '#818CF8', icon: '✕' },
  geometry:      { bg: 'linear-gradient(135deg,#065F46,#047857)', accent: '#34D399', icon: '△' },
  summaries:     { bg: 'linear-gradient(135deg,#78350F,#92400E)', accent: '#FBBF24', icon: '◎' },
  exams:         { bg: 'linear-gradient(135deg,#881337,#9F1239)', accent: '#FB7185', icon: '≡' },
  uncategorized: { bg: 'linear-gradient(135deg,#1E293B,#334155)', accent: '#94A3B8', icon: '◫' }
};
```

---

### צבעי רמות חטיבה עליונה (3/4/5 יחידות)

נמצאים ב-`index.html`, בחלק `// UNIT_IDENTITY`:

```javascript
const UNIT_IDENTITY = {
  '3-unit': { bg: 'linear-gradient(135deg,#1E3A5F,#1D4ED8)', accent: '#60A5FA', ... },
  '4-unit': { bg: 'linear-gradient(135deg,#3730A3,#5B21B6)', accent: '#A78BFA', ... },
  '5-unit': { bg: 'linear-gradient(135deg,#78350F,#B45309)', accent: '#FCD34D', ... }
};
```

### צבעי רצועת סוג מסמך (על כרטיס הקובץ)

נמצאים ב-`index.html`, בחלק `// DOCTYPE_STRIP`:

```javascript
const DOCTYPE_STRIP = {
  'worksheet':    'linear-gradient(90deg,#4338CA,#6D28D9)',
  'exam':         'linear-gradient(90deg,#881337,#9F1239)',
  'summary-work': 'linear-gradient(90deg,#065F46,#047857)',
  // ...
};
```

---

## 2. איך לשנות טקסטים וכותרות

### כותרת האתר

ב-`index.html`, בתוך `<header>`:

```html
<div class="header-logo-text">מאגר מתמטיקה <span>| math repo</span></div>
```

### תיאורי שכבות (ב-GRADE_IDENTITY)

שנה את `desc`:
```javascript
'7': { ..., desc: 'אלגברה · גיאומטריה · מבחנים · סיכומים', ... },
```

### תוויות Hebrew לקטגוריות / doctypes

```javascript
const CATEGORY_HE = {
  algebra: 'אלגברה',
  geometry: 'גיאומטריה',
  // ...
};

const DOCTYPE_HE = {
  'worksheet': 'עבודה',
  'exam': 'מבחן',
  // ...
};
```

### כותרת Hero (הדף הראשי)

ב-function `renderHome(app)` — מצא `hero-title` ו-`hero-sub`:
```javascript
hero.innerHTML = `
  <div class="hero-eyebrow">...</div>
  <h1 class="hero-title">מאגר חומרי לימוד<br>במתמטיקה</h1>
  <p class="hero-sub">...</p>
`;
```

---

## 3. איך להוסיף כיתה / קטגוריה / רמה חדשה

### הוספת כיתה חדשה (למשל כיתה ו׳)

1. **`metadata/taxonomy.json`** — הוסף ל-`grades`
2. **`metadata/site-structure.json`** — הוסף ל-`nav`
3. **`index.html` JS** — הוסף ל-`GRADE_IDENTITY` ו-`GRADE_HE`
4. **`scripts/_ingest.py`** — הוסף `'6': 'middle-school'` ל-`GRADE_TO_STAGE`
5. **תיקיות:** `mkdir -p files/middle-school/grade-6/{algebra,geometry,summaries,exams,uncategorized}`
6. הרץ `bash scripts/validate-all.sh` לאחר השינוי

### הוספת קטגוריה חדשה

1. **`metadata/taxonomy.json`** — הוסף לרשימת הקטגוריות
2. **`RULES.md`** סעיף 19 — הוסף לרשימת ערכים חוקיים
3. **`index.html`** — הוסף ל-`CAT_IDENTITY`, `CATEGORY_HE`
4. **`scripts/_ingest.py`** — הוסף ל-`VALID_CATEGORIES`
5. הרץ `bash scripts/validate-all.sh`

---

## 4. איך לשנות עיצוב כרטיס קובץ

### מיקום:
- **CSS:** חפש `/* ── FILE CARD ──` ב-`index.html`
- **JS render:** חפש `function renderFileCard(f)` ב-`index.html`

### שינויים נפוצים:
- גובה רצועת הצבע: `.fc-type-strip { height: 3px; }` — שנה ל-`4px` או יותר
- ריווח: `.fc-body { padding: 1.25rem 1.25rem 0; }`
- גודל כפתורים: `.act-btn { padding: 0.52rem 0.7rem; }`

---

## 5. איך לשנות עיצוב מציג PDF

### CSS:
- חפש `/* ── PDF MODAL ──` ב-`index.html`
- רוחב מקסימלי: `.modal { max-width: 940px; }`
- גובה: `.modal { height: 88vh; }`

### טקסטים:
- כותרת: `<div class="modal-label">צפייה בקובץ</div>`
- כפתור סגירה: `onclick="closeModal()"` — הטקסט הוא `✕`
- כפתור טאב חדש: `↗ כרטיסייה`
- כפתור הורדה: `⬇ הורדה`

---

## 6. איך לשנות עיצוב חיפוש

### CSS:
- חפש `/* ── SEARCH SCREEN ──` ב-`index.html`

### JS:
- חפש `function renderSearch(app, bcs, sc)` ב-`index.html`
- הודעת אין תוצאות: `"לא נמצאו קבצים"`
- placeholder: `"חיפוש לפי כותרת, נושא או קטגוריה..."`

---

## 7. איפה קבצים נשמרים

| קובץ | מיקום |
|------|-------|
| PDF ז׳ | `files/middle-school/grade-7/` |
| PDF ח׳ | `files/middle-school/grade-8/` |
| PDF ט׳ | `files/middle-school/grade-9/` |
| בגרויות | `files/high-school/3-unit/` וכו׳ |
| אינדקס | `metadata/index.json` |
| טקסונומיה | `metadata/taxonomy.json` |
| מבנה ניווט | `metadata/site-structure.json` |

---

## 8. מה לא לערוך ידנית

| קובץ | סיבה |
|------|------|
| `metadata/index.json` | ערוך רק דרך `scripts/add-file.py` |
| `files/` | העתק קבצים רק דרך `scripts/add-file.py` |
| `metadata/taxonomy.json` | ערוך יחד עם `RULES.md` |
| `scripts/_ingest.py` | שינוי ישיר עלול לשבור batch imports |

---

## 9. בדיקות לאחר כל עריכה

```bash
# חובה לפני כל commit:
bash scripts/validate-all.sh
python3 scripts/test-logic.py

# לבדיקת UI מלאה (דורש Node.js + Playwright):
node scripts/qa-browser.js
```

---

## 10. מתי לפצל את index.html לקבצים נפרדים

### כרגע: לא נדרש.
הקובץ נקרא ומתוחזק בקלות. כל החלקים מוגדרים בהערות ברורות.

### פצל כש:
- `index.html` עולה על 3,000 שורות
- מפתחים מרובים עורכים בו-זמנית
- נדרש build tool (Vite, Webpack)

### מבנה עתידי אפשרי:
```
assets/
  css/
    tokens.css      ← CSS variables בלבד
    layout.css      ← header, main, grid
    components.css  ← cards, modal, search
  js/
    config.js       ← GRADE_IDENTITY, CAT_IDENTITY וכו׳
    nav.js          ← ניווט וhistory
    render.js       ← render functions
    search.js       ← חיפוש
    pdf.js          ← PDF viewer
```

**עד 3,000 שורות — `index.html` אחד עדיף.** פשוט יותר לפרוס ב-GitHub Pages.
