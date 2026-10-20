"""Run the edition diff for the books in a pairs file and write result tables.

Usage:
    python code/run_diff.py code/pilot_pairs.csv

pairs file columns: book,official_code,title,old_label,new_label
Reads   data/books/<label>/<book>/*.pdf
Writes  results/units/<book>__<old>__<new>__old.csv   one row per old-edition sentence unit (with labels)
        results/units/<book>__<old>__<new>__new.csv   one row per new-edition sentence unit (added text)
        results/chapter_summary.csv                    one row per old chapter per comparison
        results/book_summary.csv
        results/extraction_meta.csv                    pages, words, print-year stamps, low-text pages per PDF
The units CSVs contain textbook sentences: they are working files and must NOT be published
(see 03-design.md).  Only the summary tables, counts and short quotations may be released.
"""
import csv
import sys
from collections import defaultdict
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import ncertdiff as nd  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent


def write_units(path, units):
    with open(path, "w", newline="", encoding="utf-8-sig") as f:
        w = csv.writer(f)
        w.writerow(["chapter", "pdf_page", "printed_page", "block", "font_size", "n_words",
                    "retained_same_chapter", "retained_book", "label", "font", "note", "text"])
        for u in units:
            w.writerow([u.chapter, u.pdf_page, u.printed_page if u.printed_page is not None else "", u.block,
                        u.size, len(u.toks), u.retained_same, u.retained_book, u.label, u.font, u.note, u.text])


K = nd.K
FUZZY = True
OUT = "results"


def main(pairs_file):
    (ROOT / OUT / "units").mkdir(parents=True, exist_ok=True)
    chap_rows, book_rows, meta_rows = [], [], []
    for row in csv.DictReader(open(pairs_file, newline="", encoding="utf-8")):
        book, old_l, new_l = row["book"], row["old_label"], row["new_label"]
        old_u, old_m = nd.extract_book(ROOT / "data" / "books" / old_l / book)
        new_u, new_m = nd.extract_book(ROOT / "data" / "books" / new_l / book)
        for lab, ms in ((old_l, old_m), (new_l, new_m)):
            for m in ms:
                if not any(r["book"] == book and r["edition"] == lab and r["chapter"] == m["chapter"] for r in meta_rows):
                    meta_rows.append({"book": book, "edition": lab, **m})
        # body chapters only for the headline numbers; front/back matter is reported separately
        align, detail, ralign = nd.diff_books(old_u, new_u, k=K, fuzzy=FUZZY)
        tag = f"{book}__{old_l}__{new_l}"
        write_units(ROOT / OUT / "units" / f"{tag}__old.csv", old_u)
        write_units(ROOT / OUT / "units" / f"{tag}__new.csv", new_u)
        per = defaultdict(lambda: defaultdict(int))
        for u in old_u:
            p = per[u.chapter]
            n = len(u.toks)
            p["old_words"] += n
            p["removed_words"] += n - u.retained_book          # threshold-free headline measure
            p["moved_words"] += u.retained_book - min(u.retained_book, u.retained_same)
            p[f"units_{u.label}"] += 1
            p[f"words_in_{u.label}_units"] += n
        added = defaultdict(int)
        new_words = defaultdict(int)
        for u in new_u:
            added[u.chapter] += len(u.toks) - u.retained_book
            new_words[u.chapter] += len(u.toks)
        tot = defaultdict(int)
        for ch in sorted(per):
            p = per[ch]
            tgt = align[ch]
            fm = nd.is_front_matter(ch)
            r = {"book": book, "title": row["title"], "old_edition": old_l, "new_edition": new_l,
                 "old_chapter_file": ch, "front_or_back_matter": int(fm),
                 "aligned_new_chapter_file": tgt or "", "best_candidate": detail[ch][0] or "",
                 "share_retained_in_best_candidate": detail[ch][1],
                 "chapter_dropped": int(tgt is None),
                 "old_words": p["old_words"], "removed_words": p["removed_words"],
                 "share_removed": round(p["removed_words"] / p["old_words"], 4) if p["old_words"] else "",
                 "moved_words": p["moved_words"],
                 "new_words_in_aligned": new_words.get(tgt, 0) if tgt else 0,
                 "added_words_in_aligned": added.get(tgt, 0) if tgt else 0,
                 "units_kept": p["units_kept"], "units_reworded": p["units_reworded"],
                 "units_moved": p["units_moved"], "units_deleted": p["units_deleted"]}
            chap_rows.append(r)
            if not fm:
                for k in ("old_words", "removed_words", "moved_words"):
                    tot[k] += p[k]
                tot["chapters"] += 1
                tot["chapters_dropped"] += int(tgt is None)
                tot["removed_in_dropped_chapters"] += p["removed_words"] if tgt is None else 0
        body_new = [c for c in new_words if not nd.is_front_matter(c)]
        book_rows.append({"book": book, "title": row["title"], "old_edition": old_l, "new_edition": new_l,
                          "old_chapters": tot["chapters"], "new_chapters": len(body_new),
                          "chapters_dropped": tot["chapters_dropped"],
                          "old_words": tot["old_words"], "new_words": sum(new_words[c] for c in body_new),
                          "removed_words": tot["removed_words"],
                          "share_removed": round(tot["removed_words"] / tot["old_words"], 4),
                          "removed_words_in_dropped_chapters": tot["removed_in_dropped_chapters"],
                          "removed_words_in_surviving_chapters": tot["removed_words"] - tot["removed_in_dropped_chapters"],
                          "added_words": sum(added[c] for c in body_new),
                          "moved_words": tot["moved_words"]})
        print(tag, book_rows[-1]["old_words"], "->", book_rows[-1]["new_words"],
              "removed", book_rows[-1]["removed_words"], "added", book_rows[-1]["added_words"], flush=True)
    for name, rows in (("chapter_summary.csv", chap_rows), ("book_summary.csv", book_rows), ("extraction_meta.csv", meta_rows)):
        with open(ROOT / OUT / name, "w", newline="", encoding="utf-8-sig") as f:
            w = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
            w.writeheader()
            w.writerows(rows)


if __name__ == "__main__":
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("pairs")
    ap.add_argument("--k", type=int, default=nd.K, help="K-gram length (sensitivity check)")
    ap.add_argument("--no-fuzzy", action="store_true", help="skip the fuzzy second pass")
    ap.add_argument("--out", default="results", help="output folder under the project root")
    a = ap.parse_args()
    K, FUZZY, OUT = a.k, not a.no_fuzzy, a.out
    main(a.pairs)
