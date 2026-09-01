"""Per-language lexicon: the glue words the number engine cannot provide.

Each language ships a :class:`Lexicon` instance in ``lexicon/data/<lang>.py``.
Entries that could not be verified by a native speaker are marked in the
``review`` set (their keys) so they can be surfaced for follow-up.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple


@dataclass
class Lexicon:
    """Per-language glue words the number engine cannot provide: decimal
    point, percent, currency units, months, ordinal rules, connectors.
    Fields left at their defaults fall back to English wording; ``review``
    names entries still awaiting native-speaker verification."""

    lang: str

    # --- number glue ---
    decimal_point: str = "point"        # spoken form of "."
    negative: str = "minus"             # spoken form of a leading "-"
    connector_and: str = "and"          # generic "and"
    percent: str = "percent"
    range_to: str = "to"                # "10-15" -> "ten TO fifteen"

    # Year reading conventions (English-style pairing is off for most Indic langs)
    year_pairing: bool = False
    year_hundred_word: str = "hundred"  # "nineteen hundred"
    year_oh_word: str = "oh"            # "nineteen oh five"

    # Ordinals: a small irregular map (value -> word) plus a generic suffix that
    # is appended to the cardinal for everything else. English overrides
    # ``ordinal`` entirely (see data/en.py).
    ordinal_suffix: str = ""
    ordinal_irregular: Dict[int, str] = field(default_factory=dict)

    # --- symbols read literally when standalone / between tokens ---
    symbols: Dict[str, str] = field(default_factory=dict)

    # --- currency: symbol OR ISO code -> (major_unit, minor_unit) ---
    currency: Dict[str, Tuple[str, str]] = field(default_factory=dict)

    # --- units of measure: token -> spoken word ---
    units: Dict[str, str] = field(default_factory=dict)

    # --- months 1..12 -> name ---
    months: Dict[int, str] = field(default_factory=dict)

    # --- context trigger words (lowercased) that hint a nearby number is a year ---
    year_trigger_words: Tuple[str, ...] = ()
    # trigger words that hint a date context
    date_trigger_words: Tuple[str, ...] = ()

    # keys of any of the above that are low-confidence and need native review
    review: Tuple[str, ...] = ()

    def ordinal(self, value: int, cardinal_fn) -> str:
        """Default ordinal formation: irregular map, else cardinal + suffix."""
        if value in self.ordinal_irregular:
            return self.ordinal_irregular[value]
        base = cardinal_fn(value, self.lang)
        if self.ordinal_suffix:
            return f"{base}{self.ordinal_suffix}"
        return base
