"""Suffix ordinals must speak the sentence language even with ASCII digits
(audit plan step 5)."""

from indic_normalizer import normalize


def test_hindi_ascii_digit_ordinal():
    assert normalize("5वाँ स्थान", lang="hi") == "पाँचवाँ स्थान"


def test_hindi_ascii_digit_ordinal_regular():
    assert normalize("21वाँ जन्मदिन", lang="hi") == "इक्कीसवाँ जन्मदिन"


def test_hindi_native_digit_ordinal_still_works():
    assert normalize("५वाँ स्थान", lang="hi") == "पाँचवाँ स्थान"


def test_marathi_ascii_digit_ordinal():
    assert normalize("5वा क्रमांक", lang="mr") == "पाचवा क्रमांक"


def test_bengali_irregular_ordinal():
    assert normalize("3তম পুরস্কার", lang="bn") == "তৃতীয় পুরস্কার"


def test_english_ordinals_unaffected():
    assert normalize("He came 21st in the 3rd race", lang="en") == \
        "He came twenty first in the third race"
