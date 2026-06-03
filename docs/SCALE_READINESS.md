# Scale Readiness — maagar

**ריפו:** `yanivmizrachiy/maagar`
**עודכן:** 2026-06-03

מסמך זה מסביר את מגבלות הסביבה הנוכחית (GitHub Pages + Git), מה ניתן לאחסן שם, ומה דורש פתרון חיצוני — כשהמאגר יגדל למאות או אלפי קבצים.

---

## 1. מגבלות GitHub Pages נוכחיות

| פרמטר | מגבלה | מצב נוכחי |
|--------|--------|------------|
| גודל ריפו כולל | ~1 GB מומלץ, 5 GB מקסימום | ~20 MB ✅ |
| גודל קובץ בודד | 100 MB מקסימום ל-Git push | max 15.6 MB ✅ |
| דפים חודשיים | ללא מגבלה רשמית | ✅ |
| bandwidth | 100 GB/חודש מומלץ | ✅ |
| build זמן | לא רלוונטי (סטטי) | — |
| HTTPS | כלול בחינם | ✅ |
| CDN | כלול (Fastly) | ✅ |

**מסקנה:** עד ~500 PDF בגודל ממוצע 1-2 MB — GitHub Pages מספיק לגמרי.

---

## 2. מדיניות גודל קבצים

### מה ניתן לשמור ב-`files/` (ב-Git):
- PDF עד **15 MB** — בסדר (grade-7 PDF הנוכחי הוא 15.6 MB, גבולי)
- PDF עד **5 MB** — אידיאלי, טוען מהר גם בנייד
- PDF **5–15 MB** — קביל, מומלץ לדחוס לפני הוספה
- PDF **מעל 15 MB** — שקול GitHub Releases או LFS

### כלל:
```
אם קובץ > 10 MB → בדוק אם אפשר לצמצם ➜ אם לא, שמור ב-Releases
אם קובץ > 50 MB → חייב להיות מחוץ ל-Git
```

---

## 3. כשלא לשמור בתוך Git

### מצבים שמחייבים פתרון חיצוני:

| מצב | פתרון מומלץ |
|-----|------------|
| קובץ > 50 MB | GitHub Releases (חינמי, ציבורי) |
| וידאו / אודיו | YouTube / Vimeo + embed_url בindex.json |
| קבצים > 100 MB | Git LFS (דורש תוכנית בתשלום ב-GitHub) |
| תמונות בנפח גדול | תמזם/דחוס לפני commit |

---

## 4. Git LFS — מתי ואיך

**Git LFS** מחליף קבצים גדולים ב-pointers קטנים ושומר את הקבצים בשרת נפרד.

### מתי לשקול:
- ריפו מתקרב ל-1 GB
- קבצים גדולים נוספים שוב ושוב
- GitHub Actions איטיים בגלל clone גדול

### עלות:
- GitHub Pages: **חינמי עד 1 GB storage + 1 GB bandwidth/חודש**
- מעבר לזה: $5/חודש לכל 50 GB נוסף

### הגדרה (כשצריך):
```bash
git lfs install
git lfs track "*.pdf"
git add .gitattributes
git commit -m "chore: enable Git LFS for PDFs"
```

**מסקנה עכשווית:** Git LFS אינו נדרש כרגע. עם 4 קבצים, הריפו בסדר גמור ב-Git רגיל.

---

## 5. GitHub Releases — אחסון קבצים גדולים

GitHub Releases מאפשר לצרף קבצים עד 2 GB לכל release, בחינם.

### כיצד להשתמש:
1. צור release חדש (v0.1, v2024, וכו')
2. צרף קבצי PDF גדולים כ-assets
3. שמור ב-`index.json` את ה-`source_url` הישיר
4. הגדר `source_type: "github-release"`, `download_ready: true`

### יתרונות:
- לא מגדיל את גודל ה-clone
- URL ישיר לקובץ
- עדיין ציבורי וחינמי

---

## 6. צמיחת `metadata/index.json`

### מגבלות ביצועים נוכחיות:

| מספר רשומות | גודל JSON משוער | זמן טעינה (3G) | הערה |
|-------------|----------------|----------------|------|
| 4 (נוכחי) | ~8 KB | < 0.1 ש | ✅ |
| 100 | ~200 KB | ~0.3 ש | ✅ |
| 500 | ~1 MB | ~1.5 ש | סביר |
| 1,000 | ~2 MB | ~3 ש | כבד |
| 5,000+ | ~10 MB | ~15 ש | בעיה |

### פתרונות בשלב הרלוונטי:
- **עד 500 קבצים:** `index.json` אחד — בסדר
- **500–1,000:** שקול lazy-loading ל-JSON לפי שכבה
- **1,000+:** פצל ל-`index-grade-7.json`, `index-grade-8.json`, וכו'

### כיצד לפצל (כשצריך):
```javascript
// במקום:
fetch('./metadata/index.json')

// לטעון רק את השכבה הנבחרת:
fetch(`./metadata/index-grade-${grade}.json`)
```

---

## 7. Lazy-Loading לפי שכבה / קטגוריה

האתר הנוכחי טוען את כל ה-JSON בעמוד הראשון. זה מהיר עם קבצים מועטים.

### כשהצמיחה תצדיק:
- טעון `index.json` ראשי עם רק metadata קצרה לנווט
- טעון `index-grade-8.json` רק כשהמשתמש נכנס לשכבת ח׳
- הוסף loading indicator בין המסכים

**לא נדרש כרגע** — נדרש בעתיד עם 500+ קבצים.

---

## 8. סקלביליות חיפוש

החיפוש הנוכחי הוא client-side, עובד על כל ה-`index.json` בזיכרון.

| מספר רשומות | ביצועי חיפוש | הערה |
|-------------|-------------|------|
| עד 500 | מיידי | ✅ |
| 500–2,000 | < 0.1 ש | ✅ |
| 2,000+ | שקול debounce | |
| 10,000+ | דרוש פתרון חיצוני | Algolia, Fuse.js, Pagefind |

**אפשרות עתידית בחינם:** [Pagefind](https://pagefind.app) — static search engine שנבנה בזמן build ועובד בלי backend.

---

## 9. תעבורת מבקרים — GitHub Pages

| מבקרים/יום | עומס מוערך | סטטוס |
|------------|------------|-------|
| עד 1,000 | נמוך | ✅ ב-Pages |
| 1,000–5,000 | בינוני | ✅ ב-Pages (CDN Fastly) |
| 5,000–10,000 | גבוה | ✅ ב-Pages (בד"כ) |
| 10,000+ | שקול Cloudflare Pages | מהיר יותר |
| 50,000+/יום | יש לעבור ל-Vercel/Netlify | GitHub Pages לא מובטח |

**מסקנה:** GitHub Pages ב-Fastly CDN מטפל בתעבורה גבוהה ב-99% מהמקרים.

---

## 10. מדיניות QA Screenshots

### הבעיה:
קבצי PNG של screenshots מגדילים את הריפו וגורמים ל-clone איטי.

### מדיניות:
- **`qa-screenshots/`** — בעיין ה-repo, לתיעוד בלבד
- כל screenshot **משוחזר אוטומטית** ב-`node scripts/qa-browser.js`
- **אין להוסיף screenshots ידנית** — הם נוצרים בזמן QA run
- גודל כל screenshot: בד"כ 100–400 KB

### אם הריפו גדל בגלל screenshots:
```bash
# הוסף ל-.gitignore:
qa-screenshots/

# שנה ב-qa-browser.js:
# שמור screenshots רק כשמופעל עם --screenshots flag
```

---

## 11. סיכום — מה לעשות עכשיו לעומת עתיד

| תחום | עכשיו | עם 200+ קבצים | עם 1000+ קבצים |
|------|-------|----------------|----------------|
| אחסון PDF | `files/` ב-Git | `files/` + Releases לגדולים | LFS או Releases |
| index.json | אחד | אחד | פצל לפי שכבה |
| חיפוש | client-side | client-side | שקול Pagefind |
| CDN | GitHub Pages | GitHub Pages | Cloudflare Pages |
| QA screenshots | ב-repo | ב-repo | שקול gitignore |

**המסקנה:** הארכיטקטורה הנוכחית מוכנה לעשרות עד מאות קבצים ללא שינוי.
