"""What the 30% chapter-pairing threshold changes, and what it does not.

A word counts as removed when it is found nowhere in the new edition (run_diff.py, removed_words =
n - retained_book), so the word totals do not depend on how chapters are paired. The threshold only
decides which old chapters count as dropped, and therefore how the removed words split between
dropped and surviving chapters. This replaces threshold_sensitivity.py, which wrongly assumed that a
dropped chapter's words were all counted as removed.
Usage: python -I threshold_sensitivity_v10.py <full-corpus/results/chapter_summary.csv>
"""
import csv, sys

rows = [r for r in csv.DictReader(open(sys.argv[1], encoding="utf-8-sig"))
        if r["front_or_back_matter"] == "0" and not r["book"].startswith("lh")]  # lh* = Hindi-medium books
total = sum(int(r["removed_words"]) for r in rows)
print(f"English chapter files: {len(rows)}; removed words at any threshold: {total:,}")
for t in (0.20, 0.25, 0.30, 0.35, 0.40):
    d = [r for r in rows if float(r["share_retained_in_best_candidate"] or 0) < t]
    old, rem = sum(int(r["old_words"]) for r in d), sum(int(r["removed_words"]) for r in d)
    print(f"threshold {t:.2f}: {len(d)} dropped chapters holding {old:,} words, of which {rem:,} removed "
          f"({100 * rem / total:.1f}% of all removed words)")
d = sorted(int(r["removed_words"]) / int(r["old_words"]) for r in rows if r["chapter_dropped"] == "1" and int(r["old_words"]))
print(f"share of a dropped chapter's words counted as removed (30%): median {100 * d[len(d) // 2]:.1f}%, "
      f"range {100 * d[0]:.1f}% to {100 * d[-1]:.1f}%")
