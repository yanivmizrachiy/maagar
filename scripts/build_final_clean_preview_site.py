#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from __future__ import annotations

import os, re, shutil, subprocess
from pathlib import Path
from docx import Document
from pypdf import PdfReader, PdfWriter

ROOT = Path(__file__).resolve().parents[1]
SRC_A = ROOT / "files/middle-school/grade-8/uncategorized/עבודת-קיץ-ח-אפשר-גם-אחרת-א.docx"
SRC_B = ROOT / "files/middle-school/grade-8/uncategorized/עבודת-קיץ-ח-אפשר-גם-אחרת-ב.docx"
OUT = ROOT / "previews/final-clean-h8"
HTML = ROOT / "previews/final-clean-h8.html"
PDF = OUT / "final-clean-h8.pdf"

MARKERS = [
    "עבודת קיץ", "להקבצה מדעית", "תיכון סדיקול", "שכבת ח", "חלק א", "חלק ב",
    "שם התלמיד", "שם תלמיד", "שם:", "כיתה:", "כתה:", "תאריך:",
    "תרגילי חזרה לחופשת הקיץ", "על פי הספר אפשר גם אחרת",
]
PATTERN = re.compile(
    r"עבודת\s+קיץ|להקבצה\s+מדעית|תיכון\s+סדיקול|שכבת\s+ח|"
    r"חלק\s*[אב](?:׳|'|’)?|שם\s*(?:התלמיד(?:/ה)?|תלמיד)?\s*:|"
    r"כיתה\s*:|כתה\s*:|תאריך\s*:|תרגילי\s+חזרה\s+לחופשת\s+הקיץ|"
    r"על\s+פי\s+הספר\s+אפשר\s+גם\s+אחרת"
)


def norm(s: str) -> str:
    return " ".join((s or "").replace("\u00a0", " ").split())


def remove_xml(el) -> None:
    parent = el.getparent()
    if parent is not None:
        parent.remove(el)


def clear_part(part) -> None:
    for p in list(part.paragraphs):
        remove_xml(p._element)
    for t in list(part.tables):
        remove_xml(t._element)


def clean_doc(src: Path, dst: Path) -> None:
    doc = Document(src)
    for s in doc.sections:
        s.header.is_linked_to_previous = False
        s.footer.is_linked_to_previous = False
        s.different_first_page_header_footer = False
        clear_part(s.header)
        clear_part(s.footer)

    for i, p in enumerate(list(doc.paragraphs)):
        txt = norm(p.text)
        if txt and PATTERN.search(txt) and (i < 24 or len(txt) <= 180):
            remove_xml(p._element)

    for p in list(doc.paragraphs[:16]):
        if norm(p.text):
            break
        remove_xml(p._element)

    dst.parent.mkdir(parents=True, exist_ok=True)
    doc.save(dst)


def convert(docx: Path) -> Path:
    env = os.environ.copy()
    env["HOME"] = str(ROOT / ".lo-home-final-clean")
    Path(env["HOME"]).mkdir(exist_ok=True)
    subprocess.run([
        "libreoffice", "--headless", "--nologo", "--nofirststartwizard",
        "--convert-to", "pdf", "--outdir", str(OUT), str(docx)
    ], cwd=str(ROOT), env=env, check=True)
    out = OUT / f"{docx.stem}.pdf"
    if not out.exists() or out.stat().st_size == 0:
        raise RuntimeError("PDF conversion failed")
    return out


def merge(files: list[Path]) -> None:
    writer = PdfWriter()
    for f in files:
        reader = PdfReader(str(f))
        for page in reader.pages:
            writer.add_page(page)
    writer.add_metadata({"/Title": "H8 clean summer work", "/Creator": "LibreOffice + python-docx + pypdf"})
    with PDF.open("wb") as fp:
        writer.write(fp)


def read_text(pdf_file: Path) -> str:
    reader = PdfReader(str(pdf_file))
    return "\n".join(page.extract_text() or "" for page in reader.pages)


def verify() -> int:
    reader = PdfReader(str(PDF))
    pages = len(reader.pages)
    if pages < 1:
        raise RuntimeError("Empty PDF")
    body = read_text(PDF)
    hits = [m for m in MARKERS if m in body]
    if hits:
        raise RuntimeError("Cleanup failed: " + ", ".join(hits))
    return pages


def render() -> None:
    subprocess.run([
        "pdftoppm", "-jpeg", "-r", "180", "-jpegopt", "quality=94",
        str(PDF), str(OUT / "page")
    ], check=True)
    for i, f in enumerate(sorted(OUT.glob("page-*.jpg")), 1):
        target = OUT / f"page-{i:02d}.jpg"
        if f != target:
            f.rename(target)


def write_html(pages: int) -> None:
    cards = "".join(
        f'<section class="page"><img src="final-clean-h8/page-{i:02d}.jpg" alt="page {i}"></section>'
        for i in range(1, pages + 1)
    )
    HTML.parent.mkdir(parents=True, exist_ok=True)
    HTML.write_text(
        f'<!doctype html><html><head><meta charset="utf-8"><style>'
        f'body{{margin:0;background:#eef3f8}}main{{max-width:980px;margin:auto;padding:20px}}'
        f'.page{{background:white;margin:0 0 22px;padding:12px;border-radius:14px;box-shadow:0 15px 40px #0002}}'
        f'img{{width:100%;display:block}}</style></head><body><main>{cards}</main></body></html>',
        encoding="utf-8",
    )


def main() -> None:
    if OUT.exists():
        shutil.rmtree(OUT)
    OUT.mkdir(parents=True, exist_ok=True)
    a = OUT / "part-a-clean.docx"
    b = OUT / "part-b-clean.docx"
    clean_doc(SRC_A, a)
    clean_doc(SRC_B, b)
    merge([convert(a), convert(b)])
    pages = verify()
    render()
    write_html(pages)
    print("FINAL_CLEAN_PDF=", PDF)
    print("PAGES=", pages)
    print("CHECK=OK")


if __name__ == "__main__":
    main()
