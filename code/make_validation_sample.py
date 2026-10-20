"""Draw the stratified random validation sample and attach independent evidence for each item.

Usage: python code/make_validation_sample.py code/pilot_pairs.csv [seed]

For every sampled old-edition unit we attach the most similar unit found ANYWHERE in the new
edition by a different method from the pipeline (character-level fuzzy search, rapidfuzz
partial_ratio_alignment of the
normalised sentence against the whole normalised new book), so that the checker is not just re-reading the pipeline's own answer.
The checker then opens the two PDFs at the printed page given and fills in `hand_label`
(kept / reworded / moved / deleted) and `hand_note`.

Output: results/validation_sample_WORKING.csv  (contains textbook sentences: not for release)
"""
import csv
import random
import re
import sys
from pathlib import Path

from rapidfuzz import fuzz, process

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(Path(__file__).resolve().parent))
import ncertdiff as nd  # noqa: E402

STRATA = {  # label, in dropped chapter?, n
    ("deleted", False): 40, ("reworded", False): 20, ("moved", False): 10, ("kept", False): 20, ("deleted", True): 10}
MIN_WORDS = 5
OUTNAME = "validation_sample_WORKING.csv"


def sig(t):
    return re.sub(r"[^a-z0-9]", "", nd.clean(t).lower())


def main(pairs_file, seed=20261013):
    rng = random.Random(seed)
    pool = {k: [] for k in STRATA}
    new_text = {}
    book_stream = {}
    for row in csv.DictReader(open(pairs_file, newline="", encoding="utf-8")):
        if row["new_label"] != "rat2023":
            continue
        tag = f"{row['book']}__{row['old_label']}__{row['new_label']}"
        dropped = set()
        with open(ROOT / "results" / "chapter_summary.csv", encoding="utf-8-sig", newline="") as f:
            for r in csv.DictReader(f):
                if r["book"] == row["book"] and r["new_edition"] == "rat2023" and r["chapter_dropped"] == "1":
                    dropped.add(r["old_chapter_file"])
        with open(ROOT / "results" / "units" / f"{tag}__new.csv", encoding="utf-8-sig", newline="") as f:
            new_text[row["book"]] = [(r["chapter"], r["printed_page"], r["text"]) for r in csv.DictReader(f)]
        with open(ROOT / "results" / "units" / f"{tag}__old.csv", encoding="utf-8-sig", newline="") as f:
            for r in csv.DictReader(f):
                if nd.is_front_matter(r["chapter"]) or int(r["n_words"]) < MIN_WORDS:
                    continue
                key = (r["label"], r["chapter"] in dropped)
                if key in pool:
                    pool[key].append({"book": row["book"], **r})
    rows = []
    for key, n in STRATA.items():
        pick = rng.sample(pool[key], min(n, len(pool[key])))
        for r in pick:
            # independent check: best-aligned window anywhere in the whole new book (character level)
            stream = book_stream.setdefault(r["book"], " ".join(" ".join(nd.tokens(c[2])) for c in new_text[r["book"]]))
            so = " ".join(nd.tokens(r["text"]))
            al = fuzz.partial_ratio_alignment(so, stream)
            score = al.score if al else 0
            window = stream[max(0, al.dest_start - 30):al.dest_end + 30] if al else ""
            m = (None, score)
            best = ("", "", window)
            rows.append({"stratum": f"{key[0]}{'_dropped_chapter' if key[1] else ''}", "stratum_population": len(pool[key]),
                         "book": r["book"], "old_chapter": r["chapter"], "old_printed_page": r["printed_page"],
                         "n_words": r["n_words"], "retained_book": r["retained_book"], "pipeline_label": r["label"],
                         "pipeline_note": r["note"], "font": r["font"], "old_text": r["text"],
                         "independent_best_match_score": round(m[1]) if m else 0,
                         "best_match_new_text_normalised": best[2],
                         "hand_label": "", "hand_note": ""})
    rng.shuffle(rows)
    for i, r in enumerate(rows, 1):
        r["id"] = i
    with open(ROOT / "results" / OUTNAME, "w", newline="", encoding="utf-8-sig") as f:
        w = csv.DictWriter(f, fieldnames=["id"] + [k for k in rows[0] if k != "id"])
        w.writeheader()
        w.writerows(rows)
    print("sampled", len(rows), {f"{k[0]}{'_dropped' if k[1] else ''}": len(v) for k, v in pool.items()})


if __name__ == "__main__":
    if len(sys.argv) > 3:
        OUTNAME = sys.argv[3]
    main(sys.argv[1], int(sys.argv[2]) if len(sys.argv) > 2 else 20261013)
