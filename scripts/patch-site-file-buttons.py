#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
patch-site-file-buttons.py

משדרג את האתר לשימוש נוח יותר בקבצים:
- כפתורי פעולה ברורים: צפייה מוטמעת, פתיחה בכרטיסייה, הורדה, הדפסה כשאפשר.
- viewer מוטמע שמנסה להציג PDF ישירות וקובצי Office דרך Office Online viewer כאשר האתר פועל ציבורית.
- fallback ברור לפתיחה/הורדה כאשר הדפדפן לא מצליח להטמיע.

הסקריפט idempotent ומעדכן רק את index.html.
"""

from __future__ import annotations

from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
INDEX = REPO / "index.html"

CSS_MARKER = "/* ── STRONG FILE BUTTONS"
JS_MARKER = "// COMPONENT: EMBED VIEWER HELPERS"

CSS_BLOCK = r'''

    /* ── STRONG FILE BUTTONS ───────────────────── */
    .fc-actions.file-actions-strong {
      display: grid;
      grid-template-columns: repeat(2, minmax(0, 1fr));
      gap: 0.55rem;
    }

    .file-actions-strong .act-btn {
      min-height: 40px;
      font-size: 0.78rem;
      border-radius: 11px;
    }

    .act-open-tab {
      background: rgba(255,255,255,0.04);
      border: 1px solid var(--border-mid);
      color: var(--text-muted);
    }
    .act-open-tab:hover { border-color: var(--border-hover); color: var(--text); background: var(--surface3); }

    .embed-note {
      font-size: 0.74rem;
      color: var(--text-dim);
      line-height: 1.55;
      margin-top: 0.35rem;
    }

    @media (max-width: 520px) {
      .fc-actions.file-actions-strong { grid-template-columns: 1fr; }
    }
'''

JS_HELPERS = r'''

// ═══════════════════════════════════════════════════════════
// COMPONENT: EMBED VIEWER HELPERS
// ═══════════════════════════════════════════════════════════
function fileExt(file) {
  const ext = (file.extension || '').toLowerCase().replace(/^\./, '');
  if (ext) return ext;
  const name = (file.file_name || file.path || '').toLowerCase();
  const m = name.match(/\.([a-z0-9]+)$/);
  return m ? m[1] : '';
}

function absoluteFileUrl(url) {
  try { return new URL(url, window.location.href).href; }
  catch (_) { return url; }
}

function embeddedViewerUrl(file, directUrl) {
  const ext = fileExt(file);
  const officeExts = new Set(['doc', 'docx', 'ppt', 'pptx', 'xls', 'xlsx']);
  if (officeExts.has(ext) && location.protocol.startsWith('http')) {
    return `https://view.officeapps.live.com/op/embed.aspx?src=${encodeURIComponent(absoluteFileUrl(directUrl))}`;
  }
  return directUrl;
}

function embedNotice(file) {
  const ext = fileExt(file);
  const officeExts = new Set(['doc', 'docx', 'ppt', 'pptx', 'xls', 'xlsx']);
  if (officeExts.has(ext)) return 'קובץ Office מוטמע דרך מציג מקוון כאשר האתר פתוח מהאינטרנט. אם הוא לא נטען — פתח בכרטיסייה או הורד.';
  if (ext === 'pdf') return 'PDF מוטמע ישירות בדפדפן. אם הוא לא נטען — פתח בכרטיסייה או הורד.';
  return 'האתר ינסה להציג את הקובץ בדפדפן. אם אין תמיכה בהטמעה — השתמש בפתיחה או הורדה.';
}
'''

NEW_BUILDACTIONS = r'''function buildActions(file) {
  const actions = [];
  const isRepo  = file.source_type === 'repo-file' && file.path;
  const fileUrl = isRepo ? `./${file.path}` : (file.source_url || null);

  if (!fileUrl) return '';

  if (isRepo) {
    actions.push(`<button class="act-btn act-view js-viewer"
      data-fileid="${h(file.id)}" aria-label="צפייה מוטמעת בקובץ">
      👁 צפייה מוטמעת
    </button>`);
    actions.push(`<a class="act-btn act-open-tab"
      href="${ha(fileUrl)}" target="_blank" rel="noopener noreferrer"
      aria-label="פתיחה בכרטיסייה חדשה">↗ פתח</a>`);
    actions.push(`<a class="act-btn act-download"
      href="${ha(fileUrl)}" download="${ha(file.file_name || 'file')}"
      aria-label="הורדת קובץ">⬇ הורדה</a>`);
  } else {
    actions.push(`<a class="act-btn act-view" href="${ha(fileUrl)}"
      target="_blank" rel="noopener noreferrer" aria-label="פתח קישור">↗ פתח קישור</a>`);
  }

  if (file.print_ready === true && isRepo) {
    actions.push(`<a class="act-btn act-print"
      href="${ha(fileUrl)}" target="_blank" rel="noopener noreferrer"
      title="פתח ולחץ Ctrl+P להדפסה" aria-label="הדפסה">🖨 הדפסה</a>`);
  }

  return actions.join('');
}'''


def replace_between(text: str, start: str, end: str, replacement: str) -> str:
    a = text.find(start)
    if a == -1:
      raise SystemExit(f"start marker not found: {start[:80]}")
    b = text.find(end, a)
    if b == -1:
      raise SystemExit(f"end marker not found: {end[:80]}")
    return text[:a] + replacement + "\n\n" + text[b:]


def replace_once(text: str, old: str, new: str) -> str:
    if old not in text:
        raise SystemExit(f"Expected snippet not found: {old[:160]}")
    return text.replace(old, new, 1)


def main() -> int:
    text = INDEX.read_text(encoding="utf-8")
    original = text

    if CSS_MARKER not in text:
        text = replace_once(text, "    /* ── EMPTY STATE", CSS_BLOCK + "\n\n    /* ── EMPTY STATE")

    if JS_MARKER not in text:
        text = replace_once(
            text,
            "// ═══════════════════════════════════════════════════════════\n// COMPONENT: FILE ACTIONS",
            JS_HELPERS + "\n\n// ═══════════════════════════════════════════════════════════\n// COMPONENT: FILE ACTIONS",
        )

    if "file-actions-strong" not in text:
        text = replace_once(
            text,
            "${actions ? `<div class=\"fc-actions\">${actions}</div>` : ''}",
            "${actions ? `<div class=\"fc-actions file-actions-strong\">${actions}</div>` : ''}",
        )

    text = replace_between(
        text,
        "function buildActions(file) {",
        "// ═══════════════════════════════════════════════════════════\n// COMPONENT: EMPTY STATE",
        NEW_BUILDACTIONS,
    )

    text = text.replace("titleEl.textContent = file.title || 'קובץ';", "titleEl.textContent = file.display_title_clean || file.title || 'קובץ';")
    text = text.replace("const url      = `./${file.path}`;", "const url      = `./${file.path}`;\n  const embedUrl = embeddedViewerUrl(file, url);")
    text = text.replace("frame.src = url;", "frame.src = embedUrl;")
    text = text.replace(
        "`<a class=\"act-btn act-download\" href=\"${ha(url)}\" download=\"${ha(file.file_name||'file')}\">⬇ הורדה</a>`",
        "`<a class=\"act-btn act-download\" href=\"${ha(url)}\" download=\"${ha(file.file_name||'file')}\">⬇ הורדה</a>`,\n    `<div class=\"embed-note\">${h(embedNotice(file))}</div>`",
    )

    if text == original:
        print("No changes needed; strong file buttons already patched.")
        return 0

    INDEX.write_text(text, encoding="utf-8", newline="\n")
    print("Patched index.html with strong file buttons and embedded viewer helpers.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
