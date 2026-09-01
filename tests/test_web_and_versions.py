"""Email/URL reading + multi-dot version/IP numbers (audit plan step 7)."""

from indic_normalizer import normalize


# ---- versions & IPs ----
def test_version_three_components():
    assert normalize("Python 3.11.4 released", lang="en") == \
        "Python three point eleven point four released"


def test_ip_reads_digitwise_with_dot():
    assert normalize("server 192.168.1.1 up", lang="en") == \
        "server one nine two dot one six eight dot one dot one up"


def test_plain_decimal_unchanged():
    assert normalize("pi is 3.14", lang="en") == "pi is three point one four"


# ---- emails ----
def test_email_with_digits():
    assert normalize("mail test123@gmail.com now", lang="en") == \
        "mail test one two three at gmail dot com now"


def test_short_email():
    assert normalize("a@b.co works", lang="en") == "a at b dot co works"


# ---- urls ----
def test_www_url_with_path():
    assert normalize("visit www.example.com/page2 today", lang="en") == \
        "visit w w w dot example dot com slash page two today"


def test_bare_domain_dot_in():
    assert normalize("on flipkart.in sale", lang="en") == \
        "on flipkart dot in sale"


def test_https_url_drops_protocol():
    out = normalize("see https://docs.python.org/3 guide", lang="en")
    assert "docs dot python dot org slash three" in out
    assert "https" not in out


def test_url_trailing_period_preserved():
    out = normalize("Go to example.com.", lang="en")
    assert out == "Go to example dot com."


# ---- guards ----
def test_abbreviations_not_urls():
    out = normalize("e.g. this and etc. stay", lang="en")
    assert "dot" not in out


def test_word_in_after_period_not_tld():
    out = normalize("we trust in. God gave 42", lang="en")
    assert "dot" not in out
    assert "forty two" in out
