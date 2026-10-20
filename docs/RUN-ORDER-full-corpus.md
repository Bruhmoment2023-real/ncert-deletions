# NCERT deletions: full-corpus run (56 books)

Measures how many words each NCERT textbook lost between its last pre-rationalisation printing and the "Rationalised 2023-24" printing, using the pilot pack's pipeline unchanged (`ncertdiff.py`, `run_diff.py`, `make_validation_sample.py`, `crosscheck.py`, `classify_rules.py`). Results: `RESULTS-SUMMARY.md`; tables in `tables\`, figures in `figures\`, per-book and chapter results in `results\`, every download attempt in `retrieval-log.csv`.

**The textbooks are copyrighted by NCERT. The PDFs in `data\books\` (on E:, see STAGING.md) and the sentence files in `results\units\`, `results\*_WORKING.csv` and `results\validation_fresh*_WORKING.csv` are for analysis only. Do not redistribute them. What may be released: code, count tables, figures, sha256 hashes, capture URLs and timestamps, short quotations with page references.**

## Software (all inside the pack; no admin, no accounts, no spend)
- Python: the pack's venv `..\venv` (Python 3.12.10, PyMuPDF 1.28.2, rapidfuzz, pandas, matplotlib, pytest). Run every script as `..\venv\Scripts\python -X utf8 -I code\<script>.py` from this folder.
- OCR: Tesseract 5.5 (conda-forge build) installed with micromamba into `tools\tess` (no admin); `tools\tessdata` holds `eng` and `hin` (tessdata_fast) plus `configs\`. To rebuild: download micromamba, `MAMBA_ROOT_PREFIX=<dir> micromamba create -p tools\tess -c conda-forge tesseract poppler`; fetch `eng.traineddata`, `hin.traineddata` from github.com/tesseract-ocr/tessdata_fast and copy `Library\share\tessdata\configs` next to them.
- `data\books` is a junction to `E:\Research-Staging\07-ncert-deletions\full-corpus-books`; `code\ocr_pdf.py` and `code\ocr_quality.py` use `E:\Research-Staging\07-ncert-deletions\ocr-tmp` as scratch.

## Order to rerun
| Step | Command | Notes |
|---|---|---|
| 1 | `code\acquire.py` | Wayback captures (exact timestamps in `data\meta\cdx_allzips.txt`), one request per 5 s, resumes after interruption; checks size, zip, print-year stamp, text layer; writes `retrieval-log.csv`, `logs\acquire_state.json`. ~4 h |
| 2 | `code\prep_special.py` | copies the pilot's 2021-22 chapter files for leps2 (sha256 checked) |
| 3 | `code\fetch_alt.py <book> <ts> old_alt` | the seven books whose 2022-23 scan had no text layer: jess3 20200517154230, jess4 20200517045511, kehs1 20200615215721, hess3 20210814170507, gess1 20210813011729, gess3 20200508031850, iess4 20210814004017 |
| 4 | `code\ocr_pdf.py data\books\old\<book> data\books\old_ocr\<book> --lang eng` | gess1 gess3 iess4 jess4 jess3 hess3 kehs1; ~10-25 s per page |
| 5 | `code\make_pairs.py` | builds `code\corpus_pairs.csv` from `logs\pair_labels.csv` (which old edition is primary) |
| 6 | `code\run_corpus.py code\corpus_pairs.csv` | the pack's `run_diff.py`, one book at a time, below-normal priority advised; ~10 s per book. Alternatives: `code\alt_textlayer_pairs.csv`, `code\alt_ocr_pairs.csv` |
| 7 | `code\qa_pairs.py` | flags incomplete old text and zero-change books |
| 8 | `code\compare_official2.py code\corpus_pairs.csv` | listed vs unlisted (needs `02-official-listed-deletions.csv`, copied from the pack) |
| 9 | `code\make_validation_sample.py code\pairs_english.csv 20261017 validation_fresh_WORKING.csv`, then `code\adjudicate_validation.py` | fresh sample (seed 20261017); adjudication recorded in code |
| 10 | `code\crosscheck.py code\corpus_pairs.csv 300 1`; `code\classify_rules.py code\corpus_pairs.csv --sample 60 --seed 3` | independent matcher; keyword codebook |
| 11 | `code\run_diff.py code\corpus_pairs.csv --k 4 --out results\sensitivity\k4` (also `--k 8`, `--no-fuzzy --out results\sensitivity\nofuzzy`) | sensitivity |
| 12 | `code\ocr_quality.py 8 11` | OCR control sample, `results\ocr_quality.csv` |
| 13 | `code\aggregate.py`, `code\aggregate_sens.py`, `code\aggregate_extra.py` | all tables and figures |
| - | `-m pytest code\tests -q` | 11 tests pass |

## What was added to the pack's code (new files only; the pack's own scripts are unmodified copies)
`acquire.py`, `fetch_alt.py`, `prep_special.py`, `ocr_pdf.py`, `ocr_quality.py`, `make_pairs.py`, `run_corpus.py`, `page_anchor.py`, `compare_official2.py`, `qa_pairs.py`, `adjudicate_validation.py`, `aggregate*.py`, `official_codes.csv`.

## Known limits
- The pack's STAMP_RE misses the stamp form "Rationalised-2023-24" (hyphen), used in some books. Removed-word counts are unaffected; added-word counts include 3 stamp words per page for those books, which `aggregate.py` subtracts (`added_words_adj`).
- For NCERT file sets that split a book by unit rather than chapter (e.g. kegy1), "chapter files dropped" counts files.
- File-code titles in `02-availability.csv` were wrong for kegy1/kegy2 (swapped) and are corrected from the title pages (`code\make_pairs.py`).
