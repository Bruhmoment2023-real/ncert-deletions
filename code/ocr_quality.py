"""OCR quality on a random sample of pages with a known text layer (ground truth = the PDF's own text).

Pages with >= 150 native words are drawn at random (seeded) from books whose text layer is good, rendered
at the same DPI as the OCR run, passed through the same Tesseract settings, and compared word by word
(multiset overlap of the pack's own tokeniser).  recall = share of native words found in the OCR text;
precision = share of OCR words found in the native text.
Usage: python -I code/ocr_quality.py [n_pages_per_book=8] [seed=11]   -> results/ocr_quality.csv
"""
import csv, os, random, subprocess, sys
from collections import Counter
from pathlib import Path
ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(Path(__file__).resolve().parent))
import ncertdiff as nd
import pymupdf
TESS = ROOT / "tools/tess/Library/bin/tesseract.exe"
TMP = Path(r"E:\Research-Staging\07-ncert-deletions\ocr-tmp")
BOOKS = [("rat2023", b) for b in ("kech1", "keps1", "gess2", "iess3", "leph1")]
n_per = int(sys.argv[1]) if len(sys.argv) > 1 else 8
rng = random.Random(int(sys.argv[2]) if len(sys.argv) > 2 else 11)
TMP.mkdir(parents=True, exist_ok=True)
rows = []
for lab, b in BOOKS:
    pool = []
    for pdf in sorted((ROOT / "data/books" / lab / b).glob("*.pdf")):
        if nd.is_front_matter(pdf.stem):
            continue
        d = pymupdf.open(str(pdf))
        for i, p in enumerate(d):
            if len(p.get_text().split()) >= 150:
                pool.append((pdf, i))
    for pdf, i in rng.sample(pool, min(n_per, len(pool))):
        d = pymupdf.open(str(pdf)); p = d[i]
        truth = nd.tokens(p.get_text())
        p.get_pixmap(dpi=250, colorspace=pymupdf.csGRAY).save(str(TMP / "q.png"))
        env = dict(os.environ, TESSDATA_PREFIX=str(ROOT / "tools/tessdata"), OMP_THREAD_LIMIT="2")
        subprocess.run([str(TESS), str(TMP / "q.png"), str(TMP / "q"), "-l", "eng"], env=env, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        ocr = nd.tokens(open(TMP / "q.txt", encoding="utf-8").read())
        ct, co = Counter(truth), Counter(ocr)
        inter = sum((ct & co).values())
        rows.append({"book": b, "file": pdf.name, "pdf_page": i + 1, "native_words": len(truth), "ocr_words": len(ocr),
                     "recall": round(inter / len(truth), 4), "precision": round(inter / max(1, len(ocr)), 4)})
        print(rows[-1], flush=True)
with open(ROOT / "results/ocr_quality.csv", "w", newline="") as f:
    w = csv.DictWriter(f, fieldnames=list(rows[0])); w.writeheader(); w.writerows(rows)
tot_n = sum(r["native_words"] for r in rows)
print("pages", len(rows), "word recall", round(sum(r["recall"] * r["native_words"] for r in rows) / tot_n, 4),
      "word precision", round(sum(r["precision"] * r["ocr_words"] for r in rows) / sum(r["ocr_words"] for r in rows), 4))
