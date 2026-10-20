"""Compare measured removals with NCERT's published "List of Rationalised Content".

Usage: python code/compare_official.py code/pilot_pairs.csv

For every old-edition sentence unit we know the printed page number it sat on.  NCERT's
booklet lists page numbers per book.  A removed word is

  listed_2022   - its page is in the booklet as first published (Wayback capture, June 2022)
  listed_later  - its page is absent from the 2022 booklet but present in the booklet
                  now on ncert.nic.in (Class 9/10 revised Jan 2023, Class 12 revised Aug 2023)
  unlisted      - its page is in neither version

This is a page-level test: it is generous to the official list (anything removed on a listed
page counts as listed, even if the list names a different passage on that page).
Output: results/official_vs_measured.csv, results/unlisted_units_WORKING.csv (not for release)
"""
import csv
import sys
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(Path(__file__).resolve().parent))
import ncertdiff as nd  # noqa: E402

V_FIRST, V_NOW = "wayback202206", "live20261013"


def load_official():
    pages = defaultdict(lambda: defaultdict(set))
    with open(ROOT / "02-official-listed-deletions.csv", encoding="utf-8-sig", newline="") as f:
        for r in csv.DictReader(f):
            if r["dropped_raw"].startswith("UNRULED") or r["dropped_raw"] == "NO CHANGE":
                continue
            pages[r["book_code"]][r["booklet_version"]].update(int(x) for x in r["page_list"].split())
    return pages


def main(pairs_file):
    off = load_official()
    out, unlisted = [], []
    for row in csv.DictReader(open(pairs_file, newline="", encoding="utf-8")):
        if row["new_label"] != "rat2023":
            continue
        book, code = row["book"], row["official_code"]
        first, now = off[code].get(V_FIRST, set()), off[code].get(V_NOW, set())
        tag = f"{book}__{row['old_label']}__{row['new_label']}"
        agg = defaultdict(int)
        with open(ROOT / "results" / "units" / f"{tag}__old.csv", encoding="utf-8-sig", newline="") as f:
            for u in csv.DictReader(f):
                if nd.is_front_matter(u["chapter"]):
                    continue
                n, kept = int(u["n_words"]), int(u["retained_book"])
                rem = n - kept
                if rem == 0:
                    continue
                pp = int(u["printed_page"]) if u["printed_page"] else None
                # adjacent-page tolerance: a passage listed as "p.41" may run on to the next page
                if pp is None:
                    cls = "no_page_number"
                elif pp in first:
                    cls = "listed_2022"
                elif pp in now:
                    cls = "listed_later"
                else:
                    cls = "unlisted"
                agg[cls] += rem
                agg["total"] += rem
                if cls in ("unlisted", "listed_later", "no_page_number") and u["label"] in ("deleted", "reworded"):
                    unlisted.append([book, cls, u["chapter"], u["printed_page"], u["label"], n, rem, u["text"]])
        out.append({"book": book, "official_code": code, "title": row["title"],
                    "removed_words_total": agg["total"], "on_pages_listed_2022": agg["listed_2022"],
                    "on_pages_listed_only_in_revised_booklet": agg["listed_later"],
                    "on_unlisted_pages": agg["unlisted"], "no_page_number": agg["no_page_number"],
                    "share_unlisted_vs_2022_list": round((agg["listed_later"] + agg["unlisted"]) / agg["total"], 4) if agg["total"] else 0})
        print(out[-1])
    with open(ROOT / "results" / "official_vs_measured.csv", "w", newline="", encoding="utf-8-sig") as f:
        w = csv.DictWriter(f, fieldnames=list(out[0].keys()))
        w.writeheader()
        w.writerows(out)
    with open(ROOT / "results" / "unlisted_units_WORKING.csv", "w", newline="", encoding="utf-8-sig") as f:
        w = csv.writer(f)
        w.writerow(["book", "list_status", "chapter", "printed_page", "label", "n_words", "removed_words", "text"])
        w.writerows(unlisted)


if __name__ == "__main__":
    main(sys.argv[1])
