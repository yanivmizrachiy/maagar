#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Build a clean browser preview for the grade-8 scientific summer work.

Output is a static HTML preview with page images. It removes the extra custom
headers/footers and labels such as חלק א / חלק ב / שם / כיתה / תאריך before
rendering, so the preview matches the user's approved clean requirements.
"""
from __future__ import annotations

import os
import re
import shutil
import subprocess
from pathlib import Path

from docx import Document
from pypdf import PdfReader, PdfWriter

ROOT = Path(__file__).resolve().parents[1]
SRC_A = ROOT / "files/middle-school/grade-8/uncategorized/עבודת-קיץ-ח-אפשר-גם-אחרת-א.docx"
SRC_B = ROOT / "files/middle-school/grade-8/uncategorized/עבודת-קיץ-ח-אפשר-גם-אחרת-ב.docx"
OUT = ROOT / "previews/final-clean-h8"
HTML = ROOT / "previews/final-clean-h8.html"
PDF = OUT / "final-clean-h8.pdf"

BAD_RE = re.compile(r"(חלק\s*[אב](?:׳|'|’)?|שם\s*(?:התלמיד(?:/ה)?|תלמיד)?\s*:|כיתה\s*:|כתה\s*:|תאריך\s*:)")


def blank_paragraph(paragraph):
    for run in paragraph.runs:
        run.text = ""
    if not paragraph.runs:
        paragraph.add_run("")


def clean_docx(src: Path, dst: Path):
    doc = Document(src)
    for sec in doc.sections:
        sec.header.is_linked_to_previous = False
        sec.footer.is_linked_to_previous = False
        for p in sec.header.paragraphs:
            blank_paragraph(p)
        for p in sec.footer.paragraphs:
            blank_paragraph(p)
        for table in sec.header.tables + sec.footer.tables:
            for row in table.rows:
                for cell in row.cells:
                    for p in cell.paragraphs:
                        blank_paragraph(p)
    # Remove only standalone/top-level paragraphs that are labels, not body math.
    for p in doc.paragraphs:
        txt = " ".join((p.text or "").split())
        if BAD_RE.search(txt) and len(txt) <= 80:
            blank_paragraph(p)
    dst.parent.mkdir(parents=True, exist_ok=True)
    doc.save(dst)


def convert_to_pdf(docx: Path) -> Path:
    env = os.environ.copy()
    env["HOME"] = str(ROOT / ".lo-home-final-clean")
    Path(env["HOME"]).mkdir(exist_ok=True)
    subprocess.run([
        "libreoffice", "--headless", "--nologo", "--nofirststartwizard",
        "--convert-to", "pdf", "--outdir", str(OUT), str(docx)
    ], cwd=str(ROOT), env=env, check=True)
    pdf = OUT / (docx.stem + ".pdf")
    if not pdf.exists() or pdf.stat().st_size == 0:
        raise RuntimeError(f"PDF conversion failed: {docx}")
    return pdf


def merge_pdfs(items):
    writer = PdfWriter()
    for pdf in items:
        reader = PdfReader(str(pdf))
        for page in reader.pages:
            writer.add_page(page)
    with PDF.open("wb") as f:
        writer.write(f)


def render_pages():
    subprocess.run([
        "pdftoppm", "-jpeg", "-r", "144", "-jpegopt", "quality=92", str(PDF), str(OUT / "page")
    ], check=True)
    rendered = sorted(OUT.glob("page-*.jpg"))
    for i, p in enumerate(rendered, 1):
        p.rename(OUT / f"page-{i:02d}.jpg")


def write_html(page_count: int):
    cards = []
    for i in range(1, page_count + 1):
        cards.append(f'<section class="page" id="p{i}"><div class="num">עמוד {i} מתוך {page_count}</div><img src="final-clean-h8/page-{i:02d}.jpg" alt="עמוד {i}"></section>')
    html = f"""<!doctype html>
<html lang="he" dir="rtl">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>תצוגה מקדימה — עבודת קיץ ח׳</title>
<style>
:root{{--bg:#eef3f8;--ink:#0f172a;--panel:#ffffff;--line:#cbd5e1;}}
*{{box-sizing:border-box}}
body{{margin:0;background:var(--bg);color:var(--ink);font-family:Arial,system-ui,sans-serif}}
header{{position:sticky;top:0;z-index:10;background:rgba(255,255,255,.96);border-bottom:1px solid var(--line);padding:14px 18px;box-shadow:0 8px 28px #0f172a18}}
h1{{margin:0;font-size:24px;color:#0b4f8a}}
small{{display:block;margin-top:5px;color:#475569}}
main{{max-width:980px;margin:0 auto;padding:20px 14px 40px}}
.page{{background:var(--panel);border:1px solid var(--line);border-radius:18px;margin:0 0 22px;padding:12px;box-shadow:0 20px 50px #0f172a22}}
.num{{font-size:14px;color:#475569;margin:0 0 8px;text-align:center}}
img{{display:block;width:100%;height:auto;border-radius:10px;background:white}}
</style>
</head>
<body>
<header><h1>תצוגה מקדימה — עבודת קיץ ח׳</h1><small>PDF נקי: ללא כותרות, ללא שם/כיתה/תאריך, ללא חלק א/חלק ב. צפייה בלבד לפני אישור.</small></header>
<main>
{''.join(cards)}
</main>
</body>
</html>"""
    HTML.parent.mkdir(parents=True, exist_ok=True)
    HTML.write_text(html, encoding="utf-8")


def main():
    if OUT.exists():
        shutil.rmtree(OUT)
    OUT.mkdir(parents=True, exist_ok=True)
    a_docx = OUT / "part-a-clean.docx"
    b_docx = OUT / "part-b-clean.docx"
    clean_docx(SRC_A, a_docx)
    clean_docx(SRC_B, b_docx)
    a_pdf = convert_to_pdf(a_docx)
    b_pdf = convert_to_pdf(b_docx)
    merge_pdfs([a_pdf, b_pdf])
    page_count = len(PdfReader(str(PDF)).pages)
    if page_count != 26:
        raise RuntimeError(f"Expected 26 pages after cleanup, got {page_count}")
    render_pages()
    write_html(page_count)
    print("FINAL_CLEAN_PREVIEW_HTML=", HTML)
    print("FINAL_CLEAN_PDF=", PDF)
    print("PAGES=", page_count)


if __name__ == "__main__":
    main()
