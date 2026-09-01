"""Configuration for the normalizer pipeline."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Optional, Tuple

# The 22 scheduled languages of India + English, with the ISO codes used by the
# vendored number engine.
SUPPORTED_LANGS = (
    "as",   # Assamese
    "bn",   # Bengali
    "brx",  # Bodo
    "doi",  # Dogri
    "en",   # English (Indian)
    "gu",   # Gujarati
    "hi",   # Hindi
    "kn",   # Kannada
    "ks",   # Kashmiri
    "kok",  # Konkani
    "mai",  # Maithili
    "ml",   # Malayalam
    "mni",  # Manipuri (Meitei)
    "mr",   # Marathi
    "ne",   # Nepali
    "or",   # Odia
    "pa",   # Punjabi
    "sa",   # Sanskrit
    "sat",  # Santali
    "sd",   # Sindhi
    "ta",   # Tamil
    "te",   # Telugu
    "ur",   # Urdu
)


@dataclass
class NormalizerConfig:
    """Options controlling normalization.

    Attributes:
        lang: The sentence's (regional) language. Drives lexicon selection and
            the verbalization language for native-script digits.
        number_lang: If set, force ALL numbers to be verbalized in this
            language, overriding script-based resolution. ``force=True`` is a
            shorthand that sets this to ``lang``.
        force: Shorthand: force all numbers into ``lang``.
        default_number_lang: Language used for ASCII/Arabic (0-9) digits when
            not forced. Defaults to English, matching common Indian TTS usage.
        strip_parentheses: Remove ``(...)`` spans (content included).
        keep_square_brackets / keep_angle_brackets: Preserve ``[...]`` / ``<...>``
            spans verbatim (SSML / prosody markers).
        strip_escapes: Decode & strip escape sequences and control chars.
        latex: Convert LaTeX math spans to spoken English (auto-detect).
        latex_verbosity: "natural" or "explicit".
        detect_years: Enable year-style reading heuristic.
        year_range: Inclusive [lo, hi] range treated as candidate years.
        detect_positions: Read 3-4 digit numbers after position words
            (room/page/flight/gate/bus) in pairing style: "room 225" ->
            "room two twenty five" (English only).
        emit_variations: If True, ``normalize`` may annotate alt readings
            (currently used by the number layer for debugging/inspection).
    """

    lang: str = "en"
    number_lang: Optional[str] = None
    force: bool = False
    default_number_lang: str = "en"

    strip_parentheses: bool = True
    keep_square_brackets: bool = True
    keep_angle_brackets: bool = True
    strip_escapes: bool = True

    latex: bool = True
    latex_verbosity: str = "natural"

    detect_years: bool = True
    year_range: Tuple[int, int] = (1100, 2099)
    detect_positions: bool = True
    detect_roman: bool = False   # convert roman numerals (opt-in; risky)

    emit_variations: bool = False

    def __post_init__(self):
        if self.lang not in SUPPORTED_LANGS:
            raise ValueError(
                f"Unsupported lang {self.lang!r}. Supported: {', '.join(SUPPORTED_LANGS)}"
            )
        if self.force and self.number_lang is None:
            self.number_lang = self.lang
        if self.number_lang is not None and self.number_lang not in SUPPORTED_LANGS:
            raise ValueError(f"Unsupported number_lang {self.number_lang!r}")

    def resolve_number_lang(self, native: bool) -> str:
        """Pick the language to verbalize a number in.

        1. forced ``number_lang`` wins;
        2. else native-script digits -> the sentence language;
        3. else (ASCII digits) -> ``default_number_lang`` (English).
        """
        if self.number_lang is not None:
            return self.number_lang
        if native:
            return self.lang
        return self.default_number_lang
