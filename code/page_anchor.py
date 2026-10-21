"""Printed-page anchor for books where the pack's margin-number detector found nothing (new code).

printed_page(chapter file, pdf page) = cum_start[chapter] + delta + pdf_page - 1, where cum_start is the running
sum of PDF pages of the body chapter files in order, and delta is fixed by the book's own contents list: the
integers found in the prelims PDF are matched against cum_start + delta for every chapter, and the delta that
matches most chapter starts wins (at least 3 and 60% of chapters, else no anchor).
Usage as module: anchor(book_dir) -> (delta or None, votes, n_chapters, {chapter: running start}); folio_offset(pdf).
As a script: python -I code/page_anchor.py code/corpus_pairs.csv  -> results/folio_offsets.csv (folio offsets per chapter).
"""
import re
import sys
from pathlib import Path
import pymupdf
sys.path.insert(0, str(Path(__file__).resolve().parent))   # for ncertdiff when run as a script with -I
from collections import Counter


CHAPTER_RE = re.compile(r"^[a-z]{4}\d(\d{2,3})$")   # NCERT: <4-letter subject code><volume digit><chapter>, e.g. fess103


def chapter_order(stem: str):
    """Sort key: numeric chapter order. NCERT names chapter files <book><2-digit chapter> (fess101 .. fess109), but some
    file sets use three digits past 9 (fess1010, fess1011), so plain string sorting put chapters 10-11 before 2.
    Files whose names do not follow the scheme (e.g. 'World Map _ SDGs', fess3rf) go after the numbered chapters."""
    m = CHAPTER_RE.match(stem.lower())
    return (0, int(m.group(1)), stem) if m else (1, 0, stem)


def body_files(folder: Path):
    files = [p for p in folder.glob("*.pdf") if not re.search(r"(ps|an|gl|ap|a\d|in|sm|cc)$", p.stem)]
    return sorted(files, key=lambda p: chapter_order(p.stem))


def anchor(folder: Path):
    folder = Path(folder)
    files = body_files(folder)
    pages = [len(pymupdf.open(str(p))) for p in files]
    cum, c = [], 1
    for n in pages:
        cum.append(c); c += n
    ps = list(folder.glob("*ps.pdf"))
    nums = set()
    if ps:
        d = pymupdf.open(str(ps[0]))
        for page in list(d)[:12]:
            for ln in page.get_text("text").splitlines():
                for m in re.finditer(r"(?<![\d.])(\d{1,3})\s*$", ln.strip()):
                    nums.add(int(m.group(1)))
    best = (None, 0)
    for k in range(len(cum)):
        for v in nums:
            delta = v - cum[k]
            votes = sum(1 for cc in cum if (cc + delta) in nums)
            if votes > best[1] or (votes == best[1] and best[0] is not None and abs(delta) < abs(best[0])):
                best = (delta, votes)
    if best[0] is not None and best[1] >= max(3, 0.6 * len(cum)):
        return best[0], best[1], len(cum), dict(zip([p.stem for p in files], cum))
    return None, best[1], len(cum), dict(zip([p.stem for p in files], cum))


# ---- printed page numbers (folios) read from the page text, used to check and replace the contents-page anchor ----
# A folio is a number of 1-3 digits standing alone, or at the start or end of a short running head ("8 Resources and
# Development", "Land, Soil, Water ... Resources 9"), in a block in the top 20% or bottom 25% of the page.  The pack's
# detector looks only in the outer 14% / 7% margins, which misses these books' folios.
FOLIO_RES = (re.compile(r"^\W*(\d{1,3})\W*$"),
             re.compile(r"^(\d{1,3})\s+[^\d\s].{0,90}$"),
             re.compile(r"^.{0,90}[^\d\s.,:\-–]\s+(?<![\d\-–])(\d{1,3})\W*$"))


def page_folio(page):
    import ncertdiff as nd
    h = page.rect.height
    found = set()
    for bbox, size, txt, font in nd._page_blocks(page):
        if not (bbox[1] > 0.75 * h or bbox[3] < 0.2 * h):
            continue
        f = match_folio(nd.clean(txt))
        if f is not None:
            found.add(f)
    return found.pop() if len(found) == 1 else None


def match_folio(c):
    if len(c) > 100:
        return None
    for rx in FOLIO_RES:
        m = rx.match(c)
        if m:
            return int(m.group(1))
    return None


def folio_offset(pdf_path):
    """printed page = pdf page index (1-based) + offset, where offset is the most common (folio - index) over the file's
    pages; None unless it holds on at least 2 pages and half of the pages.  Returns (offset or None, pages agreeing, pages)."""
    doc = pymupdf.open(str(pdf_path))
    n = len(doc)
    c = Counter()
    for i, page in enumerate(doc, start=1):
        f = page_folio(page)
        if f is not None:
            c[f - i] += 1
    if c:
        off, k = c.most_common(1)[0]
        if k >= max(2, 0.5 * n):
            return off, k, n
    return None, (c.most_common(1)[0][1] if c else 0), n


def write_folio_offsets(pairs_file, out=None):
    """For every old-edition body chapter whose pages the pack's detector did not number (extraction_meta page_offset
    empty), in books where the contents anchor exists, record folio_offset(); writes results/folio_offsets.csv."""
    import csv
    root = Path(__file__).resolve().parent.parent
    meta = {(r["book"], r["edition"], r["chapter"]): r["page_offset"]
            for r in csv.DictReader(open(root / "results/extraction_meta.csv", encoding="utf-8-sig"))}
    rows = []
    for pr in csv.DictReader(open(pairs_file, encoding="utf-8", newline="")):
        folder = root / "data/books" / pr["old_label"] / pr["book"]
        delta, _, _, cum = anchor(folder)
        if delta is None:
            continue
        for p in body_files(folder):
            if meta.get((pr["book"], pr["old_label"], p.stem), "") != "":
                continue
            off, k, n = folio_offset(p)
            rows.append({"book": pr["book"], "edition": pr["old_label"], "chapter": p.stem, "folio_offset": "" if off is None else off,
                         "pages_agreeing": k, "pages": n, "contents_anchor_offset": delta + cum[p.stem] - 1})
            print(rows[-1], flush=True)
    with open(out or root / "results/folio_offsets.csv", "w", newline="", encoding="utf-8-sig") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0])); w.writeheader(); w.writerows(rows)


if __name__ == "__main__":
    import sys
    write_folio_offsets(sys.argv[1])
