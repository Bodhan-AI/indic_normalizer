"""End-to-end normalization tests, incl. context & language resolution."""

from indic_normalizer import normalize


# ---- year vs cardinal context ----
def test_year_reading_en():
    assert normalize("India became free in 1947", lang="en") == \
        "India became free in nineteen forty seven"


def test_year_2024():
    assert "twenty twenty four" in normalize("in the year 2024", lang="en")


def test_number_before_sentence_period():
    # a trailing period must not be mistaken for a decimal point
    assert normalize("India became free in 1947.", lang="en") == \
        "India became free in nineteen forty seven."
    assert normalize("Score was 100.", lang="en") == "Score was one hundred."


def test_comma_forces_cardinal():
    out = normalize("There were 1,947 people", lang="en")
    assert "one thousand nine hundred" in out and "nineteen" not in out


def test_unit_forces_cardinal():
    out = normalize("The box weighs 1947 kg", lang="en")
    assert "one thousand nine hundred" in out
    assert "kilograms" in out


def test_currency_forces_cardinal():
    out = normalize("It costs ₹1947", lang="en")
    assert "one thousand nine hundred" in out and "rupees" in out


# ---- language resolution ----
def test_ascii_digits_default_english_in_hindi_sentence():
    out = normalize("भारत 1947 में", lang="hi")
    assert "nineteen forty seven" in out  # ASCII -> English


def test_native_digits_use_regional():
    # Devanagari 1947 in a Hindi sentence -> Hindi words (no ASCII letters)
    out = normalize("१९४७", lang="hi")
    assert out and not any(c.isascii() and c.isalpha() for c in out)


def test_forced_language():
    # forcing number_lang='hi' makes ASCII 1947 read exactly like native १९४७
    out = normalize("1947", lang="hi", number_lang="hi")
    assert out == normalize("१९४७", lang="hi")


# ---- semiotic classes ----
def test_percent():
    assert normalize("Growth was 12.5% this year", lang="en") == \
        "Growth was twelve point five percent this year"


def test_time_and_date():
    out = normalize("Meeting at 10:30 am on 15/08/1947", lang="en")
    assert "ten thirty am" in out
    assert "fifteenth August nineteen forty seven" in out


def test_phone_digit_by_digit():
    out = normalize("Call +91 98765 43210 now", lang="en")
    assert "plus nine one" in out
    assert "nine eight seven six five" in out


def test_ordinals():
    assert normalize("He came 21st in the 3rd race", lang="en") == \
        "He came twenty first in the third race"


def test_alphanumeric_split_keeps_latin():
    out = normalize("COVID19 and 5G", lang="en")
    assert "COVID nineteen" in out
    assert "five G" in out  # Latin 'G' preserved, not read as grams


# ---- artifacts & brackets ----
def test_parentheses_removed_tags_preserved():
    out = normalize("Remove (this aside) but keep [tag] and <break/>", lang="en")
    assert "(this aside)" not in out and "aside" not in out
    assert "[tag]" in out and "<break/>" in out


def test_escape_sequences_stripped():
    out = normalize("Line one\\nLine two\\there", lang="en")
    assert "\\n" not in out and "\\t" not in out


# ---- latex integration ----
def test_latex_inline():
    out = normalize("The formula is $x^2 + \\frac{a}{b}$ okay", lang="en")
    assert "x squared" in out and "a over b" in out


def test_latex_chemistry():
    out = normalize("Water is \\ce{H2O}", lang="hi")
    assert "H two O" in out
