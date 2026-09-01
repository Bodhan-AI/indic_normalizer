"""Ordered registry of semiotic-class handlers."""

from __future__ import annotations

from typing import Callable, List, Tuple

from .base import Context
from . import handlers as H

# (name, callable, default_enabled). Order = application order (specific first).
_REGISTRY: List[Tuple[str, Callable, bool]] = [
    ("web", H.web_, True),                # emails/URLs first: nothing may mangle them
    ("abbrev", H.abbrev_, True),          # titles, etc./vs., dotted acronyms
    ("time", H.time_, True),
    ("ratio", H.ratio_, True),            # "3:2", "16:9" (colon pairs time rejected)
    ("date", H.date_, True),
    ("textdate", H.textdate_, True),      # "15 August 1947", "Aug 15, 1947"
    ("money", H.money_, True),
    ("range", H.range_, True),            # before percent: "10-15%" -> "ten to fifteen percent"
    ("percent", H.percent_, True),
    ("ids", H.ids_, True),                # PAN/IFSC/plates/PIN before measure
    ("bp", H.bp_, True),                  # "120/80 mmHg" before measure eats "80 mmHg"
    ("measure", H.measure_, True),
    ("native_scale", H.native_scale_, True),  # "2 करोड़" -> number in the scale's language
    ("scientific", H.scientific_, True),  # "1.5e10" before alphanumeric split
    ("code", H.code_, True),              # "AB123CD"/"6E204" spelled out
    ("decade", H.decade_, True),          # before alphanumeric: keep "1990s" intact
    ("ordinal", H.ordinal_, True),        # before alphanumeric: keep "21st" intact
    ("alphanumeric", H.alphanumeric_split, True),  # split COVID19 -> COVID 19
    ("phone", H.phone_, True),
    ("dotted", H.dotted_, True),          # versions/IPs before fraction/decimal
    ("cricket", H.cricket_, True),        # "287/5" + cricket word -> "for" reading
    ("fraction", H.fraction_, True),
    ("decimal", H.decimal_, True),
    ("position", H.position_, True),      # "room 225" -> "two twenty five"
    ("number", H.number_, True),
    ("symbol", H.symbol_, True),
    ("roman_ctx", H.roman_ctx_, True),    # "Chapter IV": trigger word makes it safe
    ("roman", H.roman_, False),   # opt-in: risky on ordinary uppercase words
]


def apply_all(text: str, ctx: Context, enable_roman: bool = False) -> str:
    """Run every enabled handler over ``text`` in registry (priority) order."""
    for name, fn, default in _REGISTRY:
        if name == "roman" and not enable_roman:
            continue
        if not default and not (name == "roman" and enable_roman):
            continue
        text = fn(text, ctx)
    return text


__all__ = ["Context", "apply_all"]
