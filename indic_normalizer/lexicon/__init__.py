"""Lexicon registry: build and cache one :class:`Lexicon` per language."""

from __future__ import annotations

from typing import Dict, List

from .base import Lexicon
from .tables import LEX_DATA

_CACHE: Dict[str, Lexicon] = {}


def get_lexicon(lang: str) -> Lexicon:
    """Return the cached :class:`Lexicon` for ``lang`` (built on first use)."""
    if lang not in _CACHE:
        overrides = LEX_DATA.get(lang, {})
        _CACHE[lang] = Lexicon(lang=lang, **overrides)
    return _CACHE[lang]


def list_review_flags() -> List[str]:
    """Return ``"<lang>: <field>"`` for every low-confidence lexicon entry."""
    out = []
    for lang in sorted(LEX_DATA):
        lex = get_lexicon(lang)
        for field in lex.review:
            out.append(f"{lang}: {field}")
    return out


__all__ = ["Lexicon", "get_lexicon", "list_review_flags"]
