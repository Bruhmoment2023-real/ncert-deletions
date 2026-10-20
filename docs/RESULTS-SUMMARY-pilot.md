# Pilot results (13 Oct 2026)

All numbers come from `results\*.csv` and can be regenerated with the commands in `code\README.md`. Word counts are words of extracted text (body text, boxes, captions, exercises, credits), with running heads, page numbers and print-year stamps removed. Front matter is excluded.

**Who checked what:** every "validation" figure below was produced by the AI agent reading text evidence, not by a person comparing the PDFs. Sean must repeat the check by hand before any error rate is reported in a paper.

## 1. How much text was removed (last pre-rationalisation printing -> "Rationalised 2023-24")

| Book (Class 12, English) | Old printing | Old words | New words | Words removed | Share | Chapters dropped | Removed in dropped chapters | Removed in surviving chapters |
|---|---|---|---|---|---|---|---|---|
| Themes in Indian History I | 2021-22 | 35,580 | 35,580 | 0 | 0.0% | 0 of 4 | 0 | 0 |
| Themes in Indian History II | 2021-22 | 47,144 | 36,865 | 10,163 | 21.6% | 1 of 5 | 10,163 | 0 |
| Themes in Indian History III | 2021-22 | 62,600 | 42,592 | 19,807 | 31.6% | 2 of 6 | 19,592 | 215 |
| Contemporary World Politics | 2021-22 | 51,915 | 39,821 | 11,956 | 23.0% | 2 of 9 | 11,875 | 81 |
| Politics in India since Independence | 2021-22 (ch. 9: 2020-21) | 61,962 | 48,016 | 13,673 | 22.1% | 1 of 9 | 7,045 | 6,628 |
| **Five books** | | **259,201** | **202,874** | **55,599** | **21.5%** | 6 of 33 | 48,675 | 6,924 |

- 88% of the removed words (48,675 of 55,599) sit in six whole chapters that were dropped: History Theme 9 (Kings and Chronicles: the Mughal Courts), Theme 12 (Colonial Cities), Theme 14 (Understanding Partition); World Politics ch. 1 (The Cold War Era), ch. 3 (US Hegemony in World Politics); Politics in India ch. 7 (Rise of Popular Movements).
- Largest cuts inside surviving chapters, all in Politics in India since Independence: ch. 3 Politics of Planned Development 3,070 words (49%), ch. 6 The Crisis of Democratic Order 1,962 (25%), ch. 2 Era of One-party Dominance 890 (13%), ch. 9 Recent Developments in Indian Politics 498 (7.5%), ch. 1 Challenges of Nation Building 159 (2.2%).
- Words added in the 2023 edition are few: 79, 111, 198 and 244 in the four changed books (mostly renumbered cross-references).
- Sensitivity to the K-gram length: five-book total is 52,613 (K=4), 55,599 (K=5), 57,032 (K=8). The ranking of books and chapters does not change. A dropped chapter never reaches 100% because short phrases recur elsewhere in the book.
- Figure: `fig1_share_removed_by_chapter.png`.

## 2. Measured removals against NCERT's own list (page-level test)

| Book | Removed words | On pages in the June 2022 list | On pages added in the revised list | On pages in neither |
|---|---|---|---|---|
| History I | 0 | 0 | 0 | 0 |
| History II | 10,163 | 9,950 | 0 | 213 |
| History III | 19,807 | 19,592 | 0 | 215 |
| World Politics | 11,956 | 11,875 | 0 | 81 |
| Politics in India | 13,673 | 12,826 | 418 | 429 |

- The official list accounts for 97.6% of removed words in these five books at page level (54,243 of 55,599 against the June 2022 list).
- What is not on the June 2022 list, read passage by passage (`unlisted_units_WORKING.csv`):
  - Politics in India p. 43, box "Party competition in a Bihar village", 279 words. Added to NCERT's list in the revised booklet.
  - Politics in India p. 12, passages on reactions to Gandhi's assassination, 139 words. Added to NCERT's list in the revised booklet.
  - Politics in India p. 35, box on Mexico's Institutional Revolutionary Party, about 200 words, plus related exercise questions on p. 44 (about 100 words). In neither version of the list. String check: "PRI" occurs 6 times in the old text and 0 times in the new.
  - Politics in India p. 159, a sentence on the Anandpur Sahib Resolution shortened (21 words; "Khalistan" 1 -> 0). In neither list.
  - History III p. 366, one sentence describing Gandhi's assassin (23 words; "Brahmin from Pune" 1 -> 0, "Nathuram Godse" 1 -> 1). In neither list.
  - History II pp. 255-256 and History III p. 432: picture credits for the dropped chapters (about 330 words). In neither list; apparatus, not narrative.
  - The rest is small: cross-references to dropped chapters reworded, figure numbers renumbered, and extraction noise.
- NCERT's April 2023 statement says unlisted changes were "minor deletions (a sentence or a word or a phrase, etc.)". In this pilot the unlisted items range from one sentence to a 279-word box. That is a description of size only.
- Figure: `fig2_listed_vs_unlisted.png`.

## 3. Changes after rationalisation (2023-24 edition -> "Reprint 2026-27")

- Politics in India since Independence: 1,245 words removed, 1,268 added. Almost all in ch. 8 "Recent Developments in Indian Politics" (1,073 removed, 1,093 added), in the section on Ayodhya. String counts in the whole book: "Babri Masjid" 8 -> 0, "Ram Janmabhoomi" 0 -> 7.
- History I: 236 removed, 654 added, nearly all in Theme 1 (the Harappan civilisation: new text on chronology and recent archaeological evidence).
- History II: no change. History III: 1 removed, 213 added. World Politics: 104 removed, 66 added.
- None of these post-2023 changes is in the "List of Rationalised Content" (the list's Class 12 file was last modified on 4 Aug 2023).

## 4. Baseline drift before rationalisation (placebo comparison)

- Politics in India since Independence, 2020-21 printing -> 2021-22 printing: 125 words removed, 17 added. Removed: a box on the film *Roja* (ch. 8). Changed: "Azad Pakistan" -> "Azad Kashmir". Added: a line on Telangana.
- So textbooks change a little between ordinary reprints. A comparison that uses an older baseline would wrongly assign such changes to rationalisation. (NCERT's own note on the Maulana Azad passage makes the same point for a 2014 change.)

## 5. Validation of the diff

Development round (pipeline v1, 93 units) found the faults fixed in v2: line-per-block layouts, hyphenation, fake-bold tables, running heads, short headings matching elsewhere. Fresh sample for the final pipeline (`validation_round2_WORKING.csv`, seed 7, units of 5+ words, five books):

| Pipeline label | Units in population | Sampled | Confirmed | Not confirmed | Uncertain | Error rate |
|---|---|---|---|---|---|---|
| deleted (surviving chapters) | 395 | 40 | 40 | 0 | 0 | 0% |
| deleted (dropped chapters) | 2,738 | 10 | 10 | 0 | 0 | 0% |
| kept | 11,307 | 20 | 20 | 0 | 0 | 0% |
| reworded | 43 | 20 | 10 | 7 | 3 | 35% |
| moved | 3 | 3 | 0 | 3 | 0 | 100% |

- With 0 errors in 50 "deleted" units, the 95% upper bound on the error rate is about 6% (rule of three).
- Larger automated cross-check with a different matcher (character alignment against the whole new book, `crosscheck_summary.csv`): of 1,500 "kept" units, 1,486 present verbatim, 14 partial, 0 absent. Of 1,524 "deleted" units, 1,477 absent, 47 partial, 0 present verbatim.
- "Reworded" and "moved" are not reliable labels. They cover 46 of about 14,500 units, so they barely move the word totals, but they must be read by hand, not counted.

## 6. Categorisation (codebook v0.1, keyword rules)

- 1,683 removed passages, 55,489 removed words classified.
- By period (chapter-level fallback): Colonial 11,469; Sultanate and Mughal 10,537; world outside South Asia 10,370; Partition and founding 8,175; 1978-1990 6,162; 1952-1974 4,564; 1991 onward 2,099; Emergency 1975-77 2,023; early India 90.
- By theme (single best keyword match): international relations and war 8,715; rulers, courts and empire 8,432; state, politics and institutions 7,061; economy and development 6,150; unclassified 5,628; religion and communal relations 5,561; colonial rule 3,881; movements and protest 2,809; art and culture 2,403; gender 1,868; nationalism and freedom movement 1,602; caste 1,004; science and environment 375.
- By form: body or box text 48,192; exercises 3,599; credits and references 2,766; headings 932.
- Agreement with 60 blind labels by the AI agent: theme raw agreement 0.67, Cohen's kappa 0.62; the labelled theme was among the rule's multi-label hits in 52 of 60. Period: kappa 0.35 with passage rules alone, 0.61 once the chapter-level period table was added (a change made after seeing the first result, so it is version 0.2 and must be reported as such).
- These totals mostly restate which chapters were dropped. Theme counts at kappa 0.62 are indicative only.

## 7. Named entities (string counts, old -> new)

- History II: Mughal 168 -> 64; Akbar 87 -> 29; Abu'l Fazl 37 -> 13; Jahangir 23 -> 4; Shah Jahan 21 -> 5; Aurangzeb 18 -> 7; Babur 20 -> 9; Humayun 14 -> 3.
- History III: Partition 78 -> 7; Calcutta 68 -> 10; Bombay 80 -> 24; Madras 47 -> 11; Muslim 89 -> 25; Hindu 45 -> 11; League 57 -> 20; Pakistan 46 -> 11; Congress 97 -> 68.
- World Politics: Cold War 91 -> 35; Soviet Union 93 -> 69; Iraq 24 -> 6; NAM 16 -> 0; Cuba 11 -> 0; Clinton 9 -> 0.
- Politics in India: Dalit 28 -> 8; Gujarat 30 -> 14; Narmada 12 -> 0; BKU 12 -> 0; Chipko 9 -> 0; Naxalite 11 -> 1; Shah Commission 12 -> 3; Emergency 89 -> 61; Gandhi 117 -> 107; Nehru 67 -> 68; Congress 383 -> 376.
- Caveat: the vocabulary comes from a small NER model that misses and mislabels South Asian names; surname strings match several people; "Fig" and "THEME" show the vocabulary needs cleaning.

## 8. Widening test (one valid book, two failures)

- Class 10 Science, 2022-23 printing -> Rationalised 2023-24: 104,120 -> 79,004 words; 24,419 removed (23.5%). Three chapters dropped: ch. 5 Periodic Classification of Elements (4,606 words), ch. 14 Sources of Energy (5,481), ch. 16 Sustainable Management of Natural Resources (5,972). Inside surviving chapters: ch. 9 Heredity and Evolution 4,802 words (63%); ch. 13 Magnetic Effects of Electric Current 2,393 (32%); ch. 11 The Human Eye 754 (15%); ch. 12 Electricity 298 (4%).
- Class 10 Democratic Politics II and Class 11 Themes in World History: the 2022-23 PDFs captured in August 2022 have little or no text layer (91 of 124 pages and 20 of 265 pages under 40 words). The numbers in `results\widen\` for these two books are **not valid**. Fix: use the 2020 or 2021 captures, or OCR.
- OCR test (RapidOCR, 3 pages, 200 dpi): about 14 s per page; 90% of OCR'd words matched the 2023 text after column-aware ordering (76% without). OCR text therefore carries roughly a 10% noise floor and is fit for chapter-level results only.
