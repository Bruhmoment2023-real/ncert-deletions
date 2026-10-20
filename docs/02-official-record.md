# 02 - The official record

Everything here was read from files now saved in `data\official\`. Nothing is quoted from memory.

## 1. Source files

| File in `data\official\` | Where from | PDF creation / modification date inside the file | Pages | Note |
|---|---|---|---|---|
| `BookletClass6_wayback202206.pdf`, `BookletClass6_live20261013.pdf` | Wayback capture 17 June 2022; ncert.nic.in 13 Oct 2026 | 15 June 2022 | 32 | Identical files (same sha256) |
| `BookletClass7_wayback202206.pdf` | Wayback 17 June 2022 | 15 June 2022 | 32 | Live download failed twice (connection reset; the saved live file is truncated and unusable) |
| `BookletClass8_*.pdf` | both | 15 June 2022 | 32 | Identical files |
| `BookletClass9_wayback202206.pdf` / `_live20261013.pdf` | both | 15 June 2022 / **created 4 Jan 2023, modified 10 Jan 2023** | 32 | **Revised after first publication** |
| `BookletClass10_wayback202206.pdf` / `_live20261013.pdf` | both | 15 June 2022 / **4 Jan 2023, modified 10 Jan 2023** | 32 | **Revised** |
| `BookletClass11_live20261013.pdf` | ncert.nic.in | 15 June 2022 | 80 | The Wayback copy is truncated in the archive; the live file carries the original June 2022 dates |
| `BookletClass12_wayback202206.pdf` / `_live20261013.pdf` | both | 15 June 2022 / **4 Aug 2023** | 108 / 106 | **Revised** |
| `Rationalisation_of_Textbooks-Brief_for_Press_Release-3.pdf` | ncert.nic.in/pdf/Rationalisation-of-textbook/ | 14 Apr 2023 | 2 | NCERT's statement on unlisted changes |
| `NCERT_Response-Periodic_Table_and_Evolution.pdf` | same folder | 1 June 2023 | 2 | Statement on science cuts |
| `Response_on_Maulana_Azad_in_NCERT_textbook.pdf` | same folder | dated 13.04.2023 | 1 | Statement on the Class 11 passage |
| `rationalised-content_wayback20220617.html`, `_live20261013.html` | index page | - | - | The page titled "List of Rationalised Content" linking the seven booklets |

- Booklet imprint page: "May 2022 / Jyestha 1944", "(c) National Council of Educational Research and Training, 2022".
- First Wayback capture of the index page: 17 June 2022. The booklets were online by then.
- sha256 of every booklet is printed by `sha256sum data\official\*.pdf`; record them in the paper's appendix.

## 2. Stated reasons (verbatim from the Class 12 booklet, page headed "Rationalisation of Content in the Textbooks")

> "In view of the COVID-19 pandemic, it is imperative to reduce content load on students. The National Education Policy 2020, also emphasises reducing the content load and providing opportunities for experiential learning with creative mindset. In this background, the NCERT has undertaken the exercise to rationalise the textbooks across all classes."

Criteria listed, verbatim:
- "Overlapping with similar content included in other subject areas in the same class"
- "Similar content included in the lower or higher class in the same subject"
- "Difficulty level"
- "Content, which is easily accessible to students without much interventions from teachers and can be learned by children through self-learning or peer-learning"
- "Content, which is irrelevant in the present context"

And: "This booklet contains information in tabular form about subject-wise contents which have been dropped and hence are not to be assessed."

## 3. Later statements

**April 2023 press brief** (file created 14 Apr 2023), verbatim:
> "However, it may be noted that reprinting of textbooks taking care of suggestions of stakeholders is a regular process which takes place every year. In view of avoiding any confusion at the level of teachers and students, minor deletion or addition if any, are not notified. In the context of rationalisation exercise also some minor deletions (a sentence or a word or a phrase, etc.) were done, which were not included in the details of the notification of the rationalisation, as this was under the regular process of reprinting of textbooks. Therefore, NCERT firmly stands on its version that nothing has been removed or deleted after rationalisation undertaken in academic session 2022-2023."

The same brief says the content was rationalised "with the help of committee of experts consisted of 8 to 10 members" and that "These had been rationalised for the session 2022-23 and the same textbooks are being continued for the session 2023-24."

**June 2023 response on evolution and the periodic table**, verbatim:
> "With respect to the removal of the concepts of periodic table and evolution are concerned, the same has not been removed from the school education curriculum but in fact are available in appropriate detail in classes 11 and 12."

It restates the criteria and says NCERT "attempted to rationalise the contents of the textbooks in 2021".

**13 April 2023 response on Maulana Azad (Class 11, Indian Constitution at Work)**, verbatim:
> "it was found that from 2014-15 onwards the name of Maulana Azad was not there in the referred para."

NCERT states this change predates rationalisation and that Jammu and Kashmir content "was updated for 2020-21 in view of the abrogation of article 370 in 2019". This is the official record's own example of why the baseline printing matters.

Not obtained as primary documents: any statement by the NCERT Director to the press (reported in April 2023 and June 2024); the Lok Sabha reply of 18 July 2022 on the experts consulted. These are known here only through news search snippets and must be fetched from the original before being cited.

## 4. The list was changed after publication

Comparing the June 2022 and current files (English-medium rows):

- **Class 12, Politics in India Since Independence (code 12119).** The revised booklet (4 Aug 2023) adds two entries that the June 2022 booklet did not have:
  - Chapter 1, page 12: "Some portion from 3rd para and last para (full)"
  - Chapter 2, page 43: "Box- Party competition in Bihar"
  - Checked by eye on a rendered image of the page (`data\meta\booklet12_live_p71.png`).
- **Class 10, Science (code 1064).** The English entries were rewritten in the Jan 2023 file. The revised file lists, among others, "Chapter: 9 Heredity and Evolution (Chapter name replaced with: Heredity)" pages 147-158, and "Chapter: 14 Sources of Energy" and "Chapter: 16 Sustainable Management of Natural Resources" as "Full chapter". The parser's rows for the June 2022 science section should be checked by eye before any claim about what the first version did or did not list.
- **Class 9.** Only whitespace-level differences were found in English rows; Hindi and Urdu rows were not compared reliably.
- **Classes 6 and 8.** No change (identical files).
- Later reprint changes (2024 onward) do not appear in any booklet.

## 5. The CSV: `02-official-listed-deletions.csv`

- Made by `code\parse_booklets.py` from the table ruling lines in the PDFs. 3,853 rows in total. 2,513 are table rows; 1,340 are text found outside a ruled table and are marked `UNRULED:` in `dropped_raw` (preface text, contents lines, Urdu sections). Filter those out for analysis.
- Columns: `class`, `booklet_version` (`wayback202206` or `live20261013`), `booklet_pdf_page`, `book_code` (NCERT's own code, e.g. 12119), `book_title`, `chapter`, `pages_raw`, `dropped_raw`, `full_chapter` (1 if the entry says full/whole chapter), `page_list` (page numbers expanded from `pages_raw`).

| Class | Version | Table rows | Books with rows | "Full chapter" rows | "No change" books |
|---|---|---|---|---|---|
| 6 | 2022 = current | 129 | 14 | 11 | 0 |
| 7 | 2022 | 95 | 14 | 16 | 0 |
| 8 | 2022 = current | 97 | 14 | 14 | 0 |
| 9 | 2022 / current | 103 / 103 | 19 | 12 | 5 |
| 10 | 2022 / current | 89 / 92 | 17 | 8 / 10 | 3 |
| 11 | current (June 2022 file) | 393 | 56 | 41 | 9 |
| 12 | 2022 / current | 592 / 594 | 64 | 31 | 6 |

Known faults of the CSV (it is a mechanical extraction):
- Italic words are sometimes missing from titles ("Social Political Life-I" for "Social and Political Life-I").
- Urdu-medium sections are mostly not parsed. Hindi text is extracted with font artefacts.
- A cell that continues on the next page becomes two rows.
- "Full pages", "Full 8 pages" are not flagged as full chapters (correct, but note the wording varies).
- Verified by eye against the PDF: the Class 12 rows for codes 12093, 12094, 12125, 12107 and 12119 only. Every row quoted in a paper must be checked against the PDF page given in `booklet_pdf_page`.

## 6. Editions and print-year stamps

- Every textbook page carries a print-year stamp in the footer: "2021-22", "2022-23", "Rationalised 2023-24", "Reprint 2026-27". `results\extraction_meta.csv` records the stamp of every chapter file used.
- Imprint pages of the 2023-24 books read "Revised Edition November 2022" (History) and "Revised Edition October 2022" (Political Science), after "Reprinted ... December 2021".
- The October 2021 zip of *Politics in India since Independence* still contained the 2020-21 printing, while the chapter PDFs captured the same week were the 2021-22 printing. The stamp, not the capture date, identifies the printing.

## 7. Copyright: what may and may not be released

- Each textbook's imprint page reads: "ALL RIGHTS RESERVED. No part of this publication may be reproduced, stored in a retrieval system or transmitted, in any form or by any means, electronic, mechanical, photocopying, recording or otherwise without the prior permission of the publisher."
- NCERT's website copyright or terms page could not be opened today (404 or connection reset), so no website licence was verified. Do not assume the books are open-licensed.
- This is not legal advice. Sean should ask a teacher or mentor to confirm, and may email NCERT's Publication Division for permission to share extracted text.

| May be released | Must not be released |
|---|---|
| All code | The textbook PDFs or zips |
| Counts and tables: `chapter_summary.csv`, `book_summary.csv`, `official_vs_measured.csv`, `validation_summary.csv`, `crosscheck_summary.csv`, `removed_words_by_*.csv`, `category_agreement_*.csv`, `entity_mentions.csv`, `extraction_meta.csv` | Everything in `results\units\` and every file with `WORKING` in its name (they hold the books' sentences) |
| The list of source URLs, Wayback timestamps and sha256 hashes (`data\meta\downloads.csv`), so others can fetch the same bytes themselves | A reconstructed "deleted text" file, even partial |
| Short quotations with page references, for the purpose of research and review (the usual fair-dealing ground; confirm) | Images of textbook pages, cartoons or maps |
| The parsed official list CSV (a factual list; the booklet itself is also NCERT copyright, so cite it and link the original) | - |
