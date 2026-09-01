"""Artifact stripping: control chars, escape sequences, whitespace, unicode.

Split into two phases so LaTeX (which is full of backslashes) can be extracted
in between:

* :func:`clean_controls` — safe to run first; NFC-normalizes, drops control &
  zero-width characters, and collapses whitespace. Leaves backslashes intact.
* :func:`strip_escapes` — run AFTER LaTeX extraction; decodes literal ``\\uXXXX``
  / ``\\xHH`` sequences and removes leftover escape artifacts (``\\n``, ``\\t``,
  stray backslashes).
"""

from __future__ import annotations

import re
import unicodedata

# Zero-width / formatting characters that add nothing for TTS.
_ZERO_WIDTH = "​‌‍‎‏﻿⁠"

_LITERAL_ESCAPE = re.compile(r"\\[nrtfv0]")
_UNICODE_ESCAPE = re.compile(r"\\u([0-9A-Fa-f]{4})|\\x([0-9A-Fa-f]{2})")
_STRAY_BACKSLASH = re.compile(r"\\+")
_WS = re.compile(r"[ \t ]+")
_MULTI_NL = re.compile(r"\s*\n\s*")


def _strip_control(text: str) -> str:
    out = []
    for ch in text:
        if ch in _ZERO_WIDTH:
            continue
        cat = unicodedata.category(ch)
        if cat in ("Cc", "Cf") and ch not in ("\n", "\t"):
            continue  # drop other control/format chars
        out.append(ch)
    return "".join(out)


def clean_controls(text: str, collapse_newlines: bool = True) -> str:
    """NFC-normalize, drop control/zero-width chars, collapse whitespace."""
    text = unicodedata.normalize("NFC", text)
    text = text.replace("−", "-")  # unicode minus -> ASCII hyphen-minus
    text = _strip_control(text)
    text = text.replace("\t", " ")
    if collapse_newlines:
        text = _MULTI_NL.sub(" ", text)
    text = _WS.sub(" ", text)
    return text.strip()


def _decode_unicode_escape(m: re.Match) -> str:
    hexval = m.group(1) or m.group(2)
    try:
        return chr(int(hexval, 16))
    except ValueError:  # pragma: no cover
        return " "


def strip_escapes(text: str) -> str:
    """Decode/strip escape-sequence artifacts. Run after LaTeX extraction."""
    text = _UNICODE_ESCAPE.sub(_decode_unicode_escape, text)
    text = _LITERAL_ESCAPE.sub(" ", text)
    text = _STRAY_BACKSLASH.sub(" ", text)
    # a decode step may have introduced control/zero-width chars
    text = _strip_control(text)
    text = _WS.sub(" ", text)
    return text.strip()
