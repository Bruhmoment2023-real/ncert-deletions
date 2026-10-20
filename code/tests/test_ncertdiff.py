"""Unit tests on synthetic text (no textbook content needed).  Run:  venv\\Scripts\\python -m pytest code/tests -q"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
import ncertdiff as nd  # noqa: E402
from parse_booklets import parse_pages  # noqa: E402

A = ("The river rises in the northern hills and flows south for nine hundred kilometres. "
     "Farmers along its banks grow rice, wheat and pulses in rotation every year. "
     "In the dry season the smaller channels shrink to a line of pools. "
     "A council of twelve elders decides how the water is shared between villages. "
     "Travellers in the last century described crowded markets on both banks.")
SENTS = nd.split_sentences(A)


def units(sentences, chapter="c1", page_of=None, block_of=None):
    out = []
    for i, s in enumerate(sentences):
        out.append(nd.Unit(chapter, (page_of or (lambda i: 1))(i), None, (block_of or (lambda i: i))(i), 10.0, s, nd.tokens(s)))
    return out


def removed(old, new):
    nd.diff_books(old, new)
    return sum(len(u.toks) - u.retained_book for u in old)


def test_tokens_join_hyphens_and_ligatures():
    assert nd.tokens("Sub-regions of the non-traditional ﬁeld") == ["subregions", "of", "the", "nontraditional", "field"]


def test_fake_bold_duplicates_collapse():
    assert nd.clean("Countries Countries Countries Countries Countries") == "Countries"
    assert nd.clean("live births) live births) live births)") == "live births)"
    assert nd.clean("very very good") == "very very good"          # only 3+ repeats are collapsed


def test_identical_editions_remove_nothing():
    assert removed(units(SENTS), units(SENTS)) == 0


def test_reflow_across_pages_and_blocks_removes_nothing():
    old = units(SENTS, page_of=lambda i: 1, block_of=lambda i: 0)
    # new edition: every line its own block, split over three pages, mid-sentence breaks
    words = A.split()
    lines = [" ".join(words[i:i + 7]) for i in range(0, len(words), 7)]
    new = units(lines, page_of=lambda i: 1 + i // 4, block_of=lambda i: i)
    assert removed(old, new) == 0
    assert all(u.label == "kept" for u in old)


def test_deleted_sentence_is_counted_exactly():
    old, new = units(SENTS), units(SENTS[:2] + SENTS[3:])
    n = removed(old, new)
    assert n == len(nd.tokens(SENTS[2]))
    assert [u.label for u in old] == ["kept", "kept", "deleted", "kept", "kept"]


def test_one_changed_word_is_reworded_not_deleted():
    changed = SENTS[3].replace("twelve", "fifteen")
    old, new = units(SENTS), units(SENTS[:3] + [changed] + SENTS[4:])
    n = removed(old, new)
    assert n == 1
    assert old[3].label in ("kept", "reworded") and old[3].retained_book == len(old[3].toks) - 1


def test_dropped_chapter_and_renumbering():
    b = ("Copper was mined in the western ranges and carried to the coast by pack animals. "
         "Each caravan paid a toll at the three fortified passes on the road.")
    old = units(SENTS, "bk01") + units(nd.split_sentences(b), "bk02")
    new = units(nd.split_sentences(b), "bk01")          # chapter 1 dropped, chapter 2 renumbered to 1
    align, detail, _ = nd.diff_books(old, new)
    assert align["bk01"] is None and align["bk02"] == "bk01"
    assert all(u.label == "deleted" for u in old if u.chapter == "bk01")
    assert all(u.label == "kept" for u in old if u.chapter == "bk02")


def test_short_heading_not_retained_from_other_chapter():
    old = units(SENTS + ["Source 3"], "bk01") + units(["Source 3", "Copper was mined in the western ranges and carried away."], "bk02")
    new = units(["Source 3", "Copper was mined in the western ranges and carried away."], "bk01")
    nd.diff_books(old, new)
    heading = [u for u in old if u.chapter == "bk01" and u.text == "Source 3"][0]
    assert heading.label == "deleted"                    # its chapter was dropped


def test_damaged_font_text_is_rescued():
    good = "This cannot be helped, for the two blocs are extraordinarily suspicious of each other."
    damaged = "T is canno be helped, for the two blocs are e raordinarily suspicious o each o her."
    old, new = units(SENTS + [damaged]), units(SENTS + [good])
    nd.diff_books(old, new)
    assert old[-1].label == "kept" and old[-1].note.startswith("fuzzy")


def test_added_text_is_seen_from_the_new_side():
    extra = "A new canal opened in the eastern district after the survey was completed."
    old, new = units(SENTS), units(SENTS + [extra])
    nd.diff_books(old, new)
    assert sum(len(u.toks) - u.retained_book for u in new) == len(nd.tokens(extra))


def test_parse_pages():
    assert parse_pages("54–61") == list(range(54, 62))
    assert parse_pages("105 113– 117") == [105, 113, 114, 115, 116, 117]
    assert parse_pages("188, 189, 196 and 197") == [188, 189, 196, 197]
    assert parse_pages("") == []
