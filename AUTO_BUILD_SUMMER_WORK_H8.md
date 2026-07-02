# בנייה אוטומטית של עבודת קיץ ח׳ מדעית

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

פלט צפוי:

- `outputs/summer-work-h8-madait/part-a-real-edited.docx`
- `outputs/summer-work-h8-madait/part-b-real-edited.docx`
- `outputs/summer-work-h8-madait/part-a-real-edited.pdf`
- `outputs/summer-work-h8-madait/part-b-real-edited.pdf`
- `outputs/summer-work-h8-madait/avoda-kayitz-h8-madait-full.pdf`
