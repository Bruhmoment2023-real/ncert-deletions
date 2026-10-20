"""Post-diff quality checks per pair (new for the full-corpus run). Writes results/qa_flags.csv.
Flags:
  OLD_TEXT_INCOMPLETE  words added / words in new edition > 10% or words-per-page of old < 75% of new
  ZERO_CHANGE_BUT_LISTED  no removal measured though NCERT's list has entries for the book
  LISTED_NO_CHANGE_ZERO   zero measured and the list says NO CHANGE (consistent)
"""
import csv, collections
from pathlib import Path
ROOT = Path(__file__).resolve().parent.parent
PACK = ROOT.parent
oc = {r["book"]: r["official_code"] for r in csv.DictReader(open(ROOT / "code/official_codes.csv"))}
off = collections.defaultdict(lambda: {"rows": 0, "nochange": 0})
for r in csv.DictReader(open(PACK / "02-official-listed-deletions.csv", encoding="utf-8-sig")):
    if r["dropped_raw"].startswith("UNRULED"):
        continue
    o = off[r["book_code"]]
    if r["dropped_raw"] == "NO CHANGE":
        o["nochange"] = 1
    else:
        o["rows"] += 1
meta = collections.defaultdict(lambda: collections.defaultdict(lambda: [0, 0]))
for r in csv.DictReader(open(ROOT / "results/extraction_meta.csv", encoding="utf-8-sig")):
    if r["chapter"].endswith(("ps", "an", "gl")):
        continue
    m = meta[r["book"]][r["edition"]]
    m[0] += int(r["words"]); m[1] += int(r["pages"])
out = []
for r in csv.DictReader(open(ROOT / "results/book_summary.csv", encoding="utf-8-sig")):
    b = r["book"]; o = off[oc[b]]
    mo, mn = meta[b][r["old_edition"]], meta[b]["rat2023"]
    wpp_o, wpp_n = mo[0] / max(1, mo[1]), mn[0] / max(1, mn[1])
    nw = int(r["new_words"]) or 1
    flags = []
    if int(r["added_words"]) / nw > 0.10 or wpp_o < 0.75 * wpp_n:
        flags.append("OLD_TEXT_INCOMPLETE")
    if int(r["removed_words"]) < 0.002 * int(r["old_words"]) and o["rows"] > 0:
        flags.append("ZERO_CHANGE_BUT_LISTED")
    if int(r["removed_words"]) < 0.002 * int(r["old_words"]) and o["nochange"]:
        flags.append("ZERO_CONSISTENT_WITH_NO_CHANGE_LIST")
    out.append({"book": b, "old_edition": r["old_edition"], "removed_words": r["removed_words"], "old_words": r["old_words"],
                "added_share_of_new": round(int(r["added_words"]) / nw, 4), "words_per_page_old": round(wpp_o), "words_per_page_new": round(wpp_n),
                "official_rows": o["rows"], "official_no_change": o["nochange"], "flags": ";".join(flags)})
with open(ROOT / "results/qa_flags.csv", "w", newline="", encoding="utf-8-sig") as f:
    w = csv.DictWriter(f, fieldnames=list(out[0])); w.writeheader(); w.writerows(out)
for o in out:
    if o["flags"]:
        print(o["book"], o["old_edition"], o["flags"], o["removed_words"], o["added_share_of_new"], o["words_per_page_old"], o["words_per_page_new"])
