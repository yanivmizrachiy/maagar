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

TEXT_MARKERS = [
    "\u05e2\u05d1\u05d5\u05d3\u05ea \u05e7\u05d9\u05e5",
    "\u05dc\u05d4\u05e7\u05d1\u05e6\u05d4 \u05de\u05d3\u05e2\u05d9\u05ea",
    "\u05ea\u05d9\u05db\u05d5\u05df \u05e1\u05d3\u05d9\u05e7\u05d5\u05dc",
    "\u05e9\u05db\u05d1\u05ea \u05d7",
    "\u05d7\u05dc\u05e7 \u05d0", "\u05d7\u05dc\u05e7 \u05d1",
    "\u05e9\u05dd \u05d4\u05ea\u05dc\u05de\u05d9\u05d3", "\u05e9\u05dd \u05ea\u05dc\u05de\u05d9\u05d3", "\u05e9\u05dd:",
    "\u05db\u05d9\u05ea\u05d4:", "\u05db\u05ea\u05d4:", "\u05ea\u05d0\u05e8\u05d9\u05da:",
    "\u05ea\u05e8\u05d2\u05d9\u05dc\u05d9 \u05d7\u05d6\u05e8\u05d4 \u05dc\u05d7\u05d5\u05e4\u05e9\u05ea \u05d4\u05e7\u05d9\u05e5",
    "\u05e2\u05dc \u05e4\u05d9 \u05d4\u05e1\u05e4\u05e8 \u05d0\u05e4\u05e9\u05e8 \u05d2\u05dd \u05d0\u05d7\u05e8\u05ea",
]
RX = re.compile("|".join(re.escape(x).replace("\\ ", r"\\s+") for x in TEXT_MARKERS))


def norm(s: str) -> str:
    return " ".join((s or "").replace("\u00a0", " ").split())


def kill(el):
    p = el.getparent()
    if p is not None:
        p.remove(el)


def empty(container):
    for p in list(container.paragraphs):
        kill(p._element)
    for t in list(container.tables):
        kill(t._element)


def clean(src: Path, dst: Path):
    doc = Document(src)
    for s in doc.sections:
        s.header.is_linked_to_previous = False
        s.footer.is_linked_to_previous = False
        s.different_first_page_header_footer = False
        empty(s.header); empty(s.footer)
    for i, p in enumerate(list(doc.paragraphs)):
        txt = norm(p.text)
        if txt and RX.search(txt) and (i < 24 or len(txt) <= 180):
            kill(p._element)
    for p in list(doc.paragraphs[:16]):
        if norm(p.text):
            break
        kill(p._element)
    dst.parent.mkdir(parents=True, exist_ok=True)
    doc.save(dst)


def pdf(docx: Path) -> Path:
    env = os.environ.copy(); env["HOME"] = str(ROOT / ".lo-home-final-clean")
    Path(env["HOME"]).mkdir(exist_ok=True)
    subprocess.run(["libreoffice","--headless","--nologo","--nofirststartwizard","--convert-to","pdf","--outdir",str(OUT),str(docx)], cwd=str(ROOT), env=env, check=True)
    out = OUT / (docx.stem + ".pdf")
    if not out.exists() or out.stat().st_size == 0:
        raise RuntimeError("pdf conversion failed")
    return out


def join(items):
    w = PdfWriter()
    for f in items:
        r = PdfReader(str(f))
        for page in r.pages:
            w.add_page(page)
    with PDF.open("wb") as fp:
        w.write(fp)


def text(pdf_path: Path) -> str:
    r = PdfReader(str(pdf_path))
    return "\n".join(page.extract_text() or "" for page in r.pages)


def verify() -> int:
    r = PdfReader(str(PDF)); pages = len(r.pages)
    if pages < 1:
        raise RuntimeError("empty pdf")
    body = text(PDF)
    hits = [x for x in TEXT_MARKERS if x in body]
    if hits:
        raise RuntimeError("cleanup check failed")
    return pages


def render():
    subprocess.run(["pdftoppm","-jpeg","-r","180","-jpegopt","quality=94",str(PDF),str(OUT / "page")], check=True)
    for i, f in enumerate(sorted(OUT.glob("page-*.jpg")), 1):
        target = OUT / f"page-{i:02d}.jpg"
        if f != target:
            f.rename(target)


def html(pages: int):
    cards = "".join(f'<section class="page"><img src="final-clean-h8/page-{i:02d}.jpg" alt="page {i}"></section>' for i in range(1, pages+1))
    HTML.parent.mkdir(parents=True, exist_ok=True)
    HTML.write_text(f'<!doctype html><html><head><meta charset="utf-8"><style>body{{margin:0;background:#eef3f8}}main{{max-width:980px;margin:auto;padding:20px}}.page{{background:white;margin:0 0 22px;padding:12px;border-radius:14px;box-shadow:0 15px 40px #0002}}img{{width:100%;display:block}}</style></head><body><main>{cards}</main></body></html>', encoding="utf-8")


def main():
    if OUT.exists(): shutil.rmtree(OUT)
    OUT.mkdir(parents=True, exist_ok=True)
    a = OUT / "part-a-clean.docx"; b = OUT / "part-b-clean.docx"
    clean(SRC_A, a); clean(SRC_B, b)
    join([pdf(a), pdf(b)])
    pages = verify(); render(); html(pages)
    print("FINAL_CLEAN_PDF=", PDF); print("PAGES=", pages); print("CHECK=OK")

if __name__ == "__main__":
    main()
