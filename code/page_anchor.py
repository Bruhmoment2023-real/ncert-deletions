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


def body_files(folder: Path):
    return sorted(p for p in folder.glob("*.pdf") if not re.search(r"(ps|an|gl|ap|a\d|in|sm|cc)$", p.stem))


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
