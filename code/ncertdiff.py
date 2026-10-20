"""ncertdiff - measure what text changed between two editions of an NCERT textbook.

Core idea (reflow-tolerant, order-insensitive, threshold-free at the word level)
-------------------------------------------------------------------------------
1. Extract text blocks from each chapter PDF (PyMuPDF), drop running heads, page
   numbers and print-year stamps, split blocks into sentence units.
2. Normalise to lower-case word tokens.
3. A word of edition A is RETAINED in edition B if it lies inside at least one run
   of K consecutive words (a "K-gram", K=5 by default) that also occurs somewhere in B.
   Otherwise it is REMOVED.  Running B against A the same way gives ADDED words.
   Because K-grams are looked up in a set, the measure does not care about page
   breaks, column order, re-typesetting or paragraphs that moved.
4. Sentence units are then labelled from the share of their words retained:
   kept / reworded / deleted (and "moved" when the words survive, but only in a
   different chapter of the new edition).  Labels are descriptive conveniences;
   the headline numbers are the word counts of step 3.
5. A second, fuzzy pass (`rescue`) repairs false removals caused by damaged PDF
   text layers (decorative fonts whose ligatures have no Unicode mapping).

Nothing here judges why text changed.
"""
from __future__ import annotations

import re
import unicodedata
from collections import Counter, defaultdict
from dataclasses import dataclass, field
from pathlib import Path

K = 5                     # K-gram length for the retained/removed test
KEPT_T = 0.90             # unit is "kept" if >= 90% of its words are retained in the aligned chapter
DEL_T = 0.50              # unit is "deleted" if < 50% of its words are retained anywhere in the new book
CHAPTER_ALIGN_MIN = 0.30  # old chapter is "dropped" if no new chapter retains >= 30% of its words
FUZZY_SAME = 88           # letters-only similarity at/above which two units count as the same sentence
FUZZY_PAIR = 60           # ... at/above which they count as a reworded pair

STAMP_RE = re.compile(r"^\s*(rationalised\s*)?(reprint\s*)?20\d\d\s*[-–]\s*\d\d(\d\d)?\s*$", re.I)
LIG = {"ﬁ": "fi", "ﬂ": "fl", "ﬀ": "ff", "ﬃ": "ffi", "ﬄ": "ffl", "’": "'", "‘": "'",
       "“": '"', "”": '"', "–": "-", "—": "-", "­": ""}
TOKEN_RE = re.compile(r"[a-z0-9ऀ-ॿ]+(?:'[a-z]+)?")
SENT_RE = re.compile(r"(?<=[.!?])[\"')\]]*\s+(?=[\"'(\[]*[A-Z0-9ऀ-ॿ])")
# "Fake bold" is sometimes typeset by printing the same words 3-5 times on top of each other; the
# text layer then reads "Countries Countries Countries Countries Countries".  Collapse such runs.
DUP_RE = re.compile(r"(?<!\S)(\S+(?: \S+){0,5}?)(?: \1){2,}(?!\S)")


def clean(text: str) -> str:
    text = unicodedata.normalize("NFKC", text)
    for a, b in LIG.items():
        text = text.replace(a, b)
    text = re.sub(r"(\w)-\s*\n\s*(\w)", r"\1\2", text)      # de-hyphenate line breaks
    text = re.sub(r"\s+", " ", text)
    text = DUP_RE.sub(r"\1", text)
    return text.strip()


def norm_for_tokens(text: str) -> str:
    """Lower-case and join hyphenated compounds, so "sub-regions" == "subregions" and a word
    hyphenated at a line end in one printing equals the unbroken word in another."""
    return re.sub(r"(?<=[a-z0-9])-(?=[a-z0-9])", "", clean(text).lower())


def tokens(text: str) -> list[str]:
    return TOKEN_RE.findall(norm_for_tokens(text))


def split_sentences(text: str) -> list[str]:
    return [s.strip() for s in SENT_RE.split(text) if s.strip()]


@dataclass
class Unit:
    chapter: str          # chapter file stem, e.g. "leps201"
    pdf_page: int         # 1-based page within the chapter PDF
    printed_page: int | None
    block: int
    size: float           # largest font size in the block
    text: str
    toks: list[str] = field(default_factory=list)
    retained_same: int = 0   # words retained in the aligned chapter
    retained_book: int = 0   # words retained anywhere in the other edition
    label: str = ""
    font: str = ""           # dominant font of the block (lets you separate body text, boxes, captions)
    note: str = ""           # "fuzzy:NN" / "fuzzy_pair:NN" when the second pass changed the label


def _page_blocks(page):
    import pymupdf

    # text only: with the default flags PyMuPDF also decodes every image on the page (very slow)
    flags = pymupdf.TEXT_PRESERVE_LIGATURES | pymupdf.TEXT_PRESERVE_WHITESPACE | pymupdf.TEXT_MEDIABOX_CLIP
    out = []
    for b in page.get_text("dict", flags=flags)["blocks"]:
        if b.get("type") != 0:
            continue
        lines, size, fonts = [], 0.0, Counter()
        for ln in b["lines"]:
            t = "".join(s["text"] for s in ln["spans"])
            if t.strip():
                lines.append(t)
                for s in ln["spans"]:
                    if s["text"].strip():
                        size = max(size, s["size"])
                        fonts[s["font"]] += len(s["text"])
        if lines:
            out.append((b["bbox"], size, "\n".join(lines), fonts.most_common(1)[0][0]))
    return out


def _in_margin(bbox, h) -> bool:
    return bbox[1] < 0.14 * h or bbox[3] > 0.93 * h


def _boiler_key(c: str) -> str:
    """Running heads ignore digits (page numbers) and doubled printing ("X 50 X 50")."""
    key = re.sub(r"[\d\s]+", " ", c.lower()).strip()
    half = len(key) // 2
    if half > 6 and key[:half].strip() == key[half:].strip():
        key = key[:half].strip()
    return key


def extract_chapter(pdf_path: str | Path) -> tuple[list[Unit], dict]:
    """Return sentence units for one chapter PDF plus extraction metadata."""
    import pymupdf

    doc = pymupdf.open(str(pdf_path))
    stem = Path(pdf_path).stem
    pages = [(_page_blocks(p), p.rect.height) for p in doc]
    n = len(pages)
    # --- boilerplate: text that repeats (ignoring digits) in the margins of many pages
    rep = Counter()
    cand = Counter()      # printed page number minus pdf index
    for i, (blocks, h) in enumerate(pages, start=1):
        seen, nums = set(), set()
        for bbox, size, txt, font in blocks:
            c = clean(txt)
            if _in_margin(bbox, h) or len(c) < 90:
                key = _boiler_key(c)
                if key not in seen:
                    seen.add(key)
                    rep[key] += 1
            if _in_margin(bbox, h):
                for m in re.finditer(r"(?<![\d-])(\d{1,3})(?![\d-])", c):
                    nums.add(int(m.group(1)))
        for v in nums:
            cand[v - i] += 1
    boiler = {k for k, c in rep.items() if k and c >= max(3, 0.25 * n)}
    offset = cand.most_common(1)[0][0] if cand and cand.most_common(1)[0][1] >= max(2, 0.3 * n) else None
    stamps = Counter()
    units: list[Unit] = []
    low_text_pages = []
    for i, (blocks, h) in enumerate(pages, start=1):
        words_on_page = 0
        for bi, (bbox, size, txt, font) in enumerate(blocks):
            c = clean(txt)
            if STAMP_RE.match(c):
                stamps[c] += 1
                continue
            if (_in_margin(bbox, h) or len(c) < 90) and _boiler_key(c) in boiler:
                continue      # running head / foot (repeats on a quarter of the chapter's pages or more)
            if _in_margin(bbox, h) and re.fullmatch(r"[\d\s]*", c):
                continue      # bare page number
            for s in split_sentences(c):
                tk = tokens(s)
                if not tk:
                    continue
                words_on_page += len(tk)
                units.append(Unit(stem, i, (i + offset) if offset is not None else None, bi,
                                  round(size, 1), s, tk, font=font))
        if words_on_page < 40:
            low_text_pages.append(i)
    meta = {"chapter": stem, "pages": n, "words": sum(len(u.toks) for u in units), "units": len(units),
            "print_stamps": "; ".join(f"{k} x{v}" for k, v in stamps.most_common(3)),
            "page_offset": offset, "low_text_pages": " ".join(map(str, low_text_pages)),
            "pdf_creation": doc.metadata.get("creationDate", ""), "pdf_mod": doc.metadata.get("modDate", "")}
    return units, meta


def grams(toks: list[str], k: int = K):
    return (tuple(toks[i:i + k]) for i in range(len(toks) - k + 1))


class Index:
    """K-gram index of one edition of a book: per chapter and for the whole book."""

    def __init__(self, units: list[Unit], k: int = K):
        self.k = k
        self.by_chapter: dict[str, set] = defaultdict(set)
        self.short: dict[str, set] = defaultdict(set)   # normalised short units (< k words), per chapter
        streams: dict[tuple, list[str]] = defaultdict(list)
        for u in units:                                  # K-grams may run across sentences inside a block
            streams[(u.chapter, u.pdf_page, u.block)].extend(u.toks)
            if len(u.toks) < k:
                self.short[u.chapter].add(" ".join(u.toks))
        # K-grams are taken over the whole chapter stream (blocks in extraction order), not block by
        # block: some pages store every printed line as its own block, and lines re-break between printings.
        chap_stream: dict[str, list[str]] = defaultdict(list)
        for (ch, _, _), tk in streams.items():
            chap_stream[ch].extend(tk)
        for ch, tk in chap_stream.items():
            self.by_chapter[ch].update(grams(tk, k))
        self.book = set().union(*self.by_chapter.values()) if self.by_chapter else set()
        self.short_book = set().union(*self.short.values()) if self.short else set()
        self._text: dict[str, str] = {}
        self._streams = streams

    def chapter_text(self, ch: str) -> str:
        if ch not in self._text:
            self._text[ch] = " " + "  ".join(" ".join(tk) for (c, _, _), tk in self._streams.items() if c == ch) + " "
        return self._text[ch]


def covered(toks: list[str], gramset: set, k: int = K) -> list[bool]:
    cov = [False] * len(toks)
    for i, g in enumerate(grams(toks, k)):
        if g in gramset:
            for j in range(i, i + k):
                cov[j] = True
    return cov


def score_units(units: list[Unit], other: Index, align: dict[str, str | None], k: int = K) -> None:
    """Fill retained_same / retained_book / label for each unit of one edition against the other edition."""
    # Coverage runs along each chapter's whole token stream, so a K-gram may span sentence,
    # block and page boundaries.
    chapters: dict[str, list[Unit]] = defaultdict(list)
    for u in units:
        chapters[u.chapter].append(u)
    for ch, us in chapters.items():
        tk = [t for u in us for t in u.toks]
        tgt = align.get(ch)
        cb = covered(tk, other.book, k)
        cs = covered(tk, other.by_chapter.get(tgt, set()), k) if tgt else [False] * len(tk)
        pos = 0
        for u in us:
            n = len(u.toks)
            rb, rs = sum(cb[pos:pos + n]), sum(cs[pos:pos + n])
            pos += n
            if n < k and rs < n:
                # Very short unit (heading, label, "Fig. 3"): whole-string match, but only inside the
                # aligned chapter.  Short strings recur all over a book, so a book-wide match would
                # wrongly "retain" the headings of a chapter that was dropped.
                s = " ".join(u.toks)
                if tgt and (s in other.short.get(tgt, set()) or (" " + s + " ") in other.chapter_text(tgt)):
                    rs = rb = n
                else:
                    rb = rs
            u.retained_book, u.retained_same = rb, min(rs, rb)
            u.label = label_for(u.retained_same / n, u.retained_book / n)


def label_for(share_same: float, share_book: float) -> str:
    if share_same >= KEPT_T:
        return "kept"
    if share_book >= KEPT_T:
        return "moved"
    if share_book < DEL_T:
        return "deleted"
    return "reworded"


def _sig(u: Unit) -> str:
    return re.sub(r"[^a-z0-9ऀ-ॿ]", "", clean(u.text).lower())


def rescue(old_units: list[Unit], new_units: list[Unit], align: dict[str, str | None]) -> int:
    """Second pass for text the K-gram test cannot match because the PDF text layer is damaged.

    Some NCERT pages set quotations in a decorative font whose ligatures ("th", "fi", "ct" ...)
    have no Unicode mapping, so the same sentence extracts as "T is canno be helped" in one
    printing and differently in another.  For units still unmatched after the K-gram pass we
    compare letters-only strings (spaces removed) with the still-unmatched units of the aligned
    chapter.  Returns the number of old units rescued as "kept".
    """
    from rapidfuzz import fuzz, process

    new_by: dict[str, list[Unit]] = defaultdict(list)
    for u in new_units:
        if len(u.toks) >= 3 and u.retained_book < KEPT_T * len(u.toks):
            new_by[u.chapter].append(u)
    sig_cache = {ch: [_sig(c) for c in us] for ch, us in new_by.items()}
    n_rescued = 0
    for o in old_units:
        n = len(o.toks)
        tgt = align.get(o.chapter)
        if n < 3 or o.retained_book >= KEPT_T * n or not tgt or not new_by.get(tgt):
            continue
        so = _sig(o)
        if len(so) < 8:
            continue
        cands, sigs = new_by[tgt], sig_cache[tgt]
        m = process.extractOne(so, sigs, scorer=fuzz.ratio)
        score, idx = (m[1], m[2]) if m else (0, None)
        if len(so) >= 25:      # the old sentence may be part of a longer new unit (or vice versa)
            m2 = process.extractOne(so, sigs, scorer=fuzz.partial_ratio)
            if m2 and m2[1] > score and len(sigs[m2[2]]) >= len(so):
                score, idx = m2[1], m2[2]
        if idx is None or score < FUZZY_PAIR:
            continue
        c = cands[idx]
        cn = len(c.toks)
        if score >= FUZZY_SAME:
            o.retained_book = o.retained_same = n
            o.label, o.note = "kept", f"fuzzy:{score:.0f}"
            c.retained_book = c.retained_same = cn
            c.label, c.note = "kept", f"fuzzy:{score:.0f}"
            n_rescued += 1
        else:
            est = round(n * score / 100)
            o.retained_book = max(o.retained_book, est)
            o.retained_same = max(o.retained_same, est)
            o.label, o.note = "reworded", f"fuzzy_pair:{score:.0f}"
            if c.label != "kept":
                c.retained_book = max(c.retained_book, round(cn * score / 100))
                c.label, c.note = "reworded", f"fuzzy_pair:{score:.0f}"
    return n_rescued


def align_chapters(old_units: list[Unit], new: Index, k: int = K) -> tuple[dict, dict]:
    """Map each old chapter to the new chapter that retains most of its words (or None = dropped)."""
    by: dict[str, list[Unit]] = defaultdict(list)
    for u in old_units:
        by[u.chapter].append(u)
    align, detail = {}, {}
    for ch, us in by.items():
        tk = [t for u in us for t in u.toks]
        best, best_f = None, 0.0
        for nch, gs in new.by_chapter.items():
            f = sum(covered(tk, gs, k)) / len(tk) if tk else 0.0
            if f > best_f:
                best, best_f = nch, f
        align[ch] = best if best_f >= CHAPTER_ALIGN_MIN else None
        detail[ch] = (best, round(best_f, 4))
    return align, detail


def extract_book(folder: str | Path) -> tuple[list[Unit], list[dict]]:
    units, metas = [], []
    for pdf in sorted(Path(folder).glob("*.pdf")):
        u, m = extract_chapter(pdf)
        units.extend(u)
        metas.append(m)
    return units, metas


def diff_books(old_units: list[Unit], new_units: list[Unit], k: int = K, fuzzy: bool = True):
    """Score both directions in place. Returns (align old->new, detail, align new->old)."""
    old_idx, new_idx = Index(old_units, k), Index(new_units, k)
    align, detail = align_chapters(old_units, new_idx, k)
    ralign, _ = align_chapters(new_units, old_idx, k)
    score_units(old_units, new_idx, align, k)
    score_units(new_units, old_idx, ralign, k)
    if fuzzy:
        rescue(old_units, new_units, align)
    return align, detail, ralign


def is_front_matter(stem: str) -> bool:
    """NCERT file suffixes: ps = prelims, an = answers, gl = glossary, ap/a1/a2 = appendix, in = index."""
    return bool(re.search(r"(ps|an|gl|ap|a\d|in|sm|cc)$", stem))
