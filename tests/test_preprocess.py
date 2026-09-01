"""Tests for the preprocessing stages."""

from indic_normalizer.preprocess import (
    clean_controls,
    strip_escapes,
    protect_tags,
    restore_tags,
    strip_parentheses,
)


def test_clean_controls_whitespace():
    assert clean_controls("a\t\tb   c") == "a b c"
    assert clean_controls("line\nbreak") == "line break"


def test_clean_controls_zero_width():
    assert clean_controls("a​b‌c") == "abc"


def test_strip_escapes_literal():
    assert strip_escapes("hello\\nworld") == "hello world"
    assert strip_escapes("a\\tb") == "a b"


def test_strip_escapes_unicode():
    # A -> 'A'
    assert strip_escapes("\\u0041BC") == "ABC"


def test_strip_parentheses_nested():
    assert strip_parentheses("keep (drop (this) too) end") == "keep end"
    assert strip_parentheses("a (b) c") == "a c"


def test_protect_and_restore_tags():
    text = "say [emph] and <break time='1s'/> now"
    masked, store = protect_tags(text)
    assert "[emph]" not in masked and "<break" not in masked
    assert len(store) == 2
    restored = restore_tags(masked, store)
    assert restored == text


def test_tags_survive_parenthesis_stripping():
    text = "[tag] (remove me) <x>"
    masked, store = protect_tags(text)
    masked = strip_parentheses(masked)
    out = restore_tags(masked, store)
    assert "[tag]" in out and "<x>" in out and "remove me" not in out
