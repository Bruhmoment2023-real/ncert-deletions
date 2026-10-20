"""Run the pack's pipeline (run_diff.py, unchanged) on each complete pair, one book at a time.

Usage: python -I code/run_corpus.py code/corpus_pairs.csv

For each row of the pairs file it calls run_diff.py as a subprocess with --out results/_run/<book>,
then moves that book's unit files to results/units/ and keeps its three summary tables in
results/perbook/<book>/ .  merge_results() then concatenates them into results/{chapter_summary,
book_summary,extraction_meta}.csv.  Skips books already done.
"""
import csv
import shutil
import subprocess
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PY = sys.executable


def run_book(row):
    book = row["book"]
    key = f"{book}__{row['old_label']}"
    done = ROOT / "results" / "perbook" / key / "book_summary.csv"
    if done.exists():
        return
    tmp_rel = f"results/_run/{key}"
    one = ROOT / "logs" / f"pair_{key}.csv"
    with open(one, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(row.keys()))
        w.writeheader()
        w.writerow(row)
    t0 = time.time()
    r = subprocess.run([PY, "-X", "utf8", "-I", str(ROOT / "code" / "run_diff.py"), str(one), "--out", tmp_rel],
                       capture_output=True, text=True)
    print(book, f"{time.time()-t0:.0f}s", (r.stdout or "").strip().splitlines()[-1:] or "", (r.stderr or "")[-300:], flush=True)
    tmp = ROOT / tmp_rel
    if r.returncode != 0 or not (tmp / "book_summary.csv").exists():
        print("  FAILED", book, flush=True)
        return
    (ROOT / "results" / "units").mkdir(parents=True, exist_ok=True)
    for f in (tmp / "units").glob("*.csv"):
        shutil.move(str(f), str(ROOT / "results" / "units" / f.name))
    pb = ROOT / "results" / "perbook" / key
    pb.mkdir(parents=True, exist_ok=True)
    for n in ("chapter_summary.csv", "extraction_meta.csv", "book_summary.csv"):
        shutil.move(str(tmp / n), str(pb / n))
    shutil.rmtree(tmp, ignore_errors=True)


def merge_results(pairs, outdir):
    keys = [f"{r['book']}__{r['old_label']}" for r in pairs]
    outdir.mkdir(parents=True, exist_ok=True)
    for n in ("chapter_summary.csv", "extraction_meta.csv", "book_summary.csv"):
        rows, fields = [], None
        for k in keys:
            p = ROOT / "results" / "perbook" / k / n
            if not p.exists():
                continue
            with open(p, newline="", encoding="utf-8-sig") as f:
                rd = csv.DictReader(f)
                fields = fields or rd.fieldnames
                rows.extend(rd)
        if rows:
            with open(outdir / n, "w", newline="", encoding="utf-8-sig") as f:
                w = csv.DictWriter(f, fieldnames=fields)
                w.writeheader()
                w.writerows(rows)


if __name__ == "__main__":
    pairs = list(csv.DictReader(open(sys.argv[1], newline="", encoding="utf-8")))
    only = set(sys.argv[2:])
    for row in pairs:
        if not only or row["book"] in only:
            run_book(row)
    # the primary pairs file merges into results/ ; any other pairs file (alternatives) into results/alt_<file stem>/
    merge_results(pairs, ROOT / "results" if Path(sys.argv[1]).name == "corpus_pairs.csv" else ROOT / "results" / ("alt_" + Path(sys.argv[1]).stem))
