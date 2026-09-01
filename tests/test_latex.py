"""Tests for the pure-Python LaTeX-to-speech engine."""

import re

import pytest

from indic_normalizer.latex import (
    latex_to_speech,
    convert_spans,
    LATEX_SPAN_PATTERN,
)
from indic_normalizer.latex.chemistry import (
    looks_like_formula,
    read_formula,
    read_ce,
)


def n(expr):
    return latex_to_speech(expr, "natural")


def e(expr):
    return latex_to_speech(expr, "explicit")


# --------------------------------------------------------------------------
# Superscripts
# --------------------------------------------------------------------------
def test_square():
    assert n(r"x^2") == "x squared"


def test_cube():
    assert n(r"x^3") == "x cubed"


def test_sup_braced_ident():
    assert n(r"x^{n}") == "x to the n"


def test_sup_negative():
    assert n(r"x^{-1}") == "x to the minus one"


def test_sup_expr():
    assert n(r"x^{n+1}") == "x to the quantity n plus one"


def test_sup_epi():
    assert n(r"e^{i\pi}") == "e to the i pi"


def test_sup_explicit():
    assert e(r"x^2") == "x to the power of two"


def test_emc2():
    assert n(r"E=mc^2") == "E equals m c squared"


def test_power_of_ten():
    assert n(r"\cdot 10^{9}") == "times ten to the nine"


# --------------------------------------------------------------------------
# Subscripts
# --------------------------------------------------------------------------
def test_sub_natural():
    assert n(r"x_1") == "x sub one"


def test_sub_explicit():
    assert e(r"x_1") == "x subscript one"


def test_sub_multi():
    assert n(r"a_{ij}") == "a sub i j"


# --------------------------------------------------------------------------
# Fractions
# --------------------------------------------------------------------------
def test_frac_general():
    assert n(r"\frac{a}{b}") == "a over b"


def test_frac_half():
    assert n(r"\frac{1}{2}") == "one half"


def test_frac_third():
    assert n(r"\frac{1}{3}") == "one third"


def test_frac_three_quarters():
    assert n(r"\frac{3}{4}") == "three quarters"


def test_frac_quarter():
    assert n(r"\frac{1}{4}") == "one quarter"


def test_frac_single_token():
    assert n(r"\frac12") == "one half"


def test_dfrac():
    assert n(r"\dfrac{a}{b}") == "a over b"


def test_frac_explicit():
    assert e(r"\frac{a}{b}") == "the fraction a over b"


def test_frac_complex_explicit():
    assert e(r"\frac{a+b}{c}") == "the quantity a plus b over the quantity c"


# --------------------------------------------------------------------------
# Roots
# --------------------------------------------------------------------------
def test_sqrt():
    assert n(r"\sqrt{x}") == "square root of x"


def test_cube_root():
    assert n(r"\sqrt[3]{8}") == "cube root of eight"


def test_nth_root():
    assert n(r"\sqrt[n]{x}") == "n-th root of x"


# --------------------------------------------------------------------------
# Big operators
# --------------------------------------------------------------------------
def test_integral_bounds():
    assert n(r"\int_0^1 x^2\,dx") == "integral from zero to one of x squared d x"


def test_integral_plain():
    assert n(r"\int") == "integral"


def test_integral_ab():
    assert n(r"\int_a^b f(x)\,dx") == "integral from a to b of f of x d x"


def test_sum():
    assert n(r"\sum_{i=1}^{n} i") == "sum from i equals one to n of i"


def test_prod():
    assert n(r"\prod") == "product"


def test_lim():
    assert n(r"\lim_{x\to 0}") == "limit as x approaches zero"


def test_oint():
    assert n(r"\oint") == "contour integral"


# --------------------------------------------------------------------------
# Relations / operators / symbols
# --------------------------------------------------------------------------
def test_greek_sum():
    assert n(r"\alpha+\beta") == "alpha plus beta"


def test_capital_greek():
    assert n(r"\Omega") == "capital omega"


def test_relations():
    assert n(r"a \leq b") == "a less than or equal to b"
    assert n(r"a \neq b") == "a not equal to b"
    assert n(r"a \geq b") == "a greater than or equal to b"
    assert n(r"a \approx b") == "a approximately b"
    assert n(r"a \equiv b") == "a equivalent to b"


def test_operators():
    assert n(r"a \pm b") == "a plus or minus b"
    assert n(r"a \times b") == "a times b"
    assert n(r"a \div b") == "a divided by b"


def test_infinity():
    assert n(r"\infty") == "infinity"


def test_implies():
    assert n(r"p \Rightarrow q") == "p implies q"


def test_iff():
    assert n(r"p \iff q") == "p if and only if q"


def test_nabla():
    assert n(r"\nabla") == "del"


def test_forall_exists():
    assert n(r"\forall") == "for all"
    assert n(r"\exists") == "there exists"


# --------------------------------------------------------------------------
# Functions
# --------------------------------------------------------------------------
def test_sin_of():
    assert n(r"\sin x") == "sine of x"


def test_sin_squared():
    assert n(r"\sin^2 x") == "sine squared of x"


def test_cos_ln():
    assert n(r"\cos x") == "cosine of x"
    assert n(r"\ln x") == "natural log of x"


# --------------------------------------------------------------------------
# Accents / decorations
# --------------------------------------------------------------------------
def test_vec():
    assert n(r"\vec{v}") == "vector v"


def test_hat():
    assert n(r"\hat{x}") == "x hat"


def test_bar():
    assert n(r"\bar{x}") == "x bar"


def test_dot_ddot():
    assert n(r"\dot{x}") == "x dot"
    assert n(r"\ddot{x}") == "x double dot"


def test_tilde():
    assert n(r"\tilde{x}") == "x tilde"


def test_vec_equation():
    assert n(r"\vec{F}=m\vec{a}") == "vector F equals m vector a"


# --------------------------------------------------------------------------
# Delimiters
# --------------------------------------------------------------------------
def test_abs():
    assert n(r"|x|") == "absolute value of x"


def test_norm():
    assert n(r"\|x\|") == "norm of x"


def test_paren_inline():
    assert n(r"(a+b)") == "a plus b"


def test_function_application():
    assert n(r"f(x)") == "f of x"


def test_left_right():
    assert n(r"\left( a+b \right)") == "a plus b"


# --------------------------------------------------------------------------
# Numbers
# --------------------------------------------------------------------------
def test_decimal():
    assert n(r"3.14") == "three point one four"


def test_multidigit():
    assert n(r"42") == "forty two"


def test_degrees():
    assert n(r"90^\circ") == "ninety degrees"


# --------------------------------------------------------------------------
# Text
# --------------------------------------------------------------------------
def test_text():
    assert n(r"\text{if } x>0") == "if x greater than zero"


def test_mathrm():
    assert n(r"\mathrm{d}x") == "d x"


# --------------------------------------------------------------------------
# The quadratic formula
# --------------------------------------------------------------------------
def test_quadratic():
    got = n(r"\frac{-b\pm\sqrt{b^2-4ac}}{2a}")
    assert got == (
        "minus b plus or minus square root of "
        "b squared minus four a c over two a"
    )


# --------------------------------------------------------------------------
# Chemistry
# --------------------------------------------------------------------------
def test_ce_water():
    assert n(r"\ce{H2O}") == "H two O"


def test_ce_reaction():
    assert n(r"\ce{2H2 + O2 -> 2H2O}") == (
        "two H two plus O two yields two H two O"
    )


def test_ce_sulfate():
    assert n(r"\ce{SO4^2-}") == "S O four two minus"


def test_ce_co2():
    assert read_ce("CO2") == "C O two"


def test_ce_h2so4():
    assert read_ce("H2SO4") == "H two S O four"


def test_ce_state():
    assert read_ce("NaCl(aq)") == "N a C l aqueous"


def test_ce_equilibrium():
    assert "in equilibrium with" in read_ce("N2 + 3H2 <=> 2NH3")


def test_bare_formula():
    assert looks_like_formula("H2O")
    assert read_formula("H2O") == "H two O"


def test_bare_formula_more():
    assert looks_like_formula("CO2")
    assert looks_like_formula("C6H12O6")
    assert looks_like_formula("NaCl")


def test_not_formula_acronyms():
    assert not looks_like_formula("NASA")
    assert not looks_like_formula("IPL")
    assert not looks_like_formula("Hi")
    assert not looks_like_formula("hello")
    assert not looks_like_formula("")


# --------------------------------------------------------------------------
# Environments
# --------------------------------------------------------------------------
def test_pmatrix():
    assert n(r"\begin{pmatrix}1&2\\3&4\end{pmatrix}") == (
        "matrix, row one one two, row two three four"
    )


def test_matrix():
    assert n(r"\begin{matrix}a&b\\c&d\end{matrix}") == (
        "matrix, row one a b, row two c d"
    )


def test_vmatrix():
    got = n(r"\begin{vmatrix}a&b\\c&d\end{vmatrix}")
    assert got.startswith("determinant")


def test_cases():
    got = n(r"\begin{cases}x & x>0 \\ -x & x<0\end{cases}")
    assert "; " in got
    assert got.split("; ")[0].strip() == "x x greater than zero"


def test_align():
    got = n(r"\begin{aligned}a &= b \\ c &= d\end{aligned}")
    assert got == "a equals b. c equals d"


# --------------------------------------------------------------------------
# convert_spans + pattern
# --------------------------------------------------------------------------
def test_convert_spans_inline():
    out = convert_spans("value is $x^2+1$ here")
    assert out == "value is  x squared plus one  here"


def test_convert_spans_display():
    out = convert_spans(r"see \[E=mc^2\] now")
    assert "E equals m c squared" in out


def test_convert_spans_paren():
    out = convert_spans(r"take \(\alpha\) please")
    assert " alpha " in out


def test_convert_spans_ce():
    out = convert_spans(r"water \ce{H2O} molecule")
    assert "H two O" in out


def test_convert_spans_env():
    out = convert_spans(r"M = \begin{pmatrix}1&2\\3&4\end{pmatrix} ok")
    assert "matrix" in out


def test_convert_spans_double_dollar():
    out = convert_spans(r"$$\frac{1}{2}$$")
    assert "one half" in out


def test_convert_spans_leaves_text():
    assert convert_spans("no math here") == "no math here"


def test_pattern_is_compiled():
    assert isinstance(LATEX_SPAN_PATTERN, re.Pattern)
    assert LATEX_SPAN_PATTERN.search("a $x$ b") is not None


# --------------------------------------------------------------------------
# Robustness: never raise
# --------------------------------------------------------------------------
@pytest.mark.parametrize(
    "bad",
    [
        r"\frac{1}{",
        r"\left( x",
        r"}{}\unknown^",
        r"\begin{matrix}a&b",
        r"^^^___",
        r"\sqrt[",
        r"$$$",
        r"\ce{",
        r"",
        r"\\\\",
        None,
    ],
)
def test_malformed_no_raise(bad):
    # Should never raise, always returns a string.
    assert isinstance(latex_to_speech(bad), str)


def test_convert_spans_malformed_no_raise():
    assert isinstance(convert_spans(r"broken $x^{ math $ here"), str)
    assert isinstance(convert_spans(None), str)


def test_unknown_command_degrades():
    # Unknown commands are dropped; identifiers still read.
    assert n(r"\foobar x + 1") == "x plus one"
