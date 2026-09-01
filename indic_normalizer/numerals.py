"""Unicode numeral handling for Indic scripts.

We rely on :mod:`unicodedata` for decoding any Unicode decimal digit to its
value, and keep an explicit script -> (digit range, language hint) table so we
can (a) recognise native-script digits, and (b) name the script of a run of
digits. Language resolution for verbalization only needs: "is this digit
ASCII, or native-script?"  (see :mod:`indic_normalizer.normalizer`).
"""

from __future__ import annotations

import unicodedata
from typing import Optional

# Zero code point for each Indic (and Perso-Arabic) digit block we care about.
# value = codepoint - zero.
SCRIPT_DIGIT_ZERO = {
    "devanagari": 0x0966,   # ० hi, mr, ne, sa, kok, mai, brx, doi
    "bengali": 0x09E6,      # ০ bn, as, mni (Bengali script)
    "gurmukhi": 0x0A66,     # ੦ pa
    "gujarati": 0x0AE6,     # ૦ gu
    "oriya": 0x0B66,        # ୦ or
    "tamil": 0x0BE6,        # ௦ ta
    "telugu": 0x0C66,       # ౦ te
    "kannada": 0x0CE6,      # ೦ kn
    "malayalam": 0x0D66,    # ൦ ml
    "arabic": 0x0660,       # ٠ (Arabic-Indic) ur, sd, ks
    "arabic_ext": 0x06F0,   # ۰ (Extended Arabic-Indic) ur, ks
    "meetei": 0xABF0,       # ꯰ mni (Meetei Mayek)
    "olchiki": 0x1C50,      # ᱐ sat (Ol Chiki)
}

# Reverse lookup: value tables per script, built lazily.
_SCRIPT_DIGITS = {
    name: [chr(zero + d) for d in range(10)] for name, zero in SCRIPT_DIGIT_ZERO.items()
}

ASCII_DIGITS = set("0123456789")


def is_ascii_digit(ch: str) -> bool:
    """True if ``ch`` is one of "0"-"9"."""
    return ch in ASCII_DIGITS


def is_native_digit(ch: str) -> bool:
    """True if ``ch`` is a non-ASCII Unicode decimal digit (Indic/Perso-Arabic)."""
    if ch in ASCII_DIGITS:
        return False
    return ch.isdigit() and unicodedata.decimal(ch, None) is not None


def digit_value(ch: str) -> Optional[int]:
    """Numeric value of a single digit char (ASCII or native), else None."""
    if ch in ASCII_DIGITS:
        return ord(ch) - 48
    return unicodedata.decimal(ch, None)


def to_ascii_digits(s: str) -> str:
    """Convert every native digit in ``s`` to its ASCII equivalent.

    Non-digit characters are passed through unchanged.
    """
    out = []
    for ch in s:
        v = digit_value(ch)
        out.append(str(v) if (v is not None and ch.isdigit()) else ch)
    return "".join(out)


def digits_are_native(s: str) -> bool:
    """True if the run of digit characters in ``s`` contains any native digit."""
    return any(is_native_digit(ch) for ch in s if ch.isdigit())


def script_of_digits(s: str) -> Optional[str]:
    """Name of the digit script used in ``s`` (first native digit wins)."""
    for ch in s:
        if is_native_digit(ch):
            cp = ord(ch)
            for name, zero in SCRIPT_DIGIT_ZERO.items():
                if zero <= cp <= zero + 9:
                    return name
    return None
