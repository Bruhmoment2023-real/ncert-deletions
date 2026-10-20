"""Depth layer 2: BibTeX + RIS library for every DOI / arXiv id cited anywhere in the paper folder.

Usage: python depth_citations.py <paper_folder>
Scans *.md/*.csv/*.txt in the paper folder (not .venv*, raw HTTP dumps, bibliometrics\\data) plus bibliometrics\\evidence-table.csv and depth\\reading-notes.
Entries come from Crossref's own BibTeX/RIS transform (cached, throttled, no identifier sent); arXiv entries from the arXiv API;
DOIs Crossref does not know are looked up through doi.org content negotiation. Nothing is hand-written.
"""
import os, re, sys, glob, time
import xml.etree.ElementTree as ET
from urllib.parse import quote
import requests
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import common as C

P = os.path.abspath(sys.argv[1])
OUT = os.path.join(P, "depth", "citations")
os.makedirs(OUT, exist_ok=True)
C.HOST_INTERVAL["doi.org"] = 0.4
SKIP = re.compile(r"(\.venv|venv|__pycache__|node_modules|\\raw\\|bibliometrics\\data|bibliometrics\\pdfs|\\depth\\citations)", re.I)
files = []
for ext in ("md", "csv", "txt", "tsv", "json"):
    files += glob.glob(os.path.join(P, "**", f"*.{ext}"), recursive=True)
files = [f for f in files if not SKIP.search(f) and os.path.getsize(f) < 3_000_000 and "api_log" not in f and "run_" not in os.path.basename(f)]
# bibliometrics tables are derived from the corpus, not cited: only the evidence table counts
files = [f for f in files if "bibliometrics" not in f or f.endswith("evidence-table.csv")]
dois, arx, where = {}, {}, {}
for f in files:
    try:
        tx = open(f, encoding="utf-8", errors="replace").read()
    except Exception:
        continue
    for d in re.findall(r"10\.\d{4,9}/[^\s\"<>)\]\},;|]+", tx):
        d = re.sub(r"(\.pdf|\.full|\.html?)$", "", re.sub(r"[&?#].*$", "", d.rstrip(".,;:'*_`").lower()))
        if d.count("(") > d.count(")"):
            d = d.rsplit("(", 1)[0]
        if re.match(r"10\.48550/arxiv\.", d):
            arx.setdefault(d.split("arxiv.", 1)[1], set()).add(f)
        else:
            dois.setdefault(d, set()).add(f)
    for a in re.findall(r"arxiv(?:\.org/(?:abs|pdf)/|:\s?)(\d{4}\.\d{4,5})", tx, re.I):
        arx.setdefault(a, set()).add(f)
print(len(files), "files scanned;", len(dois), "DOIs;", len(arx), "arXiv ids", flush=True)

bib, ris, unresolved = {}, {}, []
for d in sorted(dois):
    st, b = C.fetch(f"https://api.crossref.org/works/{quote(d, safe='/.-_()')}/transform/application/x-bibtex")
    st2, r = C.fetch(f"https://api.crossref.org/works/{quote(d, safe='/.-_()')}/transform/application/x-research-info-systems")
    if st == 200 and b.strip().startswith("@"):
        bib[d] = b.strip()
        if st2 == 200 and r.strip().startswith("TY"):
            ris[d] = r.strip()
        continue
    # doi.org content negotiation fallback (DataCite etc.)
    try:
        time.sleep(0.5)
        h = requests.get("https://doi.org/" + d, headers={"Accept": "application/x-bibtex", "User-Agent": C.UA}, timeout=40)
        if h.status_code == 200 and h.text.strip().startswith("@"):
            bib[d] = h.text.strip()
            h2 = requests.get("https://doi.org/" + d, headers={"Accept": "application/x-research-info-systems", "User-Agent": C.UA}, timeout=40)
            if h2.status_code == 200 and h2.text.strip().startswith("TY"):
                ris[d] = h2.text.strip()
            continue
    except Exception:
        pass
    unresolved.append((d, f"Crossref {st}; doi.org content negotiation failed"))
# arXiv
for a in sorted(arx):
    st, tx = C.fetch(f"http://export.arxiv.org/api/query?id_list={a}")
    try:
        ns = {"a": "http://www.w3.org/2005/Atom"}
        e = ET.fromstring(tx).find("a:entry", ns)
        title = re.sub(r"\s+", " ", e.find("a:title", ns).text).strip()
        if title.lower() == "error":
            raise ValueError
        au = [x.find("a:name", ns).text for x in e.findall("a:author", ns)]
        yr = e.find("a:published", ns).text[:4]
        key = f"arxiv{a.replace('.', '_')}"
        bib["arxiv:" + a] = (f"@misc{{{key},\n  title = {{{title}}},\n  author = {{{' and '.join(au)}}},\n  year = {{{yr}}},\n  eprint = {{{a}}},\n  archivePrefix = {{arXiv}},\n"
                             f"  url = {{https://arxiv.org/abs/{a}}},\n  note = {{Metadata from the arXiv API (no DOI used)}}\n}}")
        ris["arxiv:" + a] = "TY  - GEN\n" + "".join(f"AU  - {x}\n" for x in au) + f"TI  - {title}\nPY  - {yr}\nUR  - https://arxiv.org/abs/{a}\nN1  - Metadata from the arXiv API\nER  -"
    except Exception:
        unresolved.append(("arxiv:" + a, f"arXiv API status {st}, no entry"))
open(os.path.join(OUT, "references.bib"), "w", encoding="utf-8").write("\n\n".join(bib[k] for k in bib) + "\n")
open(os.path.join(OUT, "references.ris"), "w", encoding="utf-8").write("\n\n".join(ris[k] for k in ris) + "\n")
nobib = [k for k in bib if k not in ris]
rd = (f"# Citation library\n\n- **Entries:** {len(bib)} BibTeX (`references.bib`), {len(ris)} RIS (`references.ris`), de-duplicated by DOI / arXiv id.\n"
      f"- **Identifiers found in the folder:** {len(dois)} DOIs + {len(arx)} arXiv ids, from {len(files)} text files (prior-work notes, design and outline files, follow-ups, evidence table, reading notes).\n"
      f"- **Source of fields:** Crossref's BibTeX/RIS transform (or doi.org content negotiation, or the arXiv API); no field was typed by hand.\n"
      f"- **Not resolved ({len(unresolved)}):** " + ("; ".join(f"`{k}` ({w})" for k, w in unresolved) if unresolved else "none") + "\n"
      f"- **Known limit:** only sources with a DOI or arXiv id are captured. A source cited by title only (a report, a government page, a dataset, a statute) is not in the library; add it by hand in Zotero.\n"
      f"- **In BibTeX but not RIS:** {len(nobib)}.\n\n## Import into Zotero\n1. Zotero > File > Import... > choose `references.bib` (or `references.ris`) > keep 'Place imported collections and items into new collection'.\n"
      f"2. Check the few entries with odd capitalisation or missing pages; Crossref's metadata is only as good as the publisher's deposit.\n")
open(os.path.join(OUT, "README.md"), "w", encoding="utf-8").write(rd)
print(len(bib), "bib,", len(ris), "ris,", len(unresolved), "unresolved")
