"""Regression tests for P0 bugs found in the 2026-08 edge-case audit."""

from indic_normalizer import normalize


# ---- P0-1: currency tokens must not match inside words ("years 2020") ----
def test_word_ending_in_rs_is_not_currency():
    out = normalize("last 5 years 2020 was worst", lang="en")
    assert "rupees" not in out
    assert "years" in out
    assert "twenty twenty" in out  # year reading survives


def test_hours_not_read_as_rupees():
    out = normalize("two hours 30 minutes", lang="en")
    assert "rupees" not in out
    assert "hours" in out


def test_real_currency_still_works():
    assert "rupees" in normalize("Rs 100 fee", lang="en")
    assert "rupees" in normalize("It costs ₹1947", lang="en")


# ---- P0-2: bare $...$ must not bridge two currency amounts ----
def test_two_dollar_amounts_not_eaten_as_latex():
    out = normalize("I paid $5 and she paid $10 yesterday.", lang="en")
    assert "five dollars" in out
    assert "ten dollars" in out
    assert "she paid" in out


def test_currency_dollar_range():
    out = normalize("$5-$10 range", lang="en")
    assert "five dollars" in out
    assert "ten dollars" in out


def test_math_after_currency_dollar():
    out = normalize("cost $5 and $x+y$ math", lang="en")
    assert "five dollars" in out
    assert "x plus y" in out


def test_single_variable_dollar_math_still_spoken():
    out = normalize("let $n$ be even", lang="en")
    assert "$" not in out


# ---- P0-3: unbalanced '(' must not delete the rest of the input ----
def test_unbalanced_open_paren_keeps_text():
    out = normalize("a ( b 42", lang="en")
    assert "b" in out
    assert "forty two" in out


def test_balanced_parens_still_stripped():
    out = normalize("text (remove (this) too) kept", lang="en")
    assert out == "text kept"


# ---- P0-4: angle masking must only protect tag-shaped spans ----
def test_comparison_operators_not_masked_as_tags():
    out = normalize("5 < 10 and 20 > 15", lang="en")
    assert "five" in out
    assert "ten" in out
    assert "twenty" in out
    assert "fifteen" in out


def test_real_tags_still_preserved():
    out = normalize("Hello <break time='1s'/> world </emphasis> 42", lang="en")
    assert "<break time='1s'/>" in out
    assert "</emphasis>" in out
    assert "forty two" in out
