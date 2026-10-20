# ncert-diff: pipeline

Measures what text changed between two editions of an NCERT textbook. Free software only, CPU only, no accounts.

## Set-up (Windows, everything on D:)

```
cd D:\Research-Publishing\07-ncert-deletions
python -m venv venv
venv\Scripts\python -m pip install --cache-dir D:\Research-Publishing\.pip-cache pymupdf rapidfuzz pandas matplotlib pytest
# optional: entity counts and OCR
venv\Scripts\python -m pip install --cache-dir D:\Research-Publishing\.pip-cache spacy rapidocr-onnxruntime
venv\Scripts\python -m pip install --cache-dir D:\Research-Publishing\.pip-cache https://github.com/explosion/spacy-models/releases/download/en_core_web_sm-3.8.0/en_core_web_sm-3.8.0-py3-none-any.whl
```

Versions used on 2026-10-13: Python 3.12.10, PyMuPDF 1.28.2, spaCy 3.8.16 with en_core_web_sm 3.8.0. Pin the rest with `venv\Scripts\python -m pip freeze > code\requirements-lock.txt` before any results are published.

## Order of running (pilot)

| Step | Command (prefix each with `venv\Scripts\python -X utf8`) | Time here | Writes |
|---|---|---|---|
| 1 | `code\fetch_books.py code\pilot_manifest.csv` | ~10 min, 420 MB | `data\books\<edition>\<book>\*.pdf`, hashes in `data\meta\downloads.csv` |
| 2 | `code\parse_booklets.py` | 20 s | `02-official-listed-deletions.csv` |
| 3 | `code\run_diff.py code\pilot_pairs.csv` | 25 s | `results\units\*.csv`, `chapter_summary.csv`, `book_summary.csv`, `extraction_meta.csv` |
| 4 | `code\compare_official.py code\pilot_pairs.csv` | 2 s | `results\official_vs_measured.csv`, `unlisted_units_WORKING.csv` |
| 5 | `code\make_validation_sample.py code\pilot_pairs.csv <seed> <outfile>` | 10 s | sample sheet for hand checking |
| 6 | `code\crosscheck.py code\pilot_pairs.csv 300 1` | 25 s | `results\crosscheck_summary.csv` |
| 7 | `code\classify_rules.py code\pilot_pairs.csv [--sample 60 --seed 3]` | 5 s | category tables; blind label sheet |
| 8 | `code\agreement.py hand` (or `agent`) | 1 s | `results\category_agreement_<who>.csv` |
| 9 | `code\entity_counts.py code\pilot_pairs.csv 3` | **7 min** | `results\entity_mentions.csv` |
| 10 | `code\make_figures.py` | 5 s | two PNG figures |
| - | `-m pytest code\tests -q` | 1 s | 11 tests on synthetic text |

Sensitivity: `code\run_diff.py code\pilot_pairs.csv --k 4 --out results\sensitivity\k4` (also `--k 8`, `--no-fuzzy`).
Widening test: `code\fetch_books.py code\widen_manifest.csv` then `code\run_diff.py code\widen_pairs.csv --out results\widen`.

Note: `fetch_books.py` takes whole-book zips. The 2021-22 baseline of `leps2` was fetched chapter by chapter with curl (the URLs and sha256 values are the `old2122` rows of `data\meta\downloads.csv`); `data\books\old2122\leps2\leps2ps.pdf` is a copy of the 2020-21 prelims.

## Files

- `ncertdiff.py` - extraction, tokenising, K-gram retained/removed test, chapter alignment, labels, fuzzy second pass.
- `run_diff.py` - runs pairs of editions, writes tables.
- `parse_booklets.py` - NCERT "List of Rationalised Content" PDFs to CSV (uses the ruling lines of the tables).
- `compare_official.py` - page-level comparison of measured removals with the official list (both versions of the list).
- `make_validation_sample.py`, `crosscheck.py` - validation.
- `codebook.json`, `chapter_periods.csv`, `classify_rules.py`, `agreement.py` - categorisation.
- `classify_llm.py` - optional local-model second coder. **Written, not run.**
- `entity_counts.py` - before/after mention counts of names.
- `ocr_fallback.py` - OCR for PDFs without a text layer (RapidOCR, ~14 s per page). Tested on 3 pages only; the side-car files are **not yet read** by `ncertdiff.py`.
- `fetch_books.py` - polite sequential Wayback downloader (one request per 5 s).

## How a word is judged "removed"

A word in the old edition is retained if it sits inside at least one run of 5 consecutive words that also occurs in the new edition (first in the aligned chapter, then anywhere in the book). Otherwise it is removed. Chapter text is treated as one stream, so page breaks, columns and re-typesetting do not matter. Sentence labels: kept (90% or more of its words retained in the aligned chapter), moved (90% or more retained, but elsewhere in the book), deleted (under 50% retained), reworded (in between). Thresholds are constants at the top of `ncertdiff.py`.

## Known weak points (measured, see `results\RESULTS-SUMMARY.md`)

- "reworded" and "moved" labels are unreliable (about half of sampled "reworded" units were not confirmed). Use word counts and the deleted/kept labels; treat reworded/moved as a queue for reading.
- Text set in the decorative quotation font extracts with letters missing; the fuzzy pass repairs most of it.
- Tables typeset as "fake bold" repeat every word 3-5 times; collapsed by a regular expression, a few fragments survive.
- Pictures, cartoons and maps are invisible to a text diff.
- Some 2022-23 PDFs have no text layer at all (found: `jess4`, parts of `kehs1`).
- `WORKING` files and everything under `results\units\` contain textbook sentences. Do not publish them.
