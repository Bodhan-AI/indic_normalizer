"""Bracket handling.

* ``(...)`` — removed entirely (content included), honouring nesting.
* ``[...]`` and ``<...>`` — *preserved verbatim*; they are SSML / prosody
  markers or tags. They are masked with private-use sentinels before the rest
  of the pipeline runs, then restored unchanged at the very end.
"""

from __future__ import annotations

import re
from typing import List, Tuple

# Private-use sentinels wrapping a PUA-digit-encoded index. Using PUA "digit"
# chars (0xE100+d) means the sentinel contains no ASCII digits/letters/
# punctuation, so no class handler can match or corrupt it.
_OPEN = ""
_CLOSE = ""
_PUA0 = 0xE100

_SQUARE = re.compile(r"\[[^\[\]]*\]")
# Only tag-shaped spans (<name...>, </name>, <!...>): a bare "<" used as a
# comparison operator ("5 < 10") must stay visible to the number handlers.
_ANGLE = re.compile(r"</?[A-Za-z!][^<>]*>")


def _encode(i: int) -> str:
    return "".join(chr(_PUA0 + int(c)) for c in str(i))


def _decode(s: str) -> int:
    return int("".join(str(ord(c) - _PUA0) for c in s))


def protect_tags(text: str, square: bool = True, angle: bool = True) -> Tuple[str, List[str]]:
    """Replace ``[...]`` / ``<...>`` spans with sentinels; return (masked, store)."""
    store: List[str] = []

    def _mask(m: re.Match) -> str:
        idx = len(store)
        store.append(m.group(0))
        return f"{_OPEN}{_encode(idx)}{_CLOSE}"

    if square:
        text = _SQUARE.sub(_mask, text)
    if angle:
        text = _ANGLE.sub(_mask, text)
    return text, store


_RESTORE = re.compile(_OPEN + f"([{chr(_PUA0)}-{chr(_PUA0 + 9)}]+)" + _CLOSE)


def restore_tags(text: str, store: List[str]) -> str:
    """Re-insert the spans masked by :func:`protect_tags` (its inverse)."""
    def _un(m: re.Match) -> str:
        return store[_decode(m.group(1))]

    return _RESTORE.sub(_un, text)


_PAREN_INNER = re.compile(r"\([^()]*\)")


def strip_parentheses(text: str) -> str:
    """Remove balanced ``(...)`` spans including nested content.

    Only balanced pairs are removed (innermost-first); an unmatched "(" or ")"
    is kept as a literal so it cannot swallow the rest of the utterance.
    """
    prev = None
    while prev != text:
        prev = text
        text = _PAREN_INNER.sub("", text)
    result = text
    # tidy spaces left behind, and stray space before punctuation
    result = re.sub(r"[ \t]{2,}", " ", result)
    result = re.sub(r"\s+([,.;:!?])(?=[\s\w]|$)", r"\1", result)
    return result.strip()
