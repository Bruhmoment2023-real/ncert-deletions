# Counting what was cut: a word-level measurement of the 2022-23 rationalisation of NCERT textbooks

Sean Solano Paul, Independent researcher, Bengaluru, India. Funding: none. Competing interests: none.

## Summary

In June 2022 NCERT published lists of content it had "rationalised" (dropped) from its school textbooks for Classes 6 to 12. This repository holds the code, count tables, figures and logs for a word-level measurement of what was actually removed. For 56 textbooks, the last pre-revision printing is compared with the "Rationalised 2023-24" printing using a containment test that is not affected by re-typesetting: a word counts as removed if it lies in no run of five consecutive words that also appears in the new edition. The tables report removed-word counts and shares by book, class, subject, chapter and printed page, a check of NCERT's page lists against the measured removals, sensitivity runs (K = 4, 8, no fuzzy matching), a hand-checked validation sample, and an OCR control. No textbook text is redistributed here.

## Repository layout

| Folder | Contents |
|---|---|
| `code/` | Full pipeline (acquisition, extraction, diff, comparison with the official lists, classification, aggregation, figures) and `code/tests/` (pytest, synthetic text only) |
| `data/official-lists/` | Parsed official lists of rationalised content (`02-official-listed-deletions.csv`), book availability notes, retrieval log |
| `data/capture-index/` | Archive capture index (`cdx_allzips.txt`) and download hashes (sha256) for the pilot books |
| `data/pairs/` | Per-book old/new edition pairing records |
| `results/` | Per-book, per-chapter, per-edition-pair count tables, validation and OCR-control summaries, sensitivity runs; `results/pilot/` holds the 5-book pilot |
| `tables/` | Paper tables 0-15 as CSV |
| `figures/` | PNG figures |
| `logs/` | Run logs |
| `docs/` | Design, prior-work and official-record notes, run-order notes, data dictionary, results summaries, bibliography (`references.bib`, `.ris`) |
| `literature/` | Code, protocol and tables for the literature mapping (see its `README.md`) |

## How to reproduce

- Python 3.12.10 (Windows). Install: `python -m venv venv`, then `venv\Scripts\python -m pip install -r requirements.txt` (`requirements.txt` is the pip freeze of the original environment; spaCy and OCR packages are only needed for entity counts and OCR).
- OCR (only for the seven books whose 2022-23 scan has no text layer): Tesseract 5.5 with `eng` and `hin` tessdata_fast; see `docs/RUN-ORDER-full-corpus.md` for the exact set-up.
- Run order, with every command, is in `docs/RUN-ORDER-full-corpus.md` (56-book run) and `docs/RUN-ORDER-pilot.md` (pilot). In short: `code/acquire.py` (download the books, see below) -> `fetch_alt.py` / `ocr_pdf.py` -> `make_pairs.py` -> `run_corpus.py` -> `qa_pairs.py` -> `compare_official2.py` -> `crosscheck.py`, `classify_rules.py`, sensitivity runs -> `aggregate*.py`. Tests: `python -m pytest code/tests -q`.
- Chapter-threshold sensitivity (paper section 2.3; needs only the repo): `python -I code/threshold_sensitivity_v10.py results/chapter_summary.csv` prints, for thresholds 20/25/30/35/40%, the dropped English chapters and how the 622,576 removed words split between dropped and surviving chapters (the word totals themselves do not depend on the threshold). Saved output: `results/threshold_sensitivity_v10_output.txt`. It replaces an earlier `threshold_sensitivity.py`, which wrongly counted every word of a dropped chapter as removed.
- The scripts expect the original working layout (`data/books/<edition>/<book>/*.pdf`, `data/official/` booklets) and some hard-coded D:/E: scratch paths; adjust the paths at the top of each script.

## How to obtain the textbooks and official booklets (not included)

- Abstract text of third-party papers (the `abstract`/`AB` columns and abstract-derived quote columns of the bibliographic tables, and abstract fields in the OpenAlex JSON). Identifiers, titles, years, venues, keywords and citation data are kept; re-fetch abstracts with the bibliometrics pipeline if needed.
- Per-paper reading notes on the literature (they contain quotations from copyrighted papers) and the literature gap-analysis note (scoping). The scripts that built the notes are kept; run them on your own copies of the papers.
The textbooks are copyright NCERT and are not redistributed. To rebuild the corpus:

1. Textbook PDFs are published at https://ncert.nic.in/textbook.php . The pre-revision and 2023-24 printings were taken from Internet Archive Wayback Machine captures of the NCERT zip files. `data/capture-index/cdx_allzips.txt` lists the captures; `logs/acquire_state.json` and `data/official-lists/retrieval-log.csv` give the capture timestamp accepted for each book and edition; `code/pairs_english.csv`, `code/corpus_pairs.csv` and `data/pairs/` give the pairing. `code/acquire.py` and `code/fetch_books.py` perform the downloads (one request per 5 s).
2. The official "List of Rationalised Content" booklets (Classes 6-12) are at https://ncert.nic.in/rationalised-content.php (June 2022 version via Wayback Machine). `code/parse_booklets.py` turns them into `data/official-lists/02-official-listed-deletions.csv`.

## Data sources and licences

| Source | Used for | Terms |
|---|---|---|
| NCERT textbooks (ncert.nic.in, archived copies) | Input text for the comparison | NCERT copyright; not included; obtain from source |
| NCERT "List of Rationalised Content" booklets | Official deletion lists | NCERT publication; only the parsed list of entries (chapter, page range, short topic headings) is included in `data/official-lists/`; the booklet PDFs are not |
| Internet Archive CDX capture index | Capture timestamps | Index of public captures; listing only |
| Literature metadata (OpenAlex, Crossref, Semantic Scholar, ERIC, arXiv) | Literature mapping in `literature/` | Used via public APIs; only derived tables and screening logs are included |

Code is MIT (`LICENSE`). The author's derived data, tables and figures are CC BY 4.0 (`LICENSE-DATA.md`); third-party source data keep their own terms.

## Not included and why

- Textbook PDFs and extracted textbook text (copyright NCERT): `data/books/` (about 1.4 GB), `results/units/`, `results/widen/units/`, `results/sensitivity/*/units/` (sentence-level files).
- Every file that holds passage or sentence text: the `*_WORKING.csv` sheets (passage classification, unlisted units, validation and label samples). Only counts derived from them are kept (`removed_words_by_*.csv`, `validation_fresh_summary.csv`, `crosscheck_summary.csv`, `tables/`). Regenerate with the scripts in `code/` once the textbooks are obtained.
- Official booklet PDFs and HTML captures, NCERT policy and press pages (third-party publications): `data/official/`, `data/meta/pages`, `data/meta/press`. Regenerate with `code/fetch_books.py` / `parse_booklets.py`.
- Full-text PDFs of third-party papers (`bibliometrics/pdfs`), their extracted text (`depth/reading-notes/_text`), raw bibliographic API dumps and cached responses (`bibliometrics/data/raw`, `depth/citations/_cache`), interactive HTML figures and bundled JS libraries. Regenerate with `literature/python/pipeline.py`.
- Environments, OCR tools and scratch (`staged-from-E`, `.pytest_cache`, venvs, Tesseract/micromamba), and intermediate rerun working copies.

## Citation

See `CITATION.cff`. Solano Paul, S. (2026). *Counting what was cut: a word-level measurement of the 2022-23 rationalisation of NCERT textbooks* (code and data). Independent researcher, Bengaluru, India. Zenodo DOI to be added.
