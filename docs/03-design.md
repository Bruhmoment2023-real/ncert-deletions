# 03 - Design

The paper measures what changed. It makes no claim about why. Every design choice below serves that.

## 1. Research questions

- **RQ1 (size).** How many words, and what share of each chapter and book, were removed between the last pre-rationalisation printing and the "Rationalised 2023-24" edition? How much was added?
- **RQ2 (shape).** How is the removed text distributed: whole chapters versus cuts inside surviving chapters; by subject, class, historical period, descriptive theme and form (body text, boxes, exercises, credits)?
- **RQ3 (the list).** How much of the measured removal falls on pages named in NCERT's "List of Rationalised Content" as first published in June 2022? How much falls only on pages added when the list was revised? How much on neither? How large are the unlisted items compared with NCERT's own description ("a sentence or a word or a phrase")?
- **RQ4 (before and after).** How much do the same books change between ordinary reprints before 2022 (baseline) and in reprints after 2023?
- **RQ5 (names).** Which named people, places, events and groups are mentioned less or more after the revision?

No hypothesis about motive is tested. If Sean wants a pre-registration, RQ1-RQ5, the codebook and the thresholds below can be posted on OSF before the full run (free; needs an account, so it is his decision).

## 2. Corpus

- Unit: one NCERT textbook, English medium, in three or four printings: an older baseline (2020-21), the last pre-rationalisation printing (2021-22 or 2022-23), "Rationalised 2023-24", and the latest reprint.
- Source: the per-book zip and per-chapter PDFs of ncert.nic.in as captured by the Wayback Machine. Each file is identified by URL, capture timestamp and sha256 (`data\meta\downloads.csv`).
- The printing is identified by the print-year stamp in the page footer, not by the capture date.
- Scope and availability per book: `02-availability.csv` and section 8.

## 3. Method

1. **Extract.** PyMuPDF text blocks per page. Remove print-year stamps, bare page numbers and running heads (short text repeated on a quarter or more of a chapter's pages). Record the printed page number, font and size of each block. Split blocks into sentence units.
2. **Normalise.** Unicode NFKC; ligatures expanded; line-end hyphens and in-word hyphens joined; lower case; runs of a phrase repeated three or more times collapsed (fake-bold artefact); tokens are letter or digit strings.
3. **Align chapters.** Each old chapter is matched to the new chapter that retains the largest share of its words. Under 30% retained in every new chapter means the chapter was dropped. This handles renumbering.
4. **Word-level test (the headline measure).** An old word is retained if it lies in at least one run of K=5 consecutive words that also occurs in the new edition. Otherwise it is removed. The chapter is treated as one word stream, so page breaks, column order and re-typesetting have no effect. The same test run from the new edition gives added words. The idea is shingle containment (Broder 1997).
5. **Sentence labels (descriptive).** kept: 90% or more of the unit's words retained in the aligned chapter. moved: 90% or more retained, but elsewhere in the book. deleted: under 50% retained. reworded: in between. Units under 5 words are matched as whole strings inside the aligned chapter only.
6. **Second pass for damaged text layers.** Units still unmatched are compared, letters only, with unmatched units of the aligned chapter (rapidfuzz). Similarity 88 or more: same sentence. 60 to 87: reworded pair.
7. **Official list.** Each removed word carries the printed page of the old edition. It is "listed" if that page appears for that book in the June 2022 booklet, "listed later" if only in the revised booklet, otherwise "unlisted". The test is deliberately generous to the list: anything removed on a listed page counts as listed.
8. **Outputs.** Per chapter: old words, removed words, share removed, added words, dropped or not. Per book: totals, split between dropped and surviving chapters.

Fixed in advance: K=5; thresholds 0.90, 0.50, 0.30; fuzzy 88 and 60; minimum unit length for sampling 5 words. Reported as sensitivity: K=4 and K=8; fuzzy pass off.

Why not an ordinary diff: line and sequence diffs (Myers 1986) assume the same order and line breaks. The 2023 books were re-typeset and re-paginated, so an order-sensitive diff flags moved lines as changes.

## 4. Categorisation and the codebook

The codebook is `code\codebook.json` (version 0.1, written before any passage was categorised) with `code\chapter_periods.csv`.

- **Unit:** a passage = removed units in one text block.
- **Three descriptive dimensions:**
  - Period (12 values): prehistory and Harappan; early India to 600 CE; 600-1200; 1200-1750; 1750-1946; 1947-1951; 1952-1974; 1975-1977; 1978-1990; 1991 onward; world outside South Asia; none.
  - Theme (12 values plus unclassified): religion and communal relations; caste and social hierarchy; gender; state, politics and institutions; rulers, courts and empire; colonial rule; nationalism and the freedom movement; movements and protest; economy and development; international relations and war; art, culture and knowledge; science and environment.
  - Form: exercise or question; credit or reference; heading or label; body or box text.
- **Rules:** written definitions, an include example and an exclude example per theme, and a keyword list. Theme = the theme with most distinct keyword hits; ties by fixed order; all hits also stored as multi-labels. Period = keyword, else median year mentioned, else the period of the chapter from a hand-made chapter table keyed to the chapter's printed title.
- **Category names are descriptive.** No category is called "sensitive", "controversial" or "political". Period boundaries are calendar dates.
- **Who decides the truth:** two human coders (Sean and one other person, for example a teacher) label a random sample of 150-200 passages without seeing the rule output. Report raw agreement and Cohen's kappa for human-human, and for rules against each human. Target kappa 0.7; below that, report the dimension as indicative only or merge categories.
- **Pilot result (AI agent as the single labeller, 60 passages):** theme kappa 0.62; period kappa 0.35 from passage rules alone, 0.61 with the chapter table. So period should be coded at chapter and section level, and theme rules need revision. Any revision is a new codebook version; both versions get reported.
- **Optional third coder:** a small open model on CPU (`code\classify_llm.py`, temperature 0, codebook definitions in the prompt). Not run. It is scored against the human labels like the rules and is never the ground truth.
- **Most robust presentation:** lead with chapter-level facts (which chapter titles lost what share), then section headings, and only then keyword themes with their kappa beside them.

## 5. Entity count

- Names come from spaCy `en_core_web_sm` run over both editions; each name is then counted by exact whole-word search in the old and the new text. The counts do not depend on the diff and can be checked with Ctrl+F.
- To do before use: an alias table made by hand (Gandhi / Gandhiji / Mahatma Gandhi); remove junk entries ("Fig", "THEME"); hand-check NER recall on 200 names because the small model is weak on South Asian names; report counts for a fixed, pre-listed set of names as well as the data-driven top changes.

## 6. Validation plan

- **Diff.** Stratified random sample by pipeline label, drawn by `make_validation_sample.py` with a recorded seed. A person opens both PDFs at the printed page and records kept / reworded / moved / deleted. Report the error rate per stratum with a confidence interval. Sample size for the full study: 100 deleted, 100 kept, all reworded and moved up to 100, across all books.
- **Pilot status.** Done once by the AI agent from text evidence: 0 of 50 deleted wrong, 0 of 20 kept wrong, 7 of 20 reworded wrong, 3 of 3 moved wrong. This does not count as hand validation.
- **Independent matcher.** `crosscheck.py`: of 1,500 kept units none was absent from the new book; of 1,524 deleted units none was present verbatim.
- **Placebo.** History Part I, officially "No Changes": measured 0 words removed. Reprint-to-reprint baseline: 125 words in one book.
- **String checks.** Named phrases counted directly in both editions (for example "PRI" 6 -> 0).
- **Extraction audit.** Per file: words per page, pages under 40 words, print stamp. Pages under 40 words are inspected (picture pages versus missing text layer).

## 7. Threats to validity, and the answer to each

| Threat | Effect | Answer |
|---|---|---|
| Wrong baseline printing | Earlier reprint changes get counted as rationalisation | Stamp-verified printing; baseline comparison between ordinary reprints; multiple baselines where captures exist |
| PDF on the website differs from the printed book | Measures the PDF, not the paper book | Say so; the PDFs are NCERT's own published files; spot-check a few pages against a printed copy from school |
| Wayback capture is incomplete or truncated | Missing chapters look like deletions | sha256 and file counts; chapter count checked against the contents page; truncated captures (exactly 1,048,576 bytes) rejected |
| Missing or damaged text layer | False removals or false additions | Low-text page audit; fuzzy pass; OCR only as a last resort and then chapter-level results only |
| Images, cartoons, maps, captions inside images | Invisible to the method | Stated limit; optional image inventory per page as later work |
| Short phrases recurring by chance | Removal undercounted (dropped chapters show 93-98%, not 100%) | Report K=4 and K=8; for dropped chapters also report the chapter's full word count |
| "Reworded" and "moved" labels unreliable | Mislabelled units | Headline numbers use words and deleted/kept only; reworded and moved are read by hand |
| Words are not importance | A short sentence can matter more than a long box | Report counts and also list every unlisted passage; make no claim about importance |
| Keyword categories are crude | Bias could enter | Pre-written codebook, blind human labels, kappa reported, chapter-level results first |
| One coder | Coder bias | Two human coders; disagreement table published |
| English medium only | Hindi and Urdu editions may differ | State scope; Hindi pilot listed as later work |
| Page-level list test is generous | Understates unlisted change | Stated; unlisted passages are also read and listed individually |
| Additions ignored | One-sided picture | Added words reported next to removed words everywhere |
| Classes 6-8 now have wholly new books | Current files are not comparable | Use the 2023-24 captures; treat the new-series books as out of scope |

## 8. Scope of the full study

`02-availability.csv` lists 56 books. Every one has at least one pre-2022 or 2022 capture and at least one later capture in the Wayback zip index. Print stamps are verified for 8 books only.

| Tier | Books | Why | Download | Status |
|---|---|---|---|---|
| 1 (pilot, done) | Class 12 History I-III, Political Science I-II | Most discussed | 420 MB | Diffed, three printings each |
| 2 | Class 6-12 History and Political Science (about 18 more books), Class 11-12 Sociology (4) | Completes the social-science story reported by the press | about 1.0-1.2 GB | Retrievable; stamps unchecked |
| 3 | Class 9-10 Science (2), Class 11-12 Biology and Chemistry (6) | Evolution, periodic table | about 0.9 GB (Class 12 Biology alone is 180 MB) | Class 10 Science diffed |
| 4 | Geography (8), Economics (5) | Controls: subjects with little public dispute | about 0.5 GB | Retrievable |
| 5 (optional) | Class 12 History and Political Science, Hindi medium | Cross-language check | about 0.25 GB | Text layer not checked; likely needs OCR |

- Known gaps: the zip index shows no 2023-24 capture for four books (Class 10 Economics, Class 11 Understanding Society, Class 11 Biology, Class 12 Macroeconomics); use the 2024 or 2025 captures and note the reprint year, or look for per-chapter captures.
- The August 2022 captures of at least two books have no usable text layer. Prefer 2020 or 2021 captures and check the stamp.
- Run time: about 5 s per book for the diff. The cost is download time and hand validation, not computing.
- Recommended paper scope: tiers 1-3 (about 35 books), with tier 4 as a comparison group if time allows.

## 9. What may be released

See `02-official-record.md` section 7. In short: code, counts, hashes and URLs yes; textbook text and PDFs no; short quotations with page references only.

## 10. What a referee or a hostile reader would attack

| Attack | From | Answer in the design |
|---|---|---|
| "Counting words says nothing about intent." | Referee | Agreed, and the paper says so in its first paragraph. It answers a different question: how much, where, and how the list compares with the books. |
| "This is not new; the Indian Express did it." | Referee | The press established the deletions and quoted passages. No word counts, shares, list audit, reprint baseline or public code were found. The contribution statement is limited to that. |
| "You chose the sensitive books to make the cuts look political." | Reader defending the revision | Tier 4 control subjects and science are in scope; History Part I with zero change is reported; all books in scope are reported, not a selection. |
| "Deletions were load reduction; you ignore the stated criteria." | Reader defending the revision | NCERT's reasons are quoted in full. The paper reports that 97.6% of removed words in the pilot are on listed pages and that most removal is whole chapters. Whether a cut meets a criterion such as "overlap with another class" is not judged here; it is named as a testable follow-up (does the same content appear in the other class's book?). |
| "You hide the unlisted deletions inside a 97.6% figure." | Reader critical of the revision | Every unlisted passage of the pilot is listed individually with page and size, including those added to the list a year later. The page-level test is stated to favour the list. |
| "The categories are your politics." | Either side | Codebook written first, descriptive names, two blind human coders, kappa published, chapter-title results given first. |
| "Your baseline is wrong: that change was made years ago." | NCERT's own argument in the Azad note | Print-stamp verification and the reprint baseline address exactly this. |
| "PDF text extraction is unreliable." | Referee | Extraction audit, validation sample with error rates, independent matcher, synthetic unit tests, known failures reported (text-less PDFs, decorative fonts). |
| "Additions matter as much as deletions." | Referee | Additions are measured the same way and reported (2023: few; 2024-26 reprints: about as many words added as removed in one chapter). |
| "English only." | Referee | Scope stated; Hindi listed as later work. |
| "You redistribute copyrighted books." | NCERT | Nothing but counts, code, hashes and short quotations is released. |
| "Selective quotation." | Either side | Quotations are chosen by rule (for example the five largest unlisted passages), not by interest. |
