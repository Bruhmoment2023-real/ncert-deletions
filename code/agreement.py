"""Agreement between the keyword rules and a labelled sample (accuracy and Cohen's kappa).

Usage: python code/agreement.py [label_column_prefix=hand]
Reads  results/category_label_sample_WORKING.csv  (columns <prefix>_theme, <prefix>_period filled in)
       results/passages_classified_WORKING.csv    (rule output)
Writes results/category_agreement_<prefix>.csv    (confusion counts, no textbook text: releasable)
"""
import csv
import sys
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def kappa(pairs):
    n = len(pairs)
    po = sum(a == b for a, b in pairs) / n
    ca, cb = Counter(a for a, _ in pairs), Counter(b for _, b in pairs)
    pe = sum(ca[k] * cb.get(k, 0) for k in ca) / (n * n)
    return po, (po - pe) / (1 - pe) if pe < 1 else 1.0


def main(prefix="hand"):
    rules = {}
    with open(ROOT / "results" / "passages_classified_WORKING.csv", encoding="utf-8-sig", newline="") as f:
        for r in csv.DictReader(f):
            rules[(r["chapter"], r["printed_page"], r["block"])] = r
    rows = []
    with open(ROOT / "results" / "category_label_sample_WORKING.csv", encoding="utf-8-sig", newline="") as f:
        for r in csv.DictReader(f):
            if r.get(f"{prefix}_theme"):
                rows.append((r, rules[(r["chapter"], r["printed_page"], r["block"])]))
    out = []
    for dim in ("theme", "period"):
        pairs = [(r[f"{prefix}_{dim}"], q[f"{dim}_rule"]) for r, q in rows]
        po, k = kappa(pairs)
        print(f"{dim}: n={len(pairs)} raw agreement={po:.3f} Cohen's kappa={k:.3f}")
        out.append([dim, "ALL", "ALL", len(pairs), round(po, 3), round(k, 3)])
        if dim == "theme":
            multi = sum(r[f"{prefix}_theme"] in q["themes_all"].split("|") or r[f"{prefix}_theme"] == q["theme_rule"] for r, q in rows)
            print(f"theme: labelled theme is among ALL rule themes (multi-label) in {multi}/{len(rows)}")
            out.append(["theme_multilabel_hit", "ALL", "ALL", len(rows), round(multi / len(rows), 3), ""])
        for (a, b), c in sorted(Counter(pairs).items(), key=lambda t: -t[1]):
            out.append([dim, a, b, c, "", ""])
    with open(ROOT / "results" / f"category_agreement_{prefix}.csv", "w", newline="", encoding="utf-8-sig") as f:
        w = csv.writer(f)
        w.writerow(["dimension", f"{prefix}_label", "rule_label", "n", "raw_agreement", "cohens_kappa"])
        w.writerows(out)


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else "hand")
