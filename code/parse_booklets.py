"""Parse NCERT "List of Rationalised Content" booklets (Classes 6-12) into one CSV.

The booklets are ruled three-column tables (Chapter | Page No. | Dropped Topics/Chapters)
under headings of the form "<book code> - <book title>".  We use the ruling lines
in the PDF to find row bands and column boundaries, then drop each word into its cell.

Usage:  python code/parse_booklets.py
Input : data/official/BookletClass<N>_*.pdf
Output: 02-official-listed-deletions.csv   (one row per table row, every booklet version)

This is a mechanical extraction.  Rows are not interpreted; `full_chapter`, `page_list`
are convenience fields derived by regular expressions and are documented in 02-official-record.md.
"""
import csv
import glob
import re
import sys
from pathlib import Path

import pymupdf

ROOT = Path(__file__).resolve().parent.parent
HEAD_RE = re.compile(r"^\s*(\d{3,5})\s*[–—\-:]?\s*([^\W\d].*)$")  # "<book code> - <title starting with a letter>"
DASH = r"\-–—"  # hyphen, en dash, em dash (hyphen first so it is literal inside [...])


def clusters(vals, tol=2.5):
    out = []
    for v in sorted(vals):
        if out and v - out[-1][-1] <= tol:
            out[-1].append(v)
        else:
            out.append([v])
    return [sum(c) / len(c) for c in out]


def page_geometry(page):
    """Return (column x-boundaries, horizontal segments [(y,x0,x1)], y-extent of table)."""
    hs, vs = [], []
    for d in page.get_drawings():
        for it in d["items"]:
            if it[0] == "l":
                a, b = it[1], it[2]
                if abs(a.y - b.y) < 1 and abs(a.x - b.x) > 20:
                    hs.append((a.y, min(a.x, b.x), max(a.x, b.x)))
                elif abs(a.x - b.x) < 1 and abs(a.y - b.y) > 8:
                    vs.append((a.x, min(a.y, b.y), max(a.y, b.y)))
            elif it[0] == "re":
                r = it[1]
                if r.width > 20 and r.height < 1.5:
                    hs.append((r.y0, r.x0, r.x1))
                elif r.height > 8 and r.width < 1.5:
                    vs.append((r.x0, r.y0, r.y1))
    H = page.rect.height
    hs = [h for h in hs if 30 < h[0] < H - 60]
    vs = [v for v in vs if 30 < v[1] and v[2] < H - 60]
    return hs, vs


def parse_pages(text):
    """'54-61' -> [54..61]; '9 11-14' -> [9,11,12,13,14]. Returns list of ints (may be empty)."""
    t = text.replace("−", "-")
    out = []
    for m in re.finditer(r"(\d{1,3})\s*(?:[%s]|to)\s*(\d{1,3})|(\d{1,3})" % DASH, t):
        if m.group(1):
            a, b = int(m.group(1)), int(m.group(2))
            if b < a:  # '128-47' style abbreviation
                s = str(a)[: len(str(a)) - len(str(b))] + str(b)
                b = int(s) if s.isdigit() and int(s) >= a else a
            if b - a <= 120:
                out.extend(range(a, b + 1))
        else:
            out.append(int(m.group(3)))
    return sorted(set(out))


def parse_booklet(path, klass, version):
    doc = pymupdf.open(path)
    rows = []
    book_code, book_title, chapter = "", "", ""
    seen_table = False  # front matter (cover, imprint, contents) has no ruled tables: skip it
    for pno, page in enumerate(doc, start=1):
        if page.rotation:
            page.remove_rotation()  # some pages of the revised booklets are stored rotated
        hs, vs = page_geometry(page)
        words = page.get_text("words")
        H = page.rect.height
        # drop the running head (page number) and the running foot ("List of Rationalised Content in ...")
        foot = [w[1] for w in words if w[4] == "Rationalised" and w[1] > H - 110]
        cut = (min(foot) - 4) if foot else H - 45
        words = [w for w in words if 40 < (w[1] + w[3]) / 2 < cut]
        # group vertical lines into tables (connected in y)
        tables = []
        if vs:
            xs = clusters([v[0] for v in vs])
            segs = sorted((v[1], v[2]) for v in vs)
            spans = []
            for a, b in segs:
                if spans and a <= spans[-1][1] + 3:
                    spans[-1][1] = max(spans[-1][1], b)
                else:
                    spans.append([a, b])
            for y0, y1 in spans:
                cx = clusters([v[0] for v in vs if v[1] >= y0 - 3 and v[2] <= y1 + 3])
                if len(cx) >= 3:
                    tables.append((y0, y1, cx))
        if tables:
            seen_table = True
            # A table that runs off the bottom of the page has no closing rule for its last row.
            # Extend the last table down to the lowest remaining word unless a book heading follows it.
            y0, y1, cx = tables[-1]
            below = [w for w in words if (w[1] + w[3]) / 2 > y1 + 1]
            if below:
                blines = {}
                for w in below:
                    blines.setdefault(round(w[1] / 3), []).append(w)
                has_head = any(HEAD_RE.match(" ".join(x[4] for x in sorted(v, key=lambda x: x[0])))
                               and min(x[0] for x in v) < cx[0] + 30 for v in blines.values())
                if not has_head:
                    tables[-1] = (y0, max(w[3] for w in below) + 1, cx)
        if not seen_table:
            continue
        items = []  # (y, kind, payload)
        used = set()
        for (y0, y1, cx) in tables:
            ncol = len(cx) - 1
            last0, last1 = cx[-2], cx[-1]
            ys = [h[0] for h in hs if y0 - 3 <= h[0] <= y1 + 3 and h[1] <= last0 + 5 and h[2] >= last1 - 5]
            bounds = clusters(ys + [y0, y1])
            chap_lines = clusters([h[0] for h in hs if y0 - 3 <= h[0] <= y1 + 3 and h[1] <= cx[0] + 5 and h[2] >= cx[1] - 5] + [y0])
            for i in range(len(bounds) - 1):
                b0, b1 = bounds[i], bounds[i + 1]
                cells = [[] for _ in range(ncol)]
                for wi, w in enumerate(words):
                    yc, xc = (w[1] + w[3]) / 2, (w[0] + w[2]) / 2
                    if b0 <= yc < b1 and cx[0] - 2 <= xc <= cx[-1] + 2:
                        for c in range(ncol):
                            if cx[c] - 2 <= xc < cx[c + 1] + (2 if c == ncol - 1 else 0):
                                cells[c].append(w)
                                used.add(wi)
                                break
                txt = []
                for c in cells:
                    c.sort(key=lambda w: (round(w[1] / 4), w[0]))
                    txt.append(" ".join(w[4] for w in c).strip())
                new_chap = any(abs(b0 - cl) < 3 for cl in chap_lines)
                items.append((b0, "row", (txt, new_chap)))
            # chapter text can be vertically centred across several fine rows: handled below
        # headings = lines of unused words
        lines = {}
        for wi, w in enumerate(words):
            if wi in used:
                continue
            lines.setdefault(round(w[1] / 3), []).append(w)
        for k in sorted(lines):
            ws = sorted(lines[k], key=lambda w: w[0])
            left = tables[0][2][0] if tables else 90
            # a book heading starts at the left margin; a stray page-number cell does not
            items.append((ws[0][1], "line" if ws[0][0] < left + 30 else "stray", " ".join(w[4] for w in ws)))
        items.sort(key=lambda t: t[0])
        # merge chapter text across merged cells: collect consecutive rows until new_chap
        i = 0
        while i < len(items):
            y, kind, payload = items[i]
            if kind in ("line", "stray"):
                m = HEAD_RE.match(payload) if kind == "line" else None
                if m and not re.fullmatch(r"[\d\s%s,]+" % DASH, payload):
                    book_code, book_title, chapter = m.group(1), m.group(2).strip(), ""
                elif re.search(r"no\s+change", payload, re.I):
                    rows.append([klass, version, pno, book_code, book_title, "", "", "NO CHANGE", 0, ""])
                elif book_title and len(payload) > 2 and not re.match(r"^(Chapter|Page No|Dropped)", payload) and rows and rows[-1][2] in (pno,) and False:
                    pass
                else:
                    # stray text outside a ruled table (table rows whose rules were not found): keep verbatim
                    if len(payload.strip()) > 1 and not re.match(r"^(List of Rationalised|CONTENTS|Subjects|Language Books)", payload):
                        rows.append([klass, version, pno, book_code, book_title, chapter, "", "UNRULED: " + payload, 0, ""])
                i += 1
                continue
            # a run of rows belonging to one merged chapter cell
            j = i
            chap_parts = []
            run = []
            while j < len(items) and items[j][1] == "row" and (j == i or not items[j][2][1]):
                txt = items[j][2][0]
                chap_parts.append(txt[0])
                run.append(txt)
                j += 1
            ctext = " ".join(p for p in chap_parts if p).strip()
            if re.match(r"^Chapter\b\s*$|^(Chapter|Chapters|Unit)\s*(Page|$)", ctext) or (run and re.match(r"^Page\s*No", run[0][1] if len(run[0]) > 1 else "")):
                i = j
                continue  # header row
            if ctext:
                chapter = ctext
            for txt in run:
                pages = txt[1] if len(txt) > 2 else ""
                topics = " | ".join(t for t in txt[2:] if t) if len(txt) > 2 else " | ".join(txt[1:])
                if not pages and not topics:
                    continue
                if re.match(r"^Dropped Topics", topics):
                    continue
                full = int(bool(re.search(r"full\s+chapter|whole\s+chapter|entire\s+chapter|complete\s+chapter", topics, re.I)))
                rows.append([klass, version, pno, book_code, book_title, chapter, pages, topics, full,
                             " ".join(map(str, parse_pages(pages)))])
            i = j
    return rows


def main():
    out = ROOT / "02-official-listed-deletions.csv"
    allrows = []
    for f in sorted(glob.glob(str(ROOT / "data" / "official" / "BookletClass*.pdf"))):
        m = re.search(r"BookletClass(\d+)_(\w+)\.pdf", f)
        try:
            doc = pymupdf.open(f)
            if sum(len(p.get_text()) for p in doc) < 5000:
                print("skip (truncated download / no text):", f, file=sys.stderr)
                continue
        except Exception as e:  # noqa
            print("skip (unreadable):", f, e, file=sys.stderr)
            continue
        r = parse_booklet(f, int(m.group(1)), m.group(2))
        print(Path(f).name, len(r), "rows")
        allrows.extend(r)
    with open(out, "w", newline="", encoding="utf-8-sig") as fh:
        w = csv.writer(fh)
        w.writerow(["class", "booklet_version", "booklet_pdf_page", "book_code", "book_title", "chapter",
                    "pages_raw", "dropped_raw", "full_chapter", "page_list"])
        w.writerows(allrows)
    print("wrote", out, len(allrows))


if __name__ == "__main__":
    main()
