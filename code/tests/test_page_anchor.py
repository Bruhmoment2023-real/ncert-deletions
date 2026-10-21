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
