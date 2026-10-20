"""Chapter-pairing threshold sensitivity (paper section 2.3). Reads results/chapter_summary.csv only (51 English books, body
chapters; front/back matter excluded as in the headline).  An old chapter is 'dropped' if the best new chapter retains less
than THR of its words (share_retained_in_best_candidate); the pipeline uses 0.30 (ncertdiff.CHAPTER_ALIGN_MIN).  Chapter-level
re-count, not a re-run of the diff: relative to the 0.30 run, a chapter that becomes dropped has all of its words counted as
removed (+ old_words - removed_words); a chapter that becomes surviving loses its moved_words (- moved_words).  The 0.30 row
is the plain sum of removed_words and equals the headline.  Writes results/threshold_sensitivity.csv."""
import csv
from pathlib import Path
ROOT = Path(__file__).resolve().parent.parent
BASE = 0.30
THRESHOLDS = (0.20, 0.25, 0.30, 0.35, 0.40)
def rd(p):
    return list(csv.DictReader(open(p, newline="", encoding="utf-8-sig")))
rows = [r for r in rd(ROOT / "results/chapter_summary.csv") if not r["book"].startswith("lh") and r["front_or_back_matter"] != "1"]
old_words = sum(int(r["old_words"]) for r in rows)
base_removed = sum(int(r["removed_words"]) for r in rows)
out = []
for thr in THRESHOLDS:
    removed, dropped = base_removed, 0
    for r in rows:
        is_dropped = float(r["share_retained_in_best_candidate"]) < thr
        was_dropped = float(r["share_retained_in_best_candidate"]) < BASE
        dropped += is_dropped
        if is_dropped and not was_dropped:
            removed += int(r["old_words"]) - int(r["removed_words"])
        elif was_dropped and not is_dropped:
            removed -= int(r["moved_words"])
    out.append({"threshold": thr, "english_books": len({r["book"] for r in rows}), "old_words": old_words, "removed_words": removed,
                "share_removed": round(removed / old_words, 4), "removed_change_vs_30": removed - base_removed, "chapters_dropped": dropped})
with open(ROOT / "results/threshold_sensitivity.csv", "w", newline="", encoding="utf-8-sig") as f:
    w = csv.DictWriter(f, fieldnames=list(out[0])); w.writeheader(); w.writerows(out)
for r in out: print(r)
