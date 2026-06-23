#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
patch-site-topic-groups.py

מוסיף ל-index.html תצוגה מקובצת לפי נושא:
- עמוד קטגוריה מציג קבוצות נושא.
- עמוד חטיבה עליונה מציג קבוצות נושא.
- תוצאות חיפוש נשארות רשימה רגילה כדי לא לפגוע במהירות חיפוש.

הסקריפט משנה רק את index.html.
הוא idempotent: אם הפאץ' כבר קיים, הוא לא מכפיל אותו.
"""

from __future__ import annotations

from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
INDEX = REPO / "index.html"

CSS_MARKER = "/* ── TOPIC GROUPS"
JS_MARKER = "// COMPONENT: TOPIC GROUPS"

CSS_BLOCK = r'''

    /* ── TOPIC GROUPS ─────────────────────────── */
    .topic-groups {
      display: flex;
      flex-direction: column;
      gap: 1.5rem;
    }

    .topic-group {
      background: rgba(17, 24, 39, 0.38);
      border: 1px solid var(--border);
      border-radius: var(--radius);
      padding: 1rem;
    }

    .topic-group-head {
      display: flex;
      align-items: center;
      justify-content: space-between;
      gap: 1rem;
      margin-bottom: 0.85rem;
      padding-bottom: 0.75rem;
      border-bottom: 1px solid var(--border);
    }

    .topic-group-title {
      font-size: 1rem;
      font-weight: 800;
      color: var(--text);
      letter-spacing: -0.01em;
    }

    .topic-group-count {
      font-size: 0.72rem;
      color: var(--text-muted);
      background: rgba(255,255,255,0.05);
      border: 1px solid var(--border);
      border-radius: 999px;
      padding: 0.18rem 0.65rem;
      white-space: nowrap;
    }

    .topic-group .files-grid {
      grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
    }
'''

JS_BLOCK = r'''

// ═══════════════════════════════════════════════════════════
// COMPONENT: TOPIC GROUPS
// ═══════════════════════════════════════════════════════════
function primaryTopic(file) {
  const topics = Array.isArray(file.topics) ? file.topics.filter(t => t && t !== 'unknown') : [];
  if (topics.length > 0) return topics[0];
  return 'ללא נושא מסווג';
}

function sortFilesForDisplay(files) {
  return [...files].sort((a, b) => {
    const ta = primaryTopic(a);
    const tb = primaryTopic(b);
    if (ta !== tb) return ta.localeCompare(tb, 'he');
    const da = DOCTYPE_HE[a.document_type] || a.document_type || '';
    const db = DOCTYPE_HE[b.document_type] || b.document_type || '';
    if (da !== db) return da.localeCompare(db, 'he');
    return String(a.title || '').localeCompare(String(b.title || ''), 'he');
  });
}

function groupedFilesHtml(files) {
  const sorted = sortFilesForDisplay(files);
  const groups = new Map();
  for (const file of sorted) {
    const topic = primaryTopic(file);
    if (!groups.has(topic)) groups.set(topic, []);
    groups.get(topic).push(file);
  }

  return `<div class="topic-groups">${[...groups.entries()].map(([topic, items]) => `
    <section class="topic-group">
      <div class="topic-group-head">
        <div class="topic-group-title">${h(topic)}</div>
        <div class="topic-group-count">${countLabel(items.length)}</div>
      </div>
      <div class="files-grid">${items.map(fileCard).join('')}</div>
    </section>
  `).join('')}</div>`;
}
'''


def replace_once(text: str, old: str, new: str) -> str:
    if old not in text:
        raise SystemExit(f"Expected snippet not found:\n{old[:160]}")
    return text.replace(old, new, 1)


def main() -> int:
    text = INDEX.read_text(encoding="utf-8")
    original = text

    if CSS_MARKER not in text:
        text = replace_once(
            text,
            "    /* ── FILE CARD ───────────────────────────── */",
            CSS_BLOCK + "\n    /* ── FILE CARD ───────────────────────────── */",
        )

    if JS_MARKER not in text:
        text = replace_once(
            text,
            "// ═══════════════════════════════════════════════════════════\n// COMPONENT: FILE CARD",
            JS_BLOCK + "\n\n// ═══════════════════════════════════════════════════════════\n// COMPONENT: FILE CARD",
        )

    text = replace_once(
        text,
        "    : `<div class=\"files-grid\">${files.map(fileCard).join('')}</div>`;",
        "    : groupedFilesHtml(files);",
    )

    text = replace_once(
        text,
        "    : `<div class=\"files-grid\">${files.map(fileCard).join('')}</div>`;",
        "    : groupedFilesHtml(files);",
    )

    if text == original:
        print("No changes needed; topic groups already patched.")
        return 0

    INDEX.write_text(text, encoding="utf-8", newline="\n")
    print("Patched index.html with topic grouped display.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
