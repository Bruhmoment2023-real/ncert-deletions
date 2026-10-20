# Literature map (bibliometrics) - 07-ncert-deletions

Data-driven map of the literature around: *A measured text comparison of India's NCERT textbooks before and after the 2022-23 rationalisation*

- **Corpus size:** 706 records (Curriculum reform and the National Education Policy 2020: 282; Textbook revision, curriculum politics and history-textbook controversies in India: 225; Computational text analysis of textbooks (any country): 195; seed: 4)
- **Date of pull:** 2026-10-13
- **Sources:** discovery in Crossref, Semantic Scholar, ERIC and arXiv; metadata from OpenAlex; forward citations from OpenCitations. No Scopus/WoS data (EMPTY - no Scopus/WoS export to merge; corpus is OpenAlex-only).
- **Made by:** an AI agent (Claude). It contains data, figures, tables and bullet-point analysis only - no manuscript prose.

## What is here

| Path | Contents |
|---|---|
| `search-protocol.md` | exact search strings, databases, inclusion/exclusion rules, PRISMA-style counts, coverage checks |
| `scopus-queries.md` | ready-to-paste Scopus and Web of Science advanced-search strings (not run: no login) |
| `gap-analysis.md` | what the map shows: dense and thin areas, where Sean's question sits, five papers to read first |
| `evidence-table.csv` | the most relevant papers with study type, setting, data, method, one-line finding (from the abstract), relation to this paper |
| `config.json` | every setting of the run: queries, rules, seeds, hand-screen exclusions |
| `data\raw\` | raw API responses per query (`crossref\`, `s2\`, `eric\`, `arxiv\`), all query hits (`all_hits.csv`), query log, raw OpenAlex records (`openalex\*.jsonl.gz`) |
| `data\clean\` | `master.csv` / `master.rds` (one row per corpus record), `bibliometrix_input.csv` / `bibliometrix_M.rds` (bibliometrix data frame), `citation_edges.csv`, `cited_references.csv`, screening logs, unresolved candidates |
| `figures\` | 49 figures (PNG at 220 dpi, SVG copies, interactive HTML) and `captions.md` |
| `tables\` | 58 CSV tables (every figure's numbers, PRISMA counts, clusters, logs) |
| `vosviewer\` | map + network files for VOSviewer (co-citation, co-authorship, keyword co-occurrence, bibliographic coupling, direct citation) and VOSviewer-computed layouts |
| `pdfs\` | 20 legally open-access PDFs of core papers and `download_log.csv` |
| `R\`, `python\` | the scripts that made everything |
| `scopus-drop\` | empty; put Scopus/WoS exports here |

## How to regenerate everything (PowerShell)

```powershell
$py = 'D:\Research-Publishing\_tools\biblio-venv\Scripts\python.exe'
$b  = 'D:\Research-Publishing\07-ncert-deletions\bibliometrics'
& $py "$b\python\pipeline.py" $b search enrich snowball refs master   # network; every response is cached in D:\Research-Publishing\_tools\biblio-cache
$env:R_LIBS_USER = 'D:\Research-Publishing\_tools\R-lib;C:\Users\seans\AppData\Local\R\win-library\4.5'   # this shell only
& 'C:\Program Files\R\R-4.5.3\bin\Rscript.exe' "$b\R\bibliometrix_analysis.R" $b                # tables + R figures + VOSviewer files
& $py "$b\python\figures.py" $b        # Python figures, VOSviewer layouts, captions.md
& $py "$b\python\pdfs.py" $b download  # open-access PDFs of the core papers
& $py "$b\python\pdfs.py" $b evidence  # rebuild evidence-table.csv from data\clean\evidence_notes.json
& $py "$b\python\docs.py" $b           # this README and search-protocol.md
```
Re-running `search` on a later date re-uses cached responses; delete the cache file to force a fresh pull. To hand-exclude a record, add its OpenAlex id and a reason under `manual_exclude` in `config.json` and re-run `master` onward.

## Analysis log

R / bibliometrix: 26 of 27 analyses completed.

Not produced:
- historiograph: FAILED: arguments imply differing number of rows: 0, 1

Python figures:
- prisma: ok
- year_sub: ok
- timeline: ok
- db: ok
- geography: ok
- citation_network: ok
- main_path: ok
- cocitation: ok
- vosviewer_cli: VOSviewer command line produced layouts for: keyword_cooccurrence, coauthorship_authors. py_cocitation_references: VOSviewer command line timed out. 

## Limits (read before using any figure)

- Discovery ran through Crossref, Semantic Scholar, ERIC and arXiv, not through an OpenAlex or Scopus topic search (see search-protocol.md section 1). Recall is unknown; the corpus is a map of the indexed literature, not a census.
- OpenAlex is broader but noisier than Scopus: it includes low-quality and predatory outlets, working-paper duplicates and occasional wrong metadata. Screening was by rules plus one AI hand pass over titles.
- OpenAlex is weak on Indian journals and books (missing abstracts, affiliations and reference lists) and on law. Country and collaboration figures only describe the records that carry affiliation data.
- Keywords are OpenAlex's machine-assigned keywords, not author keywords. Thematic maps and co-occurrence networks inherit OpenAlex's vocabulary.
- Citation links exist only where the publisher deposited a reference list. Books, reports, working papers and most law reviews appear isolated even when they are heavily used.
- Citation counts are as of the pull date and favour older papers and English-language journals.
- Evidence-table findings are taken from abstracts unless a row says 'full text read'. Check the paper before citing it.


## Hand-screening and later additions (17 Oct 2026)

- **Hand-screen:** 68 records removed as off-topic (A: ed-tech, pedagogy and general education items that do not concern textbooks or school history; B: ELT materials, ed-tech and benchmark items that are not computational analysis of textbook content): `data\clean\handscreen_exclusions.json` and `config.json` manual_exclude, each with a reason. Corpus before screening 774, after 706. `data\clean\corpus_final.jsonl.gz` is the pre-screen file; `master.csv` is the screened table. A few off-topic records remain in the corpus (see gap-analysis limits).
- **Evidence table:** hand-screened after the automatic selection (5 rows removed, list in `tables\evidence_hand_screen_removed.csv`; 2 neighbours added; read status and links to reading notes updated). Automatic version: `data\clean\evidence-table.autogen.csv`; patch script `..\depth\appendix\evidence_handpatch.py`.
- **PDFs:** open-access PDFs in `pdfs\` and `pdfs\extra\` (Lucy et al. via ERIC, Crawfurd et al., Anand and Kuruvilla, Parandhama, among others); `pdfs\_not_core\` holds PDFs that proved off-topic or mismatched. Several publisher pages returned block pages or errors; nothing was fetched around them.
- **Topic chart:** `figures\py_10_study_settings_map.png` (world and India maps of where studies are set; script `python\topic_chart_07.py`). Labels were wrapped in this pass after a first draft overlapped.
- **Depth additions:** burst detection and main path (`figures\py_20_*`, `py_22_*`, `tables\py_burst_*`, `tables\py_mainpath_*`); reference-burst detection found no bursts in this sparse network (226 in-corpus links).
- **Known failures:** bibliometrix historiograph returned zero rows; VOSviewer co-citation layout timed out (the co-authorship and keyword layouts worked); bibliographic coupling was capped at 500 documents.
- **Not done:** no Scopus or Web of Science merge (`scopus-drop\` is empty). Nothing was written to `full-corpus\`.
- **Neutrality:** captions and notes describe counts and sources; characterisations in sources are reported as their authors' views.
