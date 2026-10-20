"""Records the adjudication of the fresh validation sample (results/validation_fresh_WORKING.csv).
Adjudicated by the AI agent that ran this job, reading each old sentence against the best independent match in the
new edition (character-level alignment) - NOT by a person.  C = pipeline label confirmed, N = not confirmed,
U = uncertain (mostly equation/formula fragments whose text-layer formatting differs between printings).
Writes results/validation_fresh_adjudicated_WORKING.csv and results/validation_fresh_summary.csv."""
import csv
from collections import Counter, defaultdict
from pathlib import Path
ROOT = Path(__file__).resolve().parent.parent
V = {}
for i in (1,2,3,4,5,6,7,8,9,11,12,13,14,15,17,18,20,21,22,23,24,25,26,27,28,29,30,31,32,33,34,35,36,38,39,41,42,44,45,46,47,48,49,50,
          53,54,55,56,57,58,59,60,61,62,63,64,65,68,69,70,71,73,75,76,80,81,82,83,84,85,86,87,88,89,90,91,92,93,94,95,96,97,99,100): V[i] = "C"
for i in (10,19,40,66,67,78): V[i] = "N"
for i in (16,37,43,51,52,72,74,77,79,98): V[i] = "U"
NOTE = {10: "sentence absent from new edition (deleted, not reworded)", 19: "absent (deleted)", 40: "absent (deleted)", 66: "a different sentence in the new edition",
        67: "caption absent", 78: "heading absent", 16: "table row data reappear in another format", 43: "same text, formatting differs (kept)",
        51: "same text, formatting differs", 52: "same text, formatting differs", 72: "present verbatim (kept)", 74: "present, formatting differs",
        77: "rewritten sentence on the same point", 79: "present, formatting differs", 98: "present, formatting differs", 37: "formula fragment"}
rows = list(csv.DictReader(open(ROOT / "results/validation_fresh_WORKING.csv", encoding="utf-8-sig")))
assert len(rows) == 100 and set(V) == set(range(1, 101)), set(range(1, 101)) - set(V)
tally = defaultdict(Counter)
for r in rows:
    r["adjudicated"] = V[int(r["id"])]; r["adjudication_note"] = NOTE.get(int(r["id"]), "")
    r["hand_label"] = ""; tally[r["stratum"]][r["adjudicated"]] += 1
with open(ROOT / "results/validation_fresh_adjudicated_WORKING.csv", "w", newline="", encoding="utf-8-sig") as f:
    w = csv.DictWriter(f, fieldnames=list(rows[0])); w.writeheader(); w.writerows(rows)
with open(ROOT / "results/validation_fresh_summary.csv", "w", newline="", encoding="utf-8-sig") as f:
    w = csv.writer(f); w.writerow(["stratum", "sampled", "confirmed", "not_confirmed", "uncertain", "error_rate_not_confirmed", "error_rate_incl_uncertain", "adjudicator"])
    tot = Counter()
    for s, c in sorted(tally.items()):
        n = sum(c.values()); tot.update(c)
        w.writerow([s, n, c["C"], c["N"], c["U"], round(c["N"] / n, 3), round((c["N"] + c["U"]) / n, 3), "AI agent (not a person)"])
        print(s, n, dict(c))
