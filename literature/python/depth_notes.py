"""Depth layer 1: extractive full-text reading notes from the open-access PDFs.

Usage: python depth_notes.py <paper_folder> [max_papers]
Reads  <paper>\\bibliometrics\\pdfs\\*.pdf and evidence-table.csv ; writes <paper>\\depth\\reading-notes\\<author>-<year>-<word>.md and 00-index.md

HONEST METHOD: the PDF text is extracted with pypdf and sentences are SELECTED (never rewritten) by cue-word rules for each field.
Everything in quotation marks or under a field heading is a verbatim sentence from the PDF, with the PDF page index (1-based
page of the file, not the journal's printed page number). No field is filled from memory. 'Relation to Sean's paper' is the
sub-literature relation from the evidence table; the direction (supports / contradicts) is NOT judged by the script.
"""
import os, re, sys, csv, glob
import pandas as pd
from pypdf import PdfReader

P = os.path.abspath(sys.argv[1])
MAXN = int(sys.argv[2]) if len(sys.argv) > 2 else 25
B = os.path.join(P, "bibliometrics")
OUT = os.path.join(P, "depth", "reading-notes")
os.makedirs(OUT, exist_ok=True)
ev = pd.read_csv(os.path.join(B, "evidence-table.csv"), encoding="utf-8-sig", keep_default_na=False)
ev = ev[ev.pdf_in_folder != ""]
MST = pd.read_csv(os.path.join(B, "data", "clean", "master.csv"), encoding="utf-8-sig", keep_default_na=False).set_index("oa_id")
STOP = set("evidence effect effects study studies analysis impact towards using within results result based from with into under about their between through during after before when what which where does case some those these other cheating examination examinations exams exam students student school schools".split())


def clean(t):
    t = t.replace("­", "").replace("ﬁ", "fi").replace("ﬂ", "fl")
    t = re.sub(r"(\w)-\n(\w)", r"\1\2", t)
    t = re.sub(r"\s*\n\s*", " ", t)
    return re.sub(r"\s+", " ", t).strip()


def sents(t):
    return [s.strip() for s in re.split(r"(?<=[.!?])\s+(?=[A-Z\"'(\[])", t) if 40 <= len(s.strip()) <= 420]


def pick(items, rx, n, prefer_num=False, bad=None, minw=8, maxw=45):
    sc = []
    for pg, s in items:
        if bad and re.search(bad, s, re.I):
            continue
        w = len(s.split())
        if w < minw or w > maxw or s.count("|") > 1 or re.search(r"https?://|doi\.org|copyright|©|all rights reserved|downloaded from", s, re.I):
            continue
        hits = len(re.findall(rx, s, re.I))
        if hits:
            sc.append((hits * 2 + (2 if prefer_num and re.search(r"\d", s) else 0), pg, s))
    sc.sort(key=lambda x: (-x[0], x[1]))
    out, seen = [], set()
    for _, pg, s in sc:
        k = s[:60]
        if k not in seen:
            seen.add(k)
            out.append((pg, s))
        if len(out) == n:
            break
    return sorted(out)


RQ = r"\b(this (paper|study|article|research|chapter)|we) (examine|investigate|ask|study|test|estimate|explore|analy[sz]e|evaluate|assess|aim|seek|address|compare|document|measure)|research questions?|(whether|how) .{0,60}\?"
DATA = r"\b(data(set)?s?|sample|survey|respondents|participants|observations|records|administrative|schools|students|candidates|corpus|enrol+ed|collected|we use)\b"
METH = r"\b(difference-in-differences?|regression|randomi[sz]|instrument|fixed effects|identification|estimat\w+|specification|questionnaire|interview|thematic|coding|model|algorithm|experiment|quasi|discontinuity|control group|treatment)\b"
RES = r"\b(we find|found that|find that|results? (show|indicate|suggest|reveal)|show(s|ed)? that|increase[sd]?|decrease[sd]?|reduc\w+|significant\w*|effect of|percent|per cent|higher|lower|associated)\b|%"
LIM = r"\b(limitation\w*|caveat\w*|caution|cannot|can not|should be interpreted|future (research|work|studies)|not (be )?generali[sz]|may not|beyond the scope|one concern|threat)\b"
BADBOILER = r"^(table|figure|fig\.|source:|note:)|^\W*\d+\W*$"


# ---- extra PDFs the pack itself collected (paper folder \lit\<arxiv id>.pdf): the closest prior work
import xml.etree.ElementTree as ET
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import common as C
have_titles = set(ev.citation.str.lower())
xr = []
for fp in sorted(glob.glob(os.path.join(P, "lit", "*.pdf"))):
    aid = os.path.basename(fp)[:-4]
    if not re.match(r"^\d{4}\.\d{4,5}$", aid):
        continue
    st, tx = C.fetch(f"http://export.arxiv.org/api/query?id_list={aid}")
    try:
        ns = {"a": "http://www.w3.org/2005/Atom"}
        e = ET.fromstring(tx).find("a:entry", ns)
        ti = re.sub(r"\s+", " ", e.find("a:title", ns).text).strip()
        au = [x.find("a:name", ns).text for x in e.findall("a:author", ns)]
        yr = int(e.find("a:published", ns).text[:4])
        sm = re.sub(r"\s+", " ", e.find("a:summary", ns).text).strip()
        xr.append(dict(citation=f"{au[0]}{' et al.' if len(au) > 1 else ''} ({yr}). {ti}. arXiv:{aid}.", year=yr, doi_or_link=f"https://arxiv.org/abs/{aid}", open_access_link=f"https://arxiv.org/pdf/{aid}",
                       pdf_in_folder=fp, main_finding_from_abstract=" ".join(sents(sm)[:2]) or sm[:300], study_type="", country_or_setting="", relation_to_seans_paper="Prior work collected in the pack's lit\ folder (named in the pack's prior-work file)",
                       openalex_id="", fa_name=au[0]))
    except Exception:
        pass
if xr:
    ev = pd.concat([pd.DataFrame(xr), ev], ignore_index=True)
rows = []
used = set()
for r in ev.itertuples():
    if len(rows) >= MAXN + len(xr):
        break
    fp = r.pdf_in_folder if os.path.isabs(str(r.pdf_in_folder)) else os.path.join(B, "pdfs", r.pdf_in_folder)
    if not os.path.exists(fp):
        continue
    try:
        rd = PdfReader(fp)
        pages = []
        for i, pg in enumerate(rd.pages[:70], 1):
            try:
                pages.append((i, clean(pg.extract_text() or "")))
            except Exception:
                pages.append((i, ""))
        n_pages = len(rd.pages)
    except Exception as e:
        pages, n_pages = [], 0
    chars = sum(len(t) for _, t in pages)
    fa = (MST.loc[r.openalex_id].first_author if r.openalex_id in MST.index else ((r.fa_name if isinstance(getattr(r, "fa_name", None), str) else ""))) or "anon"
    au = re.sub(r"[^a-z]", "", fa.split(",")[0].split()[-1].lower() if fa.split() else "anon") or "anon"
    yr = int(r.year)
    word = re.sub(r"[^a-z]", "", next((w.lower() for w in re.findall(r"[A-Za-z]{5,}", r.citation.split("). ", 1)[-1]) if w.lower() not in STOP), "paper"))
    name = f"{au}-{yr}-{word}.md"
    k = 2
    while name in used:
        name = f"{au}-{yr}-{word}{k}.md"; k += 1
    used.add(name)
    hdr = f"# {r.citation}\n\n- **Link:** {r.doi_or_link}  |  **Open-access copy:** {r.open_access_link or 'see pdfs folder'}  |  **Local PDF:** `{os.path.relpath(fp, P)}`\n"
    if chars < 1500:
        txt = hdr + (f"\n> **Source status: abstract only.** The PDF ({n_pages} pages) gave no usable text (scanned or image PDF), so this note is limited to the abstract-level line in the evidence table.\n\n"
                     f"- **Main finding (from abstract):** {r.main_finding_from_abstract}\n- **Study type / setting:** {r.study_type} / {r.country_or_setting}\n- **Relation to Sean's paper:** {r.relation_to_seans_paper}\n")
        status = "abstract only"
    else:
        items = []
        for pg, t in pages:
            for s in sents(t):
                items.append((pg, s))
        refstart = next((pg for pg, t in pages if re.search(r"\b(references|bibliography)\b\s+[A-Z]", t[:400]) and pg > 3), 999)
        body = [(pg, s) for pg, s in items if pg < refstart]
        early = [x for x in body if x[0] <= 4]
        late = [x for x in body if x[0] >= max(1, min(n_pages, 70) - 8)] or body
        rq = pick(early, RQ, 2, bad=BADBOILER)
        dat = pick(body, DATA, 3, prefer_num=True, bad=BADBOILER)
        met = pick(body, METH, 3, bad=BADBOILER)
        res = pick(body, RES, 5, prefer_num=True, bad=BADBOILER)
        lim = pick(body, LIM, 3, bad=BADBOILER)
        quotes = pick([x for x in body if len(x[1].split()) <= 40], RES + "|" + LIM + "|" + RQ, 4, prefer_num=False, bad=BADBOILER)

        def sec(title, lst):
            if not lst:
                return f"## {title}\n- (no sentence matched the extraction rules; read the PDF)\n\n"
            return f"## {title}\n" + "\n".join(f"- \"{s}\" (PDF p. {pg})" for pg, s in lst) + "\n\n"
        txt = (hdr + f"- **Pages:** {n_pages} (text extracted from {len(pages)}; PDF page numbers below are positions in the file)\n"
               f"- **Source status: opened in full (extractive).** The sentences below were selected by cue-word rules from the PDF text and are verbatim; nothing is paraphrased or filled from memory. Selection can miss the most important sentence: use this to locate passages, then read them.\n"
               f"- **Evidence-table line (abstract):** {r.main_finding_from_abstract}\n\n"
               + sec("Research question", rq) + sec("Data and sample", dat) + sec("Method and identification", met) + sec("Main results (sentences with numbers first)", res)
               + sec("Limitations stated by the authors", lim) + sec("Short verbatim quotations", quotes)
               + f"## Bearing on Sean's paper\n- **Sub-literature relation:** {r.relation_to_seans_paper}\n- **Direction (supports / contradicts / method to borrow / gap):** not judged by the script; decide after reading the passages above.\n")
        status = "opened in full (extractive)"
    open(os.path.join(OUT, name), "w", encoding="utf-8").write(txt)
    rows.append(dict(note=name, citation=r.citation, year=yr, status=status, takeaway=r.main_finding_from_abstract[:200], pages=n_pages))
    print(name, status, flush=True)

idx = "# Reading notes index\n\nExtractive notes from open-access PDFs in `bibliometrics\\pdfs\\` (method in `python\\depth_notes.py`). 'Takeaway' is the abstract-level finding from the evidence table, not a reading of the full text.\n\n| Note | Citation | Status | Pages | One-line takeaway (abstract) |\n|---|---|---|---|---|\n"
for x in rows:
    idx += f"| [{x['note']}]({x['note']}) | {x['citation'].replace('|', '/')} | {x['status']} | {x['pages']} | {x['takeaway'].replace('|', '/')} |\n"
open(os.path.join(OUT, "00-index.md"), "w", encoding="utf-8").write(idx)
print(len(rows), "notes")
