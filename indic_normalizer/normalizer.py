"""The main normalization pipeline."""

from __future__ import annotations

import re
import unicodedata
from typing import Optional

from .config import NormalizerConfig
from .preprocess import (
    clean_controls,
    strip_escapes,
    protect_tags,
    restore_tags,
    strip_parentheses,
)
from .classes import Context, apply_all

_MULTISPACE = re.compile(r"[ \t]{2,}")
# glue only real sentence punctuation (followed by space/word/end) — not
# emoticons or punctuation clusters like ":)"
_SPACE_BEFORE_PUNCT = re.compile(r"\s+([,.;:!?%])(?=[\s\w]|$)")


def _latex_convert(text: str, verbosity: str) -> str:
    """Convert LaTeX spans if the engine is available; otherwise pass through."""
    try:
        from .latex import convert_spans
    except Exception:
        return text
    try:
        return convert_spans(text, verbosity=verbosity)
    except Exception:
        return text


class Normalizer:
    """Lightweight TTS pre-normalizer for Indic languages + English."""

    def __init__(self, lang: str = "en", config: Optional[NormalizerConfig] = None, **kwargs):
        if config is not None:
            self.cfg = config
        else:
            self.cfg = NormalizerConfig(lang=lang, **kwargs)
        self.ctx = Context(self.cfg)

    def normalize(self, text: str) -> str:
        """Normalize ``text`` to spoken form.

        Stages: control/unicode cleanup -> LaTeX spans -> escape stripping ->
        tag protection -> parenthetical removal -> semiotic-class handlers ->
        tag restore -> whitespace/punctuation tidy (NFC output).
        """
        if not text:
            return ""
        cfg = self.cfg

        # 1. control/whitespace/unicode cleanup (keeps backslashes for LaTeX)
        text = clean_controls(text)

        # 2. LaTeX spans -> spoken English (before bracket handling: \[ \] \( \))
        if cfg.latex:
            text = _latex_convert(text, cfg.latex_verbosity)

        # 3. escape-sequence artifacts (safe now that LaTeX is gone)
        if cfg.strip_escapes:
            text = strip_escapes(text)

        # 4. protect [..] and <..> tags
        text, tag_store = protect_tags(
            text,
            square=cfg.keep_square_brackets,
            angle=cfg.keep_angle_brackets,
        )

        # 5. remove parentheticals
        if cfg.strip_parentheses:
            text = strip_parentheses(text)

        # 6. semiotic-class verbalization
        text = apply_all(text, self.ctx, enable_roman=cfg.detect_roman)

        # 7. restore protected tags
        text = restore_tags(text, tag_store)

        # 8. final tidy
        text = _MULTISPACE.sub(" ", text)
        text = _SPACE_BEFORE_PUNCT.sub(r"\1", text)
        # number engines may emit decomposed Indic sequences; guarantee NFC
        # output so normalize() is idempotent and TTS sees stable codepoints
        text = unicodedata.normalize("NFC", text)
        return text.strip()


def normalize(text: str, lang: str = "en", **kwargs) -> str:
    """One-shot convenience wrapper."""
    return Normalizer(lang=lang, **kwargs).normalize(text)
