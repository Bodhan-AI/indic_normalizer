# -*- coding: utf-8 -*-
"""Alphanumeric codes: multi-transition tokens spell out; scientific notation
must not steal uppercase-E flight codes."""

from indic_normalizer import normalize


# ---- scientific-notation false positive ----
def test_flight_code_not_scientific():
    assert normalize("flight 6E204 delayed", lang="en") == \
        "flight six E two zero four delayed"


def test_uppercase_sci_with_decimal_mantissa_still_works():
    assert normalize("about 1.5E10 joules", lang="en") == \
        "about one point five times ten to the power ten joules"


def test_lowercase_sci_still_works():
    assert normalize("about 2e-3 seconds", lang="en") == \
        "about two times ten to the power minus three seconds"


# ---- multi-transition codes spell out ----
def test_two_transition_code():
    assert normalize("code AB123CD here", lang="en") == \
        "code A B one two three C D here"


def test_pnr_style_code():
    assert normalize("PNR X9K42B confirmed", lang="en") == \
        "PNR X nine K four two B confirmed"


# ---- single-transition tokens keep the natural reading ----
def test_seat_still_natural():
    assert normalize("seat 32A", lang="en") == "seat thirty two A"


def test_vitamin_still_natural():
    assert normalize("vitamin B12", lang="en") == "vitamin B twelve"


def test_covid_and_5g_still_natural():
    out = normalize("COVID19 and 5G", lang="en")
    assert "COVID nineteen" in out
    assert "five G" in out


def test_y2k_unchanged():
    assert normalize("in 2000 was Y2K", lang="en") == \
        "in two thousand was Y two K"
