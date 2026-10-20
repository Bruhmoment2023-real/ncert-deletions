"""Sensitivity and OCR-comparison tables (new). Reads results/sensitivity/*/book_summary.csv (K=4, K=8, no fuzzy pass, over
the 51 English books + 5 Hindi) and results/alt_*/book_summary.csv (alternative old editions for the 7 books whose
2022-23 capture had no usable text layer).  Writes tables/table13_sensitivity.csv and tables/table14_ocr_vs_textlayer.csv."""
import csv
from pathlib import Path
ROOT = Path(__file__).resolve().parent.parent
T = ROOT / "tables"
def rd(p):
    return list(csv.DictReader(open(p, newline="", encoding="utf-8-sig")))
prim = {r["book"]: r for r in rd(ROOT / "results/book_summary.csv")}
eng = [b for b in prim if not b.startswith("lh")]
rows = []
def tot(d, books):
    ow = sum(int(d[b]["old_words"]) for b in books); rem = sum(int(d[b]["removed_words"]) for b in books)
    cd = sum(int(d[b]["chapters_dropped"]) for b in books)
    return ow, rem, cd
for name, p in (("K=5 (headline)", ROOT / "results/book_summary.csv"), ("K=4", ROOT / "results/sensitivity/k4/book_summary.csv"),
                ("K=8", ROOT / "results/sensitivity/k8/book_summary.csv"), ("K=5, no fuzzy second pass", ROOT / "results/sensitivity/nofuzzy/book_summary.csv")):
    if not p.exists():
        continue
    d = {r["book"]: r for r in rd(p)}
    ow, rem, cd = tot(d, eng)
    rows.append({"setting": name, "english_books": len(eng), "old_words": ow, "removed_words": rem, "share_removed": round(rem / ow, 4), "chapter_files_dropped": cd})
with open(T / "table13_sensitivity.csv", "w", newline="", encoding="utf-8-sig") as f:
    w = csv.DictWriter(f, fieldnames=list(rows[0])); w.writeheader(); w.writerows(rows)
alts = {}
for p in (ROOT / "results").glob("alt_*/book_summary.csv"):
    for r in rd(p):
        alts[(r["book"], r["old_edition"])] = r
out = []
for (b, ed), r in sorted(alts.items()):
    pr = prim[b]
    if ed == pr['old_edition']:
        continue
    out.append({"book": b, "primary_old_edition": pr["old_edition"], "primary_removed": pr["removed_words"], "primary_share": pr["share_removed"],
                "primary_added": pr["added_words"], "compared_old_edition": ed, "compared_removed": r["removed_words"], "compared_share": r["share_removed"],
                "compared_added": r["added_words"], "compared_chapters_dropped": r["chapters_dropped"], "primary_chapters_dropped": pr["chapters_dropped"]})
if out:
    with open(T / "table14_ocr_vs_textlayer.csv", "w", newline="", encoding="utf-8-sig") as f:
        w = csv.DictWriter(f, fieldnames=list(out[0])); w.writeheader(); w.writerows(out)
for r in rows: print(r)
for r in out: print(r)
