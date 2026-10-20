# Scopus and Web of Science queries - paper 07 (NCERT textbook rationalisation)

Status: **not run.** There is no Scopus or Web of Science login on this machine. `scopus-drop\` was empty on 2026-10-13.
These strings mirror the three sub-literatures in `search-protocol.md`. Paste each into the *Advanced search* box.

How to use
- Scopus: Advanced document search -> paste -> Search -> Export -> **CSV** with *Citation information, Bibliographical information, Abstract & keywords, Include references*.
- Web of Science: Advanced Search (Core Collection) -> paste -> Export -> **BibTeX** or *Plain text*, Record Content = **Full Record and Cited References** (500 per file).
- Save exports into `bibliometrics\scopus-drop\` and re-run `R\bibliometrix_analysis.R`.
- Coverage note: much Indian education scholarship appears in journals and edited books that Scopus/WoS do not index (for example *Contemporary Education Dialogue* is indexed, but *Economic and Political Weekly* is only partly indexed and has no abstracts or reference lists in most databases; NCERT's own journals are not indexed). Search EPW (epw.in) and JSTOR by hand for sub-literature A.

## A. Textbook revision, curriculum politics and history-textbook controversies in India

Scopus
```
TITLE-ABS-KEY ( ( ( textbook* OR "school history" OR "history curriculum" OR "history teaching" OR "history education" OR syllab* ) W/15 ( india* OR hindutva OR saffroni* OR "hindu nationalis*" ) )
  OR ncert OR "National Council of Educational Research and Training" )
AND NOT TITLE ( medical OR nursing OR dental OR pharmac* OR engineering OR clinical OR "higher education" OR universit* OR "teacher education" OR "question answering" )
AND PUBYEAR > 1989 AND ( LIMIT-TO ( LANGUAGE , "English" ) )
```
Web of Science
```
TS=(((textbook* OR "school history" OR "history curriculum" OR "history teaching" OR "history education" OR syllab*) NEAR/15 (India* OR Hindutva OR saffroni* OR "Hindu nationalis*"))
  OR NCERT OR "National Council of Educational Research and Training")
NOT TI=(medical OR nursing OR dental OR pharmac* OR engineering OR clinical OR "higher education" OR universit* OR "teacher education" OR "question answering")
AND PY=(1990-2026) AND LA=(English)
```

## B. Computational text analysis of textbooks (any country)

Scopus
```
TITLE-ABS-KEY ( ( textbook* OR schoolbook* OR "school book*" OR "curriculum document*" OR "curriculum material*" OR "children's book*" )
  W/25 ( "text mining" OR "natural language processing" OR nlp OR "computational analysis" OR "computational text analysis" OR "computational linguistic*" OR "topic model*" OR "word embedding*"
         OR "corpus-based" OR "corpus linguistic*" OR "corpus analysis" OR "quantitative text analysis" OR "text as data" OR "automated content analysis" OR "automated text analysis" OR "sentiment analysis"
         OR readability OR "lexical diversity" OR "digital humanities" OR "large language model*" ) )
AND NOT TITLE ( "question answering" OR "question generation" OR chatbot OR "tutoring system*" OR "knowledge tracing" OR medical OR nursing OR "patient education" )
AND PUBYEAR > 1989
```
Web of Science
```
TS=((textbook* OR schoolbook* OR "school book*" OR "curriculum document*" OR "curriculum material*" OR "children's book*")
  NEAR/25 ("text mining" OR "natural language processing" OR NLP OR "computational analysis" OR "computational text analysis" OR "computational linguistic*" OR "topic model*" OR "word embedding*"
           OR "corpus-based" OR "corpus linguistic*" OR "corpus analysis" OR "quantitative text analysis" OR "text as data" OR "automated content analysis" OR "automated text analysis" OR "sentiment analysis"
           OR readability OR "lexical diversity" OR "digital humanities" OR "large language model*"))
NOT TI=("question answering" OR "question generation" OR chatbot OR "tutoring system*" OR "knowledge tracing" OR medical OR nursing OR "patient education")
AND PY=(1990-2026)
```

## C. Curriculum reform and the National Education Policy 2020

Scopus
```
TITLE-ABS-KEY ( ( "National Education Policy" OR "NEP 2020" OR "NEP-2020" OR "National Curriculum Framework" OR "curriculum reform*" OR "curricular reform*" OR "curriculum load" OR "learning without burden"
   OR ( rationali?ation W/5 ( syllabus OR curriculum OR textbook* OR content ) ) )
  AND ( india* OR ncert OR cbse )
  AND ( school* OR schooling OR textbook* OR secondary OR elementary OR primary OR classroom ) )
AND NOT TITLE ( "higher education" OR universit* OR college* OR undergraduate OR "teacher education" OR medical OR nursing OR engineering OR "legal education" )
AND PUBYEAR > 1989 AND ( LIMIT-TO ( LANGUAGE , "English" ) )
```
Web of Science
```
TS=(("National Education Policy" OR "NEP 2020" OR "NEP-2020" OR "National Curriculum Framework" OR "curriculum reform*" OR "curricular reform*" OR "curriculum load" OR "learning without burden"
   OR (rationali$ation NEAR/5 (syllabus OR curriculum OR textbook* OR content)))
  AND (India* OR NCERT OR CBSE)
  AND (school* OR schooling OR textbook* OR secondary OR elementary OR primary OR classroom))
NOT TI=("higher education" OR universit* OR college* OR undergraduate OR "teacher education" OR medical OR nursing OR engineering OR "legal education")
AND PY=(1990-2026) AND LA=(English)
```

## Narrow "direct analogue" queries (run first)

Scopus
```
TITLE-ABS-KEY ( ( ncert OR ( india* W/5 textbook* ) ) AND ( rationali?ation OR delet* OR omission* OR remov* OR "revised edition*" OR revision* OR rewrit* ) AND ( 2022 OR 2023 OR "NEP 2020" OR "National Education Policy" OR covid* ) )
```
```
TITLE-ABS-KEY ( textbook* AND ( edition* OR revision* OR "over time" OR longitudinal OR diachronic ) AND ( "text mining" OR "natural language processing" OR "computational" OR "corpus" OR "quantitative content analysis" OR "text reuse" OR "collation" ) AND ( history OR "social studies" OR civics OR "social science*" ) )
```
Web of Science
```
TS=((NCERT OR (India* NEAR/5 textbook*)) AND (rationali$ation OR delet* OR omission* OR remov* OR "revised edition*" OR revision* OR rewrit*) AND (2022 OR 2023 OR "NEP 2020" OR "National Education Policy" OR covid*))
```
```
TS=(textbook* AND (edition* OR revision* OR "over time" OR longitudinal OR diachronic) AND ("text mining" OR "natural language processing" OR computational OR corpus OR "quantitative content analysis" OR "text reuse" OR collation) AND (history OR "social studies" OR civics OR "social science*"))
```
