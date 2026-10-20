"""Build code/corpus_pairs.csv (pairs file for run_corpus.py) from the acquisition state.
A book is paired when a rationalised edition is accepted in data/books/rat2023/<book> and an old
edition is in data/books/<old_label>/<book>  (old_label = old | old_ocr | old2122, see logs/pair_labels.csv)."""
import csv, json
from pathlib import Path
ROOT = Path(__file__).resolve().parent.parent
PACK = ROOT.parent
av = {r["ncert_file_code"]: r for r in csv.DictReader(open(PACK / "02-availability.csv", encoding="utf-8-sig"))}
oc = {r["book"]: r["official_code"] for r in csv.DictReader(open(ROOT / "code" / "official_codes.csv"))}
over = {}
p = ROOT / "logs" / "pair_labels.csv"
if p.exists():
    over = {r["book"]: r for r in csv.DictReader(open(p))}
TITLE_FIX = {"kegy1": "India: Physical Environment", "kegy2": "Fundamentals of Physical Geography",
             "leec1": "Introductory Macroeconomics", "leec2": "Introductory Microeconomics"}  # verified on the title pages
rows = []
for b, r in av.items():
    ol = over.get(b, {}).get("old_label", "old")
    nl = over.get(b, {}).get("new_label", "rat2023")
    od, nd_ = ROOT / "data" / "books" / ol / b, ROOT / "data" / "books" / nl / b
    if od.exists() and nd_.exists() and any(od.glob("*.pdf")) and any(nd_.glob("*.pdf")) and over.get(b, {}).get("exclude") != "1":
        rows.append({"book": b, "official_code": oc[b], "title": TITLE_FIX.get(b, r["title"]), "old_label": ol, "new_label": nl})
with open(ROOT / "code" / "corpus_pairs.csv", "w", newline="", encoding="utf-8") as f:
    w = csv.DictWriter(f, fieldnames=["book", "official_code", "title", "old_label", "new_label"])
    w.writeheader(); w.writerows(rows)
print(len(rows), "pairs")
