# אפשרויות Analytics — maagar

**ריפו:** `yanivmizrachiy/maagar`
**עודכן:** 2026-06-03

> **חשוב:** אין כרגע שום קוד tracking באתר. מסמך זה מסביר את האפשרויות בלבד.
> **אסור להוסיף analytics ללא אישור מפורש של יניב.**
> אסור לאסוף נתונים על תלמידים, מורים, או משתמשים ללא הסכמה.

---

## מצב נוכחי

האתר **לא אוסף כל מידע** על מבקרים. אין cookies. אין pixels. אין scripts חיצוניים מלבד גופן Heebo מ-Google Fonts.

---

## מה GitHub מספק בחינם (ללא התקנה)

### GitHub Traffic API

GitHub מאפשר לראות סטטיסטיקות בסיסיות ישירות ב-repository settings:

| מה רואים | מגבלה |
|----------|-------|
| Views לכל page | 14 יום אחורה בלבד |
| Unique visitors | 14 יום בלבד |
| Clones | 14 יום בלבד |
| Top referrers | 14 יום בלבד |

**גישה:** https://github.com/yanivmizrachiy/maagar/graphs/traffic

**חסרונות:**
- רק 14 יום היסטוריה
- לא מבחין בין מסכים שונים (הכל `index.html` אחד)
- אין מידע על פעולות (לחיצות, הורדות)
- לא עובד ב-real-time

---

## אפשרויות Privacy-Friendly (ללא cookies)

### אפשרות 1 — GoatCounter (מומלץ)

**מה זה:** Analytics פשוט, privacy-first, open source.

| פרמטר | ערך |
|-------|-----|
| עלות | חינמי לאתר קטן (<100K views/חודש) |
| cookies | ❌ אין |
| GDPR compliant | ✅ |
| data שנאסף | pageviews, מדינה, referrer, דפדפן |
| היסטוריה | ללא מגבלה (בחשבון חינמי) |
| self-host | ✅ אפשרי |
| אשכנזי/עברית | לא ממשק עברי, אבל פשוט מאוד |

**מה יניב יראה:** מונה daily pageviews, top referrers, מדינות.

**מה נדרש להפעיל:**
1. נרשם ב-[goatcounter.com](https://www.goatcounter.com)
2. מוסיף שורת script אחת ל-`index.html`
3. **דורש אישור יניב**

---

### אפשרות 2 — Cloudflare Web Analytics

**מה זה:** Analytics חינמי של Cloudflare, privacy-first.

| פרמטר | ערך |
|-------|-----|
| עלות | חינמי |
| cookies | ❌ אין |
| GDPR compliant | ✅ |
| data שנאסף | pageviews, מדינה, דפדפן, OS, referrer |
| מגבלה | דורש שהאתר מאחורי Cloudflare |
| היסטוריה | 6 חודשים |

**חסרון:** האתר כרגע על GitHub Pages ישירות, לא מאחורי Cloudflare. ניתן להעביר DNS לCloudflare (דורש domain מותאם).

---

### אפשרות 3 — Plausible Analytics

**מה זה:** Analytics premium, privacy-first.

| פרמטר | ערך |
|-------|-----|
| עלות | $9/חודש (עד 10K visitors) |
| cookies | ❌ אין |
| GDPR compliant | ✅ |
| data שנאסף | pageviews, bounce rate, מדינה, דפדפן, referrer |
| self-host | ✅ אפשרי בחינם |

**לא מומלץ כרגע** — בתשלום עבור אתר בשלב ראשוני.

---

### אפשרות 4 — Umami (self-hosted)

**מה זה:** Analytics open source, self-hosted בחינם.

| פרמטר | ערך |
|-------|-----|
| עלות | חינמי אם self-host |
| cookies | ❌ אין |
| GDPR compliant | ✅ |
| דורש | server / Vercel / Railway לאחסון |

**חסרון:** דורש הגדרת server נפרד.

---

### אפשרות 5 — Google Analytics (לא מומלץ)

| פרמטר | ערך |
|-------|-----|
| עלות | חינמי |
| cookies | ✅ כן (דורש consent banner) |
| GDPR | דרוש cookie consent — בעייתי לאתר עם תלמידים |
| נתונים שנשלחים | ל-Google — לא מתאים לאתר חינוכי |

**לא מומלץ** — לא מתאים לאתר עם תלמידים/מורים ישראלים.

---

## המלצה

עבור שלב ראשון (כשהאתר גדל ויש ביקורים אמיתיים):

> **GoatCounter** — חינמי, ללא cookies, מספק מידע שימושי בסיסי, לא אוסף נתונים רגישים.

שורת הקוד שצריך להוסיף (כשיניב מאשר):
```html
<!-- GoatCounter — Analytics ללא cookies (ממתין לאישור יניב) -->
<!-- <script data-goatcounter="https://ACCOUNT.goatcounter.com/count"
        async src="//gc.zgo.at/count.js"></script> -->
```

---

## חוקים מחייבים לפני הוספה

- [ ] **אישור מפורש של יניב** — חובה לפני כל קוד tracking
- [ ] **בדיקה שהשימוש מותר לאתר חינוכי** — לא לאסוף נתוני קטינים
- [ ] **הוספת privacy notice** אם אוספים כלשהו
- [ ] **אין פיקסלים, אין third-party scripts** ללא בדיקה
- [ ] **כל שינוי עובר validate-all.sh** לפני push
- [ ] **בדיקת contamination scan** מוגדלת לכלול scripts חיצוניים חדשים

---

## הוספה ל-RULES.md

כשיניב יאשר אפשרות ספציפית, יש לעדכן:
1. `RULES.md` סעיף ה-analytics
2. קוד ב-`index.html` עם הערת approval
3. `STATE/full-repo-truth-report.md`
4. הרצת validate-all.sh לאחר שינוי
