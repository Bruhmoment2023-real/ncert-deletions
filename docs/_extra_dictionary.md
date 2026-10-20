# Paper-specific data (outside `bibliometrics\`)

Meanings are taken from `code\README.md`, `results\RESULTS-SUMMARY.md` and the column names; the code in `code\` is the authority. A "word" is a word of extracted text (body text, boxes, captions, exercises, credits; running heads and page numbers removed). A word of the old edition is "retained" if it sits inside at least one run of 5 consecutive words (K = 5) that also occurs in the new edition (first in the aligned chapter, then anywhere in the book); otherwise "removed". Sampling or reading here was done by an AI agent, not by a person; Sean must repeat the validation by hand before any error rate is reported.

## Raw inputs (copyrighted or third-party; analysis only, do not redistribute)

| Path | Source and access date | Size | Content and problems |
|---|---|---|---|
| `data\books\{old,old2122,new,rat2023,latest}\<book>\*.pdf` | NCERT textbook chapter PDFs, retrieved from Wayback Machine captures of ncert.nic.in zips (one request per 5 s) on 2026-10-13 (`code\fetch_books.py`, hashes in `data\meta\downloads.csv`) | 1.3 GB | Edition folders: `old` (last printing before rationalisation), `old2122` (2021-22 baseline for one book), `rat2023`/`new` ("Rationalised 2023-24"), `latest` (reprint 2026-27). Scanned or low-text-layer PDFs extract poorly; decorative quotation fonts lose letters (see README "Known weak points"). Copyrighted. |
| `data\official\Booklet<Class>_{wayback202206,live20261013}.pdf` | NCERT "List of Rationalised Content" booklets by class: the June 2022 version via Wayback and the live version fetched 2026-10-13 | 85 MB | Three of the live booklets (Classes 9, 10, 12) were revised after June 2022, with dates inside the PDFs. |
| `data\meta\downloads.csv` | download log: book, edition label, requested timestamp, final URL, bytes, sha256, number of files | 31 rows x 7 | Needed to re-fetch the same captures. |
| `full-corpus\` (outside this analysis) | another agent's wider corpus | not described here | Not part of this appendix; do not write there. |

## Derived results (`results\`)

| File | Rows x columns (checked 2026-10-17) | Variables |
|---|---|---|
| `book_summary.csv` | 11 x 15 | book, title, old_edition, new_edition, old_chapters, new_chapters, chapters_dropped, old_words, new_words, removed_words, share_removed (fraction of old words removed), removed_words_in_dropped_chapters, removed_words_in_surviving_chapters, added_words |
| `chapter_summary.csv` | 80 x 20 | per old chapter: book, title, editions, old_chapter_file, front_or_back_matter, aligned_new_chapter_file, best_candidate, share_retained_in_best_candidate, chapter_dropped, old_words, removed_words, share_removed, moved_words |
| `official_vs_measured.csv` | 5 x 9 | book, official_code, title, removed_words_total, on_pages_listed_2022, on_pages_listed_only_in_revised_booklet, on_unlisted_pages, no_page_number, share_unlisted_vs_2022_list: measured removals against NCERT's own list at page level |
| `unlisted_units_WORKING.csv` | 215 x 8 | removed units not on the June 2022 list: book, list_status, chapter, printed_page, label, n_words, removed_words, text. WORKING file: read by the AI agent, not hand-verified. |
| `extraction_meta.csv` | 112 x 11 | per chapter file: edition, pages, words, units, print_stamps (printing year stamps), page_offset, low_text_pages, pdf_creation, pdf_mod |
| `crosscheck_summary.csv`, `validation_summary.csv`, `validation_round1_dev_WORKING.csv`, `validation_round2_WORKING.csv` | 4 x 5, 10 x 8, 93 x 19, 93 x 19 | validation of the diff against an independent fuzzy-match score; error rate per stratum. Agent-made, not human-checked. |
| `passages_classified_WORKING.csv`, `removed_words_by_{theme,period,form}.csv`, `category_label_sample_WORKING.csv`, `category_agreement_agent.csv` | 1,683 x 12; 43, 30, 16 rows; 60 x 11; 47 x 6 | rule-based categorisation of removed passages by theme, period and form, with an agent second coder and Cohen's kappa. Needs two human coders before any theme number is published. |
| `entity_mentions.csv` | 1,449 x 7 | book, entity, ner_label_most_common, mentions_old, mentions_new, change, share_removed (spaCy named entities, before and after) |
| `units\*.csv`, `sensitivity\`, `widen\` | per book; K = 4, K = 8 and no-fuzzy variants; a widening test | the unit-level labels (kept, deleted, reworded, moved) behind the tables. Reworded and moved labels are unreliable (about half of sampled "reworded" units were not confirmed). |
| `fig1_*.png`, `fig2_*.png` | 2 PNG | share removed by chapter; listed versus unlisted removals |
| `02-official-listed-deletions.csv` (paper root) | 3,853 x 10 | the official booklets as rows: class, booklet_version, booklet_pdf_page, book_code, book_title, chapter, pages_raw, dropped_raw, full_chapter, page_list |
| `02-availability.csv` (paper root) | 56 x 16 | which NCERT books have Wayback captures in which periods |

## Known problems
- Pilot scope: five Class 12 books (English) plus Class 10 Science; widening is another agent's task in `full-corpus\`.
- Extraction is from PDF text layers; scanned editions need OCR (`code\ocr_fallback.py`, tested on 3 pages only, not wired in).
- All validation so far is by the AI agent. No person has compared the PDFs.
- The tone of the study is measurement only; no theme or intent claims are made in the tables.
