"""Corpus-wide tables and figures from the per-book results (new for the full-corpus run).

Reads  results/{book_summary,chapter_summary,extraction_meta,official_vs_measured,qa_flags}.csv, results/units/*,
       results/removed_words_by_{theme,form,period}.csv, retrieval-log.csv, ../02-availability.csv
Writes tables/*.csv and figures/*.png.   Every number is a sum of the per-book CSVs; no model, no sampling.
Headline totals use the 51 English-medium books.  The 5 Hindi-medium Class 12 books (lhhs1-3, lhps1-2)
are translations of English books already counted, so they are tabulated apart and never added in.
"""
import csv
import re
import sys
from collections import defaultdict
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

ROOT = Path(__file__).resolve().parent.parent
PACK = ROOT.parent
T = ROOT / "tables"; F = ROOT / "figures"
T.mkdir(exist_ok=True); F.mkdir(exist_ok=True)

SCI = {"Science", "Physics", "Chemistry", "Biology"}
SUBJ_FIX = {"History (Hindi medium)": "History", "Political Science (Hindi medium)": "Political Science"}
TITLE_FIX = {"kegy1": "India: Physical Environment", "kegy2": "Fundamentals of Physical Geography",
             "leec1": "Introductory Macroeconomics", "leec2": "Introductory Microeconomics"}


def rd(p):
    with open(p, newline="", encoding="utf-8-sig") as f:
        return list(csv.DictReader(f))


def wr(name, rows, fields=None):
    fields = fields or list(rows[0].keys())
    with open(T / name, "w", newline="", encoding="utf-8-sig") as f:
        w = csv.DictWriter(f, fieldnames=fields); w.writeheader(); w.writerows(rows)


def meta():
    m = {}
    for r in rd(PACK / "02-availability.csv"):
        b = r["ncert_file_code"]
        subj = r["subject"]
        hindi = "Hindi" in subj
        subj = SUBJ_FIX.get(subj, subj)
        group = "Science" if subj in SCI else "Social science"
        m[b] = {"class": int(r["class"]), "subject": subj, "group": group, "language": "Hindi" if hindi else "English",
                "title": TITLE_FIX.get(b, r["title"].replace(" (file-code order unverified)", ""))}
    return m


def captures():
    """chosen old / new capture per book from the retrieval log"""
    pairs = {r["book"]: r for r in rd(ROOT / "code/corpus_pairs.csv")}
    last = {}
    for r in rd(ROOT / "retrieval-log.csv"):
        if r["verdict"] in ("accepted", "needs_ocr", "fetched_alt"):
            last.setdefault((r["book"], r["role"]), []).append(r)
    out = {}
    for b, p in pairs.items():
        ol = p["old_label"]
        o = last.get((b, "old2122" if ol == "old2122" else ("old_alt" if ol == "old_alt" else "old")), [None])[-1]
        n = last.get((b, "rat2023"), [None])[-1]
        stamp = lambda r: (r["print_stamps"].split(" x")[0] if r else "")
        out[b] = {"old_label": ol, "old_capture": o["capture_ts"][:8] if o else "", "old_stamp": "2021-22" if ol == "old2122" else stamp(o), "new_capture": n["capture_ts"][:8] if n else "",
                  "new_stamp": stamp(n)}
    return out


def stamp_words(book, label):
    """words (3 per occurrence) of the stamp 'Rationalised-2023-24' that the pack's stamp filter does not remove"""
    n = 0
    p = ROOT / "results/units" / f"{book}__{label}__rat2023__new.csv"
    if p.exists():
        for r in rd(p):
            n += 3 * len(re.findall(r"rationalised[\s-]*2023[\s-]*24", r["text"].lower()))
    return n


def main():
    M, C = meta(), captures()
    bs = {r["book"]: r for r in rd(ROOT / "results/book_summary.csv")}
    ov = {r["book"]: r for r in rd(ROOT / "results/official_vs_measured.csv")}
    qa = {r["book"]: r for r in rd(ROOT / "results/qa_flags.csv")}
    rows = []
    for b, r in bs.items():
        m, c, o = M[b], C[b], ov.get(b, {})
        ow, nw, rem = int(r["old_words"]), int(r["new_words"]), int(r["removed_words"])
        sw = stamp_words(b, c["old_label"])
        added = max(0, int(r["added_words"]) - sw)
        sv = int(o.get("removed_in_surviving_chapters", 0) or 0)
        lst = int(o.get("on_pages_listed_2022", 0) or 0) + int(o.get("on_pages_listed_only_in_revised_booklet", 0) or 0)
        unl = int(o.get("on_unlisted_pages", 0) or 0)
        nop = int(o.get("no_page_number", 0) or 0)
        rows.append({"book": b, "class": m["class"], "subject": m["subject"], "group": m["group"], "language": m["language"], "title": m["title"],
                     "old_print_stamp": c["old_stamp"], "old_capture": c["old_capture"], "old_source": c["old_label"],
                     "new_print_stamp": c["new_stamp"], "new_capture": c["new_capture"],
                     "old_words": ow, "new_words": nw, "removed_words": rem, "share_removed": round(rem / ow, 4) if ow else 0,
                     "added_words_adj": added, "old_chapter_files": r["old_chapters"], "chapter_files_dropped": r["chapters_dropped"],
                     "removed_in_dropped_chapters": r["removed_words_in_dropped_chapters"], "removed_in_surviving_chapters": r["removed_words_in_surviving_chapters"],
                     "surv_listed_pages": lst, "surv_unlisted_pages": unl, "surv_page_not_testable": nop,
                     "official_full_chapter_entries": o.get("official_full_chapter_entries", ""),
                     "official_no_change": qa[b]["official_no_change"], "official_rows": qa[b]["official_rows"],
                     "qa_flags": qa[b]["flags"]})
    rows.sort(key=lambda x: (x["language"], x["class"], x["subject"], x["book"]))
    wr("table1_by_book.csv", rows)
    eng = [r for r in rows if r["language"] == "English"]

    def agg(keyf, rs, name):
        g = defaultdict(lambda: defaultdict(int))
        for r in rs:
            k = keyf(r)
            g[k]["books"] += 1
            for f in ("old_words", "new_words", "removed_words", "added_words_adj", "old_chapter_files", "chapter_files_dropped",
                      "removed_in_dropped_chapters", "removed_in_surviving_chapters", "surv_listed_pages", "surv_unlisted_pages", "surv_page_not_testable"):
                g[k][f] += int(r[f])
            g[k]["books_zero_removal"] += int(r["removed_words"] <= 0.002 * r["old_words"])
        out = []
        for k, v in sorted(g.items(), key=lambda kv: str(kv[0])):
            d = {"group": k if isinstance(k, str) else " | ".join(map(str, k))}
            d.update(v)
            d["share_removed"] = round(v["removed_words"] / v["old_words"], 4) if v["old_words"] else 0
            out.append(d)
        wr(name, out)
        return out

    by_class = agg(lambda r: f"Class {r['class']:02d}", eng, "table2_by_class.csv")
    agg(lambda r: r["subject"], eng, "table3_by_subject.csv")
    agg(lambda r: r["group"], eng, "table4_science_vs_social.csv")
    by_cg = agg(lambda r: (f"Class {r['class']:02d}", r["group"]), eng, "table5_by_class_and_group.csv")
    agg(lambda r: (r["group"], r["subject"]), eng, "table5b_by_group_and_subject.csv")
    tot = agg(lambda r: "All 51 English-medium books", eng, "table6_corpus_total.csv")
    agg(lambda r: r["old_print_stamp"], eng, "table7_by_baseline_print_year.csv")
    hin = [r for r in rows if r["language"] == "Hindi"]
    agg(lambda r: "Hindi-medium (reported apart, not added to totals)", hin, "table8_hindi_medium.csv")

    # listed vs unlisted: only books whose surviving-chapter removals could be placed on pages for >= 90% of words
    lu = []
    for scope, rs in (("all English", eng), ("Science", [r for r in eng if r["group"] == "Science"]), ("Social science", [r for r in eng if r["group"] == "Social science"])):
        ok = [r for r in rs if int(r["removed_in_surviving_chapters"]) > 0 and int(r["surv_page_not_testable"]) <= 0.1 * int(r["removed_in_surviving_chapters"])]
        s = lambda f, L: sum(int(r[f]) for r in L)
        lu.append({"scope": scope, "books": len(rs), "books_with_page_test": len(ok),
                   "removed_total": s("removed_words", rs), "removed_in_dropped_chapters": s("removed_in_dropped_chapters", rs),
                   "surviving_removed_in_testable_books": s("removed_in_surviving_chapters", ok),
                   "of_which_on_listed_pages": s("surv_listed_pages", ok), "of_which_on_unlisted_pages": s("surv_unlisted_pages", ok),
                   "share_unlisted_of_testable_surviving": round(s("surv_unlisted_pages", ok) / max(1, s("removed_in_surviving_chapters", ok)), 4),
                   "surviving_removed_in_untestable_books": s("removed_in_surviving_chapters", [r for r in rs if r not in ok])})
    wr("table9_listed_vs_unlisted.csv", lu)

    # chapters dropped
    ch = []
    for r in rd(ROOT / "results/chapter_summary.csv"):
        if r["chapter_dropped"] == "1" and r["front_or_back_matter"] != "1":
            m = M[r["book"]]
            ch.append({"book": r["book"], "class": m["class"], "subject": m["subject"], "group": m["group"], "language": m["language"],
                       "chapter_file": r["old_chapter_file"], "old_words": r["old_words"], "removed_words": r["removed_words"], "share_removed": r["share_removed"]})
    ch.sort(key=lambda x: (x["language"], x["class"], x["book"], x["chapter_file"]))
    wr("table10_chapter_files_dropped.csv", ch)

    # surviving chapters with the largest cuts
    big = []
    for r in rd(ROOT / "results/chapter_summary.csv"):
        if r["chapter_dropped"] == "0" and r["front_or_back_matter"] != "1" and M[r["book"]]["language"] == "English":
            big.append({"book": r["book"], "chapter_file": r["old_chapter_file"], "old_words": int(r["old_words"]), "removed_words": int(r["removed_words"]), "share_removed": float(r["share_removed"] or 0)})
    big.sort(key=lambda x: -x["removed_words"])
    wr("table11_largest_cuts_in_surviving_chapters.csv", big[:25])

    # themes / forms (codebook v0.2, keyword rules, unvalidated)
    for dim in ("theme", "form"):
        g = defaultdict(lambda: defaultdict(int))
        for r in rd(ROOT / f"results/removed_words_by_{dim}.csv"):
            if M[r["book"]]["language"] != "English":
                continue
            g[r[dim]][M[r["book"]]["group"]] += int(r["removed_words"])
        out = [{dim: k, "Science": v["Science"], "Social science": v["Social science"], "total": v["Science"] + v["Social science"]} for k, v in g.items()]
        out.sort(key=lambda x: -x["total"])
        wr(f"table12_{dim}_of_removed_passages.csv", out)

    # ---- figures
    col = {"Science": "#1b6ca8", "Social science": "#c15f1d"}
    fig, ax = plt.subplots(figsize=(8, 11))
    es = sorted(eng, key=lambda r: (r["class"], r["group"], -r["share_removed"]))
    ys = list(range(len(es)))[::-1]
    ax.barh(ys, [100 * r["share_removed"] for r in es], color=[col[r["group"]] for r in es])
    ax.set_yticks(ys); ax.set_yticklabels([f"{r['class']} {r['book']} {r['title'][:24]}" for r in es], fontsize=6)
    ax.set_xlabel("Share of old-edition words not found in the rationalised edition (%)")
    ax.set_title("Words removed, by book (51 English-medium books)")
    for g, c in col.items():
        ax.barh([], [], color=c, label=g)
    ax.legend(loc="lower right"); fig.tight_layout(); fig.savefig(F / "fig1_share_removed_by_book.png", dpi=150); plt.close(fig)

    fig, ax = plt.subplots(figsize=(8, 4.5))
    cls = sorted({r["class"] for r in eng})
    bot = [0] * len(cls)
    for g in ("Science", "Social science"):
        v = [sum(r["removed_words"] for r in eng if r["class"] == c and r["group"] == g) for c in cls]
        ax.bar([str(c) for c in cls], v, bottom=bot, color=col[g], label=g); bot = [a + b for a, b in zip(bot, v)]
    ax.set_xlabel("Class"); ax.set_ylabel("Words removed"); ax.set_title("Words removed by class"); ax.legend()
    fig.tight_layout(); fig.savefig(F / "fig2_words_removed_by_class.png", dpi=150); plt.close(fig)

    fig, ax = plt.subplots(figsize=(8, 4.5))
    labs, parts = [], defaultdict(list)
    for g in ("Science", "Social science"):
        rs = [r for r in eng if r["group"] == g]
        labs.append(g)
        t = sum(r["removed_words"] for r in rs) or 1
        parts["Whole chapter files dropped"].append(100 * sum(int(r["removed_in_dropped_chapters"]) for r in rs) / t)
        parts["Inside surviving chapters, on listed pages"].append(100 * sum(int(r["surv_listed_pages"]) for r in rs) / t)
        parts["Inside surviving chapters, on unlisted pages"].append(100 * sum(int(r["surv_unlisted_pages"]) for r in rs) / t)
        parts["Inside surviving chapters, page not testable"].append(100 * sum(int(r["surv_page_not_testable"]) for r in rs) / t)
    bot = [0, 0]
    for k, v in parts.items():
        ax.bar(labs, v, bottom=bot, label=k); bot = [a + b for a, b in zip(bot, v)]
    ax.set_ylabel("% of removed words"); ax.set_title("Where the removed words sit relative to NCERT's lists"); ax.legend(fontsize=7)
    fig.tight_layout(); fig.savefig(F / "fig3_listed_vs_unlisted.png", dpi=150); plt.close(fig)

    th = rd(T / "table12_theme_of_removed_passages.csv")
    fig, ax = plt.subplots(figsize=(8, 5))
    names = [r["theme"] for r in th][::-1]
    ax.barh(names, [int(r["Social science"]) for r in th][::-1], color=col["Social science"], label="Social science")
    ax.barh(names, [int(r["Science"]) for r in th][::-1], left=[int(r["Social science"]) for r in th][::-1], color=col["Science"], label="Science")
    ax.set_xlabel("Words removed (codebook v0.2 keyword rules; indicative)"); ax.legend(); ax.tick_params(axis="y", labelsize=7)
    fig.tight_layout(); fig.savefig(F / "fig4_removed_words_by_theme.png", dpi=150); plt.close(fig)

    fig, ax = plt.subplots(figsize=(7, 4))
    ax.hist([100 * float(r["share_removed"] or 0) for r in big], bins=20, color="#555")
    ax.set_xlabel("Share of a surviving chapter removed (%)"); ax.set_ylabel("Chapter files"); ax.set_title("Surviving chapters: distribution of share removed")
    fig.tight_layout(); fig.savefig(F / "fig5_surviving_chapter_cuts.png", dpi=150); plt.close(fig)
    print(open(T / "table6_corpus_total.csv", encoding="utf-8-sig").read())


if __name__ == "__main__":
    main()
