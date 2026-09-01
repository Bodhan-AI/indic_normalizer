"""Numeric range handler: N-M -> 'N to M' (audit plan step 2)."""

from indic_normalizer import normalize


def test_year_range():
    assert normalize("1939-1945 war", lang="en") == \
        "nineteen thirty nine to nineteen forty five war"


def test_year_range_en_dash():
    assert normalize("the 1914–1918 conflict", lang="en") == \
        "the nineteen fourteen to nineteen eighteen conflict"


def test_page_range():
    assert normalize("pages 10-15", lang="en") == "pages ten to fifteen"


def test_percent_range():
    assert normalize("10-15% growth", lang="en") == \
        "ten to fifteen percent growth"


def test_unit_range():
    assert normalize("carry 5-10 kg only", lang="en") == \
        "carry five to ten kilograms only"


def test_fiscal_year_style():
    out = normalize("FY 2024-25 results", lang="en")
    assert "twenty twenty four to twenty five" in out


def test_range_trailing_period():
    assert normalize("It lasted 1939-1945.", lang="en") == \
        "It lasted nineteen thirty nine to nineteen forty five."


def test_native_digit_range_hindi():
    out = normalize("१०-१५ लोग", lang="hi")
    assert "दस से पंद्रह" in out


# ---- guards: phone-shaped strings must stay digit-by-digit ----
def test_hyphenated_phone_three_groups_still_phone():
    out = normalize("Call 011-2345-6789", lang="en")
    assert "zero one one two three four five six seven eight nine" in out
    assert " to " not in out


def test_hyphenated_phone_two_long_groups_still_phone():
    out = normalize("Call 98765-43210", lang="en")
    assert "nine eight seven six five four three two one zero" in out
    assert " to " not in out


def test_hyphen_date_still_date():
    out = normalize("Born 15-08-1947 in Delhi", lang="en")
    assert "fifteenth August nineteen forty seven" in out
