# Full-corpus results (17 Oct 2026)

Measurement only: how much text differs between each book's last pre-rationalisation printing and its "Rationalised 2023-24" printing. No claim is made about reasons. Words are words of extracted text (body, boxes, captions, exercises, credits; running heads, page numbers and print stamps removed; front matter excluded), counted by the pilot pack's pipeline unchanged (a word is "removed" if it sits in no run of 5 consecutive words found anywhere in the new edition). Every number below is a sum of `tables\*.csv`, which are sums of `results\perbook\*`; rerun steps are in `README.md`. NCERT's textbooks are copyrighted: they were kept for analysis only and must not be redistributed.

**Who checked what:** the validation figures in section 5 were produced by the AI agent that ran the job, reading text evidence. No person has checked them. The pilot's condition (Sean redoes the check by hand) still applies.

## 1. Coverage
- All 56 listed books were retrieved and paired: 51 English-medium for the headline, 5 Hindi-medium Class 12 reported apart and never added in. Every rationalised edition carries the print stamp "Rationalised 2023-24" (jess2, leec1, kebo1 from April-May 2023 captures, kesy2 from a May 2024 capture, the rest December 2023). Nothing was left unpaired. `tables\table0_pairing_and_retrieval.csv` gives capture, stamp and caveats per book; `retrieval-log.csv` has all 257 attempt records (163 accepted, 40 rejected on the stamp, 46 truncated or failed Wayback transfers (some captures appear in two runs), 7 alternative captures, 1 sha mismatch on a front-matter file).
- Baseline printing (stamp read inside the PDFs), English books: 2022-23 for 28; 2021-22 for 14 (including leps2, whose chapter files came from the pilot); 2020-21 for 9. For these 23, ordinary reprint changes since the baseline may be counted as removals (pilot: 125 words in one book). Many 2022 captures were cut short by the archive, which is why earlier printings were used (table0).
- Seven books' 2022-23 PDFs had no usable text layer (gess1, gess3, iess4, hess3, jess3, jess4, kehs1). Each was OCR'd with Tesseract (English) and also paired using an earlier text-layer printing. The text-layer pairing is the headline; the OCR pairing is the comparison (section 6).
- The live ncert.nic.in site was not used for the books: Classes 6-8 there are now new books, so the 2023-24 Wayback captures serve throughout. One live check was made (lehs1 live file size equals the December 2023 capture, 22,405,219 bytes).
- Disk: about 7.2 GB on E: (includes superseded and rejected zips and OCR copies), more than the 2-3 GB expected. See `STAGING.md`.

## 2. How much was removed (51 English-medium books)
- 622,576 of 2,848,082 words removed (21.9%); 16,311 words added (stamp text excluded). Sensitivity: K=4 gives 20.4%, K=8 22.7%, no fuzzy pass 22.3%; chapter-file counts 79 (80 at K=8).
- By class (removed / old words): 6: 25,460 / 131,421 (19.4%); 7: 39,134 / 149,921 (26.1%); 8: 40,944 / 179,946 (22.8%); 9: 28,331 / 207,340 (13.7%); 10: 40,972 / 248,892 (16.5%); 11: 196,965 / 929,752 (21.2%); 12: 250,770 / 1,000,810 (25.1%).
- By subject: Science (15 books: Science, Physics, Chemistry, Biology) 365,330 / 1,327,527 (27.5%); Social science (36 books) 257,246 / 1,520,555 (16.9%): Geography 21.3%, History 20.5%, Political Science 14.7%, Sociology 13.1%, Economics 11.4%.
- Highest shares: Class 11 Chemistry II 48.0%, Class 12 Chemistry I 46.9%, Class 12 Physics II 37.9%, Class 11 Themes in World History 33.8%, Class 7 Our Pasts II 33.0%, Class 10 Democratic Politics II 31.7%.
- Eight books show no removal (0.2% or less): iess2, iess3, iess4, jess2, jess3, keps2, kesy1, lehs1. NCERT's list says "No change" for each.
- Hindi medium (5 books): 72,583 of 361,596 words (20.1%); History Part I (lhhs1) 0, as in English. Counts are approximate: the PDFs use a legacy font encoding and the diff ran on the encoded strings.
- Tables 1-8; figures 1-2.

## 3. Whole chapters and cuts inside chapters
- 79 of 465 chapter files (17%) were dropped as whole files (Science 40 of 181; Social science 39 of 284); they hold 411,444 words, 66.1% of all removed words (Science 61.9%, Social science 72.0%). The other 211,132 removed words sit inside surviving chapters. Table 10.
- NCERT's lists carry 74 "Full Chapter" entries for these books against 79 measured dropped files; the counts are close (matching by identity was not done). For unit-based file sets (e.g. kegy1) a "chapter" is a unit file.
- Largest cuts inside surviving chapters: Class 12 Physics II ch. 6 file (10,312 words, 46%), Class 11 Physics I ch. 2 file (6,310, 47%), Class 11 Biology ch. 7 (5,247, 67.5%), Class 10 Science ch. 9 (4,802, 63%). Table 11; figure 5.

## 4. Against NCERT's own lists (page-level test, as in the pilot)
- Applies to words in surviving chapters. Class 11 uses the live booklet (internal date June 2022) because the archived copy is truncated, so "listed only in a later revision" cannot be separated there. Where the pack's detector found no printed page numbers, a contents-list anchor fills them (`page_anchor.py`); 10 books stay untestable and are shown separately (8 more have no removal inside surviving chapters).
- 33 of 51 books are testable: of 171,438 removed words in their surviving chapters, 135,221 (78.9%) sit on pages named in the lists and 36,217 (21.1%) do not. Science (10 testable books): 21.6% unlisted; Social science (23 books): 20.5%. A further 39,694 words in 10 books (fesc1, gess2, gess3, gesc1, iess4, iesc1, keps2, legy2, lech1, leph1) could not be placed on a page. The test is generous to the lists (anything removed on a listed page counts as listed). Table 9; figure 3.
- Unlisted removals appear in both groups; the largest single pages hold about 450-550 words (table 15: pages only, no text). Passage-by-passage reading of unlisted items, done for the pilot, was not repeated.
- Pilot comparison: lehs1 (0), lehs2 (10,163), lehs3 (19,807) and leps2 (13,673) equal the pilot's figures; leps1 is 11,940 against the pilot's 11,956 because the baseline capture differs.

## 5. Validation (fresh random sample, seed 20261017, English books only, 100 units; AI-adjudicated, not by a person)
- Deleted in surviving chapters (40): 38 confirmed, 0 not confirmed, 2 uncertain. Deleted in dropped chapters (10): 10 confirmed. Kept (20): 20 confirmed. Moved (10): 10 confirmed (verbatim text found elsewhere, mostly glossary boxes). Reworded (20): 6 confirmed, 6 not confirmed (sentence actually absent), 8 uncertain (equation fragments whose formatting differs).
- With 0 errors in 70 "deleted" units the 95% upper bound is about 4%. "Reworded" is again unreliable: do not count it; the word totals do not depend on it.
- Automated cross-check with a different matcher, all 56 books: "kept" 16,512 present verbatim, 288 partial, 0 absent; "deleted" 14,322 absent, 1,026 partial, 1 present verbatim; "reworded" 112 / 588 / 142; "moved" 467 / 30 / 0 (present / partial / absent).
- Not done: human hand validation; two-coder labelling. Hindi books were not in the read sample.

## 6. OCR
- Control: 40 random pages from five books with a good text layer, rendered at 250 dpi and OCR'd: word recall 94.5%, precision 90.9% (lower on equation-heavy physics pages). `results\ocr_quality.csv`.
- Noise on scans: where NCERT says "No change", OCR of the 2022-23 scan reports 4.0% of words removed (iess4) and 3.2% (jess3), against 1 and 0 words from the text-layer printing, plus thousands of "added" words. Table 14 compares OCR with the text-layer headline for the seven books: removed counts differ by -4,897 to +1,505 words per book (kehs1 27,022 vs 31,919; gess1 12,749 vs 11,593); chapter-file counts are identical. OCR figures are fit for chapter-level results only.
- Hindi: Tesseract `hin` was spot-checked on one page (about 7 s per page; the first paragraph read correctly except leading digits of 4-digit years lost and one conjunct). Hindi results use the text layer, not OCR.

## 7. What was removed, by codebook v0.2 keyword rules (unvalidated, indicative)
- No second coder and no agreement statistic for this corpus. The codebook was written for Class 12 history and politics, so Science text is mostly "unclassified" (192,987 of 365,330 words) or "science_environment" (114,744). Social-science removed words by theme: economy and development 48,921; state, politics and institutions 25,075; religion and communal relations 21,727; international relations and war 20,980; rulers, courts, empire 16,250; colonial rule 12,338; movements and protest 10,872; caste 9,162; art and culture 7,911; gender 7,072; nationalism 3,972; unclassified 54,544. Periods were not tabulated (the period rules cover Class 12 chapters only).
- By form (all books): body or box text 509,536; exercise questions 54,337; credits and references 39,931; headings 14,474. Table 12; figure 4.

## 8. Not settled
- Hand validation and two-coder theme labels (Sean).
- No drift baseline (two pre-rationalisation printings per book); 23 baselines pre-date 2022-23.
- Printed page numbers for 10 books; officially listed items were not matched passage by passage.
- Whether the PDFs match the printed books word for word.
