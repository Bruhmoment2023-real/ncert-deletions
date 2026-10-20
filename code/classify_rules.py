"""Apply the pre-written codebook (code/codebook.json) to removed passages with keyword rules.

Usage:
    python code/classify_rules.py code/pilot_pairs.csv            # classify all removed passages
    python code/classify_rules.py code/pilot_pairs.csv --sample 60 --seed 3
          -> also writes results/category_label_sample_WORKING.csv with the rule output HIDDEN
             (column left out) so that a human can label blind; agreement is then computed by
             code/agreement.py

Outputs:
    results/passages_classified_WORKING.csv   (contains textbook text: not for release)
    results/removed_words_by_theme.csv, results/removed_words_by_period.csv, results/removed_words_by_form.csv
"""
import argparse
import csv
import json
import random
import re
import statistics
import sys
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(Path(__file__).resolve().parent))
import ncertdiff as nd  # noqa: E402

CB = json.loads((ROOT / "code" / "codebook.json").read_text(encoding="utf-8"))
THEMES = list(CB["themes"].keys())
THEME_RE = {t: [(k, re.compile(r"(?<![a-z])" + re.escape(k) + r"(?![a-z])")) for k in v["keywords"]] for t, v in CB["themes"].items()}
PERIODS = CB["periods"]
QWORDS = r"(discuss|explain|write|find out|compare|describe|mention|state|why|what|how|which|do you|list|identify|read|look at|match|fill)"


def theme_of(text):
    low = nd.clean(text).lower()
    hits = {t: sum(1 for k, rx in THEME_RE[t] if rx.search(low)) for t in THEMES}
    best = max(THEMES, key=lambda t: (hits[t], -THEMES.index(t)))
    multi = [t for t in THEMES if hits[t] > 0]
    return (best if hits[best] > 0 else "unclassified"), multi


def period_of(text, chapter_period=""):
    low = nd.clean(text).lower()
    for p, v in PERIODS.items():
        if any(re.search(r"(?<![a-z])" + re.escape(k) + r"(?![a-z])", low) for k in v.get("keywords", [])):
            return p, "keyword"
    if re.search(r"\bbce\b|\bb\.c\.", low):
        return "p2_early_india", "bce"
    years = [int(y) for y in re.findall(r"(?<!\d)(1[0-9]{3}|20[0-2][0-9])(?!\d)", low)]
    if years:
        y = statistics.median(years)
        for p, v in PERIODS.items():
            if "years" in v and v["years"][0] <= y <= v["years"][1]:
                return p, "year"
    return (chapter_period or "no_period"), ("chapter" if chapter_period else "none")


def form_of(text):
    t = nd.clean(text)
    low = t.lower()
    if t.endswith("?") or re.match(r"^(\d+\.|[•�*-])?\s*" + QWORDS + r"\b", low):
        return "exercise_question"
    if re.search(r"fig\. ?\d|credit:|source: |university press|publications?,|\(eds?\.?\)|\bpp?\. ?\d", low):
        return "credit_reference"
    if len(low.split()) < 6 and "." not in t[:-1]:
        return "heading_label"
    return "body_or_box_text"


def passages(pairs_file):
    chap_period = {}
    cp = ROOT / "code" / "chapter_periods.csv"
    if cp.exists():
        for r in csv.DictReader(open(cp, encoding="utf-8")):
            chap_period[r["chapter_file"]] = r["period"]
    out = []
    for row in csv.DictReader(open(pairs_file, newline="", encoding="utf-8")):
        if row["new_label"] != "rat2023":
            continue
        tag = f"{row['book']}__{row['old_label']}__{row['new_label']}"
        groups = defaultdict(list)
        with open(ROOT / "results" / "units" / f"{tag}__old.csv", encoding="utf-8-sig", newline="") as f:
            for u in csv.DictReader(f):
                if nd.is_front_matter(u["chapter"]) or u["label"] not in ("deleted", "reworded"):
                    continue
                groups[(u["chapter"], u["pdf_page"], u["block"])].append(u)
        for (ch, pg, bl), us in groups.items():
            text = " ".join(u["text"] for u in us)
            removed = sum(int(u["n_words"]) - int(u["retained_book"]) for u in us)
            th, multi = theme_of(text)
            per, how = period_of(text, chap_period.get(ch, ""))
            out.append({"book": row["book"], "chapter": ch, "printed_page": us[0]["printed_page"], "block": bl,
                        "removed_words": removed, "theme_rule": th, "themes_all": "|".join(multi),
                        "period_rule": per, "period_how": how, "form_rule": form_of(text), "font": us[0]["font"], "text": text})
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("pairs")
    ap.add_argument("--sample", type=int, default=0)
    ap.add_argument("--seed", type=int, default=3)
    a = ap.parse_args()
    ps = passages(a.pairs)
    with open(ROOT / "results" / "passages_classified_WORKING.csv", "w", newline="", encoding="utf-8-sig") as f:
        w = csv.DictWriter(f, fieldnames=list(ps[0].keys()))
        w.writeheader()
        w.writerows(ps)
    for dim in ("theme_rule", "period_rule", "form_rule"):
        agg = defaultdict(lambda: [0, 0])
        for p in ps:
            agg[(p["book"], p[dim])][0] += p["removed_words"]
            agg[(p["book"], p[dim])][1] += 1
        name = {"theme_rule": "theme", "period_rule": "period", "form_rule": "form"}[dim]
        with open(ROOT / "results" / f"removed_words_by_{name}.csv", "w", newline="", encoding="utf-8-sig") as f:
            w = csv.writer(f)
            w.writerow(["book", name, "removed_words", "passages"])
            for (b, c), (words, n) in sorted(agg.items()):
                w.writerow([b, c, words, n])
    print("passages:", len(ps), "removed words:", sum(p["removed_words"] for p in ps))
    if a.sample:
        rng = random.Random(a.seed)
        pool = [p for p in ps if p["form_rule"] == "body_or_box_text" and len(p["text"].split()) >= 15]
        pick = rng.sample(pool, min(a.sample, len(pool)))
        with open(ROOT / "results" / "category_label_sample_WORKING.csv", "w", newline="", encoding="utf-8-sig") as f:
            w = csv.writer(f)
            w.writerow(["id", "book", "chapter", "printed_page", "block", "text", "hand_theme", "hand_period", "hand_note"])
            for i, p in enumerate(pick, 1):
                w.writerow([i, p["book"], p["chapter"], p["printed_page"], p["block"], p["text"], "", "", ""])
        print("label sample written:", len(pick), "of", len(pool), "eligible passages")


if __name__ == "__main__":
    main()
