# -*- coding: utf-8 -*-
"""Indian ID formats: PAN, IFSC, vehicle plates, PIN codes (backlog batch)."""

from indic_normalizer import normalize


def test_pan():
    assert normalize("PAN ABCDE1234F given", lang="en") == \
        "PAN A B C D E one two three four F given"


def test_ifsc():
    assert normalize("IFSC SBIN0001234 branch", lang="en") == \
        "IFSC S B I N zero zero zero one two three four branch"


def test_vehicle_plate_spaced():
    assert normalize("car KA 01 AB 1234 parked", lang="en") == \
        "car K A zero one A B one two three four parked"


def test_vehicle_plate_unspaced():
    assert normalize("plate MH12CD4321 seen", lang="en") == \
        "plate M H one two C D four three two one seen"


def test_pincode():
    assert normalize("PIN 560001 area", lang="en") == \
        "PIN five six zero zero zero one area"


def test_pincode_variant():
    out = normalize("pincode: 110001", lang="en")
    assert "one one zero zero zero one" in out


# ---- guards ----
def test_ordinary_caps_word_with_number_unaffected():
    out = normalize("COVID19 and 5G", lang="en")
    assert "COVID nineteen" in out
    assert "five G" in out


def test_six_digit_number_without_pin_context_is_cardinal():
    out = normalize("population 560001 rose", lang="en")
    assert "five lakh sixty thousand and one" in out
