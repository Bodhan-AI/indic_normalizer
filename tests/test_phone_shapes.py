"""Phone-shape tightening + leading-zero reading (audit plan step 3)."""

from indic_normalizer import normalize


# ---- false positives: number lists must not become phone numbers ----
def test_year_pair_not_phone():
    out = normalize("years 2020 2021 were tough", lang="en")
    assert "twenty twenty" in out
    assert "twenty twenty one" in out


def test_year_list_not_phone():
    out = normalize("from 2019 2020 2021 sessions", lang="en")
    assert "twenty nineteen" in out
    assert "twenty twenty one" in out


def test_small_number_list_not_phone():
    out = normalize("scores 100 200 300 today", lang="en")
    assert "one hundred two hundred three hundred" in out


def test_long_decimal_reads_point_not_digits():
    out = normalize("pi is 3.14159265358979", lang="en")
    assert "three point one four one five nine" in out


# ---- true phones keep working ----
def test_intl_mobile_still_phone():
    out = normalize("Call +91 98765 43210 now", lang="en")
    assert "plus nine one nine eight seven six five four three two one zero" in out


def test_bare_mobile_5_5_still_phone():
    out = normalize("Call 98765 43210", lang="en")
    assert "nine eight seven six five four three two one zero" in out


def test_contiguous_10_digit_still_phone():
    out = normalize("Call 9876543210", lang="en")
    assert "nine eight seven six five four three two one zero" in out


def test_aadhaar_4_4_4_still_digitwise():
    out = normalize("Aadhaar 1234 5678 9012", lang="en")
    assert "one two three four five six seven eight nine zero one two" in out


def test_landline_3_4_4_still_phone():
    out = normalize("Call 011-2345-6789", lang="en")
    assert "zero one one two three four five six seven eight nine" in out


# ---- leading zeros read digit-by-digit ----
def test_leading_zero_code():
    assert normalize("dial 0091 first", lang="en") == "dial zero zero nine one first"


def test_agent_007():
    assert normalize("agent 007 reporting", lang="en") == \
        "agent zero zero seven reporting"


def test_plain_zero_unchanged():
    assert normalize("0 items", lang="en") == "zero items"
