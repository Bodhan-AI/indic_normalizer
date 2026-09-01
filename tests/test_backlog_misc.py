# -*- coding: utf-8 -*-
"""Backlog batch: native scale words, dotted dates, scientific notation,
context-gated roman numerals."""

from indic_normalizer import normalize


# ---- scale-word-aware language: ASCII digits + native scale word ----
def test_ascii_number_native_scale_hindi():
    assert normalize("2 करोड़ लोग", lang="hi") == "दो करोड़ लोग"


def test_ascii_decimal_native_scale_hindi():
    assert normalize("2.5 लाख रुपये", lang="hi") == "दो दशमलव पाँच लाख रुपये"


def test_ascii_number_english_scale_still_english():
    assert normalize("2 crore people", lang="hi") == "two crore people"


# ---- European dotted dates (4-digit year only) ----
def test_dotted_date():
    assert normalize("on 15.8.1947 India", lang="en") == \
        "on fifteenth August nineteen forty seven India"


def test_dotted_date_invalid_falls_to_version():
    out = normalize("build 10.0.19045 shipped", lang="en")
    assert "point" in out
    assert "August" not in out


def test_version_short_year_not_date():
    out = normalize("release 4.5.20 notes", lang="en")
    assert "point" in out


# ---- scientific notation ----
def test_scientific_notation():
    assert normalize("energy 1.5e10 joules", lang="en") == \
        "energy one point five times ten to the power ten joules"


def test_scientific_negative_exponent():
    assert normalize("about 2e-3 seconds", lang="en") == \
        "about two times ten to the power minus three seconds"


# ---- context-gated roman numerals (always on, unlike detect_roman) ----
def test_chapter_roman():
    assert normalize("Chapter IV begins", lang="en") == "Chapter four begins"


def test_class_single_letter_roman():
    assert normalize("Class X results", lang="en") == "Class ten results"


def test_world_war():
    assert normalize("during World War II era", lang="en") == \
        "during World War two era"


def test_roman_without_trigger_left_alone():
    out = normalize("Chapter is IV today", lang="en")
    assert "IV" in out


def test_x_variable_without_trigger():
    assert normalize("X marks the spot", lang="en") == "X marks the spot"
