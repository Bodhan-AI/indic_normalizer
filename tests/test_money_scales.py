"""Currency scale words (lakh/crore) + singular units (audit plan step 4)."""

from indic_normalizer import normalize


# ---- scale words: amount + scale + currency, no paise misreading ----
def test_rupee_lakh():
    assert normalize("₹5 lakh was sanctioned", lang="en") == \
        "five lakh rupees was sanctioned"


def test_rs_decimal_crore():
    assert normalize("Rs 2.5 crore budget", lang="en") == \
        "two point five crore rupees budget"


def test_rupee_decimal_lakh():
    assert normalize("₹1.5 lakh fine", lang="en") == \
        "one point five lakh rupees fine"


def test_usd_million():
    assert normalize("a USD 50 million deal", lang="en") == \
        "a fifty million dollars deal"


def test_hindi_native_scale():
    out = normalize("₹५ लाख की लागत", lang="hi")
    assert "पाँच लाख रुपये" in out


def test_scale_word_prefix_not_matched():
    # "lakhpati" is not a scale word
    out = normalize("Rs 100 lakhpati", lang="en")
    assert "one hundred rupees lakhpati" in out


# ---- singular units ----
def test_one_rupee():
    assert normalize("a ₹1 coin", lang="en") == "a one rupee coin"


def test_one_dollar():
    assert normalize("a $1 bill", lang="en") == "a one dollar bill"


def test_one_rupee_one_paisa():
    assert normalize("₹1.01 exactly", lang="en") == \
        "one rupee and one paisa exactly"


def test_plural_still_plural():
    out = normalize("₹2 given", lang="en")
    assert "two rupees" in out
