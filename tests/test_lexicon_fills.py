# -*- coding: utf-8 -*-
"""Lexicon review-flag cleanup: months, pa/ur ordinals, Devanagari-language
glue words, best-effort ks/sd/sa fills (still review-flagged)."""

from indic_normalizer import normalize
from indic_normalizer.lexicon import list_review_flags


# ---- month names in dates ----
def test_bengali_month():
    out = normalize("১৫/৮/১৯৪৭", lang="bn")
    assert "আগস্ট" in out


def test_tamil_month():
    out = normalize("௧௫/௮/௧௯௪௭", lang="ta")
    assert "ஆகஸ்ட்" in out


def test_marathi_month():
    out = normalize("१५/८/१९४७", lang="mr")
    assert "ऑगस्ट" in out


def test_kashmiri_month_urdu_forms():
    out = normalize("۱۵/۸/۱۹۴۷", lang="ks")
    assert "اگست" in out


# ---- pa / ur ordinals (concatenation-safe) ----
def test_punjabi_ordinal_regular():
    assert normalize("5ਵਾਂ ਦਿਨ", lang="pa") == "ਪੰਜਵਾਂ ਦਿਨ"


def test_punjabi_ordinal_irregular():
    assert normalize("2ਵਾਂ", lang="pa") == "ਦੂਜਾ"


def test_urdu_ordinal_irregular():
    assert normalize("2واں", lang="ur") == "دوسرا"


# ---- Devanagari-language glue words (Hindi loans) ----
def test_maithili_decimal_point():
    assert "दशमलव" in normalize("३.१४", lang="mai")


def test_konkani_percent():
    assert "प्रतिशत" in normalize("५०%", lang="kok")


def test_dogri_currency():
    assert "रुपये" in normalize("₹५००", lang="doi")


def test_maithili_range():
    assert "से" in normalize("१०-१५", lang="mai")


def test_maithili_money_connector_not_english():
    out = normalize("₹५०.५०", lang="mai")
    assert " and " not in out
    assert "रुपये" in out and "पैसे" in out


# ---- review flags: filled-and-trusted cleared, best-effort kept ----
def test_review_flags_state():
    flags = list_review_flags()
    assert "bn: months" not in flags       # trusted fill
    assert "pa: ordinal" not in flags      # trusted fill
    assert "mai: decimal_point" not in flags
    assert "ta: ordinal" in flags          # sandhi: needs a native-informed rule
    assert "ks: months" in flags           # filled best-effort, still flagged
    assert "sat: months" in flags          # still missing
