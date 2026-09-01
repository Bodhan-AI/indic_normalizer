# -*- coding: utf-8 -*-
"""Last backlog ideas: Ms., BP readings, cricket scores, electrical units,
suffix currency, dot-less St."""

from indic_normalizer import normalize


def test_ms_title():
    assert normalize("Ms. Rao spoke", lang="en") == "Miz Rao spoke"


# ---- blood pressure ----
def test_bp_trigger_word():
    assert normalize("BP 120/80 noted", lang="en") == \
        "BP one hundred and twenty over eighty noted"


def test_bp_mmhg_unit():
    assert normalize("reading 120/80 mmHg high", lang="en") == \
        "reading one hundred and twenty over eighty millimeters of mercury high"


# ---- cricket scores ----
def test_cricket_score_with_overs():
    assert normalize("India 287/5 in 50 overs", lang="en") == \
        "India two hundred and eighty seven for five in fifty overs"


def test_cricket_score_with_wickets():
    out = normalize("they were 45/3 after losing wickets", lang="en")
    assert "forty five for three" in out


def test_slash_without_cricket_context_still_fraction():
    assert normalize("24/7 support", lang="en") == \
        "twenty four over seven support"


# ---- new units ----
def test_mah():
    assert normalize("battery 5000 mAh lasts", lang="en") == \
        "battery five thousand milliamp hours lasts"


def test_hz_family():
    out = normalize("50 Hz supply and 2.4 GHz band", lang="en")
    assert "fifty hertz supply" in out
    assert "two point four gigahertz band" in out


def test_rpm_and_kwh():
    out = normalize("3000 rpm motor used 1.5 kWh", lang="en")
    assert "three thousand revolutions per minute" in out
    assert "one point five kilowatt hours" in out


# ---- suffix currency ----
def test_rupee_symbol_suffix():
    assert normalize("100₹ given", lang="en") == "one hundred rupees given"


def test_rs_word_suffix():
    assert normalize("fee 250 rs paid", lang="en") == \
        "fee two hundred and fifty rupees paid"


def test_yrs_not_suffix_currency():
    out = normalize("over 5 yrs time", lang="en")
    assert "rupees" not in out


# ---- dot-less St ----
def test_dotless_street():
    assert normalize("21st Main St nearby", lang="en") == \
        "twenty first Main Street nearby"


def test_dotless_st_before_capital_left_alone():
    out = normalize("St Xavier plays", lang="en")
    assert out == "St Xavier plays"
