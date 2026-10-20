"""OCR fallback for chapter PDFs whose text layer is missing (text stored as outlines or images).

Found in the pilot: the 2022-23 printing of Class 10 "Democratic Politics-II" (jess4) and parts of
Class 11 "Themes in World History" (kehs1) carry almost no extractable text.  First choice is always
another Wayback capture of the same printing year or the year before (the 2020 and 2021 uploads have
normal text layers).  When no such capture exists, run this script.

Tool: RapidOCR (pip install rapidocr-onnxruntime) - free, offline, CPU only, no account.
Speed measured on this laptop: about 14 seconds per page at 200 dpi  ->  a 120-page book is ~30 minutes.

Usage:
    python code/ocr_fallback.py data/books/old/jess4 [--min-words 40] [--pages 2-4] [--dpi 200]
Writes <chapter>.ocr.json next to each PDF: {"<pdf page>": "text in reading order"} for every page whose
text layer has fewer than --min-words words.  (Reading these side-car files in ncertdiff.extract_chapter is
a listed next step; the pilot results do not use OCR text.)

Column handling: OCR returns one box per printed line.  Lines are grouped into columns by their left
edge (gap > 12% of page width starts a new column), columns are read left to right, lines top to bottom.
"""
import argparse
import json
import sys
from pathlib import Path

import numpy as np
import pymupdf


def order_lines(res, width):
    """res: list of [box(4 points), text, conf] -> text in column-aware reading order."""
    items = []
    for box, text, conf in res:
        xs = [p[0] for p in box]
        ys = [p[1] for p in box]
        items.append((min(xs), min(ys), max(xs), text))
    if not items:
        return ""
    # full-width lines (headings) stay in place by y; others are assigned to columns by left edge
    lefts = sorted({round(i[0] / (0.12 * width)) for i in items if (i[2] - i[0]) < 0.6 * width})
    def col(i):
        if (i[2] - i[0]) >= 0.6 * width:
            return -1
        return lefts.index(round(i[0] / (0.12 * width)))
    items.sort(key=lambda i: (col(i), i[1]))
    return " ".join(i[3] for i in items)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("folder")
    ap.add_argument("--min-words", type=int, default=40)
    ap.add_argument("--dpi", type=int, default=200)
    ap.add_argument("--pages", default="", help="optional range a-b (1-based) for a short test")
    a = ap.parse_args()
    from rapidocr_onnxruntime import RapidOCR
    ocr = RapidOCR()
    lo, hi = (map(int, a.pages.split("-")) if a.pages else (1, 10 ** 6))
    for pdf in sorted(Path(a.folder).glob("*.pdf")):
        doc = pymupdf.open(pdf)
        out = {}
        for i, page in enumerate(doc, start=1):
            if not (lo <= i <= hi) or len(page.get_text().split()) >= a.min_words:
                continue
            pix = page.get_pixmap(dpi=a.dpi)
            img = np.frombuffer(pix.samples, dtype=np.uint8).reshape(pix.height, pix.width, pix.n)[:, :, :3]
            res, _ = ocr(img)
            out[str(i)] = order_lines(res or [], pix.width)
            print(pdf.name, "page", i, len(out[str(i)].split()), "words", flush=True)
        if out:
            pdf.with_suffix(".ocr.json").write_text(json.dumps(out, ensure_ascii=False, indent=1), encoding="utf-8")


if __name__ == "__main__":
    sys.exit(main())
