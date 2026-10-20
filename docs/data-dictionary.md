# Data dictionary: 07-ncert-deletions - bibliometrics files

Generated 2026-10-17 by `_tools/depth-kit/appendix.py`. All files below were built from free databases (OpenAlex, Crossref, Semantic Scholar, ERIC, arXiv, OpenCitations) on the dates in `data/raw/query_log.csv`; access date = pull date unless a row says otherwise.

## Files

| Path (under `bibliometrics\`) | What it is | Rows | Columns | Known problems |
|---|---|---|---|---|
| `config.json` | every setting of the run: queries, inclusion/exclusion rules, seeds, manual_exclude (hand-screen exclusions with reasons), evidence relation text | 17 | JSON |  |
| `evidence-table.csv` | the 30-60 most relevant papers with study type, data, method, one-line finding, read status, relation to the paper | 51 | 19 | Findings from abstracts unless read_status says full text; hand-screened and patched after the automatic selection. |
| `data/api_log.json` | log of API calls, cache hits and errors | 35 | JSON | Contains no personal identifier. |
| `data/clean/bibliometrix_M.rds` | bibliometrix data frame (M) as saved R object |  | R data frame |  |
| `data/clean/bibliometrix_input.csv` | master table reshaped to Web of Science field tags for bibliometrix | 706 | 29 | CR (cited references) built from OpenAlex referenced_works labels; only references resolved within the cap are labelled. |
| `data/clean/citation_edges.csv` | direct citation links between corpus records (citing, cited: OpenAlex ids) | 226 | 2 | Only links where OpenAlex has the reference list. |
| `data/clean/cited_references.csv` | works cited by corpus records, with how often and how many are in the corpus | 4628 | 10 | Capped number of references resolved to metadata (see refs_stats.json). |
| `data/clean/corpus_final.jsonl.gz` | corpus after one snowball round, raw OpenAlex JSON per line | 774 | JSON per line | Written BEFORE hand-screen exclusions: master.csv has fewer rows (the exclusions in config.json manual_exclude are applied in the master stage). |
| `data/clean/corpus_stage1.jsonl.gz` | OpenAlex records that passed the title pre-screen and the topical screen (before snowballing) | 752 | JSON per line | Raw OpenAlex JSON per line. |
| `data/clean/evidence-table.autogen.csv` | the automatic evidence table before hand-screening (kept for comparison) | 54 | 18 |  |
| `data/clean/evidence_candidates.json` | ranked candidates for the evidence table | 70 | JSON |  |
| `data/clean/evidence_notes.json` | per-paper evidence-table fields (study type, method, finding from abstract, relation) | 54 | JSON | Findings come from abstracts only. |
| `data/clean/handscreen_exclusions.json` | OpenAlex ids excluded by hand-screen, with reason | 68 | JSON |  |
| `data/clean/master.csv` | one row per corpus record: the cleaned master table | 706 | 49 | Abstracts missing for part of the records; keywords are OpenAlex machine-assigned. |
| `data/clean/master.rds` | master.csv as an R data frame |  | R data frame |  |
| `data/clean/prisma_search.json` | PRISMA-style counts for the search stage | 10 | JSON |  |
| `data/clean/prisma_snowball.json` | PRISMA-style counts for the snowball stage | 11 | JSON |  |
| `data/clean/refs_stats.json` | counts of cited references and how many were resolved | 6 | JSON |  |
| `data/clean/screening_log_search.csv` | decision and reason for every candidate screened in the search stage | 2060 | 8 |  |
| `data/clean/screening_log_snowball.csv` | decision and reason for every candidate screened in the snowball stage | 603 | 7 |  |
| `data/clean/snowball_central_papers.csv` | the most central corpus papers whose references and citations were snowballed | 25 | 6 |  |
| `data/clean/unresolved_candidates.csv` | search hits with no OpenAlex match (no DOI or not indexed) | 174 | 7 | These are lost to the map; check by hand if important. |
| `data/raw/all_hits.csv` | every hit returned by the discovery queries (Crossref, Semantic Scholar, ERIC, arXiv, seeds), before de-duplication | 10629 | 16 | Hits include off-topic records; duplicates across databases. |
| `data/raw/prior_work_ids.json` | OpenAlex ids/titles of papers named in the pack's prior-work notes, used as seeds | 3 | JSON | Titles that could not be matched are listed in run_search.log. |
| `data/raw/query_log.csv` | one row per query: database, search string, hits retrieved, date | 48 | 8 | Totals reported by Crossref are for the whole index, not for the topic. |
| `data/raw/arxiv/` | raw API responses, 2 files, 0.1 MB (one file per query page; cached in `_tools/biblio-cache`) | | | Response formats differ by database; OpenAlex rate-limits. |
| `data/raw/crossref/` | raw API responses, 18 files, 3.5 MB (one file per query page; cached in `_tools/biblio-cache`) | | | Response formats differ by database; OpenAlex rate-limits. |
| `data/raw/eric/` | raw API responses, 5 files, 0.5 MB (one file per query page; cached in `_tools/biblio-cache`) | | | Response formats differ by database; OpenAlex rate-limits. |
| `data/raw/openalex/` | raw API responses, 3 files, 6.4 MB (one file per query page; cached in `_tools/biblio-cache`) | | | Response formats differ by database; OpenAlex rate-limits. |
| `data/raw/s2/` | raw API responses, 12 files, 11.9 MB (one file per query page; cached in `_tools/biblio-cache`) | | | Response formats differ by database; OpenAlex rate-limits. |
| `tables/` | 63 CSV tables: the numbers behind every figure (`R_*` from bibliometrix, `py_*` from Python) | | | see `figures/captions.md` for each caution |

## Variables

### master.csv

| Variable | Meaning and units |
|---|---|
| oa_id | OpenAlex work id (W...) |
| doi | DOI without URL prefix |
| title / year / date / type / language | bibliographic basics (OpenAlex) |
| source / source_type / publisher / issn | journal or venue and its type |
| authors / n_authors / first_author | author names, ';'-separated |
| institutions / countries / first_author_country / corresponding_country / international_collab | affiliations and ISO-2 country codes; international_collab = more than one country |
| cited_by_count / fwci / local_citations / n_refs | OpenAlex citations at pull date; field-weighted citation impact; citations from other corpus records; length of reference list |
| is_oa / oa_status / oa_url / best_pdf_url / all_pdf_urls / best_oa_landing | open-access status and links (OpenAlex) |
| sublit / sublits_all / origin / found_in / relevance | which sub-literature the record was found for; how it entered (search, snowball, seed); databases that returned it; relevance score used to rank evidence |
| primary_topic / subfield / field / domain / keywords / topics / concepts | OpenAlex classification (machine-assigned) |
| abstract / has_abstract | abstract text rebuilt from OpenAlex inverted index; flag |
| is_retracted | OpenAlex retraction flag |
| sr | short reference label used in bibliometrix |
| crossref_cited_by / crossref_n_refs / s2_citation_count / s2_pdf_url | cross-checks from Crossref and Semantic Scholar |

### evidence-table.csv

| Variable | Meaning and units |
|---|---|
| rank, citation, year, doi_or_link, open_access_link, oa_status, pdf_in_folder | identification and access |
| sub_literature, study_type, country_or_setting, data, method | coding by the agent from title and abstract |
| main_finding_from_abstract, read_status | one line from the abstract; 'abstract read' or 'metadata only' (no record was read in full unless marked) |
| relation_to_seans_paper | agent's judgement |
| local_citations, global_citations_openalex, openalex_id | citation counts at pull date |

### citation_edges.csv

| Variable | Meaning and units |
|---|---|
| citing, cited | OpenAlex ids; edge = citing record lists cited record in its references |

### tables/R_*.csv, tables/py_*.csv

| Variable | Meaning and units |
|---|---|
| (varies) | each table holds the numbers behind the figure of the same name; see figures/captions.md |

Counts (citations, records) have no unit beyond 'number of'; years are calendar years; `fwci` is a ratio (1 = world average for field, year and type).


---

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
