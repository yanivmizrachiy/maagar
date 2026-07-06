# בנייה אוטומטית של עבודת קיץ ח׳ מדעית

> **ארכיון — משימה חד-פעמית שהושלמה (2026-07-01). מסמך זה אינו מקור כללים** (הכללים ב-`RULES.md` בלבד).
> התוצרים החיים נמצאים ב-`previews/final-clean-h8/` ומתפרסמים ידנית דרך workflow ‏"Publish H8 Preview (manual)".

המטרה: לבנות קובץ אמת מתוך שני קבצי המקור בריפו, בלי דמו.

קבצי מקור:

- `files/middle-school/grade-8/uncategorized/עבודת-קיץ-ח-אפשר-גם-אחרת-א.docx`
- `files/middle-school/grade-8/uncategorized/עבודת-קיץ-ח-אפשר-גם-אחרת-ב.docx`

הסקריפט הקיים:

- `scripts/build_summer_work_h8_madait.py`

מה הוא עושה:

1. פותח את שני קבצי ה-DOCX המקוריים.
2. מוסיף כותרת עליונה וכותרת תחתונה.
3. מוסיף מקום לסמל בית הספר.
4. ממיר כל חלק ל-PDF.
5. מאחד את שני החלקים ל-PDF מלא.
6. מייצר דפי תצוגה מקדימה.

פקודה להפעלה בסביבת Linux עם LibreOffice:

```bash
python3 -m pip install --upgrade python-docx pypdf pillow
python3 scripts/build_summer_work_h8_madait.py
```

פלט בפועל (בריפו):

- `previews/final-clean-h8/part-a-title-fixed.docx` + `.pdf`
- `previews/final-clean-h8/part-b-clean.docx` + `.pdf`
- `previews/final-clean-h8/final-clean-h8.pdf`
- עמוד תצוגה: `previews/final-clean-h8.html`

(תיקיית `outputs/` המקורית הייתה זמנית ואינה בריפו.)
