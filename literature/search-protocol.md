# Search protocol - 07-ncert-deletions

- Paper question: A measured text comparison of India's NCERT textbooks before and after the 2022-23 rationalisation
- Date of search and data pull: **2026-10-13**
- Years covered: 1990-2026; language: English (OpenAlex language field `en` or missing)
- Built by an AI agent (Claude) with the scripts in `python\` and `R\`; all numbers below are read from the run logs.

## 1. Databases

| Role | Database | Access | Note |
|---|---|---|---|
| Discovery | Crossref REST API | free, no key, `mailto` polite pool | relevance-ranked keyword search; top N per query |
| Discovery | Semantic Scholar Graph API (bulk search) | free, no key | boolean search on title/abstract; top N by citations per query |
| Discovery | ERIC API | free, no key | education topics only |
| Discovery | arXiv API | free, no key | preprints |
| Enrichment (authors, institutions, countries, topics, keywords, abstracts, references, citation counts, OA links) | **OpenAlex** single-record lookups (`/works/doi:...`, `/works/mag:...`, `/works/W...`) | free, no key | see limit 1 below |
| Forward citations for snowballing | OpenCitations Index API v2 | free, no key | DOI-to-DOI citations only |
| Cross-check | Crossref (per-DOI), Semantic Scholar (batch) | free, no key | citation counts and reference-list coverage compared in `tables\coverage_crosscheck.csv` |
| Not used | Scopus, Web of Science, Lens, Dimensions | need accounts | equivalent strings are in `scopus-queries.md` |
| Not usable | RePEc/IDEAS | its API needs a registered access code; the public search page returned no parseable result list to a script | economics working papers still enter via Crossref, Semantic Scholar and snowballing |

**Why OpenAlex was not the search engine.** Since 2026 OpenAlex charges keyless list/search calls against a small daily budget shared by everyone on the same IP address ($0.10/day). On the day of the pull that budget was already exhausted by other work on this network, and an API key needs an account (ruled out). Single-record lookups remain free and unlimited, so records were *discovered* in Crossref / Semantic Scholar / ERIC / arXiv and then *enriched* one by one from OpenAlex. Consequence: a work that is in OpenAlex but not found by any of the four discovery databases is missed, except where snowballing caught it.

## 2. Exact search strings

### B_computational_textbook_analysis: Computational text analysis of textbooks (any country)

| database | query | hits in database | records retrieved | status |
|---|---|---|---|---|
| crossref | computational text analysis of textbooks | 6758138.0 | 250 | ok |
| crossref | natural language processing school textbooks content analysis | 9760199.0 | 250 | ok |
| crossref | topic modeling history textbooks | 2635178.0 | 250 | ok |
| crossref | word embeddings gender bias textbooks | 734175.0 | 250 | ok |
| crossref | corpus-based analysis of school textbooks | 12358061.0 | 250 | ok |
| crossref | quantitative content analysis textbook editions changes over time | 9035828.0 | 250 | ok |
| crossref | text mining curriculum documents | 801613.0 | 250 | ok |
| s2 | (textbook \| textbooks \| schoolbooks) + ("text mining" \| "natural language processing" \| "topic modeling" \| "topic modelling" \| "word embeddings" \| "computational text analysis" \| "quantitative text analysis" \| "text as data" \| "corpus linguistics" \| "corpus-based") | 1281.0 | 800 | ok |
| s2 | (textbooks \| "history textbooks" \| "school textbooks") + "content analysis" + (computational \| automated \| quantitative \| corpus) | 670.0 | 670 | ok |
| s2 | textbooks + (gender \| race \| bias \| representation) + ("word embeddings" \| "natural language processing" \| computational \| "machine learning" \| "text analysis") | 409.0 | 409 | ok |
| s2 | ("history textbooks" \| "social studies textbooks" \| "civics textbooks") + (quantitative \| corpus \| "text analysis" \| digital) + analysis | 155.0 | 155 | ok |
| s2 | (textbook \| textbooks) + (editions \| revision \| revisions \| longitudinal) + ("content analysis" \| "text analysis" \| corpus \| comparison) | 1199.0 | 800 | ok |
| eric | textbooks AND "content analysis" AND (computational OR "text mining" OR "natural language processing" OR corpus) | 77.0 | 77 | ok |
| arxiv | all:textbooks AND (all:"content analysis" OR all:"text analysis" OR all:"word embeddings") AND (all:gender OR all:history OR all:bias OR all:curriculum) | 1.0 | 1 | ok |
| arxiv | ti:textbooks AND (all:"natural language processing" OR all:computational) | 29.0 | 29 | ok |

### A_textbook_politics_india: Textbook revision, curriculum politics and history-textbook controversies in India

| database | query | hits in database | records retrieved | status |
|---|---|---|---|---|
| crossref | NCERT textbooks | 25098.0 | 250 | ok |
| crossref | history textbook controversy India | 2314666.0 | 250 | ok |
| crossref | rewriting history textbooks India Hindutva | 2246744.0 | 250 | ok |
| crossref | politics of school textbooks India nationalism | 2230953.0 | 250 | ok |
| crossref | NCERT rationalisation textbooks deletions | 34235.0 | 250 | ok |
| crossref | National Curriculum Framework India textbooks | 2915814.0 | 250 | ok |
| crossref | representation gender caste Indian school textbooks | 2165464.0 | 250 | ok |
| s2 | (NCERT \| "National Council of Educational Research and Training") + (textbook \| textbooks \| curriculum \| syllabus) | 267.0 | 267 | ok |
| s2 | (India \| Indian) + ("history textbooks" \| "history textbook" \| "textbook controversy" \| "textbook controversies" \| "textbook revision" \| "rewriting history" \| saffronisation \| saffronization) | 853.0 | 800 | ok |
| s2 | (India \| Indian) + textbooks + (politics \| nationalism \| Hindutva \| ideology \| identity \| secularism \| communalism \| gender \| caste) | 726.0 | 726 | ok |
| s2 | (India \| Indian) + ("curriculum politics" \| "politics of curriculum" \| "National Curriculum Framework" \| "curriculum reform") + (school \| schools \| textbooks) | 192.0 | 191 | ok |
| s2 | ("textbook rationalisation" \| "textbook rationalization" \| "rationalised content" \| "syllabus rationalisation" \| "deleted chapters" \| "textbook deletions") + (NCERT \| India \| CBSE) | 1.0 | 1 | ok |
| eric | NCERT OR "National Council of Educational Research and Training" | 40.0 | 34 | ok |
| eric | India AND textbooks AND (history OR politics OR nationalism OR "content analysis") | 58.0 | 48 | ok |

### C_nep_curriculum_reform: Curriculum reform and the National Education Policy 2020

| database | query | hits in database | records retrieved | status |
|---|---|---|---|---|
| crossref | National Education Policy 2020 India school curriculum | 13534179.0 | 250 | ok |
| crossref | NEP 2020 curriculum reform school education | 11081290.0 | 250 | ok |
| crossref | National Curriculum Framework India school education reform | 6412351.0 | 250 | ok |
| crossref | curriculum load reduction rationalisation India school syllabus | 2357365.0 | 250 | ok |
| s2 | ("National Education Policy 2020" \| "NEP 2020" \| "National Education Policy") + (India \| Indian) + (curriculum \| school \| schools \| textbooks \| reform) | 1422.0 | 800 | ok |
| s2 | ("National Curriculum Framework" \| "curriculum reform" \| "curricular reform" \| "curriculum load") + (India \| Indian \| NCERT) + (school \| schools) | 228.0 | 227 | ok |
| eric | "National Education Policy" AND India | 80.0 | 80 | ok |
| eric | India AND "curriculum reform" AND (school OR secondary OR elementary) | 7.0 | 6 | ok |

Per-query retrieval caps: crossref = 250, s2 = 800, eric = 300, arxiv = 100. Crossref totals are large because its search is an OR-type relevance ranking; only the top-ranked records were taken. Raw responses for every query are in `data\raw\<database>\`.

### Seed papers (known key works, each verified to exist by a Crossref title match; they bypass the keyword rules)

| seed title | result |
|---|---|
| Content Analysis of Textbooks via Natural Language Processing: Findings on Gender, Race, and Ethnicity in Texas U.S. History Textbooks | matched 10.1177/2332858420940312 |
| What We Teach About Race and Gender: Representation in Images and Text of Children's Books | matched 10.2139/ssrn.4416772 |
| Sexist textbooks: Automated analysis of gender bias in 1,255 books from 34 countries | matched 10.1371/journal.pone.0310366 |
| Educate to hate: the use of education in the creation of antagonistic national identities in India and Pakistan | matched 10.1080/03057920701467834 |
| Teaching History in Schools: the Politics of Textbooks in India | matched 10.1093/hwj/dbn050 |
| The History Debate and School Textbooks in India: a Personal Memoir | matched 10.1093/hwj/dbn054 |
| The Hindutva View of History: Rewriting Textbooks in India and the United States | NOT MATCHED in Crossref |
| The Construction of History and Nationalism in India: Textbooks, Controversies and Politics | matched 10.1080/09584935.2013.856606 |
| Prejudice and Pride: School Histories of the Freedom Struggle in India and Pakistan | matched 10.1177/097318490300100107 |
| Hindu Nationalism, History and Identity in India: Narrating a Hindu past under the BJP | NOT MATCHED in Crossref |
| Curriculum as Destiny: Forging National Identity in India, Pakistan, and Bangladesh | NOT MATCHED in Crossref |

## 3. Inclusion and exclusion rules (applied identically to search hits and snowballed records)

A record is **included** if all of the following hold:
1. It resolves to an OpenAlex work record (by DOI, MAG id, or a Crossref title match of at least 93% similarity).
2. OpenAlex type is article, review, preprint, book chapter, book, dissertation, report or other (editorials, errata, paratext, datasets, peer reviews are dropped).
3. Publication year 1990-2026; language English or unrecorded.
4. It satisfies at least one sub-literature rule below: every `include` pattern must match in title + abstract, and every `title_must` pattern must match in the title.
5. Its title does not match the exclusion pattern.

Book-series and proceedings trap: a record whose abstract is a series/proceedings blurb (detected by wording such as 'this volume constitutes the refereed proceedings', or the same abstract shared by 3+ records) is screened on its title alone; whole-volume records (titles starting 'Proceedings of', 'Front matter', etc.) are dropped.

The patterns are case-insensitive regular expressions (`\b` = word boundary, `\w*` = any word ending, `.{0,80}` = within 80 characters).

**B_computational_textbook_analysis - Computational text analysis of textbooks (any country)**

- include (title+abstract): `((textbooks?|schoolbooks?|school books?|curricul(um|a|ar) (materials?|documents?|texts?|standards)|children'?s books).{0,220}(text mining|natural language processing|\bnlp\b|computational (text |content |linguistic )?(analys[ie]s|methods?|approach\w*|tools?)|topic model\w*|word embeddings?|corpus[- ](based|linguistic\w*|analysis|driven)|corpus linguistics|quantitative text analysis|text[- ]as[- ]data|automated (content|text) analysis|sentiment analysis|readability|lexical (diversity|density|coverage)|digital humanities|large language models?|machine learning)|(text mining|natural language processing|\bnlp\b|computational (text |content |linguistic )?(analys[ie]s|methods?|approach\w*|tools?)|topic model\w*|word embeddings?|corpus[- ](based|linguistic\w*|analysis|driven)|corpus linguistics|quantitative text analysis|text[- ]as[- ]data|automated (content|text) analysis|sentiment analysis|readability|digital humanities).{0,220}(textbooks?|schoolbooks?|school books?|children'?s books))`
- title_must (title): `(textbooks?|schoolbooks?|school books?|curricul\w+|children'?s books|teaching materials?)`

**A_textbook_politics_india - Textbook revision, curriculum politics and history-textbook controversies in India**

- include (title+abstract): `((textbooks?|ncert|school history|history (teaching|curriculum|education)).{0,160}\b(india\w*|hindutva|saffron\w*|ncert|hindu nationalis\w+)\b|\b(india\w*|hindutva|saffron\w*|ncert|hindu nationalis\w+)\b.{0,160}(textbooks?|ncert|school history|history (teaching|curriculum|education))|\bncert\b)`
- title_must (title): `(textbooks?|ncert|curricul\w+|syllab\w+|history|school\w*|education\w*|pedagog\w+|hindutva|saffron\w*)`

**C_nep_curriculum_reform - Curriculum reform and the National Education Policy 2020**

- include (title+abstract): `(national education policy|nep[- ]?2020|\bnep\b|national curriculum framework|\bncf\b|curricul\w+ reforms?|rationali[sz]ation of (the )?(syllabus|curriculum|content|textbooks?)|curriculum (load|burden)|learning without burden|education(al)? reforms?)`
- include (title+abstract): `\b(india\w*|ncert|cbse)\b`
- include (title+abstract): `\b(schools?|schooling|textbooks?|curricul\w+|syllab\w+|secondary|elementary|primary|classroom)\b`
- title_must (title): `(national education policy|\bnep\b|nep[- ]?2020|curricul\w+|\bncf\b|reform\w*|syllab\w+|education policy|rationali[sz]\w+)`

**Exclusion pattern (title):** `(\bmedical|\bnursing|\bdental|pharmac|engineering|\bmbbs|clinical|physiotherap|management education|\bmba\b|librar|agricultur|veterinar|ayurved|homeopath|higher education|universit|teacher education|\bcolleges?\b|undergraduate|legal education|question (answering|generation)|chatbot|tutoring system|knowledge tracing|\bocr\b|speech recognition)`

A record matching several rules is assigned to the first one in the order listed (its other matches are kept in `sublits_all`).

## 4. Snowballing (one round)

- Central papers: the 25 corpus records ranked highest on local citations + topical relevance + log(global citations) - listed in `data\clean\snowball_central_papers.csv`.
- Backward: every OpenAlex `referenced_works` entry of those papers not already in the corpus (425 candidates).
- Forward: citing DOIs from OpenCitations, up to 150 per central paper (178 candidates). OpenCitations only knows DOI-to-DOI links, so citing preprints and books without DOIs are missed.
- All candidates were looked up in OpenAlex and screened with the rules in section 3: 6 backward and 16 forward records were added.

## 5. PRISMA-style counts

| stage | n |
|---|---|
| Records identified through database searching (all query hits) | 10629 |
|    of which from arxiv | 30 |
|    of which from crossref | 4500 |
|    of which from eric | 245 |
|    of which from s2 | 5846 |
|    of which from seed | 8 |
| Duplicates removed (same DOI / id / title across queries and databases) | 2402 |
| Unique records screened on title (+ abstract where the database supplied one) | 8227 |
| Removed at title pre-screen (off-topic) | 6167 |
| Records looked up in OpenAlex | 2060 |
| Duplicates removed after OpenAlex matching (same work / same title) | 19 |
| Excluded at full screen: offtopic_fails_inclusion_rule | 987 |
| Excluded at full screen: no_openalex_record (no DOI / not indexed) | 174 |
| Excluded at full screen: type_excluded | 103 |
| Excluded at full screen: language_not_english | 22 |
| Excluded at full screen: year_out_of_range | 1 |
| Excluded at full screen: paratext_or_container_record | 1 |
| Excluded at full screen: offtopic_exclusion_term_in_title | 1 |
| Included after search screening | 752 |
| Snowball: central papers used | 25 |
| Snowball: backward-reference candidates | 425 |
| Snowball: forward-citation candidates (OpenCitations) | 178 |
| Snowball: duplicates of corpus records | 4 |
| Snowball excluded: offtopic_fails_inclusion_rule | 447 |
| Snowball excluded: type_excluded | 57 |
| Snowball excluded: year_out_of_range | 38 |
| Snowball excluded: no_openalex_record | 16 |
| Snowball excluded: offtopic_exclusion_term_in_title | 11 |
| Snowball excluded: language_not_english | 6 |
| Snowball excluded: paratext_or_container_record | 2 |
| Snowball: included (backward) | 6 |
| Snowball: included (forward) | 16 |
| Corpus before hand-screening | 774 |
| Removed at hand-screening (see tables/hand_screen_removed.csv) | 68 |
| FINAL CORPUS | 706 |
|    with abstract | 644 |
|    with DOI | 633 |
|    with a reference list in OpenAlex | 361 |
| Distinct cited references / resolved to metadata | 9461 / 4893 |

Figure: `figures\py_01_prisma_flow.png`.

## 6. Hand-screening

After rule screening and snowballing, the agent read the titles (with source and year) of the whole corpus and removed 68 records as off-topic or mis-matched; every removal and its reason is in `tables\hand_screen_removed.csv`. This is a single-screener pass by an AI agent on titles, not a two-person human screen; borderline records were kept.

Removal reasons:
- A: not about textbooks/school history (ed-tech, pedagogy or general education): 51
- B: not computational analysis of textbook content (ELT/ESP materials, ed-tech, LLM benchmark, instructor opinion): 17

## 7. Coverage and cross-checks

| item | value |
|---|---|
| corpus records | 706.0 |
| records with DOI | 633.0 |
| found in Crossref (DOI lookup) | 624.0 |
| found in Semantic Scholar (batch DOI lookup) | 623.0 |
| Spearman corr. OpenAlex vs Crossref cited-by | 0.924 |
| Spearman corr. OpenAlex vs Semantic Scholar cited-by | 0.864 |
| median cited-by: OpenAlex | 1.0 |
| median cited-by: Crossref | 0.0 |
| median cited-by: Semantic Scholar | 1.0 |
| records with no reference list in OpenAlex | 345.0 |
|   of which Crossref holds a reference list | 18.0 |
| records with no institution/country data | 299.0 |
| records without abstract | 62.0 |
| open-access records (OpenAlex) | 465.0 |
| origin: search | 677.0 |
| origin: snowball_forward | 15.0 |
| origin: seed | 8.0 |
| origin: snowball_backward | 6.0 |
| retrieved by: s2 | 663.0 |
| retrieved by: eric | 57.0 |
| retrieved by: openalex_snowball | 21.0 |
| retrieved by: seed | 8.0 |
| retrieved by: arxiv | 4.0 |
| retrieved by: crossref | 3.0 |


- 174 title-screened candidates could not be matched to any OpenAlex record (no DOI or MAG id, or not indexed) and are **not** in the corpus. They are listed in `data\clean\unresolved_candidates.csv` (s2: 147, eric: 22, crossref: 4, arxiv: 1). ERIC reports and theses and Indian or legal journal articles without DOIs dominate this list.

- Cited references: 9461 distinct works are cited by the corpus (11357 links); 4893 of the 5000 outside the corpus were resolved to metadata for the co-citation and RPYS analyses.


### Named prior work (seed list / the substance agent's saved papers) - is it in the corpus?

| id | kind | in_corpus |
|---|---|---|
| 10.1007/bf01840446 | doi | 0 |
| 10.1038/d41586-023-01770-y | doi | 0 |
| 10.1080/09585176.2011.550770 | doi | 0 |
| 10.1086/690951 | doi | 0 |
| 10.1093/hwj/dbn050 | doi | 1 |
| 10.1093/hwj/dbn054 | doi | 1 |
| 10.1093/llc/fqu007 | doi | 0 |
| 10.1093/qje/qjad028 | doi | 0 |
| 10.1109/bigdata.2013.6691675 | doi | 0 |
| 10.1109/sequen.1997.666900 | doi | 0 |
| 10.1111/j.0011-1562.2005.00638.x | doi | 0 |
| 10.1142/9789811272295_0003 | doi | 0 |
| 10.1177/097318490300100107 | doi | 1 |
| 10.1177/2332858420940312 | doi | 1 |
| 10.1177/2455632719880622 | doi | 1 |
| 10.1371/journal.pone.0310366 | doi | 1 |
| 10.17159/2223-0386/2024/n32a5 | doi | 0 |
| 10.36948/ijfmr.2025.v07i04.52270 | doi | 1 |
| 10.4324/9780203380741 | doi | 0 |
| 10.4324/9780203848579 | doi | 1 |
| 10.4324/9781003771524-21 | doi | 0 |
| 10.4324/9781003771524-22 | doi | 0 |
| 10.4324/9781315617695 | doi | 1 |
| 10.48001/978-81-988770-9-3-15 | doi | 0 |
| 10.5958/2321-5828.2020.00051.0 | doi | 1 |

## 8. API failures during the run

- api.openalex.org: failed after retries: {"error":"Rate limit exceeded","message":"Rate l (x33)
- api.semanticscholar.org: failed after retries: {"message": "Too Many Requests. Please wait and  (x1)
- api.semanticscholar.org: batch cross-check chunk failed (x1)


## 9. Scopus / Web of Science exports
- `scopus-drop\`: EMPTY - no Scopus/WoS export to merge; corpus is OpenAlex-only.
- Ready-to-paste strings: `scopus-queries.md`.
