#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
site-action-report-md.py

ממיר את reports/site-action-report.json לדוח Markdown קריא.
הסקריפט לא משנה metadata או קבצי אתר.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any, Dict

REPO = Path(__file__).resolve().parent.parent


def yes_no(value: Any) -> str:
    return "כן" if bool(value) else "לא"


def pct(value: Any) -> str:
    if isinstance(value, (int, float)):
        return f"{value}%"
    return str(value)


def main() -> int:
    parser = argparse.ArgumentParser(description="Create Markdown summary for site action report.")
    parser.add_argument("--json", default="reports/site-action-report.json")
    parser.add_argument("--md", default="reports/site-action-report.md")
    args = parser.parse_args()

    json_path = (REPO / args.json).resolve()
    md_path = (REPO / args.md).resolve()
    if not str(json_path).startswith(str(REPO.resolve())):
        raise SystemExit("json path must be inside repository")
    if not str(md_path).startswith(str(REPO.resolve())):
        raise SystemExit("md path must be inside repository")

    data: Dict[str, Any] = json.loads(json_path.read_text(encoding="utf-8"))
    s = data.get("summary", {})
    features = data.get("browser_features", {})

    lines: list[str] = []
    lines.append("# דוח יכולות אתר המאגר")
    lines.append("")
    lines.append("## סיכום מהיר")
    lines.append("")
    lines.append(f"- סך קבצים במאגר: **{s.get('total_files', 0)}**")
    lines.append(f"- קבצים פנימיים בריפו: **{s.get('repo_files', 0)}**")
    lines.append(f"- קישורים חיצוניים: **{s.get('external_links', 0)}**")
    lines.append(f"- כרטיסים עם פתיחה: **{s.get('open_action_cards', 0)}** ({pct(s.get('open_coverage_percent', 0))})")
    lines.append(f"- כרטיסים עם הורדה: **{s.get('download_action_cards', 0)}** ({pct(s.get('download_coverage_percent', 0))})")
    lines.append(f"- כרטיסים עם צפייה מוטמעת: **{s.get('embedded_view_total', 0)}** ({pct(s.get('embed_coverage_percent', 0))})")
    lines.append(f"- כרטיסים ללא פעולה שימושית: **{s.get('no_action_cards', 0)}**")
    lines.append("")

    lines.append("## יכולות אתר")
    lines.append("")
    lines.append("| יכולת | פעיל | קובץ | נטען ב-index |")
    lines.append("|---|---:|---|---:|")
    labels = {
        "core_browser": "דפדפן מאגר בסיסי",
        "url_state_filters": "שמירת חיפוש/סינון בכתובת",
        "file_deep_links": "קישור עומק לקובץ",
        "file_share_buttons": "שיתוף קובץ מכרטיס",
        "current_view_share_buttons": "שיתוף תצוגה נוכחית",
    }
    for key, item in features.items():
        if not isinstance(item, dict):
            continue
        active = item.get("exists") and item.get("loaded_in_index") and item.get("required_snippets_present")
        lines.append(
            f"| {labels.get(key, key)} | {yes_no(active)} | `{item.get('file', '')}` | {yes_no(item.get('loaded_in_index'))} |"
        )
    lines.append("")

    lines.append("## התפלגות לפי שכבה")
    lines.append("")
    lines.append("| שכבה | כמות |")
    lines.append("|---|---:|")
    for key, value in sorted((s.get("by_grade") or {}).items()):
        lines.append(f"| {key} | {value} |")
    lines.append("")

    lines.append("## התפלגות לפי תחום")
    lines.append("")
    lines.append("| תחום | כמות |")
    lines.append("|---|---:|")
    for key, value in sorted((s.get("by_category") or {}).items()):
        lines.append(f"| {key} | {value} |")
    lines.append("")

    lines.append("## קבצים ללא פעולה")
    lines.append("")
    no_action = data.get("no_action_cards") or []
    if no_action:
        lines.append("| id | כותרת | שכבה | סוג |")
        lines.append("|---|---|---|---|")
        for item in no_action[:50]:
            lines.append(
                f"| {item.get('id', '')} | {item.get('title', '')} | {item.get('grade', '')} | {item.get('document_type', '')} |"
            )
        if len(no_action) > 50:
            lines.append(f"\n> מוצגים 50 ראשונים מתוך {len(no_action)}.")
    else:
        lines.append("אין קבצים ללא פעולה שימושית.")
    lines.append("")

    md_path.parent.mkdir(parents=True, exist_ok=True)
    md_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"Markdown report: {md_path.relative_to(REPO)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
