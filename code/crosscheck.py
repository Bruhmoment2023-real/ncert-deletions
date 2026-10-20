"""Automated cross-check of pipeline labels with an independent matcher (not a substitute for
the hand validation; it widens the sample).

The pipeline decides with word K-grams.  Here every sampled old-edition unit is instead aligned,
character by character, against the whole normalised text of the new edition
(rapidfuzz.partial_ratio_alignment).  Score >= 97 means the sentence is present essentially
verbatim; score <= 68 means nothing like it is present.

Usage: python code/crosscheck.py code/pilot_pairs.csv [n_kept_per_book=300] [seed=1]
Output: results/crosscheck_summary.csv
"""
import csv
import random
import sys
from collections import Counter
from pathlib import Path

from rapidfuzz import fuzz

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(Path(__file__).resolve().parent))
import ncertdiff as nd  # noqa: E402


def main(pairs_file, n_kept=300, seed=1):
    rng = random.Random(seed)
    tally = Counter()
    for row in csv.DictReader(open(pairs_file, newline="", encoding="utf-8")):
        if row["new_label"] != "rat2023":
            continue
        tag = f"{row['book']}__{row['old_label']}__{row['new_label']}"
        with open(ROOT / "results" / "units" / f"{tag}__new.csv", encoding="utf-8-sig", newline="") as f:
            stream = " ".join(" ".join(nd.tokens(r["text"])) for r in csv.DictReader(f))
        with open(ROOT / "results" / "units" / f"{tag}__old.csv", encoding="utf-8-sig", newline="") as f:
            units = [r for r in csv.DictReader(f) if not nd.is_front_matter(r["chapter"]) and int(r["n_words"]) >= 6]
        kept = [u for u in units if u["label"] == "kept"]
        other = [u for u in units if u["label"] != "kept"]
        if len(other) > 400:   # dropped chapters: a random 400 is enough
            other = rng.sample(other, 400)
        for u in rng.sample(kept, min(n_kept, len(kept))) + other:
            so = " ".join(nd.tokens(u["text"]))
            al = fuzz.partial_ratio_alignment(so, stream)
            sc = al.score if al else 0
            verdict = "present(>=97)" if sc >= 97 else ("absent(<=68)" if sc <= 68 else "partial(69-96)")
            tally[(u["label"], verdict)] += 1
    labels = ["kept", "reworded", "moved", "deleted"]
    verdicts = ["present(>=97)", "partial(69-96)", "absent(<=68)"]
    with open(ROOT / "results" / "crosscheck_summary.csv", "w", newline="", encoding="utf-8-sig") as f:
        w = csv.writer(f)
        w.writerow(["pipeline_label"] + verdicts + ["n"])
        for lab in labels:
            row = [tally[(lab, v)] for v in verdicts]
            w.writerow([lab] + row + [sum(row)])
            print(lab, dict(zip(verdicts, row)))


if __name__ == "__main__":
    a = sys.argv
    main(a[1], int(a[2]) if len(a) > 2 else 300, int(a[3]) if len(a) > 3 else 1)
