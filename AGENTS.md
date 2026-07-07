# AGENTS.md

קובץ זה אינו דף כללים.

הכללים המחייבים היחידים של הריפו נמצאים רק ב־`RULES.md`.

כל GPT / Codex / Claude / AI Agent שעובד על `yanivmizrachiy/maagar` חייב להתחיל כך:

1. לקרוא את `RULES.md`.
2. לקרוא את `metadata/index.json` כדי להבין את הקבצים הפעילים.
3. לבדוק את מבנה הניווט ב־`metadata/site-structure.json`.
4. לזכור: אין תוכן פיקטיבי, אין כפתור בלי פעולה אמיתית, ואין הורדה בלי קובץ אמיתי.
5. לזכור את חוזה הניווט הפעיל: בית → שכבה → תחום → רשימת משימות/קבצים.
6. לא להחזיר שלב נושא חובה בין תחום לבין רשימת הקבצים.
7. לזכור: `topics` הם metadata, תגיות, חיפוש וסינון; הם לא תחנת ניווט חובה.
8. לחיצה על שם משימה חייבת לפתוח split viewer: תצוגה מוטמעת + פרטי משימה + כפתורי פעולה.
9. להריץ בדיקות לפני ואחרי שינוי כשעובדים מקומית:

```bash
git status
bash scripts/validate-all.sh
python3 scripts/test-logic.py
python3 scripts/validate-real-buttons.py
python3 scripts/validate-direct-task-flow.py
```

אם יש שינוי UI:

```bash
npx playwright test tests/ --project=chromium
python3 scripts/validate-real-buttons.py
python3 scripts/validate-direct-task-flow.py
```

הבדיקה `scripts/validate-real-buttons.py` היא guard פעיל נגד כפתורים לא אמיתיים, קישורי `#`, קישורי `javascript:void(0)`, והורדות שאינן נשענות על קובץ אמיתי תחת `files/`.

הבדיקה `scripts/validate-direct-task-flow.py` היא guard פעיל נגד החזרת הזרימה הישנה של תחום → נושא → קבצים.

אסור להתייחס לקובץ זה כמקור כללים. אם צריך להוסיף כלל חדש — מוסיפים אותו רק ל־`RULES.md`.
