"""Printed-page anchor for books where the pack's margin-number detector found nothing (new code).

printed_page(chapter file, pdf page) = cum_start[chapter] + delta + pdf_page - 1, where cum_start is the running
sum of PDF pages of the body chapter files in order, and delta is fixed by the book's own contents list: the
integers found in the prelims PDF are matched against cum_start + delta for every chapter, and the delta that
matches most chapter starts wins (at least 3 and 60% of chapters, else no anchor).
Usage as module: anchor(book_dir) -> (delta or None, votes, n_chapters)
"""
import re
from pathlib import Path
import pymupdf


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
