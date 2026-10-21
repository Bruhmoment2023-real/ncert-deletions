"""Page-level comparison with NCERT's lists (full-corpus version; the pack's compare_official.py logic plus three additions).

Same test as the pack's: a removed word is listed_2022 / listed_later / unlisted by the printed page it sat on.
Additions (all flagged in the output):
  1. Class 11: the Wayback copy of the Class 11 booklet is truncated, so the live booklet (internal date June 2022) is
     used as the first-published list.  listed_later is then not measurable for Class 11 (reported as listed_2022).
  2. Printed page numbers missing from the pack's detector are filled from page_anchor.anchor() (contents-list anchor),
     only where the anchor is trustworthy (see page_anchor.py and ANCHOR_RULE below).  Units still without a page are
     reported as no_page_number, not as unlisted.
     2b (21 Oct 2026). Before the anchor, a chapter's folio offset read from the page text (results/folio_offsets.csv,
     written by `page_anchor.py code/corpus_pairs.csv`) is used when it exists (page_source "folio"); the contents
     anchor is used only for chapters without one.  Both are used only in books where the anchor rule below holds, so
     the set of books with placeable pages is unchanged.  The anchor had put fess1 chapters 1-3, all of hess4 and lesy1
     (-1) and all of keec1 (+2) on the wrong pages.
  3. The count of NCERT "Full Chapter" entries is reported next to the number of chapter files measured as dropped.
Usage: python -I code/compare_official2.py code/corpus_pairs.csv
Output: results/official_vs_measured.csv, results/unlisted_units_WORKING.csv (textbook text: not for release)
ANCHOR_RULE: anchor used when it exists and (fewer than 2 chapters have a detected offset, or it agrees with >= 80% of them).
"""
import csv, re, sys
from collections import defaultdict
from pathlib import Path
ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(Path(__file__).resolve().parent))
import ncertdiff as nd
import page_anchor as pa

def load_official():
    pages = defaultdict(lambda: defaultdict(set)); full = defaultdict(lambda: defaultdict(set))
    cls = {}
    for r in csv.DictReader(open(ROOT / "02-official-listed-deletions.csv", encoding="utf-8-sig", newline="")):
        if r["dropped_raw"].startswith("UNRULED") or r["dropped_raw"] == "NO CHANGE":
            continue
        pages[r["book_code"]][r["booklet_version"]].update(int(x) for x in r["page_list"].split())
        cls[r["book_code"]] = r["class"]
        if r["full_chapter"] == "1":
            full[r["book_code"]][r["booklet_version"]].add(r["chapter"])
    return pages, full, cls

def load_folios():
    p = ROOT / "results/folio_offsets.csv"
    if not p.exists():
        return {}
    return {(r["book"], r["edition"], r["chapter"]): int(r["folio_offset"])
            for r in csv.DictReader(open(p, encoding="utf-8-sig")) if r["folio_offset"] != ""}


def main(pairs_file):
    off, full, cls = load_official()
    folio = load_folios()
    meta = {}
    for r in csv.DictReader(open(ROOT / "results/extraction_meta.csv", encoding="utf-8-sig")):
        if r["edition"] != "rat2023" and r["page_offset"] != "":
            meta[(r["book"], r["chapter"])] = int(r["page_offset"]) + 1
    chap = {(r["book"], r["old_chapter_file"]): r for r in csv.DictReader(open(ROOT / "results/chapter_summary.csv", encoding="utf-8-sig"))}
    out, unlisted = [], []
    for row in csv.DictReader(open(pairs_file, newline="", encoding="utf-8")):
        book, code = row["book"], row["official_code"]
        first = off[code].get("wayback202206", set()); now = off[code].get("live20261013", set())
        is11 = row["old_label"] and code.startswith("11")
        if is11 and not first:
            first, now = now, set()
        delta, votes, nch, cum = pa.anchor(ROOT / "data/books" / row["old_label"] / book)
        det = [(c, s) for c, s in cum.items() if (book, c) in meta]
        agree = sum(1 for c, s in det if delta is not None and meta[(book, c)] == s + delta)
        anchor_ok = delta is not None and (len(det) < 2 or agree >= 0.8 * len(det))
        tag = f"{book}__{row['old_label']}__{row['new_label']}"
        agg = defaultdict(int)
        dropped_set = {c for (b, c), r in chap.items() if b == book and r["chapter_dropped"] == "1" and r["front_or_back_matter"] != "1"}
        with open(ROOT / "results/units" / f"{tag}__old.csv", encoding="utf-8-sig", newline="") as f:
            for u in csv.DictReader(f):
                if nd.is_front_matter(u["chapter"]):
                    continue
                n, kept = int(u["n_words"]), int(u["retained_book"]); rem = n - kept
                if rem == 0:
                    continue
                if u["chapter"] in dropped_set:     # whole chapter gone: counted apart from the page-level test
                    agg["dropped_chapter"] += rem; agg["total"] += rem
                    continue
                pp = int(u["printed_page"]) if u["printed_page"] else None
                src = "detected"
                fo = folio.get((book, row["old_label"], u["chapter"]))
                if pp is None and anchor_ok and fo is not None:
                    pp = int(u["pdf_page"]) + fo; src = "folio"
                elif pp is None and anchor_ok and u["chapter"] in cum:
                    pp = cum[u["chapter"]] + delta + int(u["pdf_page"]) - 1; src = "anchored"
                if pp is None:
                    c = "no_page_number"
                elif pp in first: c = "listed_2022"
                elif pp in now: c = "listed_later"
                else: c = "unlisted"
                agg[c] += rem; agg["total"] += rem
                if c != "no_page_number": agg["src_" + src] += rem
                if c in ("unlisted", "listed_later") and u["label"] in ("deleted", "reworded"):
                    unlisted.append([book, c, u["chapter"], pp, src, u["label"], n, rem, u["text"]])
        fc = full[code].get("wayback202206") or full[code].get("live20261013") or set()
        dropped = sum(1 for (b, _), r in chap.items() if b == book and r["chapter_dropped"] == "1" and not r["front_or_back_matter"] == "1")
        out.append({"book": book, "official_code": code, "removed_words_total": agg["total"], "removed_in_dropped_chapters": agg["dropped_chapter"],
                    "removed_in_surviving_chapters": agg["total"] - agg["dropped_chapter"],
                    "on_pages_listed_2022": agg["listed_2022"], "on_pages_listed_only_in_revised_booklet": agg["listed_later"],
                    "on_unlisted_pages": agg["unlisted"], "no_page_number": agg["no_page_number"],
                    "words_page_from_detector": agg["src_detected"], "words_page_from_folio": agg["src_folio"],
                    "words_page_from_anchor": agg["src_anchored"],
                    "anchor_used": int(anchor_ok), "anchor_votes": f"{votes}/{nch}",
                    "official_full_chapter_entries": len(fc), "measured_chapter_files_dropped": dropped,
                    "class11_live_used_as_first": int(bool(is11))})
    with open(ROOT / "results/official_vs_measured.csv", "w", newline="", encoding="utf-8-sig") as f:
        w = csv.DictWriter(f, fieldnames=list(out[0])); w.writeheader(); w.writerows(out)
    with open(ROOT / "results/unlisted_units_WORKING.csv", "w", newline="", encoding="utf-8-sig") as f:
        w = csv.writer(f); w.writerow(["book", "list_status", "chapter", "printed_page", "page_source", "label", "n_words", "removed_words", "text"]); w.writerows(unlisted)
    for o in out:
        t = o["removed_in_surviving_chapters"] or 1
        print(o["book"], o["removed_words_total"], "surviving", o["removed_in_surviving_chapters"], "listed %.0f%%" % (100 * (o["on_pages_listed_2022"] + o["on_pages_listed_only_in_revised_booklet"]) / t),
              "unlisted %.0f%%" % (100 * o["on_unlisted_pages"] / t), "nopage %.0f%%" % (100 * o["no_page_number"] / t), "anchor", o["anchor_used"],
              "fullchap", o["official_full_chapter_entries"], "droppedfiles", o["measured_chapter_files_dropped"])
if __name__ == "__main__":
    main(sys.argv[1])
