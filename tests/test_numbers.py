"""Tests for the number verbalization layer."""

from indic_normalizer import numbers as N
from indic_normalizer.lexicon import get_lexicon

EN = get_lexicon("en")
HI = get_lexicon("hi")


def test_cardinal_en():
    assert N.cardinal(38, "en") == "thirty eight"
    assert N.cardinal(100, "en") == "one hundred"
    assert "forty seven" in N.cardinal(1947, "en")


def test_cardinal_indic_all_langs_no_crash():
    from indic_normalizer.config import SUPPORTED_LANGS
    for lang in SUPPORTED_LANGS:
        out = N.cardinal(1947, lang)
        assert isinstance(out, str) and out.strip(), lang


def test_sindhi_fallback():
    # upstream engine raises on some sd inputs; we fall back to digit-by-digit
    out = N.cardinal(1947, "sd")
    assert out and len(out.split()) >= 4


def test_year_pairing_en():
    assert N.year(1947, "en", EN) == "nineteen forty seven"
    assert N.year(1900, "en", EN) == "nineteen hundred"
    assert N.year(1905, "en", EN) == "nineteen oh five"
    assert N.year(2000, "en", EN) == "two thousand"
    assert N.year(2047, "en", EN) == "twenty forty seven"


def test_year_no_pairing_indic():
    # Indic langs read years as full cardinals (no English-style pairing)
    assert N.year(1947, "hi", HI) == N.cardinal(1947, "hi")


def test_decimal():
    assert N.decimal("3.14", "en", EN) == "three point one four"
    assert N.decimal("-2.5", "en", EN) == "minus two point five"
    assert N.decimal("3.14", "hi", HI).split()[1] == HI.decimal_point


def test_ordinal_en():
    assert N.ordinal(1, "en", EN) == "first"
    assert N.ordinal(2, "en", EN) == "second"
    assert N.ordinal(3, "en", EN) == "third"
    assert N.ordinal(21, "en", EN) == "twenty first"
    assert N.ordinal(20, "en", EN) == "twentieth"


def test_split_digits():
    assert N.split_digits("90210", "en") == "nine zero two one zero"


def test_native_digit_input():
    # Devanagari digits decode to the same value
    assert N.cardinal("१९४७", "hi") == N.cardinal(1947, "hi")
