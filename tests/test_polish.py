"""P2 polish batch (audit plan step 8)."""

from indic_normalizer import normalize


# ---- money: zero major part drops "zero rupees and" ----
def test_zero_rupees_drops_major():
    assert normalize("₹0.50 candy", lang="en") == "fifty paise candy"


def test_zero_dollars_drops_major():
    assert normalize("$0.99 app", lang="en") == "ninety nine cents app"


def test_negative_money():
    assert normalize("Loss of ₹-500", lang="en") == \
        "Loss of minus five hundred rupees"


# ---- decades ----
def test_decade_4digit():
    assert normalize("the 1990s music", lang="en") == \
        "the nineteen nineties music"


def test_decade_2digit():
    assert normalize("back in the 90s era", lang="en") == \
        "back in the nineties era"


def test_decade_apostrophe():
    assert normalize("the 1980's style", lang="en") == \
        "the nineteen eighties style"


# ---- signs ----
def test_negative_measure():
    assert normalize("-5°C in Leh", lang="en") == \
        "minus five degrees celsius in Leh"


def test_negative_percent():
    assert normalize("-12% dip", lang="en") == "minus twelve percent dip"


def test_unicode_minus():
    assert normalize("−42 today", lang="en") == "minus forty two today"


def test_plus_number():
    assert normalize("+42 improvement", lang="en") == \
        "plus forty two improvement"


# ---- time: sentence period after am/pm survives ----
def test_ampm_keeps_sentence_period():
    out = normalize("at 10:30 am. Next day", lang="en")
    assert "ten thirty am. Next day" in out


def test_ampm_not_matched_inside_word():
    out = normalize("10:30 ample time", lang="en")
    assert "ample" in out


# ---- ratio / score ----
def test_score_ratio():
    assert normalize("won 3:2 against them", lang="en") == \
        "won three to two against them"


def test_aspect_ratio():
    assert normalize("a 16:9 screen", lang="en") == "a sixteen to nine screen"


# ---- comparisons spoken ----
def test_lt_gt_spoken():
    assert normalize("5 < 10 and 20 > 15", lang="en") == \
        "five less than ten and twenty greater than fifteen"


# ---- punctuation glue ----
def test_smiley_not_glued():
    assert normalize("great :) 42 done", lang="en") == "great :) forty two done"


def test_normal_punct_still_glued():
    assert normalize("wait , what ?", lang="en") == "wait, what?"
