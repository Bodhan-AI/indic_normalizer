"""Shared context and helpers for semiotic-class handlers.

Each handler is a callable ``(text, ctx) -> text`` that rewrites the spans it
recognises into spoken words. Handlers run in a fixed priority order (specific
-> general); because each handler replaces its matches with *words*, later
numeric handlers never re-match already-verbalized spans.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Tuple

from ..config import NormalizerConfig
from ..lexicon import get_lexicon, Lexicon
from ..numerals import digits_are_native


@dataclass
class Context:
    """Per-run state shared by all handlers: the config plus number-language
    and lexicon resolution."""

    cfg: NormalizerConfig

    @property
    def sentence_lex(self) -> Lexicon:
        """Lexicon of the sentence language (``cfg.lang``)."""
        return get_lexicon(self.cfg.lang)

    def resolve(self, sample: str) -> Tuple[str, Lexicon]:
        """Resolve the verbalization language + lexicon for a numeric token.

        ``sample`` is the raw matched digit text; native-script digits route to
        the sentence language, ASCII digits to English (unless forced).
        """
        native = digits_are_native(sample)
        lang = self.cfg.resolve_number_lang(native)
        return lang, get_lexicon(lang)
