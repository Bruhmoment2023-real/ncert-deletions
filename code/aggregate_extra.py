"""Pairing/retrieval status per book (table0) and the largest unlisted passages (table15; counts only, no text)."""
import csv
from collections import defaultdict
from pathlib import Path
ROOT = Path(__file__).resolve().parent.parent
T = ROOT / "tables"
def rd(p): return list(csv.DictReader(open(p, newline="", encoding="utf-8-sig")))
t1 = {r["book"]: r for r in rd(T / "table1_by_book.csv")}
log = rd(ROOT / "retrieval-log.csv")
att = defaultdict(list)
for r in log:
    if r["role"] in ("old", "rat2023") and r["verdict"] not in ("accepted",):
        att[(r["book"], r["role"])].append(f"{r['capture_ts'][:8]}:{r['verdict']}" + (f" ({r['note'][:40]})" if r["verdict"] == "rejected" else ""))
labels = {r["book"]: r for r in rd(ROOT / "code/corpus_pairs.csv")}
out = []
for b, r in t1.items():
    n = []
    if r["old_source"] == "old_alt":
        n.append("2022-23 capture had no usable text layer; older text-layer printing used as primary, OCR of the 2022-23 scan run as a comparison (table14)")
    if r["old_source"] == "old2122":
        n.append("2021-22 chapter PDFs fetched one by one (pilot); zip of Oct 2021 still held 2020-21")
    if r["old_print_stamp"] in ("2020-21", "2021-22"):
        n.append("baseline is an earlier printing than 2022-23: ordinary reprint changes could be included")
    if b.startswith("lh"):
        n.append("Hindi medium: text layer is in a legacy font encoding; the diff runs on the encoded strings (consistent across editions); counts are approximate words")
    if r["new_print_stamp"].lower().startswith("rationalised") is False:
        n.append("new edition stamp not read")
    out.append({"book": b, "class": r["class"], "subject": r["subject"], "language": r["language"], "title": r["title"],
                "paired": "yes", "old_capture": r["old_capture"], "old_print_stamp": r["old_print_stamp"], "old_source": r["old_source"],
                "new_capture": r["new_capture"], "new_print_stamp": r["new_print_stamp"],
                "newer_captures_tried_and_rejected": "; ".join(att[(b, "rat2023")]),
                "preferred_old_captures_tried_and_rejected": "; ".join(att[(b, "old")]), "notes": " | ".join(n)})
with open(T / "table0_pairing_and_retrieval.csv", "w", newline="", encoding="utf-8-sig") as f:
    w = csv.DictWriter(f, fieldnames=list(out[0])); w.writeheader(); w.writerows(out)
g = defaultdict(int)
for r in rd(ROOT / "results/unlisted_units_WORKING.csv"):
    if r["list_status"] == "unlisted" and not r["book"].startswith("lh"):
        g[(r["book"], r["chapter"], r["printed_page"], r["page_source"])] += int(r["removed_words"])
top = sorted(g.items(), key=lambda kv: -kv[1])[:30]
with open(T / "table15_largest_unlisted_pages.csv", "w", newline="", encoding="utf-8-sig") as f:
    w = csv.writer(f); w.writerow(["book", "chapter_file", "printed_page", "page_source", "removed_words_on_page_not_in_lists"])
    for (b, c, p, s), v in top: w.writerow([b, c, p, s, v])
print(len(out), "books;", "top unlisted:", top[:5])
