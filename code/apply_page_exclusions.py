"""Drop documented duplicate pages from chapter PDFs before extraction (new, 21 Oct 2026).

Reads code/page_exclusions.csv (book, edition_label, chapter_file, exclude_pdf_pages "a-b" or "a b c", reason).
For each row: the untouched original is moved once to data/books/_excluded_originals/<label>/<book>/<file>.pdf and the
chapter PDF in data/books/<label>/<book>/ is rewritten without the listed pages (1-based PDF page indices).
Idempotent: if the original is already saved, the trimmed file is rebuilt from it.  sha256 of both files and the page
counts are appended to logs/page_exclusions.log.
Usage: python -I code/apply_page_exclusions.py
"""
import csv
import hashlib
import shutil
import time
from pathlib import Path

import pymupdf

ROOT = Path(__file__).resolve().parent.parent


def pages(spec):
    out = set()
    for part in spec.replace(",", " ").split():
        a, _, b = part.partition("-")
        out.update(range(int(a), int(b or a) + 1))
    return out


def sha(p):
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()


def main():
    log = ROOT / "logs" / "page_exclusions.log"
    for r in csv.DictReader(open(ROOT / "code" / "page_exclusions.csv", encoding="utf-8", newline="")):
        target = ROOT / "data" / "books" / r["edition_label"] / r["book"] / f"{r['chapter_file']}.pdf"
        orig = ROOT / "data" / "books" / "_excluded_originals" / r["edition_label"] / r["book"] / f"{r['chapter_file']}.pdf"
        if not orig.exists():
            orig.parent.mkdir(parents=True, exist_ok=True)
            shutil.move(str(target), str(orig))
        drop = pages(r["exclude_pdf_pages"])
        src = pymupdf.open(str(orig))
        keep = [i for i in range(len(src)) if i + 1 not in drop]
        src.select(keep)
        src.save(str(target), garbage=3, deflate=True)
        msg = (f"{time.strftime('%Y-%m-%d %H:%M')} {r['book']} {r['edition_label']} {r['chapter_file']}: dropped PDF pages "
               f"{r['exclude_pdf_pages']} ({len(drop)}), kept {len(keep)}; original sha256 {sha(orig)}; trimmed sha256 {sha(target)}")
        print(msg)
        with open(log, "a", encoding="utf-8") as f:
            f.write(msg + "\n")


if __name__ == "__main__":
    main()
