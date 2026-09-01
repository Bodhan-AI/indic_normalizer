# -*- coding: utf-8 -*-
"""LaTeX speech improvements: multi-term exponent grouping, "the quantity"
dedup, region-style bigop subscripts, sentence-final fractions."""

from indic_normalizer import latex_to_speech, normalize


# ---- multi-term exponents get a boundary word ----
def test_multiterm_exponent_wrapped():
    assert latex_to_speech(r"e^{x_i+2}") == "e to the quantity x sub i plus two"


def test_nested_exponential_fraction():
    out = latex_to_speech(r"\frac{e^{e^{x_i+2}}}{\sum_j e^{e^{x_j+2}}}")
    assert out == ("e to the e to the quantity x sub i plus two over "
                   "sum over j of e to the e to the quantity x sub j plus two")


def test_simple_exponents_stay_clean():
    assert latex_to_speech(r"e^{-x}") == "e to the minus x"
    assert latex_to_speech(r"x^2") == "x squared"
    assert latex_to_speech(r"x^{2a}") == "x to the two a"
    assert latex_to_speech(r"e^{i\pi}") == "e to the i pi"


# ---- "the quantity the quantity" duplication collapses ----
def test_no_doubled_quantity_in_explicit():
    gauss = r"f(x) = \frac{1}{\sigma\sqrt{2\pi}} e^{-\frac{(x-\mu)^2}{2\sigma^2}}"
    out = latex_to_speech(gauss, verbosity="explicit")
    assert "the quantity the quantity" not in out


# ---- subscript-only big operators: region, not range ----
def test_surface_integral_over():
    out = latex_to_speech(r"\iint_S F \cdot dS")
    assert "double integral over S" in out


def test_contour_integral_around():
    out = latex_to_speech(r"\oint_C E \cdot dl")
    assert "contour integral around C" in out


def test_bare_subscript_sum_over():
    assert latex_to_speech(r"\sum_j x_j") == "sum over j of x sub j"


def test_bounded_forms_unchanged():
    assert latex_to_speech(r"\int_0^1 x\,dx") == \
        "integral from zero to one of x d x"
    assert latex_to_speech(r"\sum_{i=1}^{n} i") == \
        "sum from i equals one to n of i"


# ---- sentence-final fractions ----
def test_sentence_final_fraction():
    assert normalize("which equals 1/3.", lang="en") == \
        "which equals one third."


def test_sentence_final_cricket():
    out = normalize("chasing well, they finished 45/3.", lang="en")
    assert "forty five for three." in out


def test_fraction_before_decimal_still_blocked():
    # "1/3.5" must not read "one third point five"
    out = normalize("ratio 1/3.5 here", lang="en")
    assert "one third" not in out
