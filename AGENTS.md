# AGENTS.md

קובץ זה אינו דף כללים.

הכללים המחייבים היחידים של הריפו נמצאים רק ב־`RULES.md`.

כל GPT / Codex / Claude / AI Agent שעובד על `yanivmizrachiy/maagar` חייב להתחיל כך:

1. לקרוא את `RULES.md`.
2. לקרוא את `metadata/index.json` כדי להבין את הקבצים הפעילים.
3. לבדוק את מבנה הניווט ב־`metadata/site-structure.json`.
4. להריץ בדיקות לפני ואחרי שינוי כשעובדים מקומית:

```bash
git status
bash scripts/validate-all.sh
python3 scripts/test-logic.py
```

אם יש שינוי UI:

```bash
node scripts/qa-browser.js
```

אסור להתייחס לקובץ זה כמקור כללים. אם צריך להוסיף כלל חדש — מוסיפים אותו רק ל־`RULES.md`.
