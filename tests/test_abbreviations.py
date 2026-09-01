# -*- coding: utf-8 -*-
"""Title/abbreviation expansion + dotted acronyms (backlog batch)."""

from indic_normalizer import normalize


# ---- titles & common abbreviations ----
def test_titles():
    assert normalize("Dr. Sharma met Mr. Rao", lang="en") == \
        "Doctor Sharma met Mister Rao"


def test_company_forms():
    assert normalize("Tata Pvt. Ltd. filed", lang="en") == \
        "Tata Private Limited filed"


def test_latin_abbreviations():
    assert normalize("apples, mangoes, etc. were sold", lang="en") == \
        "apples, mangoes, et cetera were sold"


def test_versus():
    assert normalize("India vs. Australia and CSK vs MI", lang="en") == \
        "India versus Australia and CSK versus MI"


def test_number_abbrev_before_digit():
    assert normalize("House No. 5 opened", lang="en") == \
        "House Number five opened"


def test_no_word_not_expanded_without_digit():
    out = normalize("No. I refuse", lang="en")
    assert "Number" not in out


def test_saint_vs_street():
    assert normalize("St. Xavier lives on Main St. nearby", lang="en") == \
        "Saint Xavier lives on Main Street nearby"


def test_hindi_doctor():
    out = normalize("डॉ. शर्मा आए", lang="hi")
    assert "डॉक्टर शर्मा" in out


def test_lowercase_dr_not_expanded():
    out = normalize("the dr. folder", lang="en")
    assert "Doctor" not in out


# ---- dotted acronyms ----
def test_dotted_acronym():
    assert normalize("U.S.A. and B.J.P. won", lang="en") == \
        "U S A and B J P won"


def test_initials():
    assert normalize("A.P.J. Abdul Kalam", lang="en") == "A P J Abdul Kalam"


def test_single_initial_left_alone():
    assert normalize("J. Kumar arrived", lang="en") == "J. Kumar arrived"
