"""OCR for chapter PDFs that lack a usable text layer (full-corpus run; new file, the pack's code is untouched).

Free tool: Tesseract 5.5 (conda-forge build) installed under full-corpus/tools/tess without admin,
tessdata_fast eng + hin in full-corpus/tools/tessdata.

For each PDF in <src_dir>, every page with fewer than MIN_WORDS words of native text is rendered
(DPI) and passed through Tesseract, which returns a one-page PDF with a text layer.  Pages that
already have text are copied unchanged.  The result is written to <dst_dir>/<same file name>, so
the pack's pipeline reads it as an ordinary edition folder.  A side-car <dst_dir>/ocr_pages.csv
lists the OCR'd pages.

Usage: python -I code/ocr_pdf.py <src_dir> <dst_dir> [--lang eng|hin+eng] [--dpi 250]
"""
import argparse
import csv
import os
import subprocess
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
TESS = ROOT / "tools" / "tess" / "Library" / "bin" / "tesseract.exe"
TESSDATA = ROOT / "tools" / "tessdata"
TMP = Path(r"E:\Research-Staging\07-ncert-deletions\ocr-tmp")
MIN_WORDS = 40


def ocr_page(pix_png: Path, out_base: Path, lang: str):
    env = dict(os.environ, TESSDATA_PREFIX=str(TESSDATA), OMP_THREAD_LIMIT="2")
    subprocess.run([str(TESS), str(pix_png), str(out_base), "-l", lang, "pdf"], env=env, check=True,
                   stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    return out_base.with_suffix(".pdf")


def main(src, dst, lang="eng", dpi=250, only=None):
    import pymupdf
    sys.path.insert(0, str(Path(__file__).resolve().parent))
    import ncertdiff as nd
    src, dst = Path(src), Path(dst)
    dst.mkdir(parents=True, exist_ok=True)
    TMP.mkdir(parents=True, exist_ok=True)
    rows = []
    for pdf in sorted(src.glob("*.pdf")):
        if only and pdf.stem not in only:
            continue
        doc = pymupdf.open(str(pdf))
        out = pymupdf.open()
        n_ocr = 0
        t0 = time.time()
        for i, page in enumerate(doc):
            if len(nd.tokens(page.get_text("text"))) >= MIN_WORDS:   # usable Latin words, not just any characters
                out.insert_pdf(doc, from_page=i, to_page=i)
                continue
            png = TMP / "p.png"
            page.get_pixmap(dpi=dpi, colorspace=pymupdf.csGRAY).save(str(png))
            try:
                op = ocr_page(png, TMP / "p", lang)
                with pymupdf.open(str(op)) as od:
                    out.insert_pdf(od)
                n_ocr += 1
                rows.append([pdf.name, i + 1, lang, dpi])
            except Exception as e:  # noqa
                out.insert_pdf(doc, from_page=i, to_page=i)
                rows.append([pdf.name, i + 1, "FAILED " + repr(e)[:60], dpi])
        out.save(str(dst / pdf.name), garbage=3, deflate=True)
        print(pdf.name, "pages", len(doc), "ocr", n_ocr, f"{time.time()-t0:.0f}s", flush=True)
    log = dst / "ocr_pages.csv"
    new = not log.exists()
    with open(log, "a", newline="") as f:
        w = csv.writer(f)
        if new:
            w.writerow(["file", "pdf_page", "lang", "dpi"])
        w.writerows(rows)


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("src")
    ap.add_argument("dst")
    ap.add_argument("--lang", default="eng")
    ap.add_argument("--dpi", type=int, default=250)
    ap.add_argument("--only", nargs="*")
    a = ap.parse_args()
    main(a.src, a.dst, a.lang, a.dpi, a.only)
