"""Lightweight Unicode script detection (used for diagnostics / future hooks)."""

from __future__ import annotations

from typing import Optional

# (lo, hi, script-name) ranges for the scripts we care about.
_RANGES = [
    (0x0900, 0x097F, "devanagari"),
    (0x0980, 0x09FF, "bengali"),
    (0x0A00, 0x0A7F, "gurmukhi"),
    (0x0A80, 0x0AFF, "gujarati"),
    (0x0B00, 0x0B7F, "oriya"),
    (0x0B80, 0x0BFF, "tamil"),
    (0x0C00, 0x0C7F, "telugu"),
    (0x0C80, 0x0CFF, "kannada"),
    (0x0D00, 0x0D7F, "malayalam"),
    (0x0600, 0x06FF, "arabic"),
    (0x1C50, 0x1C7F, "olchiki"),
    (0xABC0, 0xABFF, "meetei"),
    (0x0041, 0x007A, "latin"),
]


def char_script(ch: str) -> Optional[str]:
    """Name of the script block ``ch`` belongs to, else None."""
    cp = ord(ch)
    for lo, hi, name in _RANGES:
        if lo <= cp <= hi:
            return name
    return None


def dominant_script(text: str) -> Optional[str]:
    """Most frequent non-Latin script in ``text``; "latin" if only Latin
    is present, None if no known script at all."""
    counts = {}
    for ch in text:
        s = char_script(ch)
        if s and s != "latin":
            counts[s] = counts.get(s, 0) + 1
    if not counts:
        return "latin" if any(char_script(c) == "latin" for c in text) else None
    return max(counts, key=counts.get)
