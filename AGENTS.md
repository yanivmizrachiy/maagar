# AGENTS.md

קובץ זה אינו דף כללים.

הכללים המחייבים היחידים של הריפו נמצאים רק ב־`RULES.md`.

כל GPT / Codex / Claude / AI Agent שעובד על `yanivmizrachiy/maagar` חייב להתחיל כך:

1. לקרוא את `RULES.md`.
2. לקרוא את `metadata/index.json` כדי להבין את הקבצים הפעילים.
3. לבדוק את מבנה הניווט ב־`metadata/site-structure.json`.
4. לזכור: אין דמו, אין fake, אין כפתור בלי פעולה אמיתית, ואין הורדה בלי קובץ אמיתי.
5. להריץ בדיקות לפני ואחרי שינוי כשעובדים מקומית:

```bash
git status
bash scripts/validate-all.sh
python3 scripts/test-logic.py
python3 scripts/validate-real-buttons.py
```

אם יש שינוי UI:

```bash
node scripts/qa-browser.js
python3 scripts/validate-real-buttons.py
```

הבדיקה `scripts/validate-real-buttons.py` היא guard פעיל נגד כפתורי דמו, טקסטי דמו גלויים, קישורי `#`, קישורי `javascript:void(0)`, והורדות שאינן נשענות על קובץ אמיתי תחת `files/`.

אסור להתייחס לקובץ זה כמקור כללים. אם צריך להוסיף כלל חדש — מוסיפים אותו רק ל־`RULES.md`.
