"""Date robustness: invalid numeric dates + textual dates (audit plan step 6)."""

from indic_normalizer import normalize


# ---- invalid numeric dates must not leak to the fraction handler ----
def test_us_style_slash_date_swaps_to_valid():
    # 08/15 is invalid as day/month but valid as month/day
    assert normalize("08/15/1947 anniversary", lang="en") == \
        "fifteenth August nineteen forty seven anniversary"


def test_hopeless_date_reads_numbers_not_fraction():
    out = normalize("code 25/17/2020 file", lang="en")
    assert "over" not in out
    assert "twenty five" in out
    assert "seventeen" in out
    assert "twenty twenty" in out


# ---- textual dates (English) ----
def test_day_month_year():
    assert normalize("15 August 1947 dawn", lang="en") == \
        "fifteenth August nineteen forty seven dawn"


def test_day_monthabbr_year():
    assert normalize("15 Aug 1947 events", lang="en") == \
        "fifteenth August nineteen forty seven events"


def test_monthabbr_day_comma_year():
    assert normalize("Aug 15, 1947 issue", lang="en") == \
        "August fifteenth nineteen forty seven issue"


def test_month_day_comma_year():
    assert normalize("August 15, 1947 issue", lang="en") == \
        "August fifteenth nineteen forty seven issue"


def test_ordinal_day_month_year():
    assert normalize("born 2nd October 1869", lang="en") == \
        "born second October eighteen sixty nine"


def test_day_month_no_year():
    assert normalize("meeting on 5 June", lang="en") == "meeting on fifth June"


# ---- guards ----
def test_month_year_not_mangled():
    assert normalize("March 2020 lockdown", lang="en") == \
        "March twenty twenty lockdown"


def test_lowercase_may_without_year_left_alone():
    out = normalize("results may 15 improve", lang="en")
    assert "May fifteenth" not in out
    assert "fifteen" in out


def test_range_before_textual_month():
    out = normalize("15-16 August plans", lang="en")
    assert "fifteen to sixteen August" in out


def test_numeric_dates_still_work():
    out = normalize("Born 15/08/1947 and 2024-03-05", lang="en")
    assert "fifteenth August nineteen forty seven" in out
    assert "fifth March twenty twenty four" in out
