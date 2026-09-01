"""Number verbalization built on the vendored engine.

The vendored ``_numengine`` handles cardinals for all 22 scheduled languages +
English. This module wraps it with graceful fallbacks and adds the readings the
engine does not provide: decimals, digit-strings, ordinals, and year-style.
"""

from __future__ import annotations

import re
from typing import List, Optional

from ._numengine import num2words as _raw_num2words

from ..numerals import to_ascii_digits


def cardinal(value, lang: str = "en") -> str:
    """Return the primary cardinal reading of a non-negative integer.

    Never raises; on engine failure falls back to a digit-by-digit reading.
    """
    s = str(value)
    s = to_ascii_digits(s)
    s = re.sub(r"[^0-9]", "", s)
    if s == "":
        return ""
    try:
        out = _raw_num2words(s, lang=lang)
        if isinstance(out, list):
            out = out[0]
        if out and out.strip():
            return out.strip()
    except Exception:
        pass
    return split_digits(s, lang)


def cardinal_variations(value, lang: str = "en") -> List[str]:
    """All cardinal readings the engine offers for ``value`` (at least one)."""
    s = re.sub(r"[^0-9]", "", to_ascii_digits(str(value)))
    if not s:
        return []
    try:
        out = _raw_num2words(s, lang=lang, variations=True)
        if isinstance(out, str):
            out = [out]
        return [o.strip() for o in out if o and o.strip()]
    except Exception:
        return [cardinal(s, lang)]


def split_digits(digit_str: str, lang: str = "en") -> str:
    """Read each digit separately: '420' -> 'four two zero'."""
    s = to_ascii_digits(str(digit_str))
    words = []
    for ch in s:
        if ch.isdigit():
            try:
                w = _raw_num2words(ch, lang=lang)
                if isinstance(w, list):
                    w = w[0]
                words.append(w.strip())
            except Exception:
                words.append(ch)
    return " ".join(words)


def decimal(number_str: str, lang: str, lex) -> str:
    """Read a decimal: integer part as cardinal, fractional part digit-by-digit."""
    s = to_ascii_digits(number_str).strip()
    neg = s.startswith("-")
    s = s.lstrip("+-")
    int_part, _, frac_part = s.partition(".")
    int_part = int_part.replace(",", "")
    pieces = []
    if neg:
        pieces.append(lex.negative)
    pieces.append(cardinal(int_part or "0", lang))
    if frac_part:
        pieces.append(lex.decimal_point)
        pieces.append(split_digits(frac_part, lang))
    return " ".join(p for p in pieces if p)


def ordinal(value: int, lang: str, lex) -> str:
    """Ordinal reading: English forms for ``en``, else the lexicon's rule
    (irregular map, then cardinal + suffix)."""
    if lang == "en":
        return english_ordinal(value)
    return lex.ordinal(value, cardinal)


def year(value: int, lang: str, lex) -> str:
    """Year-style reading.

    English-style pairing (``nineteen forty-seven``) is used when the lexicon
    opts in (``year_pairing``); otherwise the full cardinal is used, which is
    the natural reading for most Indic languages.
    """
    v = int(value)
    if not lex.year_pairing or v < 1000 or v > 9999:
        return cardinal(v, lang)

    hi, lo = divmod(v, 100)

    # 2000-2009 read as full cardinal ("two thousand five"); 2010+ pairs nicely.
    if 2000 <= v <= 2009:
        return cardinal(v, lang)

    if lo == 0:
        return f"{cardinal(hi, lang)} {lex.year_hundred_word}"
    if lo < 10:
        # "nineteen oh five"
        return f"{cardinal(hi, lang)} {lex.year_oh_word} {cardinal(lo, lang)}"
    return f"{cardinal(hi, lang)} {cardinal(lo, lang)}"


# --- English ordinals (irregular) ---
_EN_IRREGULAR = {
    "one": "first", "two": "second", "three": "third", "five": "fifth",
    "eight": "eighth", "nine": "ninth", "twelve": "twelfth",
}


def english_ordinal(value: int) -> str:
    """English ordinal words: 21 -> "twenty first", 12 -> "twelfth"."""
    words = cardinal(value, "en")
    # operate on the final word (e.g. "twenty three" -> "twenty third")
    parts = words.replace("-", " ").split()
    if not parts:
        return words
    last = parts[-1]
    if last in _EN_IRREGULAR:
        parts[-1] = _EN_IRREGULAR[last]
    elif last.endswith("y"):
        parts[-1] = last[:-1] + "ieth"      # twenty -> twentieth
    else:
        parts[-1] = last + "th"
    return " ".join(parts)
