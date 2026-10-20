"""Depth layer 4: data dictionary, rerun script and reproducibility checklist for one paper folder.

Usage: python depth_appendix.py <paper_folder>
Writes <paper>\\depth\\appendix\\{data-dictionary.md, rerun.ps1, reproducibility-checklist.md}. Inventory is generated from the files on disk
(path, size, date, rows, columns with dtype and example); meanings come from the paper's own DATA_DICTIONARY / README where one exists,
from the fixed bibliometrics glossary below, or are marked 'meaning not documented' - never guessed.
"""
import os, re, sys, glob, gzip, json, time, platform, subprocess
import pandas as pd

P = os.path.abspath(sys.argv[1])
paper = os.path.basename(P)
OUT = os.path.join(P, "depth", "appendix")
os.makedirs(OUT, exist_ok=True)
SKIP = re.compile(r"(\\\.venv|\\venv|\.venv-ocr|__pycache__|\\depth\\|\\bibliometrics\\(data\\raw|pdfs|figures|vosviewer|R|python)\\|\\cache\\|\\raw\\|node_modules)", re.I)
today = time.strftime("%Y-%m-%d")

GLOSS = {"AU": "bibliometrix: authors (short form)", "AF": "bibliometrix: authors (full names)", "TI": "bibliometrix: title (upper case)", "SO": "bibliometrix: source (journal) name", "PY": "bibliometrix: publication year", "TC": "bibliometrix: total citations (OpenAlex)", "DE": "bibliometrix: author/OpenAlex keywords", "ID": "bibliometrix: keywords-plus (here OpenAlex concepts/topics)", "AB": "bibliometrix: abstract", "DT": "bibliometrix: document type", "DI": "bibliometrix: DOI", "CR": "bibliometrix: cited references, one label per reference, separated by ;", "C1": "bibliometrix: author affiliations", "LCS": "bibliometrix: local citation score (citations from inside the corpus)", "SR": "bibliometrix: short reference key", "DB": "bibliometrix: database label", "LA": "bibliometrix: language", "J9": "bibliometrix: abbreviated journal", "SC": "bibliometrix: subject category", "RP": "bibliometrix: reprint (corresponding-author) address", "CO": "bibliometrix: country of corresponding author", "OA": "bibliometrix: open-access flag", "SU": "bibliometrix: sub-literature label",
    "oa_id": "OpenAlex work id (W...)", "doi": "DOI, lower-case, no URL prefix", "title": "work title (OpenAlex)", "year": "publication year", "date": "publication date",
    "type": "OpenAlex work type (article, review, preprint, book-chapter ...)", "language": "ISO language code", "source": "journal / repository name", "source_type": "journal, repository, book series ...",
    "authors": "author display names, '; '-separated", "n_authors": "number of authors", "first_author": "first author's name", "institutions": "author institutions, '; '-separated",
    "countries": "ISO-2 country codes of author affiliations, '; '-separated (empty when OpenAlex has no affiliation data)", "cited_by_count": "citations counted by OpenAlex at pull date",
    "fwci": "field-weighted citation impact (OpenAlex; 1 = world average for field/year/type)", "local_citations": "citations received from other records inside this corpus",
    "n_refs": "number of references in OpenAlex", "is_oa": "open-access flag (OpenAlex)", "oa_status": "gold/green/hybrid/bronze/closed", "oa_url": "best open-access landing page", "best_pdf_url": "direct PDF link, if known",
    "sublit": "primary sub-literature assigned by the screening rules", "sublits_all": "every sub-literature whose rule matched, '; '-separated", "origin": "search | snowball-backward | snowball-forward | seed",
    "found_in": "databases that returned the record (crossref, s2, eric, arxiv, seed)", "relevance": "rule-based topical score (core-term hits weighted); higher = closer to the paper's topic",
    "keywords": "OpenAlex machine-assigned keywords", "concepts": "OpenAlex concepts", "topics": "OpenAlex topics", "abstract": "abstract text (rebuilt from OpenAlex inverted index or taken from S2/ERIC/Crossref)",
    "has_abstract": "1 if an abstract is present", "is_retracted": "OpenAlex retraction flag", "sr": "short reference key used by bibliometrix", "crossref_cited_by": "Crossref is-referenced-by count", "s2_citation_count": "Semantic Scholar citation count",
    "citing": "OpenAlex id of the citing record (inside the corpus)", "cited": "OpenAlex id of the cited record (in or outside the corpus)", "cr_label": "bibliometrix-style cited-reference label",
    "in_corpus": "1 if the cited work is itself a corpus record", "global_citations": "OpenAlex citation count",
}
BIBLIO = [
    ("bibliometrics\\data\\clean\\master.csv", "one row per corpus record after screening and hand-screening (the main table)"),
    ("bibliometrics\\data\\clean\\bibliometrix_input.csv / bibliometrix_M.rds", "the same records in bibliometrix's field-tag format (AU, TI, SO, PY, TC, DE, ID, CR, C1 ...)"),
    ("bibliometrics\\data\\clean\\citation_edges.csv", "direct-citation links between corpus records (citing, cited)"),
    ("bibliometrics\\data\\clean\\cited_references.csv", "the references cited most often by the corpus, resolved to metadata"),
    ("bibliometrics\\data\\clean\\corpus_final.jsonl.gz / corpus_stage1.jsonl.gz", "full OpenAlex JSON records after / before the last screening pass"),
    ("bibliometrics\\data\\clean\\screening_log_*.csv", "every screening decision with its reason"),
    ("bibliometrics\\data\\clean\\unresolved_candidates.csv", "records found by a search but not matched in OpenAlex (kept for audit)"),
    ("bibliometrics\\data\\raw\\", "raw API responses per query (crossref, s2, eric, arxiv) + all_hits.csv + query_log.csv; OpenAlex records as .jsonl.gz"),
    ("bibliometrics\\tables\\", "numbers behind every figure (R_*.csv from bibliometrix, py_*.csv from Python), PRISMA counts, logs"),
]


def own_dictionary():
    out = []
    for f in glob.glob(os.path.join(P, "**", "*DICTIONARY*.md"), recursive=True) + glob.glob(os.path.join(P, "code", "README.md")):
        if not SKIP.search(f):
            out.append(f)
    return out


def describe(fp):
    ext = fp.lower().rsplit(".", 1)[-1]
    try:
        if ext in ("csv", "tsv", "txt") and os.path.getsize(fp) < 400e6:
            df = pd.read_csv(fp, sep="\t" if ext == "tsv" else ",", encoding="utf-8-sig", keep_default_na=False, low_memory=False, nrows=None if os.path.getsize(fp) < 60e6 else 50000)
        elif fp.lower().endswith(".csv.gz"):
            df = pd.read_csv(fp, encoding="utf-8-sig", keep_default_na=False, low_memory=False, nrows=50000)
        elif ext == "npz":
            import numpy as np
            z = np.load(fp, allow_pickle=False)
            return None, [f"{k}: array shape {z[k].shape} dtype {z[k].dtype}" for k in z.files]
        else:
            return None, None
        cols = []
        for c in df.columns:
            ex = str(df[c].iloc[0])[:40] if len(df) else ""
            cols.append(f"`{c}` ({df[c].dtype}; e.g. {ex!r})" + (f": {GLOSS[c]}" if c in GLOSS else ""))
        return len(df), cols
    except Exception as e:
        return None, [f"(could not read: {type(e).__name__})"]


files = []
for root, dirs, fs in os.walk(P):
    dirs[:] = [d for d in dirs if not SKIP.search(os.path.join(root, d) + "\\")]
    for f in fs:
        fp = os.path.join(root, f)
        if SKIP.search(fp):
            continue
        if re.search(r"\.(csv|tsv|npz|csv\.gz|xlsx|json|jsonl\.gz|rds|txt|parquet)$", f, re.I) and "bibliometrics\\tables" not in fp and "bibliometrics\\scopus" not in fp:
            files.append(fp)
files.sort()
md = [f"# Data dictionary - {paper}\n\nGenerated {today} from the files on disk by `python\\depth_appendix.py`. Inventory columns are read from the files; meanings are copied from the paper's own documentation or the fixed glossary, otherwise marked 'meaning not documented'. Large raw dumps (raw API responses, cached downloads, PDFs, virtual environments) are summarised, not listed.\n"]
own = own_dictionary()
if own:
    md.append("## Documentation that already exists in the folder (authoritative for the paper's own data)\n" + "\n".join(f"- `{os.path.relpath(f, P)}`" for f in own) + "\n")
md.append("## Bibliometrics layer (made by the literature-mapping pipeline)\n\n| Path | What it is |\n|---|---|\n" + "\n".join(f"| `{a}` | {b} |" for a, b in BIBLIO) + "\n")
md.append("Access/pull date for all bibliometrics data: see `bibliometrics\\data\\clean\\prisma_search.json` (field `date`); sources: Crossref REST API, Semantic Scholar API, ERIC API, arXiv API, OpenAlex API, OpenCitations API (all free, no key, no personal identifier sent). Known problems: OpenAlex affiliation/abstract/reference gaps for Indian journals, books and law; duplicate preprint/published versions merged by title only; keywords are machine-assigned.\n")
md.append("## File inventory\n")
for fp in files:
    rel = os.path.relpath(fp, P)
    st = os.stat(fp)
    nrows, cols = describe(fp)
    md.append(f"### `{rel}`\n- size {st.st_size/1024:.0f} KB; modified {time.strftime('%Y-%m-%d', time.localtime(st.st_mtime))}" + (f"; rows {nrows}" + (" (first 50,000 read)" if nrows == 50000 else "") if nrows is not None else ""))
    if cols:
        md.append("- columns / contents:\n" + "\n".join(f"  - {c}" if ("): " in c or c.startswith("(")) else f"  - {c}  - *meaning not documented here (see the files above / the code that writes it)*" for c in cols[:60]))
        if len(cols) > 60:
            md.append(f"  - ... {len(cols) - 60} more columns")
    md.append("")
# raw summaries
for sub in ("data\\raw", "raw", "data\\cache"):
    d = os.path.join(P, sub)
    if os.path.isdir(d):
        n = sum(len(f) for _, _, f in os.walk(d)); sz = sum(os.path.getsize(os.path.join(r, x)) for r, _, f in os.walk(d) for x in f)
        md.append(f"### `{sub}\\` (summarised)\n- {n} files, {sz/1e6:.0f} MB. Raw downloads/caches as fetched on the stated dates; not individually listed. Check the code that fills it for the source URL.\n")
open(os.path.join(OUT, "data-dictionary.md"), "w", encoding="utf-8").write("\n".join(md))

# ---- rerun.ps1
code = sorted(glob.glob(os.path.join(P, "code", "[0-9]*.py")))
steps = "\n".join(f"    @{{ Name = '{os.path.basename(c)}'; Cmd = {{ & $PackPy '{c}' }} }}" for c in code) if code else "    # (no numbered scripts found in code\\)"
packpy = next((p for p in (os.path.join(P, ".venv", "Scripts", "python.exe"), os.path.join(P, "venv", "Scripts", "python.exe"), r"D:\Research-Publishing\_tools\biblio-venv\Scripts\python.exe") if os.path.exists(p)), "python")
ps = f"""# rerun.ps1 - rebuild {paper} from raw data, in order.   Usage:  powershell -File rerun.ps1            (dry run: checks inputs and syntax only)
#                                                          powershell -File rerun.ps1 -Run       (runs everything; slow, uses the network)
# Run one job at a time on this laptop. Nothing is installed or set machine-wide.
param([switch]$Run, [switch]$SkipPack, [switch]$SkipBiblio)
if (-not (Test-Path 'D:\\')) {{ throw 'D: is missing - stop.' }}
$Paper   = '{P}'
$Biblio  = Join-Path $Paper 'bibliometrics'
$Kit     = 'D:\\Research-Publishing\\_tools\\biblio-kit'
$KitPy   = 'D:\\Research-Publishing\\_tools\\biblio-venv\\Scripts\\python.exe'
$PackPy  = '{packpy}'
$Rscript = 'C:\\Program Files\\R\\R-4.5.3\\bin\\Rscript.exe'
$env:PYTHONIOENCODING = 'utf-8'
$env:R_LIBS_USER = 'D:\\Research-Publishing\\_tools\\R-lib;C:\\Users\\seans\\AppData\\Local\\R\\win-library\\4.5'   # this process only
function Do-Step($Name, [scriptblock]$Cmd, $Check) {{
    if ($Run) {{ Write-Host "== $Name"; & $Cmd; if ($LASTEXITCODE -ne 0) {{ throw "$Name failed ($LASTEXITCODE)" }} }}
    else {{ $ok = if ($Check) {{ Test-Path $Check }} else {{ $true }}; Write-Host ("[dry run] {{0,-60}} input/script present: {{1}}" -f $Name, $ok) }}
}}
# 1. the paper's own pipeline (numbered scripts in code\\; see data\\...\\DATA_DICTIONARY or code\\README.md for what each does and which need the network)
if (-not $SkipPack) {{
  $steps = @(
{steps}
  )
  foreach ($s in $steps) {{
    if ($Run) {{ Write-Host "== $($s.Name)"; & $s.Cmd }}
    else {{ & $PackPy -I -m py_compile (Join-Path '{os.path.join(P, "code")}' $s.Name); Write-Host ("[dry run] {{0,-40}} compiles: {{1}}" -f $s.Name, ($LASTEXITCODE -eq 0)) }}
  }}
}}
# 2. the literature map (cached responses are reused; delete D:\\Research-Publishing\\_tools\\biblio-cache to force a fresh pull)
if (-not $SkipBiblio) {{
  Do-Step 'bibliometrics pipeline' {{ & $KitPy "$Kit\\pipeline.py" $Biblio search enrich snowball refs master }} "$Biblio\\config.json"
  Do-Step 'bibliometrix (R)'       {{ & $Rscript "$Kit\\R\\bibliometrix_analysis.R" $Biblio }} "$Kit\\R\\bibliometrix_analysis.R"
  Do-Step 'python figures'         {{ & $KitPy "$Kit\\figures.py" $Biblio }} "$Kit\\figures.py"
  Do-Step 'burst detection'        {{ & $KitPy "$Kit\\depth_networks.py" $Biblio }} "$Kit\\depth_networks.py"
  Do-Step 'evidence + PDFs'        {{ & $KitPy "$Kit\\evidence_auto.py" $Biblio 48; & $KitPy "$Kit\\pdfs.py" $Biblio download; & $KitPy "$Kit\\pdfs.py" $Biblio evidence }} "$Kit\\pdfs.py"
  Do-Step 'reading notes'          {{ & $KitPy "$Kit\\depth_notes.py" $Paper }} "$Kit\\depth_notes.py"
  Do-Step 'citation library'       {{ & $KitPy "$Kit\\depth_citations.py" $Paper }} "$Kit\\depth_citations.py"
  Do-Step 'docs'                   {{ & $KitPy "$Kit\\docs.py" $Biblio }} "$Kit\\docs.py"
}}
Write-Host ($(if ($Run) {{ 'done' }} else {{ 'dry run finished - re-run with -Run to execute' }}))
"""
open(os.path.join(OUT, "rerun.ps1"), "w", encoding="utf-8-sig").write(ps)

# ---- reproducibility checklist
def ver(cmd):
    try:
        return subprocess.run(cmd, capture_output=True, text=True, timeout=60).stdout.strip().splitlines()[0]
    except Exception:
        return "unknown"
pyv = ver([r"D:\Research-Publishing\_tools\biblio-venv\Scripts\python.exe", "--version"])
rv = ver([r"C:\Program Files\R\R-4.5.3\bin\Rscript.exe", "--version"]) if os.path.exists(r"C:\Program Files\R\R-4.5.3\bin\Rscript.exe") else "unknown"
try:
    bv = subprocess.run([r"C:\Program Files\R\R-4.5.3\bin\Rscript.exe", "-e", "cat(as.character(packageVersion('bibliometrix')))"], capture_output=True, text=True, timeout=120, env={**os.environ, "R_LIBS_USER": r"D:\Research-Publishing\_tools\R-lib;C:\Users\seans\AppData\Local\R\win-library\4.5"}).stdout.strip()
except Exception:
    bv = "unknown"
pk = {}
try:
    out = subprocess.run([r"D:\Research-Publishing\_tools\biblio-venv\Scripts\python.exe", "-m", "pip", "list", "--format=freeze"], capture_output=True, text=True, timeout=120).stdout
    for l in out.splitlines():
        n, _, v = l.partition("==")
        if n.lower() in ("pandas", "numpy", "scipy", "matplotlib", "networkx", "plotly", "pypdf", "requests", "rapidfuzz", "pycountry"):
            pk[n] = v
except Exception:
    pass
seeds = []
for c in glob.glob(os.path.join(P, "code", "*.py")):
    for i, l in enumerate(open(c, encoding="utf-8", errors="replace"), 1):
        if re.search(r"seed|random_state|RandomState|default_rng", l):
            seeds.append(f"`{os.path.basename(c)}:{i}`: {l.strip()[:110]}")
cl = f"""# Reproducibility checklist - {paper}

Generated {today}. Facts below were read from the machine and the folder; items marked CHECK need Sean's decision or knowledge.

## Data availability
- Literature map data (OpenAlex, Crossref, Semantic Scholar, ERIC, arXiv, OpenCitations metadata): fetched from free public APIs; rebuilt by `rerun.ps1`. Raw responses are in `bibliometrics\\data\\raw\\`; the shared HTTP cache is `D:\\Research-Publishing\\_tools\\biblio-cache`.
- The paper's own data: see `data-dictionary.md` and the paper folder's `data\\` (raw files, clean tables, build logs).
- Scopus / Web of Science: not used (no login); ready-to-paste queries in `bibliometrics\\scopus-queries.md`.

## Code availability
- Paper code: `code\\` (numbered scripts, run in order). Literature-map code: `bibliometrics\\python\\` and `bibliometrics\\R\\` (copies of `D:\\Research-Publishing\\_tools\\biblio-kit`). Depth-layer code: same folder (`depth_*.py`).
- One-command rebuild: `depth\\appendix\\rerun.ps1` (dry run by default).

## Software versions (as installed on the build machine)
- Python (literature-map venv): {pyv}; packages: {', '.join(f'{k} {v}' for k, v in sorted(pk.items()))}
- R: {rv}; bibliometrix {bv or 'unknown'}
- OS: {platform.platform()}

## Random seeds
- R analysis: `set.seed(42)` at the top of `bibliometrix_analysis.R` (word cloud / layout steps).
- Python literature-map scripts: network layouts use fixed seeds where set in `figures.py`; burst detection is deterministic.
- Paper code seeds found by search: {'; '.join(seeds) if seeds else 'none found in code\\ (check whether any analysis is stochastic)'}

## Licences of data used
- OpenAlex, arXiv metadata, Crossref metadata (facts) and OpenCitations: open (CC0 / public). Semantic Scholar API: its API licence permits research use; do not redistribute bulk dumps. ERIC: US public-domain metadata.
- Open-access PDFs in `bibliometrics\\pdfs\\`: each keeps its own licence (many CC-BY, some publisher-OA-only). They are for private reading, not for redistribution.
- Paper-specific sources: CHECK each against its terms (see the source list in the paper's own data documentation).

## What cannot be shared
- The PDFs in `bibliometrics\\pdfs\\` and any copyrighted or terms-restricted source files in `data\\raw\\` (publisher PDFs, government documents whose reuse terms are not stated). Share the scripts, the derived tables and the DOI lists instead.
- Anything containing personal or student-level data: none was collected for the literature map; CHECK the paper's own data for any.

## AI-use facts (for the paper's disclosure statement; edit to taste)
- An AI assistant (Claude, by Anthropic) wrote the literature-map pipeline and figure code, ran the database searches, applied rule-based screening plus one AI pass over titles (exclusions are logged), generated the evidence-table fields and reading notes by extractive rules (verbatim sentences from abstracts and PDFs), and built the citation library from DOIs through Crossref.
- It produced data, tables, figures and bullet-point analysis only; no manuscript text. Sean writes every sentence of the paper.
- AI-selected sentences in the evidence table and reading notes must be checked against the source before any is cited.
- CHECK the target venue's AI-disclosure rules before submission.
"""


# ---- pack status snapshot (so a reader knows what was unfinished when this appendix was generated)
try:
    rd_ = os.path.join(P, "code", "README.md")
    snap = ""
    if os.path.exists(rd_):
        tx = open(rd_, encoding="utf-8", errors="replace").read()
        m_ = re.search(r"## Status notes[^\n]*\n(.*)$", tx, re.S)
        snap = m_.group(1).strip() if m_ else ""
    resd = os.path.join(P, "results")
    nres = len(os.listdir(resd)) if os.path.isdir(resd) else 0
    cl += f"\n## Pack status when this appendix was generated ({today})\n- results\ holds {nres} files; the pack may still be changing, so re-run `depth_appendix.py` before relying on this list.\n"
    cl += ("- Status notes copied from `code\README.md`:\n" + "\n".join("  " + l for l in snap.splitlines()) + "\n") if snap else "- No status notes found in code\README.md.\n"
except Exception as e:
    cl += f"\n## Pack status\n- could not read: {e!r}\n"
open(os.path.join(OUT, "reproducibility-checklist.md"), "w", encoding="utf-8").write(cl)
print("appendix written;", len(files), "files inventoried")
