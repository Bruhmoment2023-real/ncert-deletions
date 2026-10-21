"""Chapter-file order used by the contents-page anchor (no textbook content needed)."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
import page_anchor as pa  # noqa: E402


def _names(tmp_path, names):
    for n in names:
        (tmp_path / f"{n}.pdf").write_bytes(b"")
    return [p.stem for p in pa.body_files(tmp_path)]


def test_three_digit_chapters_sort_numerically(tmp_path):
    # the real fess1 (Class 6 history) file set: chapter 1 misspelt 'fees', chapters 10-11 with three digits
    got = _names(tmp_path, ["fees101", "fess1010", "fess1011", "fess102", "fess103", "fess104", "fess105", "fess106",
                            "fess107", "fess108", "fess109", "fess1ps"])
    assert got == ["fees101", "fess102", "fess103", "fess104", "fess105", "fess106", "fess107", "fess108", "fess109",
                   "fess1010", "fess1011"]


def test_two_digit_chapters_unchanged_and_odd_names_last(tmp_path):
    got = _names(tmp_path, ["leps110", "leps102", "leps101", "World Map _ SDGs", "leps1ps", "leps1gl", "leps1a1"])
    assert got == ["leps101", "leps102", "leps110", "World Map _ SDGs"]


def test_folio_text_forms():
    # forms seen in the books' page margins
    assert pa.match_folio("1 �") == 1                                              # fess1: number + glyph
    assert pa.match_folio("� 2") == 2
    assert pa.match_folio("8 Resources and Development") == 8                           # hess4: number + running head
    assert pa.match_folio("Land, Soil, Water, Natural Vegetation and Wildlife Resources 9") == 9
    assert pa.match_folio("17 INDIAN ECONOMY 1950-1990") == 17                          # keec1
    assert pa.match_folio("2021-22") is None                                            # print-year stamp
    assert pa.match_folio("INDIAN ECONOMY 1950-1990") is None
    assert pa.match_folio("Box 2.1: Types of Economic Systems") is None
    assert pa.match_folio("1. 2.") is None


def test_exclusion_page_spec():
    import importlib
    ex = importlib.import_module("apply_page_exclusions")
    assert ex.pages("12-21") == set(range(12, 22))
    assert ex.pages("3 5-6") == {3, 5, 6}
