"""Count mentions of named people, places, events and groups in the old and the new edition.

Design choice: the counts do NOT depend on the diff.  spaCy's NER (en_core_web_sm, free, CPU) is used
only to build a vocabulary of names from both editions; every name in that vocabulary is then counted
by exact, case-sensitive whole-word search in the full text of each edition.  So "mentions of X before
and after" is a plain string count that anyone can re-check with Ctrl+F.

Usage: python code/entity_counts.py code/pilot_pairs.csv [min_old_mentions=3]
Output: results/entity_mentions.csv   (names and counts only - releasable)

Known limits (see 03-design.md): en_core_web_sm misses or mislabels many South Asian names (it tagged
"Agra" as an organisation in a test sentence); spelling variants (Gandhiji / Mahatma Gandhi / Gandhi)
are counted as separate strings unless merged in code/entity_aliases.csv (to be written by hand);
surname strings also match other people (Indira Gandhi, Rajiv Gandhi).
"""
import csv
import re
import sys
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(Path(__file__).resolve().parent))
import ncertdiff as nd  # noqa: E402

KEEP = {"PERSON", "GPE", "LOC", "EVENT", "NORP", "ORG", "WORK_OF_ART", "FAC"}


def load_text(tag, side):
    chunks = []
    with open(ROOT / "results" / "units" / f"{tag}__{side}.csv", encoding="utf-8-sig", newline="") as f:
        for u in csv.DictReader(f):
            if not nd.is_front_matter(u["chapter"]):
                chunks.append(nd.clean(u["text"]))
    return "\n".join(chunks)


def norm_name(t):
    t = re.sub(r"\s+", " ", t.strip(" .,;:'\"()[]"))
    t = re.sub(r"^(the|The) ", "", t)
    t = re.sub(r"'s$", "", t)
    return t


def main(pairs_file, min_old=3):
    import spacy
    nlp = spacy.load("en_core_web_sm", disable=["lemmatizer"])
    nlp.max_length = 3_000_000
    rows = []
    for row in csv.DictReader(open(pairs_file, newline="", encoding="utf-8")):
        if row["new_label"] != "rat2023":
            continue
        tag = f"{row['book']}__{row['old_label']}__{row['new_label']}"
        old, new = load_text(tag, "old"), load_text(tag, "new")
        vocab = defaultdict(Counter)
        for text in (old, new):
            for doc in nlp.pipe(text.split("\n"), batch_size=200):
                for e in doc.ents:
                    if e.label_ in KEEP:
                        n = norm_name(e.text)
                        if 3 <= len(n) <= 60 and re.search(r"[A-Z]", n) and not re.fullmatch(r"[\d\W]+", n):
                            vocab[n][e.label_] += 1
        for name, labs in vocab.items():
            rx = re.compile(r"(?<![A-Za-z])" + re.escape(name) + r"(?![A-Za-z])")
            co, cn = len(rx.findall(old)), len(rx.findall(new))
            if co >= min_old or cn >= min_old:
                rows.append({"book": row["book"], "entity": name, "ner_label_most_common": labs.most_common(1)[0][0],
                             "mentions_old": co, "mentions_new": cn, "change": cn - co,
                             "share_removed": round((co - cn) / co, 3) if co else ""})
        print(row["book"], "vocabulary", len(vocab), flush=True)
    rows.sort(key=lambda r: (r["book"], r["change"]))
    with open(ROOT / "results" / "entity_mentions.csv", "w", newline="", encoding="utf-8-sig") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        w.writeheader()
        w.writerows(rows)


if __name__ == "__main__":
    main(sys.argv[1], int(sys.argv[2]) if len(sys.argv) > 2 else 3)
